from typing import Optional, List
from pydantic import BaseModel, Field

class ImageRequest(BaseModel):
    """Image generation request model"""
    prompt: str = Field(
        description="The text prompt describing the image to generate. Be specific about content, style, lighting, perspective, etc."
    )
    size: str = Field(
        default="1024x1024", 
        description="The size of the generated image. Available options: 256x256, 512x512, 1024x1024, 1792x1024, 1024x1792"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "A futuristic city skyline with flying vehicles, neon lights, and tall glass buildings under a sunset sky",
                "size": "1024x1024"
            }
        }

class ImageResponse(BaseModel):
    """Image generation response model"""
    slide_index: int = Field(
        description="The slide index this image belongs to, or -1 if standalone"
    )
    slide_title: str = Field(
        description="The title of the slide this image belongs to"
    )
    prompt: str = Field(
        description="The prompt used to generate this image"
    )
    image_url: str = Field(
        description="The URL to retrieve the generated image. Format: /presentations/{presentation_id}/images/{filename}"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "slide_index": 2,
                "slide_title": "Future Technologies",
                "prompt": "A futuristic city skyline with flying vehicles, neon lights, and tall glass buildings under a sunset sky",
                "image_url": "/presentations/1/images/slide_2_image.png"
            }
        }

class LogoRequest(BaseModel):
    """Logo search request model"""
    term: str = Field(
        description="Company or brand name to search for a logo"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "term": "Microsoft"
            }
        }

class LogoResponse(BaseModel):
    """Logo search response model"""
    name: str = Field(
        description="Name of the company or brand"
    )
    url: str = Field(
        description="Website URL of the company or brand"
    )
    image_url: str = Field(
        description="URL to the logo image that can be used directly in presentations"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Microsoft",
                "url": "https://www.microsoft.com",
                "image_url": "/logos/microsoft"
            }
        }

class SlideDetails(BaseModel):
    """Model for slide type details and available fields"""
    type: str = Field(description="The slide type identifier")
    description: str = Field(description="Description of what this slide type is used for")
    fields: dict = Field(description="Map of available fields for this slide type with their descriptions")

class SlideTypesResponse(BaseModel):
    """Response model for available slide types"""
    slide_types: List[SlideDetails] = Field(description="List of available slide types and their fields")
    
    class Config:
        schema_extra = {
            "example": {
                "slide_types": [
                    {
                        "type": "welcome",
                        "description": "Opening slide with title and subtitle",
                        "fields": {
                            "title": "Main presentation title",
                            "subtitle": "Optional subtitle or tagline"
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
                    }
                ]
            }
        } 