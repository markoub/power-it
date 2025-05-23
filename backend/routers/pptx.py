from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os

from database import get_db, PresentationStepModel, PresentationStep, StepStatus, Presentation
from schemas.presentations import TopicUpdateRequest, PresentationResponse
from schemas.images import SlideTypesResponse
from services import execute_topic_update_task
from config import PRESENTATIONS_STORAGE_DIR

router = APIRouter(
    prefix="/presentations",
    tags=["presentations"],
    responses={404: {"description": "Resource not found"}},
)

@router.get("/{presentation_id}/pptx-slides",
          summary="Get PPTX slides",
          description="Gets the list of PNG images for a presentation's PPTX slides")
async def get_pptx_slides(presentation_id: int, db: AsyncSession = Depends(get_db)):
    """Get the list of PNG images for a presentation's PPTX slides"""
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
    """Get a specific PPTX slide image by filename"""
    presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id))
    image_path = os.path.join(presentation_dir, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Slide image not found")
    return FileResponse(image_path)

@router.get("/{presentation_id}/download-pptx",
          summary="Download PPTX file",
          description="Downloads the PPTX file for a presentation")
async def download_pptx(presentation_id: int, filename: str = None, db: AsyncSession = Depends(get_db)):
    """Download the PPTX file for a presentation"""
    query = select(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == PresentationStep.PPTX.value)
    )
    result = await db.execute(query)
    pptx_step = result.scalars().first()

    if not pptx_step or pptx_step.status != StepStatus.COMPLETED.value:
        raise HTTPException(status_code=404, detail="PPTX file not found or not generated yet")

    pptx_data = pptx_step.get_result()
    if not pptx_data or "pptx_path" not in pptx_data:
        raise HTTPException(status_code=404, detail="PPTX file not found")

    display_filename = filename or f"presentation_{presentation_id}.pptx"
    if not display_filename.lower().endswith('.pptx'):
        display_filename += '.pptx'

    headers = {
        "Content-Disposition": f'attachment; filename="{display_filename}"',
        "Content-Type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "X-Content-Type-Options": "nosniff",
        "Content-Description": "File Transfer",
        "Content-Transfer-Encoding": "binary",
        "Expires": "0",
        "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
        "Pragma": "public"
    }

    return FileResponse(
        pptx_data["pptx_path"],
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=display_filename,
        headers=headers
    )

@router.get("/{presentation_id}/download-pdf",
          summary="Download PDF file",
          description="Downloads the PDF version of a presentation")
async def download_pdf(presentation_id: int, filename: str = None, db: AsyncSession = Depends(get_db)):
    """Download the PDF version of a presentation"""
    query = select(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == PresentationStep.PPTX.value)
    )
    result = await db.execute(query)
    pptx_step = result.scalars().first()

    if not pptx_step or pptx_step.status != StepStatus.COMPLETED.value:
        raise HTTPException(status_code=404, detail="PDF file not found or not generated yet")

    pptx_data = pptx_step.get_result()
    if not pptx_data or "pdf_path" not in pptx_data:
        raise HTTPException(status_code=404, detail="PDF file not found")

    display_filename = filename or f"presentation_{presentation_id}.pdf"
    if not display_filename.lower().endswith('.pdf'):
        display_filename += '.pdf'

    headers = {
        "Content-Disposition": f'attachment; filename="{display_filename}"',
        "Content-Type": "application/pdf",
    }

    return FileResponse(
        pptx_data["pdf_path"],
        media_type="application/pdf",
        filename=display_filename,
        headers=headers
    )

@router.get("/slide-types", response_model=SlideTypesResponse,
            summary="Get available slide types",
            description="Returns all available slide types and their fields")
async def get_slide_types():
    """Returns all available slide types and their fields with descriptions."""
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

@router.post("/{presentation_id}/update-topic", response_model=PresentationResponse,
            summary="Update presentation topic",
            description="Updates the presentation topic and reruns research and slide generation")
async def update_presentation_topic(
    presentation_id: int,
    update_data: TopicUpdateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Presentation).filter(Presentation.id == presentation_id))
        presentation = result.scalars().first()

        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")

        new_topic = update_data.topic
        presentation.topic = new_topic
        await db.commit()
        await db.refresh(presentation)

        background_tasks.add_task(
            execute_topic_update_task,
            presentation_id,
            new_topic,
            presentation.author
        )

        return {
            "id": presentation.id,
            "name": presentation.name,
            "topic": new_topic,
            "author": presentation.author,
            "created_at": presentation.created_at.isoformat(),
            "updated_at": presentation.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Unexpected error in update_presentation_topic: {str(e)}")
        print(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )

