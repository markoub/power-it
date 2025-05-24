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
    StepUpdateRequest,
    TopicUpdateRequest
)
from schemas.images import SlideTypesResponse
from services import (
    execute_research_task,
    execute_manual_research_task,
    execute_slides_task,
    execute_images_task,
    execute_compiled_task,
    execute_pptx_task,
    execute_topic_update_task
)
from tools.images import generate_image_from_prompt
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
        # For pending research type, we don't create a research step yet
        if presentation.research_type != "pending":
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
        
        # Start appropriate research task in background only if research type is not pending
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
        elif presentation.research_type == "research":
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
        # If research_type is "pending", we don't start any background tasks
        
        return {
            "id": db_presentation.id,
            "name": db_presentation.name,
            "topic": presentation.topic if presentation.topic else None,
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
    query = (
        select(
            Presentation.id,
            Presentation.name,
            Presentation.topic,
            Presentation.author,
            Presentation.thumbnail_url,
            Presentation.created_at,
            Presentation.updated_at,
        )
        .where(Presentation.is_deleted == False)
        .order_by(Presentation.created_at.desc())
    )
    
    result = await db.execute(query)
    presentations = result.all()
    
    # Format the response
    formatted_presentations = [
        {
            "id": p.id,
            "name": p.name,
            "topic": p.topic,
            "author": p.author,
            "thumbnail_url": p.thumbnail_url,
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
        stmt = select(Presentation).filter(
            (Presentation.id == presentation_id) & (Presentation.is_deleted == False)
        )
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
            "thumbnail_url": presentation.thumbnail_url,
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


@router.delete("/{presentation_id}", status_code=204,
              summary="Delete a presentation",
              description="Soft delete a presentation by id")
async def delete_presentation(presentation_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Presentation).where(
        (Presentation.id == presentation_id) & (Presentation.is_deleted == False)
    )
    result = await db.execute(stmt)
    presentation = result.scalar_one_or_none()
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    presentation.is_deleted = True
    await db.commit()

    # invalidate cache so list reflects deletion
    _presentations_cache["data"] = None

    return Response(status_code=204)

@router.post("/{presentation_id}/steps/{step_name}/run",
           summary="Run a specific presentation step",
           description="Triggers execution of a specific step in the presentation process")
async def run_step(
    presentation_id: int, 
    step_name: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Parse request body for optional parameters
    params = {}
    try:
        body = await request.body()
        if body:
            params = json.loads(body)
    except json.JSONDecodeError:
        params = {}
    
    # Validate step name
    try:
        step = PresentationStep(step_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid step name: {step_name}")
    
    # Get presentation
    query = select(Presentation).where(
        (Presentation.id == presentation_id) & (Presentation.is_deleted == False)
    )
    result = await db.execute(query)
    presentation = result.scalars().first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # For manual research or research steps, create the step if it doesn't exist
    if step in [PresentationStep.RESEARCH, PresentationStep.MANUAL_RESEARCH]:
        step_exists_query = select(PresentationStepModel).where(
            (PresentationStepModel.presentation_id == presentation_id) &
            (PresentationStepModel.step == step_name)
        )
        step_exists_result = await db.execute(step_exists_query)
        step_exists = step_exists_result.scalars().first()
        
        if not step_exists:
            # Create the step
            new_step = PresentationStepModel(
                presentation_id=presentation_id,
                step=step_name,
                status=StepStatus.PENDING.value
            )
            db.add(new_step)
            await db.commit()
    
    # Update step status to PROCESSING
    query = update(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == step_name)
    ).values(status=StepStatus.PROCESSING.value)
    await db.execute(query)
    await db.commit()
    
    # Run appropriate task based on step name
    if step == PresentationStep.RESEARCH:
        topic = params.get('topic') or presentation.topic
        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required for AI research")
        # Update presentation topic if provided
        if params.get('topic'):
            presentation.topic = topic
            await db.commit()
        background_tasks.add_task(execute_research_task, presentation_id, topic, presentation.author)
    elif step == PresentationStep.MANUAL_RESEARCH:
        research_content = params.get('research_content')
        if not research_content:
            raise HTTPException(status_code=400, detail="Research content is required for manual research")
        background_tasks.add_task(execute_manual_research_task, presentation_id, research_content)
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
    result = await db.execute(
        select(Presentation).filter(
            (Presentation.id == presentation_id) & (Presentation.is_deleted == False)
        )
    )
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

@router.post("/{presentation_id}/slides/{slide_index}/image",
           summary="Regenerate slide image",
           description="Generate a new image for a specific slide and update the images step")
async def regenerate_slide_image(
    presentation_id: int,
    slide_index: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Regenerate a single slide image using the provided prompt."""
    data = await request.json()
    prompt = data.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")

    # Get slides step to obtain slide title
    slides_step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == PresentationStep.SLIDES.value,
        )
    )
    slides_step = slides_step_result.scalars().first()
    if not slides_step or slides_step.status != StepStatus.COMPLETED.value:
        raise HTTPException(status_code=404, detail="Slides step not available")

    slides_data = slides_step.get_result()
    if (
        not slides_data
        or "slides" not in slides_data
        or slide_index < 0
        or slide_index >= len(slides_data["slides"])
    ):
        raise HTTPException(status_code=400, detail="Invalid slide index")

    slide_title = (
        slides_data["slides"][slide_index].get("fields", {}).get("title", "")
    )

    # Generate the new image
    result = await generate_image_from_prompt(prompt, "1024x1024", presentation_id)
    if not result or not result.image_path:
        raise HTTPException(status_code=500, detail="Image generation failed")

    filename = os.path.basename(result.image_path)
    image_url = f"/presentations/{presentation_id}/images/{filename}"

    # Update images step
    images_step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == PresentationStep.IMAGES.value,
        )
    )
    images_step = images_step_result.scalars().first()
    if not images_step:
        raise HTTPException(status_code=404, detail="Images step not found")

    images_data = images_step.get_result() or []
    if isinstance(images_data, dict) and "images" in images_data:
        images_list = images_data["images"]
    else:
        images_list = images_data

    new_entry = {
        "slide_index": slide_index,
        "slide_title": slide_title,
        "prompt": prompt,
        "image_field_name": "image",
        "image_path": result.image_path,
        "image_url": image_url,
    }

    replaced = False
    for idx, item in enumerate(images_list):
        if item.get("slide_index") == slide_index:
            images_list[idx] = new_entry
            replaced = True
            break

    if not replaced:
        images_list.append(new_entry)

    if isinstance(images_data, dict) and "images" in images_data:
        images_step.set_result({"images": images_list})
    else:
        images_step.set_result(images_list)
    images_step.status = StepStatus.COMPLETED.value

    # Update compiled step if it exists
    compiled_step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == PresentationStep.COMPILED.value,
        )
    )
    compiled_step = compiled_step_result.scalars().first()
    if compiled_step and compiled_step.status == StepStatus.COMPLETED.value:
        compiled_data = compiled_step.get_result()
        if (
            compiled_data
            and "slides" in compiled_data
            and slide_index < len(compiled_data["slides"])
        ):
            compiled_data["slides"][slide_index]["image_url"] = image_url
            compiled_data["slides"][slide_index].setdefault("fields", {})[
                "image_url"
            ] = image_url
            compiled_step.set_result(compiled_data)

    await db.commit()

    return {
        "slide_index": slide_index,
        "prompt": prompt,
        "image_url": image_url,
    }

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
            return FileResponse(
                legacy_path, 
                media_type="image/png",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        
        # List files in the directory to help with debugging
        images_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id), "images")
        if os.path.exists(images_dir):
            print(f"Available files in {images_dir}:")
            for file in os.listdir(images_dir):
                print(f"  - {file}")
        
        print(f"Image not found: {filename}")
        raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
    
    print(f"Serving image: {image_path}")
    # Return the file directly with CORS headers
    return FileResponse(
        image_path, 
        media_type="image/png",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

@router.options("/{presentation_id}/images/{filename}",
          summary="Handle preflight requests for image endpoint",
          description="Handles CORS preflight requests for the image endpoint")
async def options_presentation_image(presentation_id: int, filename: str):
    """
    Handle CORS preflight requests for the image endpoint
    """
    return Response(
        content="",
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept"
        }
    )

