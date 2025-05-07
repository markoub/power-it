"""
Functions for handling PowerPoint shapes and finding specific shape elements
"""
from typing import Dict, Any, Optional

def get_layout_by_name(prs, name):
    """Get a slide layout by its name."""
    print(f"\nLooking for layout named: '{name}'")
    print("Available layouts:")
    for i, layout in enumerate(prs.slide_layouts):
        layout_name = getattr(layout, 'name', f'Layout {i}')
        print(f"  - Layout {i}: '{layout_name}'")
        
        # Only print detailed shape info if requested (to avoid errors)
        if layout_name == name:
            print(f"  ✓ Found layout: {name}")
            # Debug placeholders more carefully
            try:
                print(f"    Placeholders in this layout:")
                for p_idx, placeholder in enumerate(layout.placeholders):
                    p_type = placeholder.placeholder_format.type if hasattr(placeholder, 'placeholder_format') else 'Unknown'
                    p_name = getattr(placeholder, 'name', f'Placeholder {p_idx}')
                    print(f"      - Placeholder {p_idx}: Name='{p_name}', Type={p_type}")
            except Exception as e:
                print(f"    Error listing placeholders: {str(e)}")
            
            return layout
    
    print(f"  ✗ Layout '{name}' not found")
    return None

def find_shape_by_name(slide, name):
    """
    Find a shape in a slide by its name.
    Uses a sequence of matching strategies for better reliability.
    """
    # Step 1: Try exact matching
    for shape in slide.shapes:
        if hasattr(shape, "name") and shape.name == name:
            print(f"Found shape with exact name match: '{name}'")
            return shape
    
    # Step 2: Try case-insensitive exact matching
    for shape in slide.shapes:
        if hasattr(shape, "name") and shape.name and shape.name.lower() == name.lower():
            print(f"Found shape with case-insensitive exact match: '{shape.name}' for '{name}'")
            return shape
    
    # Step 3: Try partial case-insensitive matching
    for shape in slide.shapes:
        if hasattr(shape, "name") and shape.name and name.lower() in shape.name.lower():
            print(f"Found shape with partial case-insensitive match: '{shape.name}' for '{name}'")
            return shape
        
    # Step 4: Try if shape name contains number pattern in name
    # This helps with matching "03" or "3" with shapes named like "Text Placeholder 3"
    if name.isdigit() or (len(name) == 2 and name.startswith('0') and name[1].isdigit()):
        num = name.lstrip('0') if name.startswith('0') else name
        for shape in slide.shapes:
            if hasattr(shape, "name") and shape.name:
                # Try to find shapes where name ends with the number
                if shape.name.endswith(f" {num}") or shape.name.endswith(num):
                    print(f"Found shape with number match: '{shape.name}' for '{name}'")
                    return shape
    
    # Step 5: Try matching text content for shapes
    for shape in slide.shapes:
        if hasattr(shape, "text_frame") and hasattr(shape.text_frame, "text"):
            # Check if the shape's text exactly matches the name we're looking for
            if shape.text_frame.text == name:
                print(f"Found shape with text content match: '{getattr(shape, 'name', 'Unknown')}' with text '{name}'")
                return shape
    
    # Step 6: For Table of Contents, try to match by text and position patterns
    # Special case for finding section shapes that might have generic names
    if name.lower().startswith("section") and name.lower()[-1].isdigit():
        # Extract the section number from the name
        section_num = name.lower()[-1]
        
        # Try to find shape that is a text box with "Click to edit text" that might be a section
        for shape in slide.shapes:
            if (hasattr(shape, "text_frame") and 
                shape.text_frame.text == "Click to edit text" and
                hasattr(shape, "name") and
                ("section" in shape.name.lower() or section_num in shape.name)):
                print(f"Found potential section shape by pattern: '{shape.name}' for '{name}'")
                return shape
    
    # List all available shape names for debugging
    print(f"⚠️ WARNING: Could not find shape with name: '{name}'")
    print("Available shapes:")
    for i, shape in enumerate(slide.shapes):
        shape_name = getattr(shape, "name", "Unknown")
        shape_text = ""
        if hasattr(shape, "text_frame") and hasattr(shape.text_frame, "text"):
            shape_text = shape.text_frame.text[:30] + "..." if len(shape.text_frame.text) > 30 else shape.text_frame.text
        print(f"  - Shape {i}: '{shape_name}', Text: '{shape_text}'")
    
    return None

def get_toc_shapes(toc_slide, section_number):
    """
    Get all shapes for a specific section in the table of contents.
    Handles different naming conventions based on template analysis.
    
    Based on template analyzer, the shapes in the TableOfContents layout are named:
    - 'Section1', 'Section2', etc. for section titles (case-sensitive)
    - '01', '02', etc. for section numbers (formatted as 2 digits)
    - '01Divider', '02Divider', etc. for dividers (case-sensitive)
    """
    # Format the section number for lookup
    section_num_str = f"{section_number}"
    section_num_padded = f"{section_number:02d}"
    
    # Possible naming patterns for section shapes - based on template analysis
    # From analyzer, we see the shapes are named: 'Section1', 'Section2', etc.
    section_name_patterns = [
        f"Section{section_num_str}",  # Exact match from template
        f"section{section_num_str}"   # Lowercase variant (sometimes used)
    ]
    
    # Possible naming patterns for number shapes - based on template analysis
    # From analyzer, we see the shapes are named: '01', '02', etc.
    number_name_patterns = [
        f"{section_num_padded}",      # 01, 02, etc. (as seen in template)
        f"{section_num_str}"          # 1, 2, etc. (fallback)
    ]
    
    # Possible naming patterns for divider shapes - based on template analysis
    # From analyzer, we see the shapes are named: '01Divider', '02Divider', etc.
    divider_name_patterns = [
        f"{section_num_padded}Divider",  # Exact match from template
        f"{section_num_padded}divider"   # Lowercase variant (sometimes used)
    ]
    
    # First, print all shape names to help with debugging
    print(f"\nLooking for section shapes for section {section_number}:")
    print(f"Section patterns: {section_name_patterns}")
    print(f"Number patterns: {number_name_patterns}")
    print(f"Divider patterns: {divider_name_patterns}")
    print("\nAll shapes in the TOC slide:")
    for i, shape in enumerate(toc_slide.shapes):
        shape_name = getattr(shape, "name", "Unknown")
        shape_text = ""
        if hasattr(shape, "text_frame") and hasattr(shape.text_frame, "text"):
            shape_text = shape.text_frame.text[:30] + "..." if len(shape.text_frame.text) > 30 else shape.text_frame.text
        print(f"  Shape {i}: '{shape_name}', Text: '{shape_text}'")

    # Find section shape
    section_shape = None
    for pattern in section_name_patterns:
        shape = find_shape_by_name(toc_slide, pattern)
        if shape:
            section_shape = shape
            print(f"Found section shape with name: {getattr(shape, 'name', 'Unknown')}")
            break
    
    # If we still don't have a section shape, try direct matching with the shapes
    if not section_shape:
        print(f"Trying different approach to find section shape {section_number}")
        # Try to directly find the text boxes that might contain our section
        for shape in toc_slide.shapes:
            if hasattr(shape, "name") and shape.name and "section" in shape.name.lower():
                # Check if this is the right section number - case insensitive
                if shape.name.lower() == f"section{section_num_str}" or ("section" in shape.name.lower() and shape.name.lower().endswith(section_num_str)):
                    section_shape = shape
                    print(f"Found section shape by exact name match: {getattr(shape, 'name', 'Unknown')}")
                    break
                # Also check for a number at the end of the name
                if shape.name.lower().endswith(section_num_str):
                    section_shape = shape
                    print(f"Found section shape by name ending: {getattr(shape, 'name', 'Unknown')}")
                    break
    
    # Find number shape
    number_shape = None
    for pattern in number_name_patterns:
        shape = find_shape_by_name(toc_slide, pattern)
        if shape:
            number_shape = shape
            print(f"Found number shape with name: {getattr(shape, 'name', 'Unknown')}")
            break
    
    # If we still don't have a number shape, try direct matching with the shapes
    if not number_shape:
        print(f"Trying different approach to find number shape {section_number}")
        for shape in toc_slide.shapes:
            if hasattr(shape, "text_frame") and shape.text_frame.text:
                # Try to match the exact section number
                if shape.text_frame.text == section_num_str or shape.text_frame.text == section_num_padded:
                    number_shape = shape
                    print(f"Found number shape by text content: {getattr(shape, 'name', 'Unknown')}")
                    break
    
    # Find divider shape
    divider_shape = None
    for pattern in divider_name_patterns:
        shape = find_shape_by_name(toc_slide, pattern)
        if shape:
            divider_shape = shape
            print(f"Found divider shape with name: {getattr(shape, 'name', 'Unknown')}")
            break
    
    # Print summary of what we found
    print(f"Final results for section {section_number}:")
    print(f"  Section shape: {getattr(section_shape, 'name', 'None')}")
    print(f"  Number shape: {getattr(number_shape, 'name', 'None')}")
    print(f"  Divider shape: {getattr(divider_shape, 'name', 'None')}")
    
    return {
        'section': section_shape,
        'number': number_shape,
        'divider': divider_shape
    } 