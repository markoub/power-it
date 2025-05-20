from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List, Dict, Any, Optional
import json
import os
import time

from database import get_db, Presentation, PresentationStepModel, PresentationStep, StepStatus, SessionLocal
from models import (
    PresentationCreate, 
    StepUpdate,
    ResearchData, 
    SlidePresentation,
    ImageGeneration,
    CompiledPresentation
)
from schemas.presentations import (
    PresentationResponse,
    PresentationDetailResponse,
    PresentationStepResponse,
    StepUpdateRequest
)
from schemas.images import SlideTypesResponse
from services.presentation_service import (
    execute_research_task,
    execute_manual_research_task,
    execute_slides_task,
    execute_images_task,
    execute_compiled_task,
    execute_pptx_task
)
from config import PRESENTATIONS_STORAGE_DIR

router = APIRouter(
    prefix="/presentations",
    tags=["presentations"],
    responses={404: {"description": "Presentation not found"}},
)

# Simple time-based cache for presentation list
_presentations_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 5  # Cache TTL in seconds
}

@router.post("", response_model=PresentationResponse, status_code=201,
           summary="Create a new presentation",
           description="Creates a new presentation and initializes the required steps")
async def create_presentation(
    presentation: PresentationCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Create new presentation
        db_presentation = Presentation(
            name=presentation.name, 
            topic=presentation.topic,
            author=presentation.author
        )
        db.add(db_presentation)
        
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            error_message = str(e)
            
            # Check for unique constraint violation and provide a clearer message
            if "UNIQUE constraint failed: presentations.name" in error_message:
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": f"A presentation with the name '{presentation.name}' already exists. Please use a different name.",
                        "error_type": "unique_constraint_violation",
                        "field": "name",
                        "original_error": error_message
                    }
                )
            
            # Return detailed error information for other errors
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Failed to create presentation",
                    "error_type": type(e).__name__,
                    "error_message": error_message
                }
            )
        
        await db.refresh(db_presentation)
        
        # Determine which research step to use based on research_type
        research_step_type = PresentationStep.MANUAL_RESEARCH.value if presentation.research_type == "manual_research" else PresentationStep.RESEARCH.value
        
        # Initialize research step as pending
        research_step = PresentationStepModel(
            presentation_id=db_presentation.id,
            step=research_step_type,
            status=StepStatus.PENDING.value
        )
        db.add(research_step)
        
        # Initialize slides step as pending
        slides_step = PresentationStepModel(
            presentation_id=db_presentation.id,
            step=PresentationStep.SLIDES.value,
            status=StepStatus.PENDING.value
        )
        db.add(slides_step)
        
        # Initialize images step as pending
        images_step = PresentationStepModel(
            presentation_id=db_presentation.id,
            step=PresentationStep.IMAGES.value,
            status=StepStatus.PENDING.value
        )
        db.add(images_step)
        
        # Initialize compiled step as pending
        compiled_step = PresentationStepModel(
            presentation_id=db_presentation.id,
            step=PresentationStep.COMPILED.value,
            status=StepStatus.PENDING.value
        )
        db.add(compiled_step)
        
        # Initialize PPTX step as pending
        pptx_step = PresentationStepModel(
            presentation_id=db_presentation.id,
            step=PresentationStep.PPTX.value,
            status=StepStatus.PENDING.value
        )
        db.add(pptx_step)
        
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Failed to create presentation steps",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
        
        # Start appropriate research task in background
        if presentation.research_type == "manual_research":
            if not presentation.research_content:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Research content is required for manual research"},
                )
            background_tasks.add_task(
                execute_manual_research_task, 
                db_presentation.id, 
                presentation.research_content
            )
        else:
            if not presentation.topic:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Topic is required for AI research"},
                )
            background_tasks.add_task(
                execute_research_task, 
                db_presentation.id, 
                presentation.topic,
                presentation.author
            )
        
        return {
            "id": db_presentation.id,
            "name": db_presentation.name,
            "topic": presentation.topic if presentation.topic else "Manual Research",
            "author": presentation.author,
            "created_at": db_presentation.created_at.isoformat(),
            "updated_at": db_presentation.updated_at.isoformat()
        }
    except Exception as e:
        # Catch any other unexpected errors
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Unexpected error in create_presentation: {str(e)}")
        print(f"Traceback: {error_traceback}")
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred while creating the presentation",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": error_traceback.split("\n")
            }
        )

@router.get("", response_model=List[PresentationResponse],
          summary="List all presentations",
          description="Returns a list of all presentations with caching to improve performance")
async def list_presentations(db: AsyncSession = Depends(get_db)):
    """
    Get list of presentations with caching to improve performance
    """
    # Check if we have a valid cache
    current_time = time.time()
    if _presentations_cache["data"] is not None and current_time - _presentations_cache["timestamp"] < _presentations_cache["ttl"]:
        return _presentations_cache["data"]
    
    # Use a more efficient query that doesn't load relationships we don't need
    query = select(
        Presentation.id,
        Presentation.name,
        Presentation.topic,
        Presentation.created_at,
        Presentation.updated_at
    ).order_by(Presentation.created_at.desc())
    
    result = await db.execute(query)
    presentations = result.all()
    
    # Format the response
    formatted_presentations = [
        {
            "id": p.id,
            "name": p.name,
            "topic": p.topic,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat()
        }
        for p in presentations
    ]
    
    # Update the cache
    _presentations_cache["data"] = formatted_presentations
    _presentations_cache["timestamp"] = current_time
    
    return formatted_presentations

@router.get("/{presentation_id}", response_model=PresentationDetailResponse,
          summary="Get presentation details",
          description="Returns detailed information about a presentation including all its steps")
async def get_presentation(presentation_id: int, db: AsyncSession = Depends(get_db)):
    try:
        print(f"Retrieving presentation with ID: {presentation_id} from routers/presentations.py")
        stmt = select(Presentation).filter(Presentation.id == presentation_id)
        result = await db.execute(stmt)
        presentation = result.scalar_one_or_none()
        
        if not presentation:
            # Log before raising HTTPException for better server-side visibility
            print(f"Presentation {presentation_id} not found in database.")
            raise HTTPException(
                status_code=404,
                detail=f"Presentation {presentation_id} not found",
            )
        
        # Get steps for this presentation
        steps_stmt = select(PresentationStepModel).filter(PresentationStepModel.presentation_id == presentation_id)
        steps_result = await db.execute(steps_stmt)
        steps = steps_result.scalars().all()
        
        print(f"Found {len(steps)} steps for presentation {presentation_id}")
        
        processed_steps = []
        for step in steps:
            step_data = {
                "id": step.id,
                "step": step.step,
                "status": step.status,
                "created_at": step.created_at.isoformat() if step.created_at else None,
                "updated_at": step.updated_at.isoformat() if step.updated_at else None,
                "error_message": step.error_message,
                "result": None # Default to None
            }
            try:
                raw_result_data = step.get_result()
                
                if isinstance(raw_result_data, (dict, list)):
                    try:
                        json.dumps(raw_result_data) # Pre-flight check for serializability
                        
                        # For images step, ensure result is a dictionary because PresentationStepResponse expects a dict
                        if step.step == "images" and isinstance(raw_result_data, list):
                            # Convert the list to a dictionary to match expected schema
                            step_data["result"] = {"images": raw_result_data} 
                        else:
                            step_data["result"] = raw_result_data
                            
                    except TypeError as te:
                        print(f"TypeError: Step {step.id} result for P:{presentation_id} not JSON serializable: {str(te)}")
                        step_data["result"] = {"error": "Step result contains non-serializable data", "details": str(te)}
                elif raw_result_data is not None:
                    print(f"Warning: Step {step.id} result for P:{presentation_id} is not dict/list: {type(raw_result_data)}")
                    step_data["result"] = {"error": "Unexpected data type in step result", "type": str(type(raw_result_data)), "rawValue": str(raw_result_data)[:200] } # Include snippet
                
                # Special handling for images step URLs (should be safe if result is a list of dicts)
                if step.step == "images" and isinstance(step_data["result"], list):
                    for image_item in step_data["result"]:
                        if isinstance(image_item, dict) and "image_path" in image_item:
                            filename = os.path.basename(image_item["image_path"])
                            image_item["image_url"] = f"/presentations/{presentation_id}/images/{filename}"

            except Exception as step_processing_error:
                print(f"Error processing result for step {step.id} (P:{presentation_id}): {str(step_processing_error)}")
                step_data["result"] = {"error": "Failed to process step result", "details": str(step_processing_error)}
            
            processed_steps.append(step_data)
        
        # Build the final presentation data
        presentation_data = {
            "id": presentation.id,
            "name": presentation.name,
            "topic": presentation.topic,
            "author": presentation.author,
            "created_at": presentation.created_at.isoformat() if presentation.created_at else None,
            "updated_at": presentation.updated_at.isoformat() if presentation.updated_at else None,
            "steps": processed_steps
        }
        
        return presentation_data # FastAPI will serialize this using PresentationDetailResponse

    except HTTPException as http_exc: # Re-raise HTTPException to let FastAPI handle it
        raise http_exc
    except Exception as e:
        # Catch-all for any other unexpected errors within this endpoint
        import traceback
        error_details = traceback.format_exc()
        print(f"FATAL ERROR in get_presentation (P:{presentation_id}): {str(e)}\nTraceback: {error_details}")
        # This will now be caught by the universal middleware if not a Pydantic validation error during response build
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred while retrieving presentation {presentation_id}: {str(e)}"
        ) # It's better to raise HTTPException so universal middleware isn't the only defense.

@router.post("/{presentation_id}/steps/{step_name}/run",
           summary="Run a specific presentation step",
           description="Triggers execution of a specific step in the presentation process")
async def run_step(
    presentation_id: int, 
    step_name: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Validate step name
    try:
        step = PresentationStep(step_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid step name: {step_name}")
    
    # Get presentation
    query = select(Presentation).where(Presentation.id == presentation_id)
    result = await db.execute(query)
    presentation = result.scalars().first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Update step status to PROCESSING
    query = update(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == step_name)
    ).values(status=StepStatus.PROCESSING.value)
    await db.execute(query)
    await db.commit()
    
    # Run appropriate task based on step name
    if step == PresentationStep.RESEARCH:
        background_tasks.add_task(execute_research_task, presentation_id, presentation.topic)
    elif step == PresentationStep.MANUAL_RESEARCH:
        # For manual research, we need research content
        # This step should typically not be run directly, but just in case
        raise HTTPException(status_code=400, detail="Manual research requires content to be submitted")
    elif step == PresentationStep.SLIDES:
        background_tasks.add_task(execute_slides_task, presentation_id)
    elif step == PresentationStep.IMAGES:
        background_tasks.add_task(execute_images_task, presentation_id)
    elif step == PresentationStep.COMPILED:
        background_tasks.add_task(execute_compiled_task, presentation_id)
    elif step == PresentationStep.PPTX:
        background_tasks.add_task(execute_pptx_task, presentation_id)
    
    return {"message": f"Started {step_name} task for presentation {presentation_id}"}

@router.put("/{presentation_id}/steps/{step_name}",
          summary="Update a presentation step",
          description="Updates the result data for a specific step in the presentation process")
async def update_step(
    presentation_id: int,
    step_name: str,
    update_data: StepUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    # Validate step name
    if step_name not in [e.value for e in PresentationStep]:
        raise HTTPException(status_code=400, detail=f"Invalid step name: {step_name}")
    
    # Get step
    step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == step_name
        )
    )
    step = step_result.scalars().first()
    
    if not step:
        raise HTTPException(status_code=404, detail=f"Step {step_name} not found for this presentation")
    
    # Update step result
    step.set_result(update_data.result)
    step.status = StepStatus.COMPLETED.value
    await db.commit()
    
    return {"message": f"Updated {step_name} step for presentation {presentation_id}"}

@router.post("/{presentation_id}/save_modified",
           summary="Save modified presentation",
           description="Saves modified presentation data to the appropriate steps")
async def save_modified_presentation(
    presentation_id: int,
    modified_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Save modified presentation data to the appropriate step.
    The data will be saved to the slides step and compiled step if the latter exists.
    """
    # Get the presentation
    result = await db.execute(select(Presentation).filter(Presentation.id == presentation_id))
    presentation = result.scalar_one_or_none()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Get the slides step (required)
    slides_step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == PresentationStep.SLIDES.value
        )
    )
    slides_step = slides_step_result.scalars().first()
    
    if not slides_step:
        raise HTTPException(status_code=404, detail="Slides step not found")
    
    # Update the slides step with the modified data
    slides_step.set_result(modified_data)
    
    # Get the compiled step and update it if it exists
    compiled_step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == PresentationStep.COMPILED.value
        )
    )
    compiled_step = compiled_step_result.scalars().first()
    
    # If the compiled step exists and is completed, update it too
    if compiled_step and compiled_step.status == StepStatus.COMPLETED.value:
        compiled_step.set_result(modified_data)
    
    await db.commit()
    
    return {
        "message": f"Modified presentation saved for presentation {presentation_id}",
        "presentation_id": presentation_id
    }

@router.post("/{presentation_id}/modify",
           summary="Modify presentation",
           description="Context-aware endpoint to modify a presentation or single slide using AI")
async def modify_presentation_endpoint(
    presentation_id: int,
    request: Request
):
    """
    Context-aware endpoint to modify a presentation or single slide using Gemini.
    - If slide_index is provided, only that slide is modified and only the modified slide is returned
    - If slide_index is not provided, the entire presentation is modified
    - Works with either slides or compiled step (whichever is available)
    """
    # Parse request body
    try:
        data = await request.json()
        prompt = data.get("prompt")
        slide_index = data.get("slide_index")  # Optional parameter
        current_step = data.get("current_step")  # Get the current step from wizard context
        
        # Add detailed debug logging
        print(f"DEBUG - Modify presentation request received:")
        print(f"  - presentation_id: {presentation_id}")
        print(f"  - prompt: {prompt}")
        print(f"  - slide_index: {slide_index}")
        print(f"  - current_step: {current_step}")
        print(f"  - Request for: {'single slide' if slide_index is not None else 'entire presentation'}")
        
        if not prompt:
            return JSONResponse(
                status_code=400,
                content={"detail": "Missing prompt"},
            )
            
        # Create a DB session
        async with SessionLocal() as db:
            # Get the research step (first try regular research)
            research_step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.RESEARCH.value
                )
            )
            research_step = research_step_result.scalars().first()
            
            # If regular research not found or not completed, try manual research
            if not research_step or research_step.status != StepStatus.COMPLETED.value:
                manual_research_result = await db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.MANUAL_RESEARCH.value
                    )
                )
                research_step = manual_research_result.scalars().first()
            
            if not research_step or research_step.status != StepStatus.COMPLETED.value:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Research step not completed"},
                )
            
            # Get the data from the current step if provided, otherwise fallback to default logic
            compiled_data = None
            if current_step and current_step in [step.value for step in PresentationStep]:
                current_step_result = await db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == current_step
                    )
                )
                current_step_model = current_step_result.scalars().first()
                
                if current_step_model and current_step_model.status == StepStatus.COMPLETED.value:
                    compiled_data = current_step_model.get_result()
            
            # If current step data isn't available, try compiled first, then slides
            if not compiled_data:
                # Try to get the compiled step first, but fall back to slides step if needed
                compiled_step_result = await db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.COMPILED.value
                    )
                )
                compiled_step = compiled_step_result.scalars().first()
                
                # Check if compiled step is available and completed
                if compiled_step and compiled_step.status == StepStatus.COMPLETED.value:
                    compiled_data = compiled_step.get_result()
            
            # If still no data, try to get slides step
            slides_data = None
            if not compiled_data:
                slides_step_result = await db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.SLIDES.value
                    )
                )
                slides_step = slides_step_result.scalars().first()
                
                if not slides_step or slides_step.status != StepStatus.COMPLETED.value:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Neither compiled nor slides step is completed"},
                    )
                
                compiled_data = slides_step.get_result()
            
            # Get the research data for context
            research_data = research_step.get_result()
            
            # Validate slide_index if provided
            if slide_index is not None:
                # Check if slide index exists in the compiled data
                if compiled_data and "slides" in compiled_data and len(compiled_data["slides"]) <= slide_index:
                    # Try to get from slides step if compiled step doesn't have enough slides
                    slides_step_result = await db.execute(
                        select(PresentationStepModel).filter(
                            PresentationStepModel.presentation_id == presentation_id,
                            PresentationStepModel.step == PresentationStep.SLIDES.value
                        )
                    )
                    slides_step = slides_step_result.scalars().first()
                    
                    if slides_step and slides_step.status == StepStatus.COMPLETED.value:
                        slides_data = slides_step.get_result()
                        
                        # Use the slides data if it has enough slides
                        if "slides" in slides_data and slide_index < len(slides_data["slides"]):
                            compiled_data = slides_data
                
                # Final validation after potentially switching to slides data
                if slide_index < 0 or slide_index >= len(compiled_data.get("slides", [])):
                    return JSONResponse(
                        status_code=400,
                        content={"detail": f"Invalid slide index: {slide_index}"},
                    )
                
                # Log the request details for debugging
                print(f"Modifying slide {slide_index} in presentation {presentation_id} with prompt: {prompt}")
                
                try:
                    # Import here to avoid circular dependencies
                    from server import modify_presentation_with_gemini
                    from tools.modify import modify_single_slide
                    
                    # Use the single slide modification function
                    result = await modify_single_slide(
                        compiled_data,
                        research_data,
                        prompt,
                        slide_index
                    )
                    
                    # Save the modification back to the original step
                    if current_step and current_step in [step.value for step in PresentationStep]:
                        # Get the step again
                        original_step_result = await db.execute(
                            select(PresentationStepModel).filter(
                                PresentationStepModel.presentation_id == presentation_id,
                                PresentationStepModel.step == current_step
                            )
                        )
                        original_step = original_step_result.scalars().first()
                        
                        if original_step and original_step.status == StepStatus.COMPLETED.value:
                            # Log that we're not saving directly to the database anymore
                            print(f"Modification for slide {slide_index} in step {current_step} for presentation {presentation_id} generated but not automatically saved")
                            # Changes will only be saved when the client calls save_modified_presentation endpoint
                    
                    return JSONResponse(
                        status_code=200,
                        content=result,
                    )
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Error modifying slide: {str(e)}")
                    print(f"Traceback: {error_details}")
                    
                    return JSONResponse(
                        status_code=500,
                        content={"detail": f"Error modifying slide: {str(e)}"},
                    )
            else:
                # Modifying the entire presentation
                print(f"Modifying entire presentation {presentation_id} with prompt: {prompt}")
                
                try:
                    # Import here to avoid circular dependencies
                    from server import modify_presentation_with_gemini
                    
                    modified_data = await modify_presentation_with_gemini(
                        compiled_data,
                        research_data,
                        prompt
                    )
                    
                    return JSONResponse(
                        status_code=200,
                        content=modified_data,
                    )
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Error modifying presentation: {str(e)}")
                    print(f"Traceback: {error_details}")
                    
                    return JSONResponse(
                        status_code=500,
                        content={"detail": f"Error modifying presentation: {str(e)}"},
                    )
                
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing request: {str(e)}")
        print(f"Traceback: {error_details}")
        
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error processing request: {str(e)}"},
        )

@router.get("/{presentation_id}/images/{filename}",
          summary="Get presentation image",
          description="Serves an image file for a specific presentation")
async def get_presentation_image(presentation_id: int, filename: str):
    """
    Serve an image file directly from the presentation's storage directory
    """
    print(f"Requested image: presentation_id={presentation_id}, filename={filename}")
    
    # Construct the path to the image file
    image_path = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id), "images", filename)
    print(f"Looking for image at: {image_path}")
    print(f"File exists: {os.path.exists(image_path)}")
    
    # Check if the file exists
    if not os.path.exists(image_path):
        # Try legacy location (directly in presentation dir)
        legacy_path = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id), filename)
        print(f"Image not found at primary location, checking legacy path: {legacy_path}")
        print(f"Legacy file exists: {os.path.exists(legacy_path)}")
        
        if os.path.exists(legacy_path):
            print(f"Serving image from legacy location: {legacy_path}")
            return FileResponse(legacy_path, media_type="image/png")
        
        # List files in the directory to help with debugging
        images_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id), "images")
        if os.path.exists(images_dir):
            print(f"Available files in {images_dir}:")
            for file in os.listdir(images_dir):
                print(f"  - {file}")
        
        print(f"Image not found: {filename}")
        raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
    
    print(f"Serving image: {image_path}")
    # Return the file directly
    return FileResponse(image_path, media_type="image/png")

@router.get("/{presentation_id}/pptx-slides",
          summary="Get PPTX slides",
          description="Gets the list of PNG images for a presentation's PPTX slides")
async def get_pptx_slides(presentation_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get the list of PNG images for a presentation's PPTX slides
    """
    # Get PPTX step data
    query = select(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == PresentationStep.PPTX.value)
    )
    result = await db.execute(query)
    pptx_step = result.scalars().first()
    
    if not pptx_step or pptx_step.status != StepStatus.COMPLETED.value:
        raise HTTPException(status_code=404, detail="PPTX slides not found or not generated yet")
    
    pptx_data = pptx_step.get_result()
    if not pptx_data or "png_paths" not in pptx_data:
        raise HTTPException(status_code=404, detail="PPTX slide images not found")
    
    # Create image URLs from the paths
    slide_images = []
    for i, path in enumerate(pptx_data["png_paths"]):
        filename = os.path.basename(path)
        slide_images.append({
            "slide_index": i,
            "filename": filename,
            "url": f"/presentations/{presentation_id}/pptx-slides/{filename}"
        })
    
    return {"slides": slide_images}

@router.get("/{presentation_id}/pptx-slides/{filename}",
          summary="Get PPTX slide image",
          description="Gets a specific PPTX slide image by filename")
async def get_pptx_slide_image(presentation_id: int, filename: str):
    """
    Get a specific PPTX slide image by filename
    """
    # Construct the path to the image
    presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id))
    image_path = os.path.join(presentation_dir, filename)
    
    # Check if the file exists
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Slide image not found")
    
    return FileResponse(image_path)

@router.get("/{presentation_id}/download-pptx",
          summary="Download PPTX file",
          description="Downloads the PPTX file for a presentation")
async def download_pptx(presentation_id: int, filename: str = None, db: AsyncSession = Depends(get_db)):
    """
    Download the PPTX file for a presentation
    """
    print(f"\n\n=== DOWNLOAD PPTX REQUEST for presentation {presentation_id} ===")
    if filename:
        print(f"Requested filename: {filename}")
    
    # Get PPTX step data
    query = select(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == PresentationStep.PPTX.value)
    )
    result = await db.execute(query)
    pptx_step = result.scalars().first()
    
    if not pptx_step or pptx_step.status != StepStatus.COMPLETED.value:
        print(f"ERROR: PPTX file not found or not generated yet for presentation {presentation_id}")
        raise HTTPException(status_code=404, detail="PPTX file not found or not generated yet")
    
    pptx_data = pptx_step.get_result()
    if not pptx_data or "pptx_path" not in pptx_data:
        print(f"ERROR: PPTX file path not found in result data for presentation {presentation_id}")
        raise HTTPException(status_code=404, detail="PPTX file not found")
    
    print(f"Preparing PPTX download for presentation {presentation_id}")
    print(f"PPTX path: {pptx_data['pptx_path']}")
    print(f"File exists: {os.path.exists(pptx_data['pptx_path'])}")
    print(f"File size: {os.path.getsize(pptx_data['pptx_path']) if os.path.exists(pptx_data['pptx_path']) else 'N/A'} bytes")
    
    # Use the specified filename or create a simple one
    display_filename = filename or f"presentation_{presentation_id}.pptx"
    if not display_filename.lower().endswith('.pptx'):
        display_filename += '.pptx'
    
    print(f"Setting download filename to: {display_filename}")
    
    # Return the PPTX file with extremely explicit download headers
    headers = {
        "Content-Disposition": f'attachment; filename="{display_filename}"',
        "Content-Type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "X-Content-Type-Options": "nosniff",
        # Force download in various browsers
        "Content-Description": "File Transfer",
        "Content-Transfer-Encoding": "binary",
        "Expires": "0",
        "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
        "Pragma": "public"
    }
    
    response = FileResponse(
        pptx_data["pptx_path"],
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=display_filename,
        headers=headers
    )
    
    print(f"=== DOWNLOAD PPTX RESPONSE PREPARED for presentation {presentation_id} ===\n\n")
    return response

@router.get("/{presentation_id}/download-pdf",
          summary="Download PDF file",
          description="Downloads the PDF version of a presentation")
async def download_pdf(presentation_id: int, filename: str = None, db: AsyncSession = Depends(get_db)):
    """
    Download the PDF version of a presentation
    """
    print(f"\n\n=== DOWNLOAD PDF REQUEST for presentation {presentation_id} ===")
    if filename:
        print(f"Requested filename: {filename}")
    
    # Get PPTX step data
    query = select(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == PresentationStep.PPTX.value)
    )
    result = await db.execute(query)
    pptx_step = result.scalars().first()
    
    if not pptx_step or pptx_step.status != StepStatus.COMPLETED.value:
        print(f"ERROR: PPTX step not completed for presentation {presentation_id}")
        raise HTTPException(status_code=404, detail="PDF file not found or not generated yet")
    
    pptx_data = pptx_step.get_result()
    if not pptx_data or "pptx_path" not in pptx_data:
        print(f"ERROR: PPTX file path not found in result data for presentation {presentation_id}")
        raise HTTPException(status_code=404, detail="Source files not found")
        
    # Get the basename of the PPTX file without extension
    basename = os.path.splitext(os.path.basename(pptx_data["pptx_path"]))[0]
    pdf_path = os.path.join(os.path.dirname(pptx_data["pptx_path"]), f"{basename}.pdf")
    
    print(f"Preparing PDF download for presentation {presentation_id}")
    print(f"PDF path: {pdf_path}")
    print(f"File exists: {os.path.exists(pdf_path)}")
    print(f"File size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 'N/A'} bytes")
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF file not found at {pdf_path}")
        raise HTTPException(status_code=404, detail="PDF file not found - it may need to be regenerated")
    
    # Use the specified filename or create a simple one
    display_filename = filename or f"presentation_{presentation_id}.pdf"
    if not display_filename.lower().endswith('.pdf'):
        display_filename += '.pdf'
    
    print(f"Setting download filename to: {display_filename}")
    
    # Return the PDF file with extremely explicit download headers
    headers = {
        "Content-Disposition": f'attachment; filename="{display_filename}"',
        "Content-Type": "application/pdf",
        "X-Content-Type-Options": "nosniff",
        # Force download in various browsers
        "Content-Description": "File Transfer",
        "Content-Transfer-Encoding": "binary",
        "Expires": "0",
        "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
        "Pragma": "public"
    }
    
    response = FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=display_filename,
        headers=headers
    )
    
    print(f"=== DOWNLOAD PDF RESPONSE PREPARED for presentation {presentation_id} ===\n\n")
    return response

@router.get("/slide-types", response_model=SlideTypesResponse,
          summary="Get available slide types",
          description="Returns all available slide types and their fields to help with presentation creation")
async def get_slide_types():
    """
    Returns all available slide types and their fields with descriptions.
    This helps frontend developers understand the available slide structures.
    """
    slide_types = [
        {
            "type": "welcome",
            "description": "Opening slide with title and subtitle",
            "fields": {
                "title": "Main presentation title",
                "subtitle": "Optional subtitle or tagline",
                "author": "Optional author name"
            }
        },
        {
            "type": "tableofcontents",
            "description": "Table of contents slide listing the presentation sections",
            "fields": {
                "title": "Table of Contents",
                "sections": "List of section titles (array of strings)",
            }
        },
        {
            "type": "section",
            "description": "Section divider slide with a title",
            "fields": {
                "title": "Section title"
            }
        },
        {
            "type": "content",
            "description": "Standard content slide with title and bulleted content",
            "fields": {
                "title": "Slide title",
                "content": "Bullet points or paragraphs of text"
            }
        },
        {
            "type": "contentimage",
            "description": "Content slide with an accompanying image",
            "fields": {
                "title": "Slide title",
                "content": "Bullet points or paragraphs of text",
                "image": "Reference to the image for this slide"
            }
        },
        {
            "type": "image",
            "description": "Full image slide with optional caption",
            "fields": {
                "title": "Optional slide title",
                "caption": "Optional image caption",
                "image": "Reference to the image for this slide"
            }
        },
        {
            "type": "quote",
            "description": "Quote slide with quote text and author",
            "fields": {
                "title": "Optional slide title",
                "quote": "The quote text",
                "author": "Author of the quote"
            }
        },
        {
            "type": "conclusion",
            "description": "Conclusion slide summarizing key points",
            "fields": {
                "title": "Conclusion", 
                "content": "Summary of key points or final thoughts"
            }
        },
        {
            "type": "thankyou",
            "description": "Final thank you slide with optional contact information",
            "fields": {
                "title": "Thank You",
                "subtitle": "Optional subtitle or tagline",
                "contact": "Optional contact information"
            }
        }
    ]
    
    return {"slide_types": slide_types} 