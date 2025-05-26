from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any
import json
import os
import time

from database import get_db, Presentation, PresentationStepModel, PresentationStep, StepStatus
from models import PresentationCreate
from schemas.presentations import (
    PresentationResponse,
    PresentationDetailResponse,
    PaginatedPresentationsResponse
)
from services import execute_research_task, execute_manual_research_task
from config import PRESENTATIONS_STORAGE_DIR

router = APIRouter(
    prefix="/presentations",
    tags=["presentations"],
    responses={404: {"description": "Presentation not found"}},
)

_presentations_cache: Dict[str, Dict[str, Any]] = {}

@router.post("", response_model=PresentationResponse, status_code=201,
           summary="Create a new presentation",
           description="Creates a new presentation and initializes the required steps")
async def create_presentation(
    presentation: PresentationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
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
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Failed to create presentation",
                    "error_type": type(e).__name__,
                    "error_message": error_message
                }
            )

        await db.refresh(db_presentation)

        if presentation.research_type != "pending":
            research_step_type = PresentationStep.MANUAL_RESEARCH.value if presentation.research_type == "manual_research" else PresentationStep.RESEARCH.value
            research_step = PresentationStepModel(
                presentation_id=db_presentation.id,
                step=research_step_type,
                status=StepStatus.PENDING.value
            )
            db.add(research_step)

        slides_step = PresentationStepModel(
            presentation_id=db_presentation.id,
            step=PresentationStep.SLIDES.value,
            status=StepStatus.PENDING.value
        )
        db.add(slides_step)

        images_step = PresentationStepModel(
            presentation_id=db_presentation.id,
            step=PresentationStep.IMAGES.value,
            status=StepStatus.PENDING.value
        )
        db.add(images_step)

        compiled_step = PresentationStepModel(
            presentation_id=db_presentation.id,
            step=PresentationStep.COMPILED.value,
            status=StepStatus.PENDING.value
        )
        db.add(compiled_step)

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
        _presentations_cache.clear()
        return {
            "id": db_presentation.id,
            "name": db_presentation.name,
            "topic": presentation.topic if presentation.topic else None,
            "author": presentation.author,
            "created_at": db_presentation.created_at.isoformat(),
            "updated_at": db_presentation.updated_at.isoformat()
        }
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred while creating the presentation",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": error_traceback.split("\n")
            }
        )


@router.get("",
          response_model=PaginatedPresentationsResponse,
          summary="List all presentations",
          description="Returns a list of presentations with pagination and filtering")
async def list_presentations(
    page: int = 1,
    size: int = 10,
    status: str = "all",
    db: AsyncSession = Depends(get_db)
):
    page = max(page, 1)
    if size not in [5, 10, 50, 100]:
        size = 10

    status = status.lower()

    cache_key = f"{page}:{size}:{status}"
    cache_entry = _presentations_cache.get(cache_key)
    current_time = time.time()
    if cache_entry and current_time - cache_entry["timestamp"] < 5:
        return cache_entry["data"]

    base_query = select(Presentation).where(Presentation.is_deleted == False)

    if status == "finished":
        subq = select(PresentationStepModel.presentation_id).where(
            (PresentationStepModel.step == PresentationStep.PPTX.value) &
            (PresentationStepModel.status == StepStatus.COMPLETED.value)
        )
        base_query = base_query.where(Presentation.id.in_(subq))
    elif status == "in_progress":
        subq = select(PresentationStepModel.presentation_id).where(
            (PresentationStepModel.step == PresentationStep.PPTX.value) &
            (PresentationStepModel.status == StepStatus.COMPLETED.value)
        )
        base_query = base_query.where(~Presentation.id.in_(subq))

    total_result = await db.execute(base_query)
    total_presentations = len(total_result.scalars().all())

    query = (
        base_query.order_by(Presentation.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    result = await db.execute(query)
    presentations = result.scalars().all()

    items = [
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

    data = {"items": items, "total": total_presentations}

    _presentations_cache[cache_key] = {"data": data, "timestamp": current_time}

    return data


@router.get("/{presentation_id}", response_model=PresentationDetailResponse,
          summary="Get presentation details",
          description="Returns detailed information about a presentation including all its steps")
async def get_presentation(presentation_id: int, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Presentation).filter(
            (Presentation.id == presentation_id) & (Presentation.is_deleted == False)
        )
        result = await db.execute(stmt)
        presentation = result.scalar_one_or_none()

        if not presentation:
            raise HTTPException(
                status_code=404,
                detail=f"Presentation {presentation_id} not found",
            )

        steps_stmt = select(PresentationStepModel).filter(PresentationStepModel.presentation_id == presentation_id)
        steps_result = await db.execute(steps_stmt)
        steps = steps_result.scalars().all()

        processed_steps = []
        for step in steps:
            step_data = {
                "id": step.id,
                "step": step.step,
                "status": step.status,
                "created_at": step.created_at.isoformat() if step.created_at else None,
                "updated_at": step.updated_at.isoformat() if step.updated_at else None,
                "error_message": step.error_message,
                "result": None
            }
            try:
                raw_result_data = step.get_result()

                if isinstance(raw_result_data, (dict, list)):
                    try:
                        json.dumps(raw_result_data)
                        if step.step == "images" and isinstance(raw_result_data, list):
                            step_data["result"] = {"images": raw_result_data}
                        else:
                            step_data["result"] = raw_result_data
                    except TypeError as te:
                        step_data["result"] = {"error": "Step result contains non-serializable data", "details": str(te)}
                elif raw_result_data is not None:
                    step_data["result"] = {"error": "Unexpected data type in step result", "type": str(type(raw_result_data)), "rawValue": str(raw_result_data)[:200] }

                if step.step == "images" and isinstance(step_data["result"], list):
                    for image_item in step_data["result"]:
                        if isinstance(image_item, dict) and "image_path" in image_item:
                            filename = os.path.basename(image_item["image_path"])
                            image_item["image_url"] = f"/presentations/{presentation_id}/images/{filename}"

            except Exception as step_processing_error:
                step_data["result"] = {"error": "Failed to process step result", "details": str(step_processing_error)}

            processed_steps.append(step_data)

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

        return presentation_data

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while retrieving presentation {presentation_id}: {str(e)}"
        )


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
    _presentations_cache.clear()
    return Response(status_code=204)


@router.put("/{presentation_id}",
           summary="Update presentation metadata",
           description="Updates basic presentation metadata like name, author, topic")
async def update_presentation_metadata(
    presentation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        data = await request.json()
        result = await db.execute(
            select(Presentation).filter(
                (Presentation.id == presentation_id) & (Presentation.is_deleted == False)
            )
        )
        presentation = result.scalar_one_or_none()

        if not presentation:
            return JSONResponse(
                status_code=404,
                content={"detail": "Presentation not found"},
            )

        if "name" in data:
            presentation.name = data["name"]
        if "author" in data:
            presentation.author = data["author"]
        if "topic" in data:
            presentation.topic = data["topic"]
        if "researchMethod" in data:
            if data["researchMethod"] == "ai":
                presentation.research_type = "ai"
            elif data["researchMethod"] == "manual":
                presentation.research_type = "manual"

        await db.commit()
        await db.refresh(presentation)

        return {
            "id": presentation.id,
            "name": presentation.name,
            "author": presentation.author,
            "topic": presentation.topic,
            "research_type": presentation.research_type,
            "created_at": presentation.created_at.isoformat() if presentation.created_at else None,
            "updated_at": presentation.updated_at.isoformat() if presentation.updated_at else None,
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error updating presentation metadata: {str(e)}"},
        )
