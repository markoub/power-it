import json
import base64
import os
import uuid
import asyncio
from openai import OpenAI
from typing import Dict, Any, List, Optional
from io import BytesIO
import concurrent.futures
import time
import contextlib
import shutil
from prompts import get_prompt

# Use absolute imports
from config import OPENAI_IMAGE_CONFIG, PRESENTATIONS_STORAGE_DIR, STORAGE_DIR
from models import ImageGeneration, SlidePresentation
from tools.slide_config import SLIDE_TYPES, IMAGE_FORMATS
from offline_responses.images import (
    DUMMY_IMAGE_PATH,
    ensure_dummy_image_exists,
    load_dummy_image_b64,
)

# Check for offline mode
OFFLINE_MODE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes", "on"}

if OFFLINE_MODE:
    ensure_dummy_image_exists()

# Create a thread pool executor with limited workers
image_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# Global timeout settings
REQUEST_TIMEOUT = 60  # seconds
MAX_RETRIES = 2

def save_image_to_file(presentation_id: int, slide_index: int, image_field_name: str, image_data: str = None, prompt: str = None) -> str:
    """
    Save an image to a file for a presentation.
    In offline mode, this copies the dummy image instead of decoding base64 data.
    
    Args:
        presentation_id: ID of the presentation
        slide_index: Index of the slide (-1 for standalone images)
        image_field_name: Name of the image field (e.g., 'image', 'image1')
        image_data: Base64 encoded image data (not used in offline mode)
        
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
        # In offline mode, generate a custom placeholder image based on prompt
        try:
            # If we have image_data (from load_dummy_image_b64), use it
            if image_data:
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(image_data))
                print(f"Saved placeholder image to: {file_path}")
            else:
                # Fallback to copying dummy image
                shutil.copy(DUMMY_IMAGE_PATH, file_path)
                print(f"Copied dummy image to: {file_path}")
        except Exception as e:
            print(f"Error saving placeholder image: {str(e)}")
    else:
        # In online mode, decode and save the image from base64 data
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        print(f"Saved image to: {file_path}")
    
    return file_path

def load_image_from_file(file_path: str) -> Optional[str]:
    """
    Load an image from a file and return it as base64 encoded string.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Base64 encoded image data or None if file doesn't exist
    """
    if not os.path.exists(file_path):
        if OFFLINE_MODE and os.path.exists(DUMMY_IMAGE_PATH):
            # In offline mode, use the dummy image if the requested file doesn't exist
            file_path = DUMMY_IMAGE_PATH
        else:
            return None
    
    with open(file_path, "rb") as f:
        image_data = f.read()
        return base64.b64encode(image_data).decode()

async def _generate_image_for_slide(slide, index, presentation_id) -> List[ImageGeneration]:
    """
    Generate images for a slide based on its type.
    In offline mode, returns mock images using the dummy image file.
    """
    slide_type = getattr(slide, 'type', None)
    if not slide_type or slide_type not in SLIDE_TYPES:
        return [] # No valid type or not in config

    slide_config = SLIDE_TYPES[slide_type]
    image_fields = [comp for comp in slide_config.get("components", []) if comp.startswith("image")]

    if not hasattr(slide, 'fields') or not slide.fields or not image_fields:
        return [] # No fields or no image components required for this type

    # Get common slide details
    slide_title = slide.fields.get('title', '')
    slide_content = slide.fields.get('content', []) # Content field primarily used for single image prompts
    if isinstance(slide_content, list):
        slide_content = ' '.join(slide_content)

    generated_images = []

    for image_field in image_fields:
        # Check if the specific image field exists and has content
        field_content = slide.fields.get(image_field)
        if not field_content: # Skip if this image field is empty or missing in the slide data
            print(f"Skipping image generation for slide {index}, field {image_field}: Field is missing or empty.")
            continue 

        # Use the content of the image field directly as the core concept for the prompt.
        # Ensure it's a string.
        if isinstance(field_content, list):
            specific_content = ' '.join(field_content)
        else:
            specific_content = str(field_content) # Ensure it's a string

        if OFFLINE_MODE:
            # Generate a proper prompt for the placeholder
            # Simple prompt generation for offline mode
            prompt = f"{slide_title}: {specific_content}"
            if image_field != "image":
                prompt = f"{prompt} ({image_field})"
            print(f"OFFLINE MODE: Using placeholder for slide {index}, field {image_field}")
            
            # Get the base64 encoded dummy image with prompt-based placeholder
            dummy_image_b64 = load_dummy_image_b64(prompt)
            
            # Save the dummy image
            file_path = None
            if presentation_id is not None:
                file_path = save_image_to_file(presentation_id, index, image_field, dummy_image_b64, prompt)
                
            # Add the generated image to the list
            generated_images.append(ImageGeneration(
                slide_index=index,
                slide_title=slide_title,
                prompt=prompt,
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
        
        # Create a fresh client instance for each request to avoid gRPC issues
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=REQUEST_TIMEOUT)
        
        # Determine size based on slide type using the IMAGE_FORMATS configuration
        size = IMAGE_FORMATS.get(slide_type, IMAGE_FORMATS.get("default", "1024x1024"))
        
        image_data = None
        file_path = None
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                # Generate the image using OpenAI GPT Image with timeout
                result = client.images.generate(
                    model=OPENAI_IMAGE_CONFIG["model"],
                    prompt=prompt,
                    size=size,
                    quality=OPENAI_IMAGE_CONFIG["quality"],
                    output_format=OPENAI_IMAGE_CONFIG["output_format"]
                )
                
                image_data = result.data[0].b64_json
                
                # Save the image to a file if presentation_id is provided
                if presentation_id is not None:
                    file_path = save_image_to_file(presentation_id, index, image_field, image_data)
                
                # Add the generated image to the list
                generated_images.append(ImageGeneration(
                    slide_index=index,
                    slide_title=slide_title,
                    prompt=prompt,
                    image_field_name=image_field, # Store the field name
                    image_path=file_path,
                    image=image_data  # Include base64 image data
                ))
                print(f"Successfully generated image for slide {index}, field {image_field}")
                break # Success, exit retry loop
                
            except Exception as e:
                print(f"Error generating image for slide {index}, field {image_field} (attempt {attempt+1}/{MAX_RETRIES+1}): {str(e)}")
                if attempt < MAX_RETRIES:
                    time.sleep(2) # Wait before retrying
                # If last attempt fails, image_data remains None, won't be added

    return generated_images

async def generate_slide_images(slides: SlidePresentation, presentation_id: Optional[int] = None) -> List[ImageGeneration]:
    """
    Generate images for presentation slides.
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
        
        # Check if *any* of the required image fields are actually present and true in the slide data
        if hasattr(slide, 'fields') and slide.fields and any(slide.fields.get(img_f) for img_f in image_fields):
            tasks.append((slide, i))
            
    if not tasks:
        return [] # No images needed

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
    print(f"Generating images for {len(tasks)} slides requiring images with concurrency {concurrency}")
    
    all_generated_images = [] # Flattened list
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
                timeout=REQUEST_TIMEOUT * 1.2 * len(batch) # Adjust timeout based on batch size and potential retries
            )
            
            # Process results: Flatten the list of lists and handle exceptions/None
            for result in batch_results:
                if isinstance(result, list): # Success, got a list of ImageGeneration objects
                    all_generated_images.extend(result)
                elif isinstance(result, Exception):
                     print(f"An exception occurred during image generation batch: {result}")
                # Ignore None or empty lists implicitly
                     
        except asyncio.TimeoutError:
            print(f"Timeout occurred while waiting for image generation batch {i//concurrency + 1}")
        
        # Add a delay between batches to avoid overloading the API
        if i + concurrency < len(tasks): # Avoid sleep after the last batch
             await asyncio.sleep(2)
    
    print(f"Finished generating images. Total images generated: {len(all_generated_images)}")
    return all_generated_images

async def generate_image_from_prompt(prompt: str, size: str = "1024x1024", presentation_id: Optional[int] = None, slide_type: Optional[str] = None) -> Optional[ImageGeneration]:
    """
    Generate a single image from a prompt.
    In offline mode, returns a mock image using the dummy image file.
    """
    if OFFLINE_MODE:
        print(f"OFFLINE MODE: Using dummy image for prompt: {prompt}")
        
        # Get the base64 encoded dummy image with prompt-based placeholder
        dummy_image_b64 = load_dummy_image_b64(prompt)
            
        # Save the dummy image
        file_path = None
        if presentation_id is not None:
            file_path = save_image_to_file(presentation_id, -1, "image", dummy_image_b64, prompt)
            
        # Return a mock ImageGeneration object
        return ImageGeneration(
            slide_index=-1,
            slide_title="Mock Image",
            prompt=prompt,
            image_field_name="image",
            image_path=file_path,
            image=dummy_image_b64
        )

    image_field_name = "image" # Default field name for single image generation

    def _generate_single_image():
        # Create a fresh client for each request to avoid gRPC issues
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=REQUEST_TIMEOUT)
        
        # Check if slide_type is provided and exists in IMAGE_FORMATS
        image_size = size # Use provided size as default
        
        if slide_type:
            # Use the size from IMAGE_FORMATS if available for this slide type
            image_size = IMAGE_FORMATS.get(slide_type, IMAGE_FORMATS.get("default", "1024x1024"))
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                result = client.images.generate(
                    model=OPENAI_IMAGE_CONFIG["model"],
                    prompt=prompt,
                    size=image_size,
                    quality=OPENAI_IMAGE_CONFIG["quality"],
                    output_format=OPENAI_IMAGE_CONFIG["output_format"]
                )
                return result
            except Exception as e:
                print(f"Error in single image generation (attempt {attempt+1}/{MAX_RETRIES+1}): {str(e)}")
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
        result = await asyncio.wait_for(result_future, timeout=REQUEST_TIMEOUT * 1.2)
        
        if not result:
            return None
        
        # Get the base64 encoded image
        image_data = result.data[0].b64_json
        
        # For direct generation API, save to a file
        file_path = None
        
        if presentation_id is not None:
            # Use the default image_field_name for saving
            file_path = save_image_to_file(presentation_id, -1, image_field_name, image_data)
        else:
            # Create a temporary file for standalone images
            temp_presentation_id = 0  # Use 0 for temporary/standalone images
            file_path = save_image_to_file(temp_presentation_id, -1, image_field_name, image_data)
        
        # Return the result as an ImageGeneration object
        return ImageGeneration(
            slide_index=-1,  # -1 for standalone images
            slide_title="Generated Image",  # Generic title for standalone images
            prompt=prompt,
            image_field_name=image_field_name, # Add the field name
            image_path=file_path,
            image=image_data  # Include base64 image data
        )
        
    except asyncio.TimeoutError:
        print(f"Timeout while generating image from prompt")
        return None
    except Exception as e:
        print(f"Unexpected error generating image: {str(e)}")
        return None 