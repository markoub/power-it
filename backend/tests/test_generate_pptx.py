import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from pptx import Presentation
from typing import List

from models import SlidePresentation, CompiledPresentation, CompiledSlide
from tools.generate_pptx import generate_pptx_from_slides

@pytest.mark.asyncio
async def test_image_url_priority():
    """Test that image_url from slide data is prioritized over file pattern matching."""
    # Create a temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test presentation ID and images folder
        pres_id = "test_pres"
        images_dir = os.path.join(temp_dir, pres_id, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Create test images - one with direct path, two with pattern match (old and new)
        old_image_path = os.path.join(images_dir, "slide_2_old.png")  # Second slide
        new_image_path = os.path.join(images_dir, "slide_2_newest.png")  # Second slide
        direct_image_path = os.path.join(images_dir, "specific_image.png")  # First slide
        
        # Create dummy image files
        for path in [old_image_path, new_image_path, direct_image_path]:
            with open(path, 'w') as f:
                f.write("dummy image content")
        
        # Make the "old" image older by modifying its timestamp
        old_timestamp = os.path.getmtime(old_image_path) - 1000
        os.utime(old_image_path, (old_timestamp, old_timestamp))
        
        # Create test slides with image_url pointing to specific_image.png
        compiled_slides = [
            CompiledSlide(
                type="ContentImage",
                title="Test Slide With Direct Image URL",
                fields={
                    "content": ["Test content"],
                    "image": True
                },
                image_url=f"/presentations/{pres_id}/images/specific_image.png"
            ),
            CompiledSlide(
                type="ContentImage",
                title="Test Slide With Pattern Matching",
                fields={
                    "content": ["Test content"],
                    "image": True
                }
            )
        ]
        
        presentation = CompiledPresentation(
            title="Test Presentation",
            slides=compiled_slides
        )
        
        # Track which content_slide calls received which image paths
        image_paths_used: List[str] = []
        
        # Create a wrapper function to capture image_path arguments
        def capture_image_path(*args, **kwargs):
            if 'image_path' in kwargs:
                image_paths_used.append(kwargs.get('image_path'))
            return MagicMock()
        
        # Mock the Presentation class to avoid actual file operations
        with patch("tools.generate_pptx.Presentation") as MockPresentation, \
             patch("tools.generate_pptx.get_layout_by_name") as mock_get_layout, \
             patch("tools.generate_pptx.create_welcome_slide") as mock_welcome, \
             patch("tools.generate_pptx.create_table_of_contents_slide") as mock_toc, \
             patch("tools.generate_pptx.create_section_slide") as mock_section, \
             patch("tools.generate_pptx.create_thank_you_slide") as mock_thankyou, \
             patch("tools.generate_pptx.create_content_slide", side_effect=capture_image_path) as mock_content, \
             patch("tools.generate_pptx.PRESENTATIONS_STORAGE_DIR", temp_dir):
            
            # Setup mocks
            mock_prs = MagicMock()
            MockPresentation.return_value = mock_prs
            mock_prs.slide_layouts = [MagicMock() for _ in range(15)]
            mock_prs.slides = []
            
            # Mock layouts
            mock_get_layout.return_value = mock_prs.slide_layouts[0]
            
            # Generate PPTX
            result = await generate_pptx_from_slides(presentation, pres_id)
            
            # Verify our function captured the image paths
            assert len(image_paths_used) >= 2
            
            # First image should be the direct image path
            assert any(path is not None and "specific_image.png" in path for path in image_paths_used), "Direct image not found"
            
            # Second image should be the newest one by timestamp
            assert any(path is not None and "slide_2_newest.png" in path for path in image_paths_used), "Newest pattern-matched image not found" 