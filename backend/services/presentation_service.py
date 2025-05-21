import asyncio
import os
import json
from typing import List, Dict, Any
from sqlalchemy.future import select
from sqlalchemy import update
import traceback

from database import SessionLocal, PresentationStepModel, PresentationStep, StepStatus, Presentation
from models import ResearchData, SlidePresentation, ImageGeneration
from tools import (
    research_topic,
    process_manual_research,
    generate_slides,
    generate_slide_images,
    generate_image_from_prompt,
    generate_compiled_presentation,
    generate_pptx_from_slides, 
    convert_pptx_to_png
)
from tools.images import _generate_image_for_slide
from config import PRESENTATIONS_STORAGE_DIR

# Background task functions
async def execute_research_task(presentation_id: int, topic: str, author: str = None):
    """Execute research task for a presentation"""
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Update step status to processing
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.RESEARCH.value
                )
            )
            step = step_result.scalars().first()
            
            if not step:
                return
            
            # Get presentation to retrieve author if needed
            presentation_result = await db.execute(
                select(Presentation).filter(Presentation.id == presentation_id)
            )
            presentation = presentation_result.scalars().first()
            
            # If author wasn't provided, use it from the presentation
            if author is None and presentation and presentation.author:
                author = presentation.author
            
            # Run research tool
            research_data = await research_topic(topic)
            
            # Update step with result
            step.set_result(research_data.model_dump())
            step.status = StepStatus.COMPLETED.value
            await db.commit()
            
        except Exception as e:
            # Update step status to failed
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.RESEARCH.value
                )
            )
            step = step_result.scalars().first()
            
            if step:
                step.status = StepStatus.FAILED.value
                step.set_result({"error": str(e)})
                await db.commit()

async def execute_manual_research_task(presentation_id: int, research_content: str):
    """Execute manual research task for a presentation"""
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Update step status to processing
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.MANUAL_RESEARCH.value
                )
            )
            step = step_result.scalars().first()
            
            if not step:
                return
            
            # Process manual research
            research_data = await process_manual_research(research_content)
            
            # Update step with result
            step.set_result(research_data.model_dump())
            step.status = StepStatus.COMPLETED.value
            await db.commit()
            
        except Exception as e:
            # Update step status to failed
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.MANUAL_RESEARCH.value
                )
            )
            step = step_result.scalars().first()
            
            if step:
                step.status = StepStatus.FAILED.value
                step.set_result({"error": str(e)})
                await db.commit()

async def execute_slides_task(presentation_id: int):
    """Execute slides generation task for a presentation"""
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Get presentation to retrieve author
            presentation_result = await db.execute(
                select(Presentation).filter(Presentation.id == presentation_id)
            )
            presentation = presentation_result.scalars().first()
            author = None
            if presentation:
                author = presentation.author
            
            # Get research data - first try regular research
            research_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.RESEARCH.value
                )
            )
            research_step = research_result.scalars().first()
            
            # If no regular research found, try manual research
            if not research_step or research_step.status != StepStatus.COMPLETED.value:
                manual_research_result = await db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.MANUAL_RESEARCH.value
                    )
                )
                research_step = manual_research_result.scalars().first()
                
                # If still no valid research found, exit
                if not research_step or research_step.status != StepStatus.COMPLETED.value:
                    return
            
            # Get slides step
            slides_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.SLIDES.value
                )
            )
            slides_step = slides_result.scalars().first()
            
            if not slides_step:
                return
            
            # Mark slides step as processing
            slides_step.status = StepStatus.PROCESSING.value
            await db.commit()
            
            # Convert research data to ResearchData model
            research_data = ResearchData(**research_step.get_result())
            
            # Use default 10 slides
            target_slides = 10
            
            # Run slides generation tool with author
            slides_data = await generate_slides(research_data, target_slides, author)
            
            # Update slides step with result
            slides_step.set_result(slides_data.model_dump())
            slides_step.status = StepStatus.COMPLETED.value
            await db.commit()
            
        except Exception as e:
            # Update step status to failed
            slides_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.SLIDES.value
                )
            )
            slides_step = slides_result.scalars().first()
            
            if slides_step:
                slides_step.status = StepStatus.FAILED.value
                slides_step.set_result({"error": str(e)})
                await db.commit()

async def execute_images_task(presentation_id: int):
    """
    Background task to generate images for presentation slides
    """
    # Create a new session for the background task
    async with SessionLocal() as db:
        # Get the presentation
        result = await db.execute(select(Presentation).filter(Presentation.id == presentation_id))
        presentation = result.scalars().first()
        
        if not presentation:
            print(f"Presentation {presentation_id} not found")
            return
        
        # Get the slides step
        slides_step_result = await db.execute(
            select(PresentationStepModel).filter(
                PresentationStepModel.presentation_id == presentation_id,
                PresentationStepModel.step == PresentationStep.SLIDES.value
            )
        )
        slides_step = slides_step_result.scalars().first()
        
        if not slides_step or slides_step.status != StepStatus.COMPLETED.value:
            print(f"Slides step not completed for presentation {presentation_id}")
            return
        
        # Get the images step
        images_step_result = await db.execute(
            select(PresentationStepModel).filter(
                PresentationStepModel.presentation_id == presentation_id,
                PresentationStepModel.step == PresentationStep.IMAGES.value
            )
        )
        images_step = images_step_result.scalars().first()
        
        if not images_step:
            print(f"Images step not found for presentation {presentation_id}")
            return
        
        # If images step is already completed, don't regenerate images
        if images_step.status == StepStatus.COMPLETED.value:
            print(f"Images already generated for presentation {presentation_id}")
            return
            
        slides_data = slides_step.get_result()
        if not slides_data:
            print(f"No slides data found for presentation {presentation_id}")
            return
        
        try:
            # Mark images step as processing and close current DB session
            images_step.status = StepStatus.PROCESSING.value
            await db.commit()
            await db.close()

            slides_obj = SlidePresentation(**slides_data)
            accumulated_images: List[Dict[str, Any]] = []

            # Generate images sequentially so we can store each one as it is created
            for index, slide in enumerate(slides_obj.slides):
                try:
                    result_list = await asyncio.get_event_loop().run_in_executor(
                        image_executor,
                        _generate_image_for_slide,
                        slide,
                        index,
                        presentation_id,
                    )
                except Exception as gen_err:
                    print(f"Error generating image for slide {index}: {gen_err}")
                    result_list = []

                for img in result_list:
                    img_dict = img.model_dump()
                    if 'image' in img_dict:
                        del img_dict['image']
                    if 'image_path' in img_dict and img_dict['image_path']:
                        filename = os.path.basename(img_dict['image_path'])
                        img_dict['image_url'] = f"/presentations/{presentation_id}/images/{filename}"
                    accumulated_images.append(img_dict)

                    # Store partial result after each image
                    async with SessionLocal() as update_db:
                        update_step_result = await update_db.execute(
                            select(PresentationStepModel).filter(
                                PresentationStepModel.presentation_id == presentation_id,
                                PresentationStepModel.step == PresentationStep.IMAGES.value
                            )
                        )
                        update_step = update_step_result.scalars().first()
                        if update_step:
                            update_step.status = StepStatus.PROCESSING.value
                            update_step.set_result(accumulated_images)
                            await update_db.commit()

            # Mark step completed with all images
            async with SessionLocal() as final_db:
                final_step_result = await final_db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.IMAGES.value
                    )
                )
                final_step = final_step_result.scalars().first()
                if final_step:
                    final_step.status = StepStatus.COMPLETED.value
                    final_step.set_result(accumulated_images)
                    await final_db.commit()

            print(f"Images generated for presentation {presentation_id}: {len(accumulated_images)} images")
        except Exception as e:
            # Update the step status to error
            async with SessionLocal() as error_db:
                error_step_result = await error_db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.IMAGES.value
                    )
                )
                error_step = error_step_result.scalars().first()
                if error_step:
                    error_step.status = StepStatus.ERROR.value
                    error_step.error_message = str(e)
                    await error_db.commit()
            
            print(f"Error generating images for presentation {presentation_id}: {str(e)}")

async def execute_compiled_task(presentation_id: int):
    """
    Background task to generate the compiled presentation by combining slides and images
    """
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Get the presentation
            result = await db.execute(select(Presentation).filter(Presentation.id == presentation_id))
            presentation = result.scalars().first()
            
            if not presentation:
                print(f"Presentation {presentation_id} not found")
                return
            
            # Get the slides step (required)
            slides_step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.SLIDES.value
                )
            )
            slides_step = slides_step_result.scalars().first()
            
            if not slides_step or slides_step.status != StepStatus.COMPLETED.value:
                print(f"Slides step not completed for presentation {presentation_id}")
                return
                
            # Get the images step (required)
            images_step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.IMAGES.value
                )
            )
            images_step = images_step_result.scalars().first()
            
            if not images_step or images_step.status != StepStatus.COMPLETED.value:
                print(f"Images step not completed for presentation {presentation_id}")
                return
            
            # Get the compiled step
            compiled_step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.COMPILED.value
                )
            )
            compiled_step = compiled_step_result.scalars().first()
            
            if not compiled_step:
                print(f"Compiled step not found for presentation {presentation_id}")
                return
            
            # If compiled step is already completed, don't regenerate
            if compiled_step.status == StepStatus.COMPLETED.value:
                print(f"Compiled content already generated for presentation {presentation_id}")
                return
            
            # Update status to processing
            compiled_step.status = StepStatus.PROCESSING.value
            await db.commit()
            
            # Get slides and images data
            slides_data = slides_step.get_result()
            images_data = images_step.get_result()
            
            if not slides_data:
                raise ValueError("No slides data found")
            
            # Process image URLs for the images data
            for image in images_data:
                if isinstance(image, dict) and "image_path" in image:
                    # Extract filename from the absolute path
                    filename = os.path.basename(image["image_path"])
                    # Create a proper URL for the image
                    image["image_url"] = f"/presentations/{presentation_id}/images/{filename}"
            
            # Convert to Pydantic models
            slides_obj = SlidePresentation(**slides_data)
            images_obj = [ImageGeneration(**img) for img in images_data]
            
            # Generate the compiled presentation
            compiled_data = await generate_compiled_presentation(
                slides_obj, 
                images_obj,
                presentation_id
            )
            
            # Update the compiled step with the result
            compiled_step.set_result(compiled_data.model_dump())
            compiled_step.status = StepStatus.COMPLETED.value
            await db.commit()
            
            print(f"Compiled presentation generated for presentation {presentation_id}")
            
        except Exception as e:
            # Update the step status to error
            async with SessionLocal() as error_db:
                error_step_result = await error_db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.COMPILED.value
                    )
                )
                error_step = error_step_result.scalars().first()
                if error_step:
                    error_step.status = StepStatus.ERROR.value
                    error_step.error_message = str(e)
                    await error_db.commit()
            
            print(f"Error generating compiled presentation for presentation {presentation_id}: {str(e)}")

# Add the PPTX generation execution task
async def execute_pptx_task(presentation_id: int):
    """
    Execute the PPTX generation task for a presentation.
    This generates a PowerPoint presentation from the slides data.
    """
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Update status to processing
            query = update(PresentationStepModel).where(
                (PresentationStepModel.presentation_id == presentation_id) &
                (PresentationStepModel.step == PresentationStep.PPTX.value)
            ).values(status=StepStatus.PROCESSING.value)
            await db.execute(query)
            await db.commit()
            
            # First, check if we have compiled data (includes images)
            query = select(PresentationStepModel).where(
                (PresentationStepModel.presentation_id == presentation_id) &
                (PresentationStepModel.step == PresentationStep.COMPILED.value)
            )
            result = await db.execute(query)
            compiled_step = result.scalars().first()
            
            # If compiled step is available and completed, use it
            if compiled_step and compiled_step.status == StepStatus.COMPLETED.value:
                print(f"Using COMPILED step data for PPTX generation (with images)")
                slides_data = compiled_step.get_result()
                if not slides_data:
                    raise ValueError("No compiled slides data found")
                
                # Check if we have an images field in the result
                if isinstance(slides_data, dict) and "slides" in slides_data:
                    for idx, slide in enumerate(slides_data.get("slides", [])):
                        if "image_url" in slide and slide["image_url"]:
                            image_url = slide["image_url"]
                            print(f"Found image URL for slide {idx}: {image_url}")
                            
                            # Verify if image file exists
                            if image_url.startswith('/presentations/'):
                                parts = image_url.split('/')
                                if len(parts) >= 5:
                                    pres_id = parts[2]
                                    img_filename = parts[-1]
                                    img_path = os.path.join(PRESENTATIONS_STORAGE_DIR, pres_id, "images", img_filename)
                                    print(f"Checking if image exists at: {img_path}")
                                    print(f"Image exists: {os.path.exists(img_path)}")
                                    
                                    # If image doesn't exist in the expected location, check legacy location
                                    if not os.path.exists(img_path):
                                        legacy_path = os.path.join(PRESENTATIONS_STORAGE_DIR, pres_id, img_filename)
                                        print(f"Checking legacy path: {legacy_path}")
                                        print(f"Legacy image exists: {os.path.exists(legacy_path)}")
                                        
                                        # If image exists in legacy location, copy it to new location
                                        if os.path.exists(legacy_path):
                                            import shutil
                                            os.makedirs(os.path.dirname(img_path), exist_ok=True)
                                            shutil.copy(legacy_path, img_path)
                                            print(f"Copied image from legacy location to: {img_path}")
            else:
                # Fall back to just slides data if compiled not available
                print(f"Falling back to SLIDES step data for PPTX generation (without images)")
                query = select(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.SLIDES.value)
                )
                result = await db.execute(query)
                slides_step = result.scalars().first()
                
                if not slides_step or slides_step.status != StepStatus.COMPLETED.value:
                    raise ValueError("Slides step not completed")
                
                slides_data = slides_step.get_result()
                if not slides_data:
                    raise ValueError("No slides data found")
            
            try:
                # Convert to appropriate Pydantic model based on which step we're using
                from models import SlidePresentation, CompiledPresentation
                
                if compiled_step and compiled_step.status == StepStatus.COMPLETED.value:
                    slides_obj = CompiledPresentation(**slides_data)
                else:
                    slides_obj = SlidePresentation(**slides_data)
                
                # Generate PPTX file
                print(f"Generating PPTX for presentation {presentation_id}...")
                pptx_result = await generate_pptx_from_slides(slides_obj, presentation_id)
                
                # Convert PPTX to PNG images
                png_paths = await convert_pptx_to_png(pptx_result.pptx_path)
                
                # Update the result with PNG paths
                pptx_result.png_paths = png_paths
                
                # Convert to dictionary
                result = pptx_result.model_dump()
                
                # Update step with successful result
                query = update(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.PPTX.value)
                ).values(
                    status=StepStatus.COMPLETED.value,
                    result=json.dumps(result)
                )
                await db.execute(query)
                await db.commit()
                
                print(f"PPTX generation completed for presentation {presentation_id}")
                
            except Exception as e:
                print(f"Error generating PPTX: {str(e)}")
                raise e
            
        except Exception as e:
            print(f"Error in PPTX generation task: {str(e)}")
            
            # Update status to error
            query = update(PresentationStepModel).where(
                (PresentationStepModel.presentation_id == presentation_id) &
                (PresentationStepModel.step == PresentationStep.PPTX.value)
            ).values(
                status=StepStatus.ERROR.value,
                error_message=str(e)
            )
            await db.execute(query)
            await db.commit() 