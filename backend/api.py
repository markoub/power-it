from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress debug messages from aiosqlite
logging.getLogger("aiosqlite").setLevel(logging.WARNING)

logger = logging.getLogger("powerit-backend")

# Import database module
from database import init_db

# Import routers
from routers.presentations import router as presentations_router
from routers.presentation_steps import router as presentation_steps_router
from routers.presentation_modify import router as presentation_modify_router
from routers.presentation_images import router as presentation_images_router
from routers.images import router as images_router
from routers.logos import router as logos_router
from routers.pptx import router as pptx_router
from routers.tts import router as tts_router
from routers.research_clarification import router as research_clarification_router

# Import test router (only available in test environment)
import os
if os.getenv("POWERIT_ENV") == "test":
    from routers.test import router as test_router

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")
    yield
    # Shutdown code (if needed)
    print("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="PowerIt Presentation API",
    description="API for creating, managing, and generating AI-powered presentations",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add exception handler for detailed error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    error_details = traceback.format_exc()
    
    logger.error(f"Request to {request.url} failed with error: {error_msg}")
    logger.error(f"Traceback: {error_details}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": error_msg,
            "traceback": error_details.split("\n"),
            "request_path": str(request.url)
        },
    )

# Configure CORS
allowed_origins = ["http://localhost:3000"]
# Add test frontend origin when in test mode
if os.getenv("POWERIT_ENV") == "test":
    allowed_origins.append("http://localhost:3001")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(presentations_router)
app.include_router(presentation_steps_router)
app.include_router(presentation_modify_router)
app.include_router(presentation_images_router)
app.include_router(images_router)
app.include_router(logos_router)
app.include_router(pptx_router)
app.include_router(tts_router)
app.include_router(research_clarification_router)

# Include test router only in test environment
if os.getenv("POWERIT_ENV") == "test":
    app.include_router(test_router)

# Custom OpenAPI schema and documentation
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
    )

@app.get("/", tags=["health"])
async def root():
    return {"message": "PowerIt Presentation Assistant API is running"}

# Custom OpenAPI schema with more details
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Set OpenAPI version to 3.0.0 (compatible with Swagger UI)
    openapi_schema["openapi"] = "3.0.0"
    
    # Add additional info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Additional server information
    openapi_schema["servers"] = [
        {"url": "/", "description": "Current server"}
    ]
    
    # Add authentication information
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 