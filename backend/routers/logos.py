from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from tools.logo_fetcher import LogoFetcher

router = APIRouter(
    prefix="/logos",
    tags=["logos"],
    responses={404: {"description": "Logo not found"}}
)

# Logo Fetcher instance
logo_fetcher = LogoFetcher()

# API Models
class LogoRequest(BaseModel):
    """Request model for logo search"""
    term: str
    
    class Config:
        schema_extra = {
            "example": {
                "term": "Google"
            }
        }

class LogoResponse(BaseModel):
    """Response model for logo search"""
    name: str
    url: str
    image_url: str
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Google",
                "url": "https://worldvectorlogo.com/logo/google-1",
                "image_url": "https://cdn.worldvectorlogo.com/logos/google-1.svg"
            }
        }

@router.post("/search", response_model=LogoResponse,
           summary="Search for a logo",
           description="Search for a logo by company or brand name")
async def search_logo(request: LogoRequest):
    """
    Search for a logo by term and return its information.
    
    Parameters:
    - term: The company or brand name to search for
    
    Returns:
    - Logo information including name, URL, and image URL
    """
    logo_info = logo_fetcher.search_logo(request.term)
    if not logo_info:
        raise HTTPException(
            status_code=404,
            detail=f"No logo found for '{request.term}'"
        )
    return logo_info

@router.get("/{term}",
          summary="Get logo image",
          description="Get the SVG image data for a logo")
async def get_logo(term: str):
    """
    Fetch and return a logo image for the given term.
    
    Parameters:
    - term: The company or brand name
    
    Returns:
    - SVG image data
    """
    success, result = logo_fetcher.download_logo(term)
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=result  # This will contain the error message
        )
    
    # result is image data in bytes
    headers = {
        "Content-Disposition": f'attachment; filename="{term.lower().replace(" ", "_")}.svg"'
    }
    return Response(
        content=result, 
        media_type="image/svg+xml",
        headers=headers
    ) 