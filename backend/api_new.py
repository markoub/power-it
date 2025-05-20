from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

# Import database module
from database import init_db

# Import routers
from routers.presentations import router as presentations_router 
from routers.images import router as images_router
from routers.logos import router as logos_router

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify the exact frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(presentations_router)
app.include_router(images_router)
app.include_router(logos_router)

# Custom OpenAPI schema and documentation
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )

@app.get("/")
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