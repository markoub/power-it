from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os

from database import get_db, PresentationStepModel, PresentationStep, StepStatus
from tools.images import generate_image_from_prompt
from config import PRESENTATIONS_STORAGE_DIR

router = APIRouter(
    prefix="/presentations",
    tags=["presentations"],
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
    data = await request.json()
    prompt = data.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")

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

    result = await generate_image_from_prompt(prompt, "1024x1024", presentation_id)
    if not result or not result.image_path:
        raise HTTPException(status_code=500, detail="Image generation failed")

    filename = os.path.basename(result.image_path)
    image_url = f"/presentations/{presentation_id}/images/{filename}"

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
    images_list = images_data["images"] if isinstance(images_data, dict) and "images" in images_data else images_data

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
    image_path = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id), "images", filename)
    if not os.path.exists(image_path):
        legacy_path = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id), filename)
        if os.path.exists(legacy_path):
            return FileResponse(
                legacy_path,
                media_type="image/png",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        raise HTTPException(status_code=404, detail=f"Image not found: {filename}")

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
    return FileResponse(
        path=os.devnull,
        media_type="application/octet-stream",
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept"
        }
    )
