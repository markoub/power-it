from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exc as sqlalchemy_exc
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import json
import os
from fastapi.responses import FileResponse, JSONResponse, Response
from enum import Enum
import time
from functools import lru_cache
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import traceback

# Import database models
from database import get_db, init_db, Presentation, PresentationStepModel, PresentationStep, StepStatus, SessionLocal
from models import (
    PresentationCreate, 
    StepUpdate,
    ResearchData, 
    SlidePresentation,
    ImageGeneration,
    CompiledPresentation
)

# Import MCP tools
from tools import (
    research_topic,
    process_manual_research,
    generate_slides,
    generate_slide_images,
    generate_image_from_prompt,
    generate_compiled_presentation,
    modify_presentation,
    generate_pptx_from_slides,
    convert_pptx_to_png
)
from tools.images import load_image_from_file, save_image_to_file
from tools.logo_fetcher import LogoFetcher
from config import PRESENTATIONS_STORAGE_DIR
from tools.generate_pptx import generate_pptx_from_slides, convert_pptx_to_png

# Import routers
from routers.presentations import router as presentations_router 
from routers.images import router as images_router
from routers.logos import router as logos_router

# Import server related functions
from server import enhanced_openapi_schema

app = FastAPI(
    title="PowerIt Presentation API",
    description="API for creating, managing, and generating AI-powered presentations",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify the exact frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Universal Exception Handler Middleware
@app.middleware("http")
async def universal_exception_handler_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        tb_str = traceback.format_exc()
        # Log to server console
        print(f"UNHANDLED EXCEPTION CAUGHT BY MIDDLEWARE:\nPath: {request.url.path}\nMethod: {request.method}\nError: {str(e)}\nTraceback: {tb_str}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected server error occurred.",
                "exception_type": str(type(e).__name__),
                "error_message": str(e),
                "traceback": tb_str.splitlines()
            },
        )

# Logo Fetcher instance
logo_fetcher = LogoFetcher()

# API Models
class PresentationResponse(BaseModel):
    id: int
    name: str
    topic: Optional[str] = None
    author: Optional[str] = None
    created_at: str
    updated_at: str

class PresentationStepResponse(BaseModel):
    id: int
    step: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str

class PresentationDetailResponse(BaseModel):
    id: int
    name: str
    topic: Optional[str] = None
    author: Optional[str] = None
    created_at: str
    updated_at: str
    steps: List[PresentationStepResponse]

class StepUpdateRequest(BaseModel):
    result: Dict[str, Any]
    
class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"

class ImageResponse(BaseModel):
    slide_index: int
    slide_title: str
    prompt: str
    image_url: str

class LogoRequest(BaseModel):
    term: str

class LogoResponse(BaseModel):
    name: str
    url: str
    image_url: str

# Application startup event
@app.on_event("startup")
async def startup():
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")

# Simple time-based cache for presentation list
_presentations_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 5  # Cache TTL in seconds
}

# Include routers
app.include_router(presentations_router)
app.include_router(images_router)
app.include_router(logos_router)

# Custom exception handler for IntegrityError
@app.exception_handler(sqlalchemy_exc.IntegrityError)
async def integrity_error_exception_handler(request: Request, exc: sqlalchemy_exc.IntegrityError):
    # Log the error for debugging (optional, but recommended)
    print(f"IntegrityError: {exc.orig}")
    print(f"Params: {exc.params}")
    # You could also use a proper logger here
    # logger.error(f"IntegrityError: {exc.orig}", exc_info=True)
    
    detail = "An integrity constraint failed. This usually means you are trying to create an entry that already exists or violates a unique constraint."
    if exc.orig and hasattr(exc.orig, 'pgcode') and exc.orig.pgcode == '23505': # Specific to PostgreSQL unique violation
        detail = f"Database unique constraint violated: {exc.orig.diag.message_detail}"
    elif exc.orig: # General case for other database errors or if pgcode is not available
        detail = f"Database integrity error: {exc.orig}"

    return JSONResponse(
        status_code=400,
        content={"detail": detail, "params": exc.params if hasattr(exc, 'params') else None},
    )

# Custom OpenAPI schema and documentation
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

@app.get("/")
async def root():
    return {"message": "PowerIt Presentation Assistant API is running"}

@app.get("/health")
async def health():
    """Health endpoint that shows current configuration"""
    import config
    return {
        "status": "ok",
        "message": "PowerIt Presentation Assistant API is running",
        "offline_mode": config.OFFLINE_MODE,
        "powerit_offline_env": os.environ.get("POWERIT_OFFLINE", "0")
    }

@app.post("/health/config")
async def update_config(offline: bool = None):
    """Update runtime configuration for testing purposes"""
    if offline is not None:
        # Update the environment variable
        os.environ["POWERIT_OFFLINE"] = "1" if offline else "0"
        
        # Force reload of config and all modules that depend on OFFLINE_MODE
        import importlib
        import sys
        
        # List of modules that need to be reloaded when OFFLINE_MODE changes
        modules_to_reload = [
            'config',
            'tools.research', 
            'tools.slides',
            'tools.images',
            'tools.logo_fetcher',
            'tools.modify'
        ]
        
        for module_name in modules_to_reload:
            if module_name in sys.modules:
                try:
                    importlib.reload(sys.modules[module_name])
                    print(f"Reloaded module: {module_name}")
                except Exception as e:
                    print(f"Warning: Could not reload {module_name}: {e}")
        
        # Import config after reload to get the new OFFLINE_MODE value
        import config
        
        return {
            "status": "updated",
            "offline_mode": config.OFFLINE_MODE,
            "powerit_offline_env": os.environ.get("POWERIT_OFFLINE", "0"),
            "reloaded_modules": modules_to_reload
        }
    
    return {"status": "no changes"}

# Replace custom_openapi with the enhanced version from server.py
app.openapi = lambda: enhanced_openapi_schema(app)

# API Routes
@app.post("/images", response_model=ImageResponse)
async def generate_image(
    request: ImageRequest,
    request_obj: Request
):
    """
    Generate a single image from a prompt.
    """
    # No presentation ID here, but we'll use a special ID for standalone images
    temp_presentation_id = 0  # Use 0 for temporary/standalone images
    
    result = await generate_image_from_prompt(request.prompt, request.size, temp_presentation_id)
    if not result:
        raise HTTPException(status_code=500, detail="Image generation failed")
    
    # If we have an image path, create a URL
    if result.image_path and os.path.exists(result.image_path):
        filename = os.path.basename(result.image_path)
        # Create the response using our ImageResponse model
        return ImageResponse(
            slide_index=result.slide_index,
            slide_title=result.slide_title,
            prompt=result.prompt,
            image_url=f"/presentations/{temp_presentation_id}/images/{filename}"
        )
    else:
        raise HTTPException(status_code=500, detail="Image file not created properly")

@app.get("/presentations/{presentation_id}/images/{filename}")
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
            return FileResponse(legacy_path, media_type="image/png")
        
        # List files in the directory to help with debugging
        images_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id), "images")
        if os.path.exists(images_dir):
            print(f"Available files in {images_dir}:")
            for file in os.listdir(images_dir):
                print(f"  - {file}")
        
        print(f"Image not found: {filename}")
        raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
    
    print(f"Serving image: {image_path}")
    # Return the file directly
    return FileResponse(image_path, media_type="image/png")

@app.post("/presentations/{presentation_id}/save_modified")
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
    result = await db.execute(select(Presentation).filter(Presentation.id == presentation_id))
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

@app.post("/presentations/{presentation_id}/modify")
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

@app.post("/logos/search", response_model=LogoResponse)
async def search_logo(request: LogoRequest):
    """Search for a logo by term and return its information."""
    logo_info = logo_fetcher.search_logo(request.term)
    if not logo_info:
        raise HTTPException(
            status_code=404,
            detail=f"No logo found for '{request.term}'"
        )
    return logo_info

@app.get("/logos/{term}")
async def get_logo(term: str):
    """Fetch and return a logo image for the given term."""
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

# Background task functions
async def execute_research_task(presentation_id: int, topic: str, author: str = None):
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Update step status to processing
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.RESEARCH.value
                )
            )
            step = step_result.scalars().first()
            
            if not step:
                return
            
            # Get presentation to retrieve author if needed
            presentation_result = await db.execute(
                select(Presentation).filter(Presentation.id == presentation_id)
            )
            presentation = presentation_result.scalars().first()
            
            # If author wasn't provided, use it from the presentation
            if author is None and presentation and presentation.author:
                author = presentation.author
            
            # Run research tool
            research_data = await research_topic(topic)
            
            # Update step with result
            step.set_result(research_data.model_dump())
            step.status = StepStatus.COMPLETED.value
            await db.commit()
            
        except Exception as e:
            # Update step status to failed
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.RESEARCH.value
                )
            )
            step = step_result.scalars().first()
            
            if step:
                step.status = StepStatus.FAILED.value
                step.set_result({"error": str(e)})
                await db.commit()

async def execute_slides_task(presentation_id: int):
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Get presentation to retrieve author
            presentation_result = await db.execute(
                select(Presentation).filter(Presentation.id == presentation_id)
            )
            presentation = presentation_result.scalars().first()
            author = None
            if presentation:
                author = presentation.author
            
            # Get research data - first try regular research
            research_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.RESEARCH.value
                )
            )
            research_step = research_result.scalars().first()
            
            # If no regular research found, try manual research
            if not research_step or research_step.status != StepStatus.COMPLETED.value:
                manual_research_result = await db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.MANUAL_RESEARCH.value
                    )
                )
                research_step = manual_research_result.scalars().first()
                
                # If still no valid research found, exit
                if not research_step or research_step.status != StepStatus.COMPLETED.value:
                    return
            
            # Get slides step
            slides_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.SLIDES.value
                )
            )
            slides_step = slides_result.scalars().first()
            
            if not slides_step:
                return
            
            # Mark slides step as processing
            slides_step.status = StepStatus.PROCESSING.value
            await db.commit()
            
            # Convert research data to ResearchData model
            research_data = ResearchData(**research_step.get_result())
            
            # Use default 10 slides
            target_slides = 10
            
            # Run slides generation tool with author
            slides_data = await generate_slides(research_data, target_slides, author)
            
            # Update slides step with result
            slides_step.set_result(slides_data.model_dump())
            slides_step.status = StepStatus.COMPLETED.value
            await db.commit()
            
        except Exception as e:
            # Update step status to failed
            slides_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.SLIDES.value
                )
            )
            slides_step = slides_result.scalars().first()
            
            if slides_step:
                slides_step.status = StepStatus.FAILED.value
                slides_step.set_result({"error": str(e)})
                await db.commit()

async def execute_images_task(presentation_id: int):
    """
    Background task to generate images for presentation slides
    """
    # Create a new session for the background task
    async with SessionLocal() as db:
        # Get the presentation
        result = await db.execute(select(Presentation).filter(Presentation.id == presentation_id))
        presentation = result.scalars().first()
        
        if not presentation:
            print(f"Presentation {presentation_id} not found")
            return
        
        # Get the slides step
        slides_step_result = await db.execute(
            select(PresentationStepModel).filter(
                PresentationStepModel.presentation_id == presentation_id,
                PresentationStepModel.step == PresentationStep.SLIDES.value
            )
        )
        slides_step = slides_step_result.scalars().first()
        
        if not slides_step or slides_step.status != StepStatus.COMPLETED.value:
            print(f"Slides step not completed for presentation {presentation_id}")
            return
        
        # Get the images step
        images_step_result = await db.execute(
            select(PresentationStepModel).filter(
                PresentationStepModel.presentation_id == presentation_id,
                PresentationStepModel.step == PresentationStep.IMAGES.value
            )
        )
        images_step = images_step_result.scalars().first()
        
        if not images_step:
            print(f"Images step not found for presentation {presentation_id}")
            return
        
        # If images step is already completed, don't regenerate images
        if images_step.status == StepStatus.COMPLETED.value:
            print(f"Images already generated for presentation {presentation_id}")
            return
            
        slides_data = slides_step.get_result()
        if not slides_data:
            print(f"No slides data found for presentation {presentation_id}")
            return
        
        try:
            # Update status to processing
            images_step.status = StepStatus.PROCESSING.value
            await db.commit()
            await db.close()  # Close DB connection while processing images
            
            # Open a new connection for updating the results later
            slides_obj = SlidePresentation(**slides_data)
            
            # Use a timeout for the image generation to prevent hanging
            try:
                images = await asyncio.wait_for(
                    generate_slide_images(slides_obj, presentation_id),
                    timeout=300  # 5 minute timeout for all images
                )
            except asyncio.TimeoutError:
                async with SessionLocal() as error_db:
                    error_step_result = await error_db.execute(
                        select(PresentationStepModel).filter(
                            PresentationStepModel.presentation_id == presentation_id,
                            PresentationStepModel.step == PresentationStep.IMAGES.value
                        )
                    )
                    error_step = error_step_result.scalars().first()
                    if error_step:
                        error_step.status = StepStatus.ERROR.value
                        error_step.error_message = "Image generation timed out after 5 minutes"
                        await error_db.commit()
                print(f"Image generation timed out for presentation {presentation_id}")
                return
            
            # Create a new DB session for updating the results
            async with SessionLocal() as update_db:
                # Get the images step again
                update_step_result = await update_db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.IMAGES.value
                    )
                )
                update_step = update_step_result.scalars().first()
                
                if not update_step:
                    print(f"Images step not found after processing for presentation {presentation_id}")
                    return
                
                # Store only the image paths and metadata in the database
                image_data = []
                for img in images:
                    # Don't store the base64 data in the database
                    img_dict = img.model_dump()
                    # Remove the base64 data before storing in DB to save space
                    if 'image' in img_dict:
                        del img_dict['image'] 
                    
                    # Make sure the image_url uses the correct structure
                    if 'image_path' in img_dict and img_dict['image_path']:
                        # Extract filename from the absolute path
                        filename = os.path.basename(img_dict['image_path'])
                        # Ensure URL uses the images/ structure
                        img_dict['image_url'] = f"/presentations/{presentation_id}/images/{filename}"
                    
                    image_data.append(img_dict)
                
                # Update the images step with the result
                update_step.status = StepStatus.COMPLETED.value
                update_step.set_result(image_data)
                await update_db.commit()
                
                print(f"Images generated for presentation {presentation_id}: {len(image_data)} images")
        except Exception as e:
            # Update the step status to error
            async with SessionLocal() as error_db:
                error_step_result = await error_db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.IMAGES.value
                    )
                )
                error_step = error_step_result.scalars().first()
                if error_step:
                    error_step.status = StepStatus.ERROR.value
                    error_step.error_message = str(e)
                    await error_db.commit()
            
            print(f"Error generating images for presentation {presentation_id}: {str(e)}")

async def execute_compiled_task(presentation_id: int):
    """
    Background task to generate the compiled presentation by combining slides and images
    """
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Get the presentation
            result = await db.execute(select(Presentation).filter(Presentation.id == presentation_id))
            presentation = result.scalars().first()
            
            if not presentation:
                print(f"Presentation {presentation_id} not found")
                return
            
            # Get the slides step (required)
            slides_step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.SLIDES.value
                )
            )
            slides_step = slides_step_result.scalars().first()
            
            if not slides_step or slides_step.status != StepStatus.COMPLETED.value:
                print(f"Slides step not completed for presentation {presentation_id}")
                return
                
            # Get the images step (required)
            images_step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.IMAGES.value
                )
            )
            images_step = images_step_result.scalars().first()
            
            if not images_step or images_step.status != StepStatus.COMPLETED.value:
                print(f"Images step not completed for presentation {presentation_id}")
                return
            
            # Get the compiled step
            compiled_step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.COMPILED.value
                )
            )
            compiled_step = compiled_step_result.scalars().first()
            
            if not compiled_step:
                print(f"Compiled step not found for presentation {presentation_id}")
                return
            
            # If compiled step is already completed, don't regenerate
            if compiled_step.status == StepStatus.COMPLETED.value:
                print(f"Compiled content already generated for presentation {presentation_id}")
                return
            
            # Update status to processing
            compiled_step.status = StepStatus.PROCESSING.value
            await db.commit()
            
            # Get slides and images data
            slides_data = slides_step.get_result()
            images_data = images_step.get_result()
            
            if not slides_data:
                raise ValueError("No slides data found")
            
            # Process image URLs for the images data
            for image in images_data:
                if isinstance(image, dict) and "image_path" in image:
                    # Extract filename from the absolute path
                    filename = os.path.basename(image["image_path"])
                    # Create a proper URL for the image
                    image["image_url"] = f"/presentations/{presentation_id}/images/{filename}"
            
            # Convert to Pydantic models
            slides_obj = SlidePresentation(**slides_data)
            images_obj = [ImageGeneration(**img) for img in images_data]
            
            # Generate the compiled presentation
            compiled_data = await generate_compiled_presentation(
                slides_obj, 
                images_obj,
                presentation_id
            )
            
            # Update the compiled step with the result
            compiled_step.set_result(compiled_data.model_dump())
            compiled_step.status = StepStatus.COMPLETED.value
            await db.commit()
            
            print(f"Compiled presentation generated for presentation {presentation_id}")
            
        except Exception as e:
            # Update the step status to error
            async with SessionLocal() as error_db:
                error_step_result = await error_db.execute(
                    select(PresentationStepModel).filter(
                        PresentationStepModel.presentation_id == presentation_id,
                        PresentationStepModel.step == PresentationStep.COMPILED.value
                    )
                )
                error_step = error_step_result.scalars().first()
                if error_step:
                    error_step.status = StepStatus.ERROR.value
                    error_step.error_message = str(e)
                    await error_db.commit()
            
            print(f"Error generating compiled presentation for presentation {presentation_id}: {str(e)}")

# Add the PPTX generation execution task
async def execute_pptx_task(presentation_id: int):
    """
    Execute the PPTX generation task for a presentation.
    This generates a PowerPoint presentation from the slides data.
    """
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Update status to processing
            query = update(PresentationStepModel).where(
                (PresentationStepModel.presentation_id == presentation_id) &
                (PresentationStepModel.step == PresentationStep.PPTX.value)
            ).values(status=StepStatus.PROCESSING.value)
            await db.execute(query)
            await db.commit()
            
            # First, check if we have compiled data (includes images)
            query = select(PresentationStepModel).where(
                (PresentationStepModel.presentation_id == presentation_id) &
                (PresentationStepModel.step == PresentationStep.COMPILED.value)
            )
            result = await db.execute(query)
            compiled_step = result.scalars().first()
            
            # If compiled step is available and completed, use it
            if compiled_step and compiled_step.status == StepStatus.COMPLETED.value:
                print(f"Using COMPILED step data for PPTX generation (with images)")
                slides_data = compiled_step.get_result()
                if not slides_data:
                    raise ValueError("No compiled slides data found")
                
                # Check if we have an images field in the result
                if isinstance(slides_data, dict) and "slides" in slides_data:
                    for idx, slide in enumerate(slides_data.get("slides", [])):
                        if "image_url" in slide and slide["image_url"]:
                            image_url = slide["image_url"]
                            print(f"Found image URL for slide {idx}: {image_url}")
                            
                            # Verify if image file exists
                            if image_url.startswith('/presentations/'):
                                parts = image_url.split('/')
                                if len(parts) >= 5:
                                    pres_id = parts[2]
                                    img_filename = parts[-1]
                                    img_path = os.path.join(PRESENTATIONS_STORAGE_DIR, pres_id, "images", img_filename)
                                    print(f"Checking if image exists at: {img_path}")
                                    print(f"Image exists: {os.path.exists(img_path)}")
                                    
                                    # If image doesn't exist in the expected location, check legacy location
                                    if not os.path.exists(img_path):
                                        legacy_path = os.path.join(PRESENTATIONS_STORAGE_DIR, pres_id, img_filename)
                                        print(f"Checking legacy path: {legacy_path}")
                                        print(f"Legacy image exists: {os.path.exists(legacy_path)}")
                                        
                                        # If image exists in legacy location, copy it to new location
                                        if os.path.exists(legacy_path):
                                            import shutil
                                            os.makedirs(os.path.dirname(img_path), exist_ok=True)
                                            shutil.copy(legacy_path, img_path)
                                            print(f"Copied image from legacy location to: {img_path}")
            else:
                # Fall back to just slides data if compiled not available
                print(f"Falling back to SLIDES step data for PPTX generation (without images)")
                query = select(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.SLIDES.value
                )
            )
            result = await db.execute(query)
            slides_step = result.scalars().first()
            
            if not slides_step or slides_step.status != StepStatus.COMPLETED.value:
                raise ValueError("Slides step not completed")
            
            slides_data = slides_step.get_result()
            if not slides_data:
                raise ValueError("No slides data found")
            
            try:
                # Instead of using MCP client, directly call the functions
                from tools.generate_pptx import generate_pptx_from_slides, convert_pptx_to_png
                from models import SlidePresentation, CompiledPresentation
                
                # Convert to appropriate Pydantic model based on which step we're using
                if compiled_step and compiled_step.status == StepStatus.COMPLETED.value:
                    slides_obj = CompiledPresentation(**slides_data)
                else:
                    slides_obj = SlidePresentation(**slides_data)
                
                # Generate PPTX file
                print(f"Generating PPTX for presentation {presentation_id}...")
                pptx_result = await generate_pptx_from_slides(slides_obj, presentation_id)
                
                # Convert PPTX to PNG images
                png_paths = await convert_pptx_to_png(pptx_result.pptx_path)
                
                # Update the result with PNG paths
                pptx_result.png_paths = png_paths
                
                # Convert to dictionary
                result = pptx_result.model_dump()
                
                # Update step with successful result
                query = update(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.PPTX.value)
                ).values(
                    status=StepStatus.COMPLETED.value,
                    result=json.dumps(result)
                )
                await db.execute(query)
                await db.commit()
                
                print(f"PPTX generation completed for presentation {presentation_id}")
                
            except Exception as e:
                print(f"Error generating PPTX: {str(e)}")
                raise e
            
        except Exception as e:
            print(f"Error in PPTX generation task: {str(e)}")
            
            # Update status to error
            query = update(PresentationStepModel).where(
                (PresentationStepModel.presentation_id == presentation_id) &
                (PresentationStepModel.step == PresentationStep.PPTX.value)
            ).values(
                status=StepStatus.ERROR.value,
                error_message=str(e)
            )
            await db.execute(query)
            await db.commit()

# Add endpoint to get PPTX slide images
@app.get("/presentations/{presentation_id}/pptx-slides")
async def get_pptx_slides(presentation_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get the list of PNG images for a presentation's PPTX slides
    """
    # Get PPTX step data
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
    
    # Create image URLs from the paths
    slide_images = []
    for i, path in enumerate(pptx_data["png_paths"]):
        filename = os.path.basename(path)
        slide_images.append({
            "slide_index": i,
            "filename": filename,
            "url": f"/presentations/{presentation_id}/pptx-slides/{filename}"
        })
    
    return {"slides": slide_images}

@app.get("/presentations/{presentation_id}/pptx-slides/{filename}")
async def get_pptx_slide_image(presentation_id: int, filename: str):
    """
    Get a specific PPTX slide image by filename
    """
    # Construct the path to the image
    presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id))
    image_path = os.path.join(presentation_dir, filename)
    
    # Check if the file exists
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Slide image not found")
    
    return FileResponse(image_path)

@app.get("/presentations/{presentation_id}/download-pptx")
async def download_pptx(presentation_id: int, filename: str = None, db: AsyncSession = Depends(get_db)):
    """
    Download the PPTX file for a presentation
    """
    print(f"\n\n=== DOWNLOAD PPTX REQUEST for presentation {presentation_id} ===")
    if filename:
        print(f"Requested filename: {filename}")
    
    # Get PPTX step data
    query = select(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == PresentationStep.PPTX.value)
    )
    result = await db.execute(query)
    pptx_step = result.scalars().first()
    
    if not pptx_step or pptx_step.status != StepStatus.COMPLETED.value:
        print(f"ERROR: PPTX file not found or not generated yet for presentation {presentation_id}")
        raise HTTPException(status_code=404, detail="PPTX file not found or not generated yet")
    
    pptx_data = pptx_step.get_result()
    if not pptx_data or "pptx_path" not in pptx_data:
        print(f"ERROR: PPTX file path not found in result data for presentation {presentation_id}")
        raise HTTPException(status_code=404, detail="PPTX file not found")
    
    print(f"Preparing PPTX download for presentation {presentation_id}")
    print(f"PPTX path: {pptx_data['pptx_path']}")
    print(f"File exists: {os.path.exists(pptx_data['pptx_path'])}")
    print(f"File size: {os.path.getsize(pptx_data['pptx_path']) if os.path.exists(pptx_data['pptx_path']) else 'N/A'} bytes")
    
    # Use the specified filename or create a simple one
    display_filename = filename or f"presentation_{presentation_id}.pptx"
    if not display_filename.lower().endswith('.pptx'):
        display_filename += '.pptx'
    
    print(f"Setting download filename to: {display_filename}")
    
    # Return the PPTX file with extremely explicit download headers
    headers = {
        "Content-Disposition": f'attachment; filename="{display_filename}"',
        "Content-Type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "X-Content-Type-Options": "nosniff",
        # Force download in various browsers
        "Content-Description": "File Transfer",
        "Content-Transfer-Encoding": "binary",
        "Expires": "0",
        "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
        "Pragma": "public"
    }
    
    response = FileResponse(
        pptx_data["pptx_path"],
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=display_filename,
        headers=headers
    )
    
    print(f"=== DOWNLOAD PPTX RESPONSE PREPARED for presentation {presentation_id} ===\n\n")
    return response

@app.get("/presentations/{presentation_id}/download-pdf")
async def download_pdf(presentation_id: int, filename: str = None, db: AsyncSession = Depends(get_db)):
    """
    Download the PDF version of a presentation
    """
    print(f"\n\n=== DOWNLOAD PDF REQUEST for presentation {presentation_id} ===")
    if filename:
        print(f"Requested filename: {filename}")
    
    # Get PPTX step data
    query = select(PresentationStepModel).where(
        (PresentationStepModel.presentation_id == presentation_id) &
        (PresentationStepModel.step == PresentationStep.PPTX.value)
    )
    result = await db.execute(query)
    pptx_step = result.scalars().first()
    
    if not pptx_step or pptx_step.status != StepStatus.COMPLETED.value:
        print(f"ERROR: PPTX step not completed for presentation {presentation_id}")
        raise HTTPException(status_code=404, detail="PDF file not found or not generated yet")
    
    pptx_data = pptx_step.get_result()
    if not pptx_data or "pptx_path" not in pptx_data:
        print(f"ERROR: PPTX file path not found in result data for presentation {presentation_id}")
        raise HTTPException(status_code=404, detail="Source files not found")
        
    # Get the basename of the PPTX file without extension
    basename = os.path.splitext(os.path.basename(pptx_data["pptx_path"]))[0]
    pdf_path = os.path.join(os.path.dirname(pptx_data["pptx_path"]), f"{basename}.pdf")
    
    print(f"Preparing PDF download for presentation {presentation_id}")
    print(f"PDF path: {pdf_path}")
    print(f"File exists: {os.path.exists(pdf_path)}")
    print(f"File size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 'N/A'} bytes")
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF file not found at {pdf_path}")
        raise HTTPException(status_code=404, detail="PDF file not found - it may need to be regenerated")
    
    # Use the specified filename or create a simple one
    display_filename = filename or f"presentation_{presentation_id}.pdf"
    if not display_filename.lower().endswith('.pdf'):
        display_filename += '.pdf'
    
    print(f"Setting download filename to: {display_filename}")
    
    # Return the PDF file with extremely explicit download headers
    headers = {
        "Content-Disposition": f'attachment; filename="{display_filename}"',
        "Content-Type": "application/pdf",
        "X-Content-Type-Options": "nosniff",
        # Force download in various browsers
        "Content-Description": "File Transfer",
        "Content-Transfer-Encoding": "binary",
        "Expires": "0",
        "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
        "Pragma": "public"
    }
    
    response = FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=display_filename,
        headers=headers
    )
    
    print(f"=== DOWNLOAD PDF RESPONSE PREPARED for presentation {presentation_id} ===\n\n")
    return response

async def execute_manual_research_task(presentation_id: int, research_content: str):
    # Create a new session for the background task
    async with SessionLocal() as db:
        try:
            # Update step status to processing
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.MANUAL_RESEARCH.value
                )
            )
            step = step_result.scalars().first()
            
            if not step:
                return
            
            # Process manual research
            research_data = await process_manual_research(research_content)
            
            # Update step with result
            step.set_result(research_data.model_dump())
            step.status = StepStatus.COMPLETED.value
            await db.commit()
            
        except Exception as e:
            # Update step status to failed
            step_result = await db.execute(
                select(PresentationStepModel).filter(
                    PresentationStepModel.presentation_id == presentation_id,
                    PresentationStepModel.step == PresentationStep.MANUAL_RESEARCH.value
                )
            )
            step = step_result.scalars().first()
            
            if step:
                step.status = StepStatus.FAILED.value
                step.set_result({"error": str(e)})
                await db.commit() 