#!/usr/bin/env python3

import os
import pytest
import shutil
from models import SlidePresentation, Slide, CompiledPresentation, CompiledSlide
from tools.generate_pptx import generate_pptx_from_slides, convert_pptx_to_png
from config import PRESENTATIONS_STORAGE_DIR

@pytest.mark.asyncio
async def test_generate_pptx():
    """Test generating a PPTX file from slides without a template."""
    # Create a simple slide presentation
    slides = SlidePresentation(
        title="Test Presentation",
        slides=[
            Slide(
                title="Introduction",
                type="content",
                content=["Point 1", "Point 2", "Point 3"],
                notes="These are speaker notes for slide 1"
            ),
            Slide(
                title="Main Content",
                type="content",
                content=["Main point 1", "Main point 2", "Main point 3"],
                notes="These are speaker notes for slide 2"
            )
        ]
    )
    
    # Generate the PPTX file
    pptx_gen = await generate_pptx_from_slides(slides, "test")
    
    try:
        # Verify the PPTX file was created
        assert os.path.exists(pptx_gen.pptx_path)
        assert os.path.getsize(pptx_gen.pptx_path) > 0
    finally:
        # Clean up
        if os.path.exists(pptx_gen.pptx_path):
            os.remove(pptx_gen.pptx_path)

@pytest.mark.asyncio
async def test_generate_pptx_with_template():
    """Test generating a PPTX file from slides with a template."""
    # Create a simple slide presentation with images
    slides = CompiledPresentation(
        title="Template Test Presentation",
        slides=[
            CompiledSlide(
                title="Slide 1",
                type="content",
                content=["Point 1", "Point 2", "Point 3"],
                notes="These are speaker notes for slide 1",
            ),
            CompiledSlide(
                title="Slide 2",
                type="content",
                content=["Main point 1", "Main point 2", "Main point 3"],
                notes="These are speaker notes for slide 2",
                image_url="/presentations/test/images/test_image.png"
            )
        ]
    )
    
    # Ensure the test directory exists and has an image
    test_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, "test", "images")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a test image if it doesn't exist
    test_image_path = os.path.join(test_dir, "test_image.png")
    if not os.path.exists(test_image_path):
        # Copy a test image from the project root if available
        root_test_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_image.png")
        if os.path.exists(root_test_image):
            shutil.copy(root_test_image, test_image_path)
    
    # Skip if test image is not available
    if not os.path.exists(test_image_path):
        pytest.skip("Test image not found")
    
    # Generate the PPTX file
    pptx_gen = await generate_pptx_from_slides(slides, "test")
    
    try:
        # Verify the PPTX file was created
        assert os.path.exists(pptx_gen.pptx_path)
        assert os.path.getsize(pptx_gen.pptx_path) > 0
    finally:
        # Clean up
        if os.path.exists(pptx_gen.pptx_path):
            os.remove(pptx_gen.pptx_path) 