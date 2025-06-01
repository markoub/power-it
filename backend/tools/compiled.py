from typing import Dict, Any, List, Optional
from models import SlidePresentation, ImageGeneration, CompiledPresentation, CompiledSlide
import os

async def generate_compiled_presentation(
    slides_data: SlidePresentation, 
    images_data: List[ImageGeneration],
    presentation_id: int
) -> CompiledPresentation:
    """
    Generate a compiled presentation by combining slides with their corresponding images.
    
    Args:
        slides_data: The slides content
        images_data: The generated images for the slides
        presentation_id: The ID of the presentation
        
    Returns:
        A CompiledPresentation object containing the merged content
    """
    # Create a dictionary mapping slide indices to images for quick lookup
    # For multi-image slides, we need to organize images by both slide index and field name
    images_by_index_and_field = {}
    images_by_title_and_field = {}
    
    # Handle None or empty images_data
    if images_data is None:
        images_data = []
    
    for image in images_data:
        # Extract the field name (default to 'image' if not specified)
        field_name = getattr(image, 'image_field_name', 'image')
        
        # Store by slide index if available
        if image.slide_index is not None:
            if image.slide_index not in images_by_index_and_field:
                images_by_index_and_field[image.slide_index] = {}
            images_by_index_and_field[image.slide_index][field_name] = image
            
        # Also store by slide title for fallback
        if image.slide_title:
            if image.slide_title not in images_by_title_and_field:
                images_by_title_and_field[image.slide_title] = {}
            images_by_title_and_field[image.slide_title][field_name] = image
    
    # Debug log the organized images
    print(f"Organized {len(images_data)} images by slide index and field name")
    
    # Combine slides with their corresponding images
    compiled_slides = []
    
    for i, slide in enumerate(slides_data.slides):
        # Get the slide title and type from fields if available
        slide_title = slide.fields.get('title', '') if hasattr(slide, 'fields') and isinstance(slide.fields, dict) else ''
        slide_type = slide.type
        
        # Create a new fields dictionary that we'll update with image URLs
        updated_fields = {}
        if hasattr(slide, 'fields') and isinstance(slide.fields, dict):
            # Make a copy of the original fields
            updated_fields = dict(slide.fields)
        
        # Main image URL for backward compatibility
        image_url = None
        
        # Check if this slide has images by index
        if i in images_by_index_and_field:
            image_dict = images_by_index_and_field[i]
            
            # For each image field in this slide
            for field_name, image in image_dict.items():
                image_url_for_field = None
                
                # Use image_url if it already exists, otherwise generate from image_path
                if hasattr(image, 'image_url') and image.image_url:
                    image_url_for_field = image.image_url
                elif hasattr(image, 'image_path') and image.image_path:
                    # Extract filename from the absolute path
                    filename = os.path.basename(image.image_path)
                    # Verify the filename format and ensure it's properly formed
                    if '_' in filename and '.png' in filename:
                        # Construct URL based on presentation ID
                        image_url_for_field = f"/presentations/{presentation_id}/images/{filename}"
                        print(f"Image URL for {field_name}: {image_url_for_field}")
                    else:
                        print(f"WARNING: Invalid image filename format: {filename}")
                        continue
                
                if image_url_for_field:
                    # Store in the fields dictionary using the pattern field_name + '_url'
                    # e.g., 'image1' becomes 'image1_url'
                    url_field_name = f"{field_name}_url"
                    updated_fields[url_field_name] = image_url_for_field
                    
                    # For backward compatibility, also set the main image_url if this is the primary image
                    if field_name == 'image' and image_url is None:
                        image_url = image_url_for_field
                    # For multi-image slides like three_images, set the main image_url to the first image
                    elif field_name == 'image1' and image_url is None:
                        image_url = image_url_for_field
        
        # Fallback to title matching if no images found by index
        elif slide_title in images_by_title_and_field:
            image_dict = images_by_title_and_field[slide_title]
            
            # For each image field in this slide
            for field_name, image in image_dict.items():
                image_url_for_field = None
                
                # Use image_url if it already exists, otherwise generate from image_path
                if hasattr(image, 'image_url') and image.image_url:
                    image_url_for_field = image.image_url
                elif hasattr(image, 'image_path') and image.image_path:
                    # Extract filename from the absolute path
                    filename = os.path.basename(image.image_path)
                    # Verify the filename format and ensure it's properly formed
                    if '_' in filename and '.png' in filename:
                        # Construct URL based on presentation ID
                        image_url_for_field = f"/presentations/{presentation_id}/images/{filename}"
                        print(f"Image URL for {field_name}: {image_url_for_field}")
                    else:
                        print(f"WARNING: Invalid image filename format: {filename}")
                        continue
                
                if image_url_for_field:
                    # Store in the fields dictionary using the pattern field_name + '_url'
                    url_field_name = f"{field_name}_url"
                    updated_fields[url_field_name] = image_url_for_field
                    
                    # For backward compatibility, also set the main image_url if this is the primary image
                    if field_name == 'image' and image_url is None:
                        image_url = image_url_for_field
                    # For multi-image slides like three_images, set the main image_url to the first image
                    elif field_name == 'image1' and image_url is None:
                        image_url = image_url_for_field
        
        # Create compiled slide with updated structure
        compiled_slide = CompiledSlide(
            type=slide_type,
            fields=updated_fields,
            image_url=image_url  # Keep for backward compatibility
        )
        
        compiled_slides.append(compiled_slide)
    
    # Create the compiled presentation
    return CompiledPresentation(
        title=slides_data.title,
        slides=compiled_slides,
        author=getattr(slides_data, 'author', None)  # Preserve author if present
    ) 