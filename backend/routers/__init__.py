from .presentations import router as presentations_router
from .images import router as images_router
from .logos import router as logos_router
from .pptx import router as pptx_router

__all__ = [
    "presentations_router",
    "images_router",
    "logos_router",
    "pptx_router",
]
