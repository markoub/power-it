from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any

from database import get_db, SessionLocal, Presentation, PresentationStepModel, PresentationStep, StepStatus
from tools.modify import modify_presentation, modify_research, process_wizard_request
from schemas.presentations import PresentationDetailResponse

router = APIRouter(
    prefix="/presentations",
    tags=["presentations"],
)

@router.post("/{presentation_id}/save_modified",
           summary="Save modified presentation",
           description="Saves modified presentation data to the appropriate steps")
async def save_modified_presentation(
    presentation_id: int,
    modified_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Presentation).filter(
            (Presentation.id == presentation_id) & (Presentation.is_deleted == False)
        )
    )
    presentation = result.scalar_one_or_none()

    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    slides_step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == PresentationStep.SLIDES.value
        )
    )
    slides_step = slides_step_result.scalars().first()

    if not slides_step:
        raise HTTPException(status_code=404, detail="Slides step not found")

    slides_step.set_result(modified_data)

    compiled_step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step == PresentationStep.COMPILED.value
        )
    )
    compiled_step = compiled_step_result.scalars().first()

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
    try:
        data = await request.json()
        prompt = data.get("prompt")
        slide_index = data.get("slide_index")
        current_step = data.get("current_step")

        if not prompt:
            return JSONResponse(
                status_code=400,
                content={"detail": "Missing prompt"},
            )

        async with SessionLocal() as db:
            research_step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.RESEARCH.value
                )
            )
            research_step = research_step_result.scalars().first()

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
                    content={"detail": "Research step not completed. Cannot modify presentation before research is done."},
                )

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

            if not compiled_data:
                compiled_step_result = await db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.COMPILED.value
                    )
                )
                compiled_step_model = compiled_step_result.scalars().first()
                if compiled_step_model and compiled_step_model.status == StepStatus.COMPLETED.value:
                    compiled_data = compiled_step_model.get_result()
                else:
                    slides_step_result = await db.execute(
                        select(PresentationStepModel).filter(
                            PresentationStepModel.presentation_id == presentation_id,
                            PresentationStepModel.step == PresentationStep.SLIDES.value
                        )
                    )
                    slides_step_model = slides_step_result.scalars().first()
                    if slides_step_model and slides_step_model.status == StepStatus.COMPLETED.value:
                        compiled_data = slides_step_model.get_result()

            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step.in_([
                        PresentationStep.RESEARCH.value,
                        PresentationStep.MANUAL_RESEARCH.value,
                    ])
                )
            )
            research_step = step_result.scalars().first()
            research_data = research_step.get_result() if research_step else None

            if slide_index is not None:
                result = await modify_presentation(
                    compiled_data,
                    research_data,
                    prompt,
                    slide_index=slide_index
                )
                result_dict = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
                return JSONResponse(status_code=200, content=result_dict)
            else:
                result = await modify_presentation(compiled_data, research_data, prompt)
                result_dict = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
                return JSONResponse(status_code=200, content={"modified_presentation": result_dict, "message": "Presentation modified successfully"})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in modify_presentation_endpoint: {str(e)}")
        print(f"Traceback: {error_details}")
        return JSONResponse(status_code=500, content={"detail": f"Internal server error: {str(e)}"})


@router.post("/{presentation_id}/research/modify",
           summary="Modify research",
           description="Modify research content using AI based on user instructions")
async def modify_research_endpoint(
    presentation_id: int,
    request: Request
):
    try:
        data = await request.json()
        prompt = data.get("prompt")
        if not prompt:
            return JSONResponse(status_code=400, content={"detail": "Missing prompt"})

        async with SessionLocal() as db:
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step.in_([
                        PresentationStep.RESEARCH.value,
                        PresentationStep.MANUAL_RESEARCH.value,
                    ])
                )
            )
            research_step = step_result.scalars().first()

            if not research_step or research_step.status != StepStatus.COMPLETED.value:
                return JSONResponse(status_code=400, content={"detail": "Research step not completed"})

            research_data = research_step.get_result()
            modified = await modify_research(research_data, prompt)
            return JSONResponse(status_code=200, content=modified.model_dump())

    except Exception as e:
        import traceback
        print("Error modifying research", e)
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": f"Error modifying research: {str(e)}"})


@router.post("/{presentation_id}/save_modified_research",
           summary="Save modified research",
           description="Persist modified research data to the research step")
async def save_modified_research(
    presentation_id: int,
    modified_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    step_result = await db.execute(
        select(PresentationStepModel).filter(
            PresentationStepModel.presentation_id == presentation_id,
            PresentationStepModel.step.in_([
                PresentationStep.RESEARCH.value,
                PresentationStep.MANUAL_RESEARCH.value,
            ])
        )
    )
    step = step_result.scalars().first()
    if not step:
        raise HTTPException(status_code=404, detail="Research step not found")

    step.set_result(modified_data)
    step.status = StepStatus.COMPLETED.value
    await db.commit()

    return {"message": f"Modified research saved for presentation {presentation_id}", "presentation_id": presentation_id}


@router.post("/{presentation_id}/wizard",
           summary="Process wizard request",
           description="Process a wizard request using the new context-aware wizard system")
async def process_wizard_request_endpoint(
    presentation_id: int,
    request: Request
):
    try:
        data = await request.json()
        prompt = data.get("prompt")
        current_step = data.get("current_step", "unknown")
        context = data.get("context", {})

        if not prompt:
            return JSONResponse(
                status_code=400,
                content={"detail": "Missing prompt"}
            )

        async with SessionLocal() as db:
            presentation_result = await db.execute(
                select(Presentation).filter(Presentation.id == presentation_id)
            )
            presentation = presentation_result.scalars().first()

            if not presentation:
                return JSONResponse(status_code=404, content={"detail": "Presentation not found"})

            steps_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id
                )
            )
            steps = steps_result.scalars().all()

            presentation_data = {
                "id": presentation.id,
                "name": presentation.name,
                "topic": presentation.topic,
                "author": presentation.author,
                "steps": []
            }

            for step in steps:
                step_data = {
                    "step": step.step,
                    "status": step.status,
                    "result": step.get_result() if step.status == StepStatus.COMPLETED.value else None
                }
                presentation_data["steps"].append(step_data)

            result = await process_wizard_request(
                prompt=prompt,
                presentation_data=presentation_data,
                current_step=current_step,
                context=context
            )

            return JSONResponse(status_code=200, content=result)

    except Exception as e:
        import traceback
        print(f"Error in wizard request: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": f"Error processing wizard request: {str(e)}"})
