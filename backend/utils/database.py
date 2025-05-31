from typing import Optional, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import PresentationStepModel, PresentationStep, StepStatus


async def get_presentation_step(
    db: AsyncSession, 
    presentation_id: int, 
    step: PresentationStep
) -> Optional[PresentationStepModel]:
    """
    Get a presentation step by presentation_id and step type
    
    Args:
        db: Database session
        presentation_id: ID of the presentation
        step: PresentationStep enum value
        
    Returns:
        PresentationStepModel or None if not found
    """
    result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == step.value
        )
    )
    return result.scalars().first()


async def update_step_status(
    db: AsyncSession,
    presentation_id: int,
    step: PresentationStep,
    status: StepStatus,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> Optional[PresentationStepModel]:
    """
    Update the status of a presentation step
    
    Args:
        db: Database session
        presentation_id: ID of the presentation
        step: PresentationStep enum value
        status: New status to set
        result: Optional result data to store
        error: Optional error message to store
        
    Returns:
        Updated PresentationStepModel or None if not found
    """
    step_model = await get_presentation_step(db, presentation_id, step)
    
    if not step_model:
        return None
    
    step_model.status = status.value
    
    if result is not None:
        step_model.set_result(result)
    elif error is not None:
        step_model.set_result({"error": error})
    
    await db.commit()
    return step_model


async def get_completed_research_step(
    db: AsyncSession,
    presentation_id: int
) -> Optional[PresentationStepModel]:
    """
    Get the completed research step (either regular or manual) for a presentation
    
    Args:
        db: Database session
        presentation_id: ID of the presentation
        
    Returns:
        Completed research step or None if not found
    """
    # Try regular research first
    research_step = await get_presentation_step(db, presentation_id, PresentationStep.RESEARCH)
    
    if research_step and research_step.status == StepStatus.COMPLETED.value:
        return research_step
    
    # Try manual research
    manual_research_step = await get_presentation_step(db, presentation_id, PresentationStep.MANUAL_RESEARCH)
    
    if manual_research_step and manual_research_step.status == StepStatus.COMPLETED.value:
        return manual_research_step
    
    return None


async def reset_downstream_steps(
    db: AsyncSession,
    presentation_id: int,
    from_step: PresentationStep
) -> None:
    """
    Reset all steps that come after the given step in the workflow
    
    Args:
        db: Database session
        presentation_id: ID of the presentation
        from_step: Step from which to reset downstream steps
    """
    # Define the order of steps
    step_order = [
        PresentationStep.RESEARCH,
        PresentationStep.MANUAL_RESEARCH,
        PresentationStep.SLIDES,
        PresentationStep.IMAGES,
        PresentationStep.COMPILED,
        PresentationStep.PPTX
    ]
    
    # Find the position of the current step
    try:
        current_index = step_order.index(from_step)
    except ValueError:
        return
    
    # Reset all steps after the current one
    for i in range(current_index + 1, len(step_order)):
        step = step_order[i]
        step_model = await get_presentation_step(db, presentation_id, step)
        if step_model:
            step_model.status = StepStatus.PENDING.value
            step_model.result = None
    
    await db.commit()