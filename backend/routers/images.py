from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from models import ImageGeneration
from tools import generate_image_from_prompt
import os

router = APIRouter(
    prefix="/images",
    tags=["images"],
    responses={404: {"description": "Image not found"}},
)

class ImageRequest:
    """Model for image generation request"""
    def __init__(self, prompt: str, size: str = "1024x1024"):
        self.prompt = prompt
        self.size = size

class ImageResponse:
    """Model for image generation response"""
    def __init__(self, slide_index: int, slide_title: str, prompt: str, image_url: str):
        self.slide_index = slide_index
        self.slide_title = slide_title 
        self.prompt = prompt
        self.image_url = image_url

@router.post("", 
           summary="Generate a single image", 
           description="Generate a single image from a prompt using AI")
async def generate_image(
    request: Request
):
    """
    Generate a single image from a prompt.
    """
    try:
        # Parse request body
        data = await request.json()
        prompt = data.get("prompt")
        size = data.get("size", "1024x1024")
        
        if not prompt:
            return JSONResponse(
                status_code=400,
                content={"detail": "Missing prompt"},
            )
        
        # Validate size
        valid_sizes = ["1024x1024", "1024x1792", "1792x1024"]
        if size not in valid_sizes:
            return JSONResponse(
                status_code=400,
                content={"detail": f"Invalid size. Valid sizes are: {', '.join(valid_sizes)}"},
            )
            
        # No presentation ID here, but we'll use a special ID for standalone images
        temp_presentation_id = 0  # Use 0 for temporary/standalone images
        
        result = await generate_image_from_prompt(prompt, size, temp_presentation_id)
        if not result:
            raise HTTPException(status_code=500, detail="Image generation failed")
        
        # If we have an image path, create a URL
        if result.image_path and os.path.exists(result.image_path):
            filename = os.path.basename(result.image_path)
            # Create the response
            return JSONResponse(
                status_code=200,
                content={
                    "slide_index": result.slide_index,
                    "slide_title": result.slide_title,
                    "prompt": result.prompt,
                    "image_url": f"/presentations/{temp_presentation_id}/images/{filename}"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Image file not created properly")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error generating image: {str(e)}"},
        ) 