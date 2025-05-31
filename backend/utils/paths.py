import os
from typing import Optional, List
from pathlib import Path

from config import PRESENTATIONS_STORAGE_DIR


def get_presentation_dir(presentation_id: int) -> str:
    """
    Get the directory path for a specific presentation
    
    Args:
        presentation_id: ID of the presentation
        
    Returns:
        Full path to the presentation directory
    """
    return os.path.join(PRESENTATIONS_STORAGE_DIR, str(presentation_id))


def get_presentation_images_dir(presentation_id: int) -> str:
    """
    Get the images directory path for a specific presentation
    
    Args:
        presentation_id: ID of the presentation
        
    Returns:
        Full path to the presentation images directory
    """
    return os.path.join(get_presentation_dir(presentation_id), "images")


def ensure_presentation_dirs(presentation_id: int) -> None:
    """
    Ensure all necessary directories exist for a presentation
    
    Args:
        presentation_id: ID of the presentation
    """
    presentation_dir = get_presentation_dir(presentation_id)
    images_dir = get_presentation_images_dir(presentation_id)
    
    os.makedirs(presentation_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)


def get_image_path(presentation_id: int, image_filename: str) -> str:
    """
    Get the full path for an image file in a presentation
    
    Args:
        presentation_id: ID of the presentation
        image_filename: Name of the image file
        
    Returns:
        Full path to the image file
    """
    return os.path.join(get_presentation_images_dir(presentation_id), image_filename)


def validate_image_path(image_path: str, min_size: int = 100) -> bool:
    """
    Validate that an image file exists and meets minimum size requirements
    
    Args:
        image_path: Path to the image file
        min_size: Minimum file size in bytes (default: 100)
        
    Returns:
        True if the image is valid, False otherwise
    """
    if not os.path.exists(image_path):
        return False
    
    try:
        file_size = os.path.getsize(image_path)
        return file_size > min_size
    except Exception:
        return False


def list_presentation_images(presentation_id: int) -> List[str]:
    """
    List all image files in a presentation's images directory
    
    Args:
        presentation_id: ID of the presentation
        
    Returns:
        List of image filenames (not full paths)
    """
    images_dir = get_presentation_images_dir(presentation_id)
    
    if not os.path.exists(images_dir):
        return []
    
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    images = []
    
    for filename in os.listdir(images_dir):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            images.append(filename)
    
    return sorted(images)


def clean_filename(filename: str) -> str:
    """
    Clean a filename to ensure it's safe for filesystem use
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Ensure filename isn't empty
    if not filename:
        filename = 'unnamed'
    
    return filename