from typing import Dict, Any, List, Optional

from tools.research import research_topic
from tools.slides import generate_slides
from tools.images import generate_slide_images
from models import FullPresentation, PresentationMeta, ImageGeneration, ResearchData, SlidePresentation

async def create_presentation(
    topic: str, 
    target_slides: int = 10, 
    generate_images: bool = False, 
    presentation_id: int = None,
    author: Optional[str] = None
) -> FullPresentation:
    """
    Orchestrates the creation of a complete presentation by chaining research, slides generation, and optional image generation.
    
    Args:
        topic: The presentation topic to research
        target_slides: Approximate number of slides to generate
        generate_images: Whether to generate images for slides with visual suggestions
        presentation_id: Optional ID for persistence of generated images
        author: Optional author name for the presentation
        
    Returns:
        A FullPresentation object containing both research data, slide proposals, and optionally images
    """
    # Step 1: Research the topic
    research_data = await research_topic(topic)
    
    # Step 2: Generate slides based on research
    slides_data = await generate_slides(research_data, target_slides, author)
    
    # Step 3: Create metadata
    meta = PresentationMeta(
        topic=topic,
        target_slides=target_slides,
        actual_slides=len(slides_data.slides)
    )
    
    # Step 4: Generate images if requested
    images: List[ImageGeneration] = []
    if generate_images:
        try:
            # If presentation_id is provided, store images in the filesystem
            images = await generate_slide_images(slides_data, presentation_id)
        except Exception as e:
            print(f"Error generating images: {str(e)}")
            # Continue without images
    
    # Step 5: Combine the results
    return FullPresentation(
        research=research_data,
        slides=slides_data,
        meta=meta,
        images=images
    ) 