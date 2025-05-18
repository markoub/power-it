import os
import sys
import pytest
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path if needed
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from tools.pptx_utils import (
    list_presentation_images,
    estimate_text_length,
    calculate_content_size,
    format_section_number
)

def test_format_section_number():
    """Test formatting section numbers with leading zeros."""
    assert format_section_number(1) == "01"
    assert format_section_number(9) == "09"
    assert format_section_number(10) == "10"
    assert format_section_number(99) == "99"

def test_estimate_text_length():
    """Test estimating text length."""
    assert estimate_text_length("") == 0
    assert estimate_text_length("Hello") == 5
    assert estimate_text_length("Hello, world!") == 13

def test_calculate_content_size():
    """Test calculating content size based on text length."""
    # Small content
    small_content = ["Short point 1", "Short point 2"]
    size_small = calculate_content_size(small_content)
    assert size_small == (1, 1), "Small content should have size (1, 1)"
    
    # Medium content
    medium_content = [
        "This is a medium-length bullet point with some additional text.",
        "Here's another medium-length point that adds more content.",
        "And one more medium point to get us over the threshold."
    ]
    size_medium = calculate_content_size(medium_content)
    assert size_medium == (2, 2), "Medium content should have size (2, 2)"
    
    # Large content
    large_content = [
        "This is a very long bullet point that contains a significant amount of text to ensure we exceed the threshold for large content sizing.",
        "Here's another long point with enough text to contribute to our large content determination.",
        "A third lengthy bullet point adding even more characters to our total.",
        "Fourth point with additional text that should put us well over the threshold.",
        "Fifth substantial bullet point to really ensure we hit the large content category."
    ]
    size_large = calculate_content_size(large_content)
    assert size_large == (3, 3), "Large content should have size (3, 3)"

def test_list_presentation_images(tmp_path):
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