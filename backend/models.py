from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class Link(BaseModel):
    """Link model for research sources"""
    href: str
    title: str = "Source"

class ResearchData(BaseModel):
    """Research data for a presentation topic"""
    content: str
    links: List[Dict[str, str]] = Field(default_factory=list)

class Slide(BaseModel):
    """Individual slide with type and fields containing the slide content"""
    type: str  # welcome, tableofcontents, section, content, contentimage, conclusion
    fields: Dict[str, Any] = Field(default_factory=dict)  # Fields depend on slide type

class SlidePresentation(BaseModel):
    """Complete slide presentation with title and slides"""
    title: str
    slides: List[Slide]
    author: Optional[str] = None  # Author for the entire presentation

class ImageGeneration(BaseModel):
    """Model for generated image data"""
    slide_index: int  # Index of the slide, -1 if not tied to a specific slide
    slide_title: str  # Title of the slide for reference
    prompt: str  # The prompt used to generate the image
    image_field_name: str # The name of the image field this image corresponds to (e.g., "image", "image1")
    image_path: Optional[str] = None  # Path to the image file on disk
    image: Optional[str] = None  # Base64-encoded image data, used for memory-only handling

class PptxGeneration(BaseModel):
    """Model for generated PPTX data"""
    presentation_id: Optional[Union[int, str]] = None  # ID of the presentation, None for temporary files, str for test cases
    pptx_filename: str  # Filename of the PPTX file
    pptx_path: str  # Full path to the PPTX file
    slide_count: int  # Number of slides in the presentation
    png_paths: List[str] = Field(default_factory=list)  # Paths to PNG images of slides

class PresentationMeta(BaseModel):
    """Metadata about the presentation creation process"""
    topic: str
    target_slides: int
    actual_slides: int

class FullPresentation(BaseModel):
    """Complete presentation including research and slides"""
    research: ResearchData
    slides: SlidePresentation
    meta: PresentationMeta
    images: Optional[List[ImageGeneration]] = Field(default_factory=list)

class CompiledSlide(BaseModel):
    """Slide with integrated image for the compiled presentation"""
    type: str
    fields: Dict[str, Any] = Field(default_factory=dict)  # Fields depend on slide type
    image_url: Optional[str] = None

class CompiledPresentation(BaseModel):
    """Compiled presentation with slides and images merged"""
    title: str
    slides: List[CompiledSlide]
    author: Optional[str] = None  # Author for the entire presentation

# Add the missing models
class PresentationCreate(BaseModel):
    """Model for creating a new presentation"""
    name: str
    topic: Optional[str] = None
    research_content: Optional[str] = None
    research_type: str = "research"  # Can be "research" or "manual_research"
    author: Optional[str] = None  # Optional author name for the presentation

class StepUpdate(BaseModel):
    """Model for updating a step in a presentation"""
    result: Dict[str, Any] 