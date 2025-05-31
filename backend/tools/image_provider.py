"""
Image generation provider wrapper that supports multiple image generation backends.
Currently supports OpenAI and Gemini (Imagen 3).
"""

from typing import List, Optional
from config import IMAGE_PROVIDER
from models import ImageGeneration, SlidePresentation

# Import provider-specific modules
from tools.images import (
    generate_slide_images as generate_slide_images_openai,
    generate_image_from_prompt as generate_image_from_prompt_openai
)
from tools.gemini_images import (
    generate_slide_images_gemini,
    generate_image_from_prompt_gemini
)

async def generate_slide_images(
    slides: SlidePresentation, 
    presentation_id: Optional[int] = None,
    provider: Optional[str] = None
) -> List[ImageGeneration]:
    """
    Generate images for presentation slides using the configured provider.
    
    Args:
        slides: SlidePresentation object containing slide content
        presentation_id: ID of the presentation to store images, or None for temporary images
        provider: Override the default provider ("openai" or "gemini")
        
    Returns:
        A list of ImageGeneration objects for all generated images
    """
    # Use provided provider or fall back to configured default
    selected_provider = (provider or IMAGE_PROVIDER).lower()
    
    if selected_provider == "gemini":
        print(f"Using Gemini (Imagen 3) for image generation")
        return await generate_slide_images_gemini(slides, presentation_id)
    elif selected_provider == "openai":
        print(f"Using OpenAI for image generation")
        return await generate_slide_images_openai(slides, presentation_id)
    else:
        # Default to OpenAI if unknown provider
        print(f"Unknown provider '{selected_provider}', defaulting to OpenAI")
        return await generate_slide_images_openai(slides, presentation_id)

async def generate_image_from_prompt(
    prompt: str, 
    size: str = "1024x1024", 
    presentation_id: Optional[int] = None, 
    slide_type: Optional[str] = None,
    provider: Optional[str] = None
) -> Optional[ImageGeneration]:
    """
    Generate a single image from a prompt using the configured provider.
    
    Args:
        prompt: The text prompt for image generation
        size: Image size (e.g., "1024x1024")
        presentation_id: ID of the presentation to store the image
        slide_type: Type of slide (for size determination)
        provider: Override the default provider ("openai" or "gemini")
        
    Returns:
        ImageGeneration object or None if generation fails
    """
    # Use provided provider or fall back to configured default
    selected_provider = (provider or IMAGE_PROVIDER).lower()
    
    if selected_provider == "gemini":
        print(f"Using Gemini (Imagen 3) for single image generation")
        return await generate_image_from_prompt_gemini(prompt, size, presentation_id, slide_type)
    elif selected_provider == "openai":
        print(f"Using OpenAI for single image generation")
        return await generate_image_from_prompt_openai(prompt, size, presentation_id, slide_type)
    else:
        # Default to OpenAI if unknown provider
        print(f"Unknown provider '{selected_provider}', defaulting to OpenAI")
        return await generate_image_from_prompt_openai(prompt, size, presentation_id, slide_type)