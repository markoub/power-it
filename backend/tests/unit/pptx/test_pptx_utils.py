import os
import pytest
from pathlib import Path
import tempfile
import shutil

from tools.pptx_utils import (
    list_presentation_images,
    estimate_text_length,
    calculate_content_size,
    format_section_number
)


class TestPPTXUtils:
    """Test PowerPoint utility functions."""
    
    def test_format_section_number_basic(self):
        """Test basic section number formatting."""
        assert format_section_number(1) == "01"
        assert format_section_number(5) == "05"
        assert format_section_number(10) == "10"
    
    def test_format_section_number_edge_cases(self):
        """Test edge cases for section number formatting."""
        assert format_section_number(0) == "00"
        assert format_section_number(99) == "99"
        assert format_section_number(100) == "100"

    def test_estimate_text_length_basic(self):
        """Test basic text length estimation."""
        assert estimate_text_length("") == 0
        assert estimate_text_length("Hello") == 5
        assert estimate_text_length("Hello, world!") == 13
    
    def test_estimate_text_length_unicode(self):
        """Test text length estimation with unicode characters."""
        assert estimate_text_length("café") == 4
        assert estimate_text_length("🚀 rocket") == 8  # Emoji counts as 1 character
        assert estimate_text_length("中文字符") == 4

    def test_calculate_content_size_small(self):
        """Test calculating content size for small content."""
        small_content = ["Short point 1", "Short point 2"]
        size_small = calculate_content_size(small_content)
        assert size_small == (1, 1), "Small content should have size (1, 1)"
    
    def test_calculate_content_size_medium(self):
        """Test calculating content size for medium content."""
        medium_content = [
            "This is a medium-length bullet point with some additional text.",
            "Here's another medium-length point that adds more content.",
            "And one more medium point to get us over the threshold."
        ]
        size_medium = calculate_content_size(medium_content)
        assert size_medium == (2, 2), "Medium content should have size (2, 2)"
    
    def test_calculate_content_size_large(self):
        """Test calculating content size for large content."""
        large_content = [
            "This is a very long bullet point that contains a significant amount of text to ensure we exceed the threshold for large content sizing.",
            "Here's another long point with enough text to contribute to our large content determination.",
            "A third lengthy bullet point adding even more characters to our total.",
            "Fourth point with additional text that should put us well over the threshold.",
            "Fifth substantial bullet point to really ensure we hit the large content category."
        ]
        size_large = calculate_content_size(large_content)
        assert size_large == (3, 3), "Large content should have size (3, 3)"
    
    def test_calculate_content_size_empty(self):
        """Test calculating content size for empty content."""
        empty_content = []
        size_empty = calculate_content_size(empty_content)
        assert size_empty == (1, 1), "Empty content should have size (1, 1)"

    def test_list_presentation_images(self, tmp_path):
        """Test listing presentation images."""
        # Create a temporary presentation directory structure
        presentation_id = "999"
        images_dir = tmp_path / presentation_id / "images"
        os.makedirs(images_dir, exist_ok=True)
        
        # Create dummy image files
        test_image_files = ["slide_1_image.png", "slide_2_image.png", "slide_3_image1.png"]
        for filename in test_image_files:
            with open(os.path.join(images_dir, filename), "w") as f:
                f.write("dummy image content")
        
        # List the images
        images = list_presentation_images(presentation_id, str(tmp_path))
        
        # Check results
        assert len(images) == len(test_image_files), f"Should find {len(test_image_files)} images"
        for image_path in images:
            assert os.path.exists(image_path), f"Image path should exist: {image_path}"
            assert os.path.basename(image_path) in test_image_files, f"Image name should be in test files: {os.path.basename(image_path)}"
    
    def test_list_presentation_images_no_directory(self, tmp_path):
        """Test listing images when directory doesn't exist."""
        presentation_id = "nonexistent"
        images = list_presentation_images(presentation_id, str(tmp_path))
        assert images == [], "Should return empty list for non-existent directory"
    
    def test_list_presentation_images_empty_directory(self, tmp_path):
        """Test listing images from empty directory."""
        presentation_id = "empty"
        images_dir = tmp_path / presentation_id / "images"
        os.makedirs(images_dir, exist_ok=True)
        
        images = list_presentation_images(presentation_id, str(tmp_path))
        assert images == [], "Should return empty list for empty directory" 