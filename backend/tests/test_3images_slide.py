import os
import pytest
import asyncio
from pathlib import Path

# Add parent directory to path to import from sibling modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SlidePresentation, Slide
from tools.generate_pptx import generate_pptx_from_slides
from config import PRESENTATIONS_STORAGE_DIR

@pytest.mark.asyncio
async def test_3images_slide():
    """Test that 3Images slide type is correctly processed"""
    # Create a test slide presentation with a 3Images slide
    slides = SlidePresentation(
        title="3Images Test Presentation",
        slides=[
            # Welcome slide
            Slide(
                type="Welcome",
                fields={
                    "title": "3Images Test Presentation",
                    "subtitle": "Testing the 3Images slide type",
                    "author": "Test User"
                }
            ),
            # A 3Images slide
            Slide(
                type="3Images",
                fields={
                    "title": "Three Images Slide",
                    "image1subtitle": "Image 1 Subtitle",
                    "image2subtitle": "Image 2 Subtitle",
                    "image3subtitle": "Image 3 Subtitle"
                }
            )
        ]
    )
    
    # Set up test images directory
    test_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, "test", "images")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test image paths (use existing test_image.png if available)
    source_image = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test_image.png")
    
    if os.path.exists(source_image):
        # Copy source image to test images for all three image placeholders
        for i in range(1, 4):
            dest_image = os.path.join(test_dir, f"slide_2_image{i}.png")
            if not os.path.exists(dest_image):
                import shutil
                shutil.copy(source_image, dest_image)
    
    # Generate the PowerPoint presentation
    result = await generate_pptx_from_slides(slides, "test")
    
    # Assertions
    assert result.slide_count == 3  # Welcome + 3Images + ThankYou
    assert os.path.exists(result.pptx_path)
    
    return result 