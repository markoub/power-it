"""
Utility functions for PowerPoint generation
"""
import os
from typing import List, Tuple

def list_presentation_images(presentation_id, storage_dir):
    """List all images available for a presentation ID for debugging purposes."""
    images_dir = os.path.join(storage_dir, str(presentation_id), "images")
    print(f"\nChecking for images in: {images_dir}")
    
    if not os.path.exists(images_dir):
        print(f"Images directory does not exist: {images_dir}")
        # Check parent directory content
        parent_dir = os.path.join(storage_dir, str(presentation_id))
        if os.path.exists(parent_dir):
            print(f"Parent directory exists: {parent_dir}")
            print(f"Content of parent directory: {os.listdir(parent_dir)}")
        else:
            print(f"Parent directory does not exist: {parent_dir}")
            # Check storage root
            if os.path.exists(storage_dir):
                print(f"Storage root exists: {storage_dir}")
                print(f"Content of storage root: {os.listdir(storage_dir)}")
        return []
    
    images = os.listdir(images_dir)
    print(f"Found {len(images)} images: {images}")
    return [os.path.join(images_dir, img) for img in images]

def estimate_text_length(text: str) -> int:
    """Estimate the visual length of text based on character count."""
    return len(text)

def calculate_content_size(content: List[str]) -> Tuple[int, int]:
    """Calculate approximate content size based on text length."""
    total_length = sum(estimate_text_length(point) for point in content)
    
    # Very simple heuristic to estimate size needs
    if total_length < 100:
        return (1, 1)  # Small content
    elif total_length < 300:
        return (2, 2)  # Medium content
    else:
        return (3, 3)  # Large content

def format_section_number(index):
    """Format a section number as '01', '02', etc."""
    return f"{index:02d}" 