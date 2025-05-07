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

# Use absolute imports
from config import OPENAI_IMAGE_CONFIG, PRESENTATIONS_STORAGE_DIR
from models import ImageGeneration, SlidePresentation
from tools.slide_config import SLIDE_TYPES, IMAGE_FORMATS

# Create a thread pool executor with limited workers
image_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# Global timeout settings
REQUEST_TIMEOUT = 60  # seconds
MAX_RETRIES = 2

def save_image_to_file(presentation_id: int, slide_index: int, image_field_name: str, image_data: str) -> str:
    """
    Save a base64 encoded image to a file.
    
    Args:
        presentation_id: ID of the presentation
        slide_index: Index of the slide (-1 for standalone images)
        image_field_name: Name of the image field (e.g., 'image', 'image1')
        image_data: Base64 encoded image data
        
    Returns:
        Path to the saved image file
    """
    # Create directory for this presentation if it doesn't exist
    presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id))
    os.makedirs(presentation_dir, exist_ok=True)
    
    # Create images subdirectory as expected by the generate_pptx.py module
    images_dir = os.path.join(presentation_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Generate a filename with UUID to ensure uniqueness but avoid duplicating existing images
    # Ensure UUID is a proper string representation with full length
    unique_id = str(uuid.uuid4())
    filename = f"slide_{slide_index}_{image_field_name}_{unique_id}.png"
    file_path = os.path.join(images_dir, filename)
    
    # Decode and save the image
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
        return None
    
    with open(file_path, "rb") as f:
        image_data = f.read()
        return base64.b64encode(image_data).decode()

def _generate_image_for_slide(slide, index, presentation_id) -> List[ImageGeneration]:
    """
    Generate images for a slide based on its type - runs in a separate thread.
    Creates a fresh client for each request to avoid gRPC threading issues.
    Returns a list of ImageGeneration objects, one for each image field found.
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

        # Create a prompt based on the specific field content
        prompt = f"""Create an illustrative image for a presentation slide representing: {specific_content}

Context: This image is for the field '{image_field}' of a slide titled '{slide_title}' (type: '{slide_type}').

Important guidelines:
- Create a SIMPLE, CLEAN illustration that represents the main concept: {specific_content}
- Focus on VISUAL representation rather than text-heavy elements
- Use vibrant colors and clear imagery
- Avoid complex diagrams or dense information
- Illustration should be immediately understandable at a glance
- Aim for an elegant, professional style suitable for a business presentation
"""
        
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
                    model="gpt-image-1",
                    prompt=prompt,
                    size=size,
                    quality="medium",
                    output_format="png"
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
    Generate images for presentation slides using OpenAI GPT Image. Now handles multiple images per slide.
    
    Args:
        slides: SlidePresentation object containing slide content
        presentation_id: ID of the presentation to store images, or None for temporary images
        
    Returns:
        A list of ImageGeneration objects for all generated images across all slides.
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

    # Limit concurrent requests
    concurrency = min(2, len(tasks))
    print(f"Generating images for {len(tasks)} slides requiring images with concurrency {concurrency}")
    
    all_generated_images = [] # Flattened list
    for i in range(0, len(tasks), concurrency):
        batch = tasks[i:i+concurrency]
        batch_futures = []
        
        for slide_obj, index in batch:
            # Submit the task to the executor
            future = asyncio.get_event_loop().run_in_executor(
                image_executor,
                _generate_image_for_slide, # This now returns List[ImageGeneration]
                slide_obj, index, presentation_id
            )
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
    Generate a single image from a prompt using OpenAI GPT Image.
    Includes image_field_name in the result.
    
    Args:
        prompt: The text prompt for image generation
        size: Image size (e.g. "1024x1024"). Will be overridden by slide_type if provided.
        presentation_id: Optional ID of the presentation to store the image with
        slide_type: Optional type of slide for format determination (overrides size)
        
    Returns:
        An ImageGeneration object or None if generation fails
    """
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
                    model="gpt-image-1",
                    prompt=prompt,
                    size=image_size,
                    quality="medium",
                    output_format="png"
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