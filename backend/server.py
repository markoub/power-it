#!/usr/bin/env python3

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from fastapi.openapi.utils import get_openapi

# Import tools
from tools.research import research_topic
from tools.slides import generate_slides
from tools.images import generate_slide_images, generate_image_from_prompt
from tools.generate_pptx import generate_pptx_from_slides, convert_pptx_to_png
from tools.modify import modify_presentation
from orchestrator import create_presentation
from models import ResearchData, SlidePresentation, FullPresentation, ImageGeneration, PptxGeneration

# Import database models
from database import SessionLocal, PresentationStepModel, PresentationStep, StepStatus

# Export for api.py to use
__all__ = ['modify_presentation_with_gemini']

# Initialize FastMCP server without importing the app from api.py
# This removes the circular dependency
mcp = FastMCP(name="PresentationAssistant")

@mcp.tool()
def ping() -> str:
    """Simple ping to test if the server is running"""
    return "Presentation Assistant is running!"

@mcp.tool()
async def modify_presentation_with_gemini(
    compiled_data: Dict[str, Any],
    research_data: Dict[str, Any],
    prompt: str
) -> Dict[str, Any]:
    """
    Use Gemini to modify a presentation based on user instructions.
    
    Args:
        compiled_data: The compiled presentation data (slides with images)
        research_data: Research data for context
        prompt: User instructions for how to modify the presentation
        
    Returns:
        A modified presentation in the same format as the compiled presentation
    """
    # Use the tool function from the tools module
    result = await modify_presentation(compiled_data, research_data, prompt)
    # Convert to dict for serialization
    return result.model_dump()

# Load other MCP tools
@mcp.tool()
async def research_presentation_topic(topic: str) -> Dict[str, Any]:
    """Research a presentation topic and return information and links"""
    try:
        research_data = await research_topic(topic)
        return research_data.model_dump()
    except Exception as e:
        print(f"Error in research_presentation_topic: {str(e)}")
        raise e

@mcp.tool()
async def create_new_presentation(name: str, topic: str) -> Dict[str, Any]:
    """Create a new presentation with the given name and topic"""
    try:
        presentation_id = await create_presentation(name, topic)
        return {"presentation_id": presentation_id}
    except Exception as e:
        print(f"Error in create_new_presentation: {str(e)}")
        raise e

@mcp.tool()
async def generate_images_for_slides(slides_data: Dict[str, Any], presentation_id: Optional[int] = None) -> Dict[str, Any]:
    """Generate images for presentation slides"""
    try:
        # Convert dictionary to Pydantic model
        slides = SlidePresentation(**slides_data)
        
        # Generate images for slides
        print(f"Starting image generation for presentation {presentation_id}...")
        image_results: List[ImageGeneration] = await generate_slide_images(slides, presentation_id)
        print(f"Completed image generation. Found {len(image_results)} images total.")
        
        # Convert results to dictionary for storage
        images_list_for_db = []
        for img in image_results:
            try:
                images_list_for_db.append(img.model_dump())
                # Log successful dump for specific image
                print(f"Successfully prepared image data for slide {img.slide_index}, field {img.image_field_name} for DB.")
            except Exception as dump_error:
                print(f"ERROR: Failed to serialize ImageGeneration object for slide {img.slide_index}, field {img.image_field_name}: {dump_error}")
                # Optionally decide how to handle: skip this image, raise error, etc.
                # For now, we'll just log and skip this image to avoid failing the whole step.
                continue 
                
        print(f"Returning {len(images_list_for_db)} image data entries to be saved.")
        return {"images": images_list_for_db}
        
    except Exception as e:
        print(f"Error in generate_images_for_slides tool function: {str(e)}")
        # Re-raise the exception so the step fails if something critical went wrong before serialization
        raise e

@mcp.tool()
async def generate_pptx_presentation(slides_data: Dict[str, Any], presentation_id: Optional[int] = None) -> Dict[str, Any]:
    """Generate a PowerPoint presentation from slides data"""
    try:
        # Determine which model to use based on the data
        # CompiledPresentation has slides array with objects containing image_url
        is_compiled = False
        if "slides" in slides_data and isinstance(slides_data["slides"], list):
            for slide in slides_data["slides"]:
                if isinstance(slide, dict) and "image_url" in slide:
                    is_compiled = True
                    break
        
        # Convert dictionary to appropriate Pydantic model
        if is_compiled:
            from models import CompiledPresentation
            print("Using CompiledPresentation model (with images)")
            slides = CompiledPresentation(**slides_data)
        else:
            from models import SlidePresentation
            print("Using SlidePresentation model (without images)")
            slides = SlidePresentation(**slides_data)
        
        # Generate PPTX file
        pptx_result = await generate_pptx_from_slides(slides, presentation_id)
        
        # Convert PPTX to PNG images
        png_paths = await convert_pptx_to_png(pptx_result.pptx_path)
        
        # Update the result with PNG paths
        pptx_result.png_paths = png_paths
        
        # Convert result to dictionary
        return pptx_result.model_dump()
    except Exception as e:
        print(f"Error in generate_pptx_presentation: {str(e)}")
        raise e

@mcp.tool()
async def generate_image_tool(prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
    """Generate an image from a text prompt"""
    # ... existing code ...

# Add enhanced OpenAPI schema generator for improved Swagger docs
def enhanced_openapi_schema(app):
    """
    Create an enhanced OpenAPI schema with more detailed information.
    This includes better descriptions, examples, and response schemas.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="""
# PowerIt Presentation API

This API enables creation, management, and generation of AI-powered presentations.

## Key Features
- Research presentation topics automatically
- Generate slide content
- Create and modify images for slides
- Compile presentations with images
- Generate PowerPoint (PPTX) files
- Export presentations to PDF
- Search for company logos
        """,
        routes=app.routes,
    )
    
    # Add additional info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Additional server information
    openapi_schema["servers"] = [
        {"url": "/", "description": "Current server"}
    ]
    
    # Add authentication information (if needed in the future)
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key authentication (currently not enforced)"
        }
    }
    
    # Add more detailed tags for better organization
    openapi_schema["tags"] = [
        {
            "name": "presentations",
            "description": "Endpoints for creating and managing presentations",
        },
        {
            "name": "images",
            "description": "Endpoints for generating and managing images",
        },
        {
            "name": "logos",
            "description": "Endpoints for searching and retrieving company logos",
        }
    ]
    
    return openapi_schema

# This simplifies startup for manual testing
if __name__ == "__main__":
    print("Running presentation assistant server in stdio mode")
    mcp.run() 