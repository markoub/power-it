from typing import Dict, Any, List, Optional

from tools.research import research_topic
from tools.slides import generate_slides
from tools.image_provider import generate_slide_images
from models import FullPresentation, PresentationMeta, ImageGeneration, ResearchData, SlidePresentation

async def create_presentation(
    topic: str, 
    target_slides: int = 10, 
    generate_images: bool = False, 
    presentation_id: int = None,
    author: Optional[str] = None,
    image_provider: Optional[str] = None
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
    # Input validation
    if not topic or not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic must be a non-empty string")
    
    if not isinstance(target_slides, int) or target_slides <= 0:
        raise ValueError("Target slides must be a positive integer")
    
    if target_slides > 100:  # reasonable upper limit
        raise ValueError("Target slides cannot exceed 100")
    
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
            images = await generate_slide_images(slides_data, presentation_id, provider=image_provider)
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

async def update_presentation_topic(
    topic: str,
    target_slides: int = 10,
    generate_images: bool = False,
    presentation_id: int = None,
    author: Optional[str] = None,
    image_provider: Optional[str] = None
) -> FullPresentation:
    """
    Updates an existing presentation by rerunning research with a new topic,
    regenerating slides, and optionally regenerating images.
    
    Args:
        topic: The new presentation topic to research
        target_slides: Approximate number of slides to generate
        generate_images: Whether to generate images for slides with visual suggestions
        presentation_id: Optional ID for persistence of generated images
        author: Optional author name for the presentation
        
    Returns:
        A FullPresentation object containing the updated research data, slide proposals, and optionally images
    """
    # This is similar to create_presentation but intended for updating an existing presentation
    
    # Step 1: Research the new topic
    research_data = await research_topic(topic)
    
    # Step 2: Generate slides based on new research
    slides_data = await generate_slides(research_data, target_slides, author)
    
    # Step 3: Create updated metadata
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
            images = await generate_slide_images(slides_data, presentation_id, provider=image_provider)
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