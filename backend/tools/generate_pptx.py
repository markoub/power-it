"""
Generate PowerPoint presentations from slide content
"""
import os
import uuid
import asyncio
import re
from typing import Dict, Any, List, Optional, Union

from pptx import Presentation

from config import PRESENTATIONS_STORAGE_DIR
from models import SlidePresentation, CompiledPresentation, Slide, CompiledSlide, PptxGeneration
from tools.slide_config import SLIDE_TYPES, PRESENTATION_STRUCTURE

# Import our refactored modules
from .pptx_utils import list_presentation_images
from .pptx_shapes import get_layout_by_name, find_shape_by_name, get_toc_shapes
from .pptx_text import adjust_text_size, format_content_text
from .pptx_toc import create_table_of_contents_slide, process_toc_slide

# Import all slide creation functions
from .pptx_slides import (
    create_welcome_slide, 
    create_section_slide, 
    create_content_slide,
    create_3images_slide,
    create_thank_you_slide,
    create_content_with_logos_slide
)

def format_section_number(number):
    """Format a section number to ensure it's a two-digit string (e.g., 1 -> '01')."""
    return f"{number:02d}"

async def generate_pptx_from_slides(slides, output_path) -> PptxGeneration:
    """
    Generate a PowerPoint presentation from slide content using a template.
    
    Args:
        slides: SlidePresentation or CompiledPresentation object containing slide content,
               or a list of slides
        output_path: Path where to save the presentation
        
    Returns:
        A PptxGeneration object with the path to the PPTX file
    """
    try:
        # Handle different input types
        if isinstance(slides, list):
            # We've received a list of slide dictionaries
            slides_list = slides
            presentation_title = "Generated Presentation"
            # Try to get title from first Welcome slide if available
            for slide in slides_list:
                if slide.get('type') == 'Welcome':
                    presentation_title = slide.get('title', presentation_title)
                    break
        else:
            # We have a SlidePresentation or CompiledPresentation object
            slides_list = slides.slides
            presentation_title = getattr(slides, 'title', "Generated Presentation")
        
        # Debug images directory structure
        print(f"\n===== Debugging Image Structure for Presentation {output_path} =====")
        available_images = list_presentation_images(output_path, PRESENTATIONS_STORAGE_DIR)
        print(f"Available images: {available_images}")
        print(f"========================================================\n")
        
        # Load template and extract layouts
        template_path = os.path.join(os.path.dirname(__file__), '../template.pptx')
        print(f"Loading template from: {template_path}")
        print(f"Template exists: {os.path.exists(template_path)}")
        
        # Create presentation object
        prs = Presentation(template_path)
        
        # Display layouts
        print("\n===== TEMPLATE STRUCTURE =====")
        print(f"Total slide layouts: {len(prs.slide_layouts)}")
        for i, layout in enumerate(prs.slide_layouts):
            layout_name = getattr(layout, 'name', f'Layout {i}')
            print(f"Layout {i}: '{layout_name}'")
        print("=============================\n")
        
        # Generate presentation with the first slide layout
        welcome_layout = get_layout_by_name(prs, "Welcome")
        if welcome_layout:
            print(f"Found welcome layout by name: {getattr(welcome_layout, 'name', 'Welcome')}")
            # Print placeholder details
            placeholders = [shape for shape in welcome_layout.placeholders]
            print(f"  Placeholders in welcome layout: {len(placeholders)}")
            for i, placeholder in enumerate(placeholders):
                print(f"  - Placeholder {i}: Name='{placeholder.name}', Type={placeholder.placeholder_format.type}")
        else:
            welcome_layout = prs.slide_layouts[0]
            print(f"No welcome layout found, using first layout: {getattr(welcome_layout, 'name', 'Layout 0')}")
            
        # Find content layout
        content_image_layout = get_layout_by_name(prs, "ContentImage")
        if content_image_layout:
            print(f"Found ContentImage layout by name: {getattr(content_image_layout, 'name', 'ContentImage')}")
            # Print placeholder details
            placeholders = [shape for shape in content_image_layout.placeholders]
            print(f"  Placeholders in this layout: {len(placeholders)}")
            for i, placeholder in enumerate(placeholders):
                print(f"  - Placeholder {i}: Name='{placeholder.name}', Type={placeholder.placeholder_format.type}")
        else:
            content_image_layout = prs.slide_layouts[5]  # Typically the 6th layout in PowerPoint templates
            print(f"No ContentImage layout found, using layout 5: {getattr(content_image_layout, 'name', 'Layout 5')}")
        
        # Find TOC layout
        table_of_contents_layout = get_layout_by_name(prs, "TableOfContents")
        if table_of_contents_layout:
            print(f"Found TableOfContents layout by name: {getattr(table_of_contents_layout, 'name', 'TableOfContents')}")
        else:
            # Try to find a good fallback
            table_of_contents_layout = prs.slide_layouts[12]
            print(f"Using TableOfContents layout from index 12 directly")
        
        # Check if we have at least 13 layouts
        if table_of_contents_layout is None:
            print("WARNING: Template doesn't have enough layouts, using fallback for TOC layout")
            # Try to find a content layout instead
            for i, layout in enumerate(prs.slide_layouts):
                layout_name = getattr(layout, 'name', f'Layout {i}').lower()
                if 'content' in layout_name:
                    table_of_contents_layout = layout
                    print(f"Using {getattr(layout, 'name', f'Layout {i}')} as TOC layout")
                    break
            
            # Final fallback
            if table_of_contents_layout is None:
                table_of_contents_layout = prs.slide_layouts[0]
                print(f"Using first layout as TOC fallback")
        
        content_layout = get_layout_by_name(prs, "Content") or prs.slide_layouts[5]
        section_layout = get_layout_by_name(prs, "Section") or prs.slide_layouts[2]
        thankyou_layout = get_layout_by_name(prs, "ThankYou") or prs.slide_layouts[14] 
        
        # If ThankYou layout not found, try to find a Blank layout or use the last layout
        if not thankyou_layout:
            for i, layout in enumerate(prs.slide_layouts):
                layout_name = getattr(layout, 'name', '')
                if 'blank' in layout_name.lower() or 'thank' in layout_name.lower():
                    thankyou_layout = layout
                    print(f"Using '{layout_name}' as ThankYou slide")
                    break
            
            if not thankyou_layout:
                # Fall back to the first blank-looking layout or just use index 0
                thankyou_layout = prs.slide_layouts[0]
                print(f"No ThankYou layout found, using first layout as fallback")
        
        print(f"\nGenerating PPTX presentation with {len(slides_list)} slides")
        
        # Add welcome slide as the first slide
        # Find welcome slide data from the slides collection
        welcome_data = {}
        for slide in slides_list:
            if getattr(slide, 'type', None) == 'Welcome' and hasattr(slide, 'fields'):
                welcome_data = slide.fields
                print(f"Found Welcome slide data: {welcome_data}")
                break
        
        welcome_slide = create_welcome_slide(prs, welcome_layout, presentation_title, welcome_data)
        
        # Check if we need to add a table of contents slide
        sections = [slide for slide in slides_list if getattr(slide, 'type', None) == 'Section']
        toc_data = None
        
        # Look for a TableOfContents type slide in the data
        for slide in slides_list:
            if getattr(slide, 'type', None) == 'TableOfContents' and hasattr(slide, 'fields'):
                toc_data = slide.fields
                print(f"\nFound TableOfContents slide data: {toc_data}")
                break
        
        # If we don't have toc_data, create it from section slides
        if not toc_data:
            toc_data = {
                "title": "Table of Contents",
                "sections": []
            }
            # Extract section titles from section slides
            for i, slide in enumerate(sections):
                if hasattr(slide, 'fields') and 'title' in slide.fields:
                    toc_data["sections"].append(slide.fields['title'])
                else:
                    toc_data["sections"].append(f"Section {i+1}")
            
            print(f"Created TOC data from sections: {toc_data}")
        
        # Use our dedicated function to create the TOC slide correctly
        if toc_data and toc_data.get("sections"):
            # Create a TOC slide with properly formatted textboxes
            toc_slide = create_table_of_contents_slide(prs, toc_data)
            print("TOC slide created successfully with section titles")
        else:
            print("No TOC data available, skipping TOC slide")
        
        # Track section count for numbering
        section_count = 0
        
        # Add all content slides
        for i, slide in enumerate(slides_list):
            # Get slide title from fields
            slide_title = slide.fields.get("title", f"Slide {i+1}") if hasattr(slide, "fields") else getattr(slide, "title", f"Slide {i+1}")
            slide_type = getattr(slide, 'type', 'ContentImage')
            print(f"\n===== Processing slide {i+1}: {slide_title} =====")
            print(f"SLIDE DEBUG: Slide type detected: '{slide_type}'")
            print(f"SLIDE DEBUG: Slide fields: {getattr(slide, 'fields', {}).keys()}")
            
            # Skip welcome and TOC slides since we've already created them
            if slide_type in ['Welcome', 'TableOfContents']:
                print(f"Skipping {slide_type} slide - already created")
                continue
            
            # Log slide type for debugging
            print(f"SLIDE DEBUG: Processing slide type: '{slide_type}'")
            
            # Get slide fields
            fields = getattr(slide, "fields", {})
            
            # Create appropriate slide based on type
            if slide_type == 'Section':
                section_count += 1
                create_section_slide(prs, section_layout, slide_title, section_count)
            elif slide_type == 'Content':
                content = fields.get("content", [])
                create_content_slide(prs, content_layout, slide_title, content)
            elif slide_type == 'ContentWithLogos':
                print(f"SLIDE DEBUG: Found ContentWithLogos slide! Title: {slide_title}")
                print(f"SLIDE DEBUG: Fields: {fields.keys()}")
                content = fields.get("content", [])
                
                print(f"\nLOGO DEBUG: === Processing ContentWithLogos slide {i} ===")
                print(f"LOGO DEBUG: Original fields for ContentWithLogos slide:")
                for k, v in fields.items():
                    if k.startswith('logo'):
                        print(f"LOGO DEBUG:   - {k}: {v}")
                
                # Collect logo paths
                logo_paths = {}
                
                # Import logo fetcher directly here to ensure it's available
                from tools.logo_fetcher import download_logo
                
                for logo_key in ['logo1', 'logo2', 'logo3']:
                    if logo_key in fields and fields[logo_key]:
                        logo_value = fields[logo_key]
                        print(f"LOGO DEBUG: Processing {logo_key}: {logo_value}")
                        
                        # Check if logo_value is a file path that exists
                        if os.path.exists(logo_value):
                            logo_paths[logo_key] = logo_value
                            print(f"LOGO DEBUG: Found existing logo file for {logo_key}: {logo_value}")
                        else:
                            # Extract a logo term for fetching
                            logo_term = logo_value
                            
                            # If it's a file path that doesn't exist, extract the company name
                            if '/' in logo_value:
                                # Extract file name without extension
                                logo_term = os.path.basename(logo_value)
                                logo_term = os.path.splitext(logo_term)[0]
                                # Clean up any prefixes like slide_id_ or logo_
                                logo_term = re.sub(r'^(slide_id_|slide_|logo_)', '', logo_term)
                                # Remove logo number suffix if present
                                logo_term = re.sub(r'_(logo\d+)$', '', logo_term)
                            
                            print(f"LOGO DEBUG: Attempting to download logo for term: '{logo_term}'")
                            try:
                                # Try to download the logo
                                success, result = download_logo(logo_term)
                                if success:
                                    logo_paths[logo_key] = result
                                    print(f"LOGO DEBUG: Successfully downloaded logo for {logo_key}: {result}")
                                    
                                    # Verify the file exists and has content
                                    if os.path.exists(result):
                                        file_size = os.path.getsize(result)
                                        print(f"LOGO DEBUG: Logo file size: {file_size} bytes")
                                        if file_size == 0:
                                            print(f"LOGO DEBUG: WARNING - Logo file is empty!")
                                    else:
                                        print(f"LOGO DEBUG: WARNING - Downloaded logo file doesn't exist!")
                                else:
                                    print(f"LOGO DEBUG: Failed to download logo for {logo_key}: {result}")
                                    
                                    # Try with a simpler term (just use the company name directly)
                                    simple_term = logo_term.split('_')[0]
                                    if simple_term != logo_term:
                                        print(f"LOGO DEBUG: Trying simpler term: '{simple_term}'")
                                        success, result = download_logo(simple_term)
                                        if success:
                                            logo_paths[logo_key] = result
                                            print(f"LOGO DEBUG: Successfully downloaded logo with simpler term: {result}")
                            except Exception as e:
                                print(f"LOGO DEBUG: Error downloading logo for {logo_key}: {str(e)}")
                                import traceback
                                print(f"LOGO DEBUG: Error details:\n{traceback.format_exc()}")
                
                # Count how many valid logo paths we have
                valid_logos = sum(1 for path in logo_paths.values() if path and os.path.exists(path))
                print(f"LOGO DEBUG: Found {valid_logos} valid logos for ContentWithLogos slide")
                
                if valid_logos == 0:
                    print(f"LOGO DEBUG: NO VALID LOGOS FOUND - Creating slide will not have logos!")
                
                # Find appropriate layout for ContentWithLogos
                logo_content_layout = None
                
                # First try to find by exact name
                for i, layout in enumerate(prs.slide_layouts):
                    layout_name = getattr(layout, 'name', '')
                    if layout_name == 'ContentWithLogos':
                        logo_content_layout = layout
                        print(f"Found ContentWithLogos layout by exact name match")
                        break
                
                # If not found by exact name, try partial match
                if not logo_content_layout:
                    for i, layout in enumerate(prs.slide_layouts):
                        layout_name = getattr(layout, 'name', f'Layout {i}').lower().replace(' ', '')
                        if 'logo' in layout_name or 'contentlogo' in layout_name:
                            logo_content_layout = layout
                            print(f"Found ContentWithLogos layout by partial name: {getattr(layout, 'name', f'Layout {i}')}")
                            break
                
                # If still not found, look for layouts with picture placeholders for logos
                if not logo_content_layout:
                    print("Looking for layouts with picture placeholders that could be used for logos")
                    for i, layout in enumerate(prs.slide_layouts):
                        # Check if this layout has picture placeholders
                        logo_placeholders = 0
                        for shape in layout.placeholders:
                            if hasattr(shape, "placeholder_format") and shape.placeholder_format.type == 18:  # PICTURE
                                logo_placeholders += 1
                        
                        # If we found at least one picture placeholder and a content placeholder,
                        # this might be suitable for ContentWithLogos
                        if logo_placeholders > 0:
                            has_content = any(hasattr(shape, "placeholder_format") and 
                                            shape.placeholder_format.type == 2
                                            for shape in layout.placeholders)
                            if has_content:
                                logo_content_layout = layout
                                print(f"Found suitable layout with {logo_placeholders} picture placeholders: {getattr(layout, 'name', f'Layout {i}')}")
                                break
                
                # If no specific layout found, use content layout as fallback
                if not logo_content_layout:
                    print("No ContentWithLogos layout found, using content layout as fallback")
                    logo_content_layout = content_layout
                
                create_content_with_logos_slide(prs, logo_content_layout, slide_title, content, logo_paths)
            elif slide_type == '3Images':
                # Find appropriate layout for 3Images
                threeim_layout = None
                for i, layout in enumerate(prs.slide_layouts):
                    layout_name = getattr(layout, 'name', f'Layout {i}').lower().replace(' ', '')
                    if '3images' in layout_name or 'threeimages' in layout_name or 'images3' in layout_name:
                        threeim_layout = layout
                        print(f"Found 3Images layout by name: {getattr(layout, 'name', f'Layout {i}')}")
                        break
                
                # If no specific 3Images layout found, use content layout as fallback
                if not threeim_layout:
                    print("No 3Images layout found, using content layout as fallback")
                    threeim_layout = content_layout
                
                # Get image paths and subtitles from fields
                image_paths = {
                    'image1': None,
                    'image2': None,
                    'image3': None
                }
                
                # Handle both naming conventions for subtitles (subtitleimage1 or image1subtitle)
                subtitles = {}
                for i in range(1, 4):
                    # Check both possible field name formats and use the first one found
                    subtitle_value = fields.get(f'image{i}subtitle', '') or fields.get(f'subtitleimage{i}', '')
                    subtitles[f'image{i}subtitle'] = subtitle_value
                
                # Check for image fields in the slide data
                if output_path is not None:
                    images_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(output_path), "images")
                    print(f"\nLooking for 3Images slide images in: {images_dir}")
                    if os.path.exists(images_dir):
                        print(f"Images directory exists with files: {os.listdir(images_dir)}")
                        
                        # Try to find images by slide ID if available
                        slide_id = getattr(slide, 'id', None)
                        slide_index = i + 1  # 1-based for filenames
                        
                        for img_num in range(1, 4):
                            img_field = f'image{img_num}'
                            print(f"Looking for {img_field}...")
                            
                            # First try to find image by specific image field name
                            if hasattr(slide, 'fields') and img_field in slide.fields:
                                # Handle direct path or pattern
                                image_attr = slide.fields[img_field]
                                if image_attr and os.path.exists(image_attr):
                                    image_paths[img_field] = image_attr
                                    print(f"  Found direct {img_field} path: {image_attr}")
                                    continue
                            
                            # Try various naming patterns for images
                            image_patterns = [
                                # Pattern 1: slide_id_{slide_id}_{img_field}
                                f"slide_id_{slide_id}_{img_field}" if slide_id else None,
                                # Pattern 2: slide_{slide_index}_{img_field}
                                f"slide_{slide_index}_{img_field}",
                                # Pattern 3: just {img_field}
                                f"{img_field}"
                            ]
                            
                            found_image = False
                            for pattern in image_patterns:
                                if not pattern:
                                    continue
                                    
                                print(f"  Trying pattern: {pattern}")
                                matching_images = [f for f in os.listdir(images_dir) 
                                                  if pattern.lower() in f.lower()]
                                
                                if matching_images:
                                    # Sort by modification time (newest first)
                                    matching_images.sort(key=lambda f: os.path.getmtime(os.path.join(images_dir, f)), 
                                                        reverse=True)
                                    image_path = os.path.join(images_dir, matching_images[0])
                                    image_paths[img_field] = image_path
                                    print(f"  Found {img_field} with pattern '{pattern}': {image_path}")
                                    found_image = True
                                    break
                            
                            if not found_image:
                                print(f"  No image found for {img_field}")
                
                print(f"Final image paths for 3Images slide:")
                for key, path in image_paths.items():
                    if path:
                        print(f"  {key}: {path} (exists: {os.path.exists(path)})")
                    else:
                        print(f"  {key}: Not found")
                
                # Create the 3Images slide
                create_3images_slide(prs, threeim_layout, slide_title, image_paths, subtitles)
                
            elif slide_type == 'ContentImage':
                content = fields.get("content", [])
                image_attr = fields.get('image')
                
                # Try to find the image file if we have output_path
                image_path = None
                
                # First, check if the slide has an image_url attribute (from compiled presentation)
                image_url = getattr(slide, 'image_url', None)
                if image_url:
                    print(f"  Using image URL from slide data: {image_url}")
                    # If it's a relative URL, convert to absolute path
                    if not image_url.startswith('http') and output_path is not None:
                        # Extract filename from URL path
                        image_filename = os.path.basename(image_url)
                        images_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(output_path), "images")
                        if os.path.exists(images_dir):
                            # Try to find the exact file
                            if image_filename in os.listdir(images_dir):
                                image_path = os.path.join(images_dir, image_filename)
                                print(f"  Found exact image at: {image_path}")
                
                # First try to find by slide ID if available
                if not image_path and hasattr(slide, 'id') and output_path is not None:
                    slide_id = getattr(slide, 'id')
                    images_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(output_path), "images")
                    if os.path.exists(images_dir):
                        # Look for image with exact slide ID
                        id_pattern = f"slide_id_{slide_id}_"
                        matching_id_images = [f for f in os.listdir(images_dir) if id_pattern in f.lower()]
                        if matching_id_images:
                            # Sort matching images by modification time (newest first)
                            matching_id_images.sort(key=lambda f: os.path.getmtime(os.path.join(images_dir, f)), reverse=True)
                            image_path = os.path.join(images_dir, matching_id_images[0])
                            print(f"  Found image by slide ID: {image_path} (Last modified: {os.path.getmtime(image_path)})")
                
                # Fall back to pattern matching only if no image_path was found
                if not image_path and image_attr and output_path is not None:
                    images_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(output_path), "images")
                    if os.path.exists(images_dir):
                        # Find image matching slide pattern - index is 0-based internally but 1-based for filenames
                        # Use slide_index+1 to match slide_1_*, slide_2_*, etc.
                        slide_index = i + 1
                        image_pattern = f"slide_{slide_index}_"
                        print(f"  Looking for images with pattern: {image_pattern}")
                        matching_images = [f for f in os.listdir(images_dir) if image_pattern in f.lower()]
                        if matching_images:
                            # Print all matching images with their timestamps for debugging
                            print(f"  All matching images for slide {slide_index}:")
                            for img in matching_images:
                                img_path = os.path.join(images_dir, img)
                                mod_time = os.path.getmtime(img_path)
                                print(f"    - {img} (Modified: {mod_time})")
                            
                            # Sort matching images by modification time (newest first)
                            matching_images.sort(key=lambda f: os.path.getmtime(os.path.join(images_dir, f)), reverse=True)
                            image_path = os.path.join(images_dir, matching_images[0])
                            print(f"  Selected image for slide {slide_index}: {image_path} (Last modified: {os.path.getmtime(image_path)})")
                
                create_content_slide(
                    prs, 
                    content_image_layout, 
                    slide_title, 
                    content, 
                    add_image=bool(image_path), 
                    image_path=image_path
                )
            
            # Add speaker notes if available - check both old and new format
            notes = getattr(slide, 'notes', None) or fields.get('notes')
            if notes:
                # Get the slide we just added
                current_slide = prs.slides[-1]
                if hasattr(current_slide, "notes_slide") and current_slide.notes_slide:
                    current_slide.notes_slide.notes_text_frame.text = notes
                    print(f"  Added speaker notes")
        
        # Add ThankYou slide at the end
        create_thank_you_slide(prs, thankyou_layout)
        
        # Create directory for this presentation if it doesn't exist
        pptx_filename = f"presentation_{uuid.uuid4()}.pptx"
        
        if output_path is not None:
            if output_path == "test":
                presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, "test")
            else:
                presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(output_path))
            
            os.makedirs(presentation_dir, exist_ok=True)
            pptx_path = os.path.join(presentation_dir, pptx_filename)
        else:
            os.makedirs(os.path.join(PRESENTATIONS_STORAGE_DIR, "temp"), exist_ok=True)
            pptx_path = os.path.join(PRESENTATIONS_STORAGE_DIR, "temp", pptx_filename)
        
        # Save the presentation
        print(f"Saving PPTX to: {pptx_path}")
        prs.save(pptx_path)
        print(f"PPTX saved successfully: {os.path.exists(pptx_path)}")
        
        return PptxGeneration(
            presentation_id=output_path,
            pptx_filename=pptx_filename,
            pptx_path=pptx_path,
            slide_count=len(prs.slides)
        )

    except Exception as e:
        print(f"Error generating PPTX: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

async def convert_pptx_to_png(pptx_path: str, output_dir: Optional[str] = None) -> List[str]:
    """Convert a PPTX file to PNG images using the LibreOffice CLI."""
    if output_dir is None:
        output_dir = os.path.dirname(pptx_path)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get basename without extension
    basename = os.path.splitext(os.path.basename(pptx_path))[0]
    
    print(f"Converting PPTX file: {pptx_path}")
    print(f"Output directory: {output_dir}")
    
    # Use LibreOffice to export each slide to PNG images
    cmd = ["soffice", "--headless", "--convert-to", "png", "--outdir", output_dir, pptx_path]
    
    try:
        print(f"Running command: {' '.join(cmd)}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        print(f"LibreOffice stdout: {stdout.decode() if stdout else 'None'}")
        print(f"LibreOffice stderr: {stderr.decode() if stderr else 'None'}")
        print(f"LibreOffice exit code: {process.returncode}")

        if process.returncode != 0:
            print(f"Error converting PPTX to PNG: {stderr.decode()}")
            return []

        # Gather generated PNG files
        png_files = [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.endswith('.png')
        ]

        png_files.sort()

        print(f"Generated {len(png_files)} PNG files")
        for png_file in png_files:
            print(f"  - {png_file}")

        return png_files
        
    except Exception as e:
        print(f"Error in convert_pptx_to_png: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return [] 