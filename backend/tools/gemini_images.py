import json
import base64
import os
import uuid
import asyncio
try:
    from google import genai
    from google.genai import types
except ImportError:
    # Fallback for when google-genai is not installed
    genai = None
    types = None
from PIL import Image as PILImage
from io import BytesIO
from typing import Dict, Any, List, Optional
from prompts import get_prompt
import concurrent.futures
import time

# Use absolute imports
from config import GEMINI_API_KEY, PRESENTATIONS_STORAGE_DIR, STORAGE_DIR, OFFLINE_MODE
from models import ImageGeneration, SlidePresentation
from tools.slide_config import SLIDE_TYPES, IMAGE_FORMATS
from offline_responses.images import (
    DUMMY_IMAGE_PATH,
    ensure_dummy_image_exists,
    load_dummy_image_b64,
)

if OFFLINE_MODE:
    ensure_dummy_image_exists()

# Create a thread pool executor with limited workers
image_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# Global timeout settings
REQUEST_TIMEOUT = 60  # seconds
MAX_RETRIES = 2

# Gemini image generation model
GEMINI_IMAGE_MODEL = "imagen-3.0-generate-002"

def save_image_to_file(presentation_id: int, slide_index: int, image_field_name: str, image_bytes: bytes = None) -> str:
    """
    Save an image to a file for a presentation.
    In offline mode, this copies the dummy image instead of saving image bytes.
    
    Args:
        presentation_id: ID of the presentation
        slide_index: Index of the slide (-1 for standalone images)
        image_field_name: Name of the image field (e.g., 'image', 'image1')
        image_bytes: Raw image bytes (not used in offline mode)
        
    Returns:
        Path to the saved image file
    """
    # Create directory for this presentation if it doesn't exist
    presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id))
    os.makedirs(presentation_dir, exist_ok=True)
    
    # Create images subdirectory as expected by the generate_pptx.py module
    images_dir = os.path.join(presentation_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Generate a filename with UUID to ensure uniqueness
    unique_id = str(uuid.uuid4())
    filename = f"slide_{slide_index}_{image_field_name}_{unique_id}.png"
    file_path = os.path.join(images_dir, filename)
    
    if OFFLINE_MODE:
        # In offline mode, copy the dummy image file instead of saving bytes
        import shutil
        try:
            shutil.copy(DUMMY_IMAGE_PATH, file_path)
            print(f"Copied dummy image to: {file_path}")
        except Exception as e:
            print(f"Error copying dummy image: {str(e)}")
    else:
        # In online mode, save the image bytes directly
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        print(f"Saved Gemini-generated image to: {file_path}")
    
    return file_path

def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 encoded string."""
    return base64.b64encode(image_bytes).decode()

async def _generate_image_for_slide(slide, index, presentation_id) -> List[ImageGeneration]:
    """
    Generate images for a slide based on its type using Gemini Imagen 3.
    In offline mode, returns mock images using the dummy image file.
    """
    slide_type = getattr(slide, 'type', None)
    if not slide_type or slide_type not in SLIDE_TYPES:
        return []

    slide_config = SLIDE_TYPES[slide_type]
    image_fields = [comp for comp in slide_config.get("components", []) if comp.startswith("image")]

    if not hasattr(slide, 'fields') or not slide.fields or not image_fields:
        return []

    # Get common slide details
    slide_title = slide.fields.get('title', '')
    slide_content = slide.fields.get('content', [])
    if isinstance(slide_content, list):
        slide_content = ' '.join(slide_content)

    generated_images = []

    for image_field in image_fields:
        # Check if the specific image field exists and has content
        field_content = slide.fields.get(image_field)
        if not field_content:
            print(f"Skipping image generation for slide {index}, field {image_field}: Field is missing or empty.")
            continue 

        # Use the content of the image field directly as the core concept for the prompt
        if isinstance(field_content, list):
            specific_content = ' '.join(field_content)
        else:
            specific_content = str(field_content)

        if OFFLINE_MODE:
            print(f"OFFLINE MODE: Using dummy image for slide {index}, field {image_field}")
            
            # Save the dummy image
            file_path = None
            if presentation_id is not None:
                file_path = save_image_to_file(presentation_id, index, image_field)
                
            # Get the base64 encoded dummy image
            dummy_image_b64 = load_dummy_image_b64()
                
            # Add the generated image to the list
            generated_images.append(ImageGeneration(
                slide_index=index,
                slide_title=slide_title,
                prompt=f"Dummy image for {specific_content}",
                image_field_name=image_field,
                image_path=file_path,
                image=dummy_image_b64
            ))
            print(f"Successfully generated dummy image for slide {index}, field {image_field}")
            continue

        # Get the prompt template from the centralized prompt system
        prompt_template = await get_prompt("image_generation")
        prompt = prompt_template.format(
            specific_content=specific_content,
            image_field=image_field,
            slide_title=slide_title,
            slide_type=slide_type
        )
        
        # Create Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Determine aspect ratio based on slide type
        size = IMAGE_FORMATS.get(slide_type, IMAGE_FORMATS.get("default", "1024x1024"))
        # Convert size to aspect ratio for Gemini
        width, height = map(int, size.split('x'))
        aspect_ratio = f"{width}:{height}"
        
        image_bytes = None
        file_path = None
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                # Generate the image using Gemini Imagen 3
                response = client.models.generate_images(
                    model=GEMINI_IMAGE_MODEL,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio=aspect_ratio,
                        safety_filter_level="block_low_and_above",
                    )
                )
                
                if response.generated_images:
                    image_bytes = response.generated_images[0].image.image_bytes
                    
                    # Save the image to a file if presentation_id is provided
                    if presentation_id is not None:
                        file_path = save_image_to_file(presentation_id, index, image_field, image_bytes)
                    
                    # Convert to base64 for response
                    image_data = image_bytes_to_base64(image_bytes)
                    
                    # Add the generated image to the list
                    generated_images.append(ImageGeneration(
                        slide_index=index,
                        slide_title=slide_title,
                        prompt=prompt,
                        image_field_name=image_field,
                        image_path=file_path,
                        image=image_data
                    ))
                    print(f"Successfully generated Gemini image for slide {index}, field {image_field}")
                    break
                    
            except Exception as e:
                print(f"Error generating Gemini image for slide {index}, field {image_field} (attempt {attempt+1}/{MAX_RETRIES+1}): {str(e)}")
                if attempt < MAX_RETRIES:
                    time.sleep(2)

    return generated_images

async def generate_slide_images_gemini(slides: SlidePresentation, presentation_id: Optional[int] = None) -> List[ImageGeneration]:
    """
    Generate images for presentation slides using Gemini Imagen 3.
    In offline mode, returns mock images using the dummy image file.
    
    Args:
        slides: SlidePresentation object containing slide content
        presentation_id: ID of the presentation to store images, or None for temporary images
        
    Returns:
        A list of ImageGeneration objects for all generated images
    """
    tasks = []
    
    # Identify slides that require image generation based on their type config and fields
    for i, slide in enumerate(slides.slides):
        slide_type = getattr(slide, 'type', None)
        if not slide_type or slide_type not in SLIDE_TYPES:
            continue
            
        slide_config = SLIDE_TYPES[slide_type]
        image_fields = [comp for comp in slide_config.get("components", []) if comp.startswith("image")]
        
        # Check if any of the required image fields are actually present and true in the slide data
        if hasattr(slide, 'fields') and slide.fields and any(slide.fields.get(img_f) for img_f in image_fields):
            tasks.append((slide, i))
            
    if not tasks:
        return []

    if OFFLINE_MODE:
        print(f"OFFLINE MODE: Generating dummy images for {len(tasks)} slides")
        
        all_generated_images = []
        for slide_obj, index in tasks:
            # Generate dummy images for this slide
            result = await _generate_image_for_slide(slide_obj, index, presentation_id)
            all_generated_images.extend(result)
            
        print(f"OFFLINE MODE: Generated {len(all_generated_images)} dummy images")
        return all_generated_images

    # Limit concurrent requests
    concurrency = min(2, len(tasks))
    print(f"Generating Gemini images for {len(tasks)} slides requiring images with concurrency {concurrency}")
    
    all_generated_images = []
    for i in range(0, len(tasks), concurrency):
        batch = tasks[i:i+concurrency]
        batch_futures = []
        
        for slide_obj, index in batch:
            # Since _generate_image_for_slide is now async, we run it directly
            future = _generate_image_for_slide(slide_obj, index, presentation_id)
            batch_futures.append(future)
        
        try:
            # Wait for the batch to complete with a timeout
            batch_results = await asyncio.wait_for(
                asyncio.gather(*batch_futures, return_exceptions=True),
                timeout=REQUEST_TIMEOUT * 1.2 * len(batch)
            )
            
            # Process results
            for result in batch_results:
                if isinstance(result, list):
                    all_generated_images.extend(result)
                elif isinstance(result, Exception):
                    print(f"An exception occurred during Gemini image generation batch: {result}")
                     
        except asyncio.TimeoutError:
            print(f"Timeout occurred while waiting for Gemini image generation batch {i//concurrency + 1}")
        
        # Add a delay between batches to avoid overloading the API
        if i + concurrency < len(tasks):
            await asyncio.sleep(2)
    
    print(f"Finished generating Gemini images. Total images generated: {len(all_generated_images)}")
    return all_generated_images

async def generate_image_from_prompt_gemini(prompt: str, size: str = "1024x1024", presentation_id: Optional[int] = None, slide_type: Optional[str] = None) -> Optional[ImageGeneration]:
    """
    Generate a single image from a prompt using Gemini Imagen 3.
    In offline mode, returns a mock image using the dummy image file.
    """
    if OFFLINE_MODE:
        print(f"OFFLINE MODE: Using dummy image for prompt: {prompt}")
        
        # Save the dummy image
        file_path = None
        if presentation_id is not None:
            file_path = save_image_to_file(presentation_id, -1, "image")
            
        # Get the base64 encoded dummy image
        dummy_image_b64 = load_dummy_image_b64()
            
        # Return a mock ImageGeneration object
        return ImageGeneration(
            slide_index=-1,
            slide_title="Mock Image",
            prompt=prompt,
            image_field_name="image",
            image_path=file_path,
            image=dummy_image_b64
        )

    image_field_name = "image"

    def _generate_single_image():
        # Create Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Check if slide_type is provided and exists in IMAGE_FORMATS
        image_size = size
        
        if slide_type:
            # Use the size from IMAGE_FORMATS if available for this slide type
            image_size = IMAGE_FORMATS.get(slide_type, IMAGE_FORMATS.get("default", "1024x1024"))
        
        # Convert size to aspect ratio for Gemini
        width, height = map(int, image_size.split('x'))
        aspect_ratio = f"{width}:{height}"
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = client.models.generate_images(
                    model=GEMINI_IMAGE_MODEL,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio=aspect_ratio,
                        safety_filter_level="block_low_and_above",
                    )
                )
                
                if response.generated_images:
                    return response.generated_images[0].image.image_bytes
                    
            except Exception as e:
                print(f"Error in single Gemini image generation (attempt {attempt+1}/{MAX_RETRIES+1}): {str(e)}")
                if attempt < MAX_RETRIES:
                    time.sleep(2)
        return None
    
    try:
        # Use the thread pool executor with timeout
        result_future = asyncio.get_event_loop().run_in_executor(
            image_executor,
            _generate_single_image
        )
        
        # Wait for the result with a timeout
        image_bytes = await asyncio.wait_for(result_future, timeout=REQUEST_TIMEOUT * 1.2)
        
        if not image_bytes:
            return None
        
        # Save to file
        file_path = None
        
        if presentation_id is not None:
            file_path = save_image_to_file(presentation_id, -1, image_field_name, image_bytes)
        else:
            # Create a temporary file for standalone images
            temp_presentation_id = 0
            file_path = save_image_to_file(temp_presentation_id, -1, image_field_name, image_bytes)
        
        # Convert to base64 for response
        image_data = image_bytes_to_base64(image_bytes)
        
        # Return the result as an ImageGeneration object
        return ImageGeneration(
            slide_index=-1,
            slide_title="Generated Image",
            prompt=prompt,
            image_field_name=image_field_name,
            image_path=file_path,
            image=image_data
        )
        
    except asyncio.TimeoutError:
        print(f"Timeout while generating Gemini image from prompt")
        return None
    except Exception as e:
        print(f"Unexpected error generating Gemini image: {str(e)}")
        return None