from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class Link(BaseModel):
    """Link model for research sources"""
    href: str = Field(description="URL of the source")
    title: str = Field(default="Source", description="Title of the source")

class ResearchData(BaseModel):
    """Research data for a presentation topic"""
    content: str = Field(description="Main research content with information about the topic")
    links: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="List of reference links with href and title"
    )

class Slide(BaseModel):
    """Individual slide with type and fields containing the slide content"""
    type: str = Field(
        description="Type of slide which determines its structure and visual appearance. Available types: welcome, tableofcontents, section, content, contentimage, image, quote, conclusion, thankyou"
    )
    fields: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Fields depend on slide type and contain the actual content (e.g., title, content, image references)"
    )

class SlidePresentation(BaseModel):
    """Complete slide presentation with title and slides"""
    title: str = Field(description="Title of the presentation")
    slides: List[Slide] = Field(description="List of slides in the presentation")
    author: Optional[str] = Field(None, description="Author name for the entire presentation")

class ImageGeneration(BaseModel):
    """Model for generated image data"""
    slide_index: int = Field(
        description="Index of the slide, -1 if not tied to a specific slide"
    )
    slide_title: str = Field(
        description="Title of the slide for reference"
    )
    prompt: str = Field(
        description="The prompt used to generate the image"
    )
    image_field_name: str = Field(
        description="The name of the image field this image corresponds to (e.g., 'image', 'image1')"
    )
    image_path: Optional[str] = Field(
        None, 
        description="Path to the image file on disk"
    )
    image: Optional[str] = Field(
        None, 
        description="Base64-encoded image data, used for memory-only handling"
    )

class PptxGeneration(BaseModel):
    """Model for generated PPTX data"""
    presentation_id: Optional[Union[int, str]] = Field(
        None,  
        description="ID of the presentation, None for temporary files, str for test cases"
    )
    pptx_filename: str = Field(
        description="Filename of the PPTX file"
    )
    pptx_path: str = Field(
        description="Full path to the PPTX file"
    )
    slide_count: int = Field(
        description="Number of slides in the presentation"
    )
    png_paths: List[str] = Field(
        default_factory=list,
        description="Paths to PNG images of slides for preview"
    )

class PresentationMeta(BaseModel):
    """Metadata about the presentation creation process"""
    topic: str = Field(
        description="Main topic of the presentation"
    )
    target_slides: int = Field(
        description="Target number of slides requested"
    )
    actual_slides: int = Field(
        description="Actual number of slides generated"
    )

class FullPresentation(BaseModel):
    """Complete presentation including research and slides"""
    research: ResearchData = Field(
        description="Research data about the presentation topic"
    )
    slides: SlidePresentation = Field(
        description="Slide content for the presentation"
    )
    meta: PresentationMeta = Field(
        description="Metadata about the presentation"
    )
    images: Optional[List[ImageGeneration]] = Field(
        default_factory=list,
        description="Generated images for the presentation slides"
    )

class CompiledSlide(BaseModel):
    """Slide with integrated image for the compiled presentation"""
    type: str = Field(
        description="Type of slide (welcome, content, contentimage, etc.)"
    )
    fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Fields containing the slide content specific to the slide type"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL to the image for this slide if applicable (format: /presentations/{id}/images/{filename})"
    )

class CompiledPresentation(BaseModel):
    """Compiled presentation with slides and images merged"""
    title: str = Field(
        description="Title of the presentation"
    )
    slides: List[CompiledSlide] = Field(
        description="List of slides with integrated image URLs where applicable"
    )
    author: Optional[str] = Field(
        None,
        description="Author name for the entire presentation"
    )

# Add the missing models
class PresentationCreate(BaseModel):
    """Model for creating a new presentation"""
    name: str = Field(
        description="Name of the presentation"
    )
    topic: Optional[str] = Field(
        None,
        description="Main topic for the presentation. Required if research_type is 'research'"
    )
    research_content: Optional[str] = Field(
        None,
        description="Manual research content. Required if research_type is 'manual_research'"
    )
    research_type: str = Field(
        default="research",
        description="Type of research to perform: 'research' for AI-generated or 'manual_research' for user-provided content"
    )
    author: Optional[str] = Field(
        None,
        description="Author name for the presentation"
    )

class StepUpdate(BaseModel):
    """Model for updating a step in a presentation"""
    result: Dict[str, Any] = Field(
        description="Result data for the step. Structure depends on step type"
    ) 