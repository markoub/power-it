from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import Dict, Any
import json

from database import get_db, Presentation, PresentationStepModel, PresentationStep, StepStatus
from schemas.presentations import StepUpdateRequest
from services import (
    execute_research_task,
    execute_manual_research_task,
    execute_slides_task,
    execute_images_task,
    execute_compiled_task,
    execute_pptx_task,
)

router = APIRouter(
    prefix="/presentations",
    tags=["presentations"],
)

@router.post("/{presentation_id}/steps/{step_name}/run",
           summary="Run a specific presentation step",
           description="Triggers execution of a specific step in the presentation process")
async def run_step(
    presentation_id: int,
    step_name: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    params: Dict[str, Any] = {}
    try:
        body = await request.body()
        if body:
            params = json.loads(body)
    except json.JSONDecodeError:
        params = {}

    try:
        step = PresentationStep(step_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid step name: {step_name}")

    query = select(Presentation).where(
        (Presentation.id == presentation_id) & (Presentation.is_deleted == False)
    )
    result = await db.execute(query)
    presentation = result.scalars().first()

    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if step in [PresentationStep.RESEARCH, PresentationStep.MANUAL_RESEARCH]:
        step_exists_query = select(PresentationStepModel).where(
            (PresentationStepModel.presentation_id == presentation_id) &
            (PresentationStepModel.step == step_name)
        )
        step_exists_result = await db.execute(step_exists_query)
        step_exists = step_exists_result.scalars().first()

        if not step_exists:
            new_step = PresentationStepModel(
                presentation_id=presentation_id,
                step=step_name,
                status=StepStatus.PENDING.value
            )
            db.add(new_step)
            await db.commit()

    query = update(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == step_name)
    ).values(status=StepStatus.PROCESSING.value)
    await db.execute(query)
    await db.commit()

    if step == PresentationStep.RESEARCH:
        topic = params.get('topic') or presentation.topic
        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required for AI research")
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
    db: AsyncSession = Depends(get_db),
):
    if step_name not in [e.value for e in PresentationStep]:
        raise HTTPException(status_code=400, detail=f"Invalid step name: {step_name}")

    step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == step_name
        )
    )
    step = step_result.scalars().first()

    if not step:
        raise HTTPException(status_code=404, detail=f"Step {step_name} not found for this presentation")

    step.set_result(update_data.result)
    step.status = StepStatus.COMPLETED.value
    await db.commit()

    return {"message": f"Updated {step_name} step for presentation {presentation_id}"}
