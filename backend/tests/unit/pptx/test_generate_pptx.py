import os
import pytest
import shutil
from pathlib import Path

from models import SlidePresentation, Slide, CompiledPresentation, CompiledSlide
from tools.generate_pptx import generate_pptx_from_slides, convert_pptx_to_png
from config import PRESENTATIONS_STORAGE_DIR
from tests.utils import assert_file_exists_and_valid, MockFactory

class TestGeneratePPTX:
    """Test PowerPoint generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_pptx_basic(self, tmp_path, monkeypatch):
        """Test generating a PPTX file from slides without a template."""
        # Mock the storage directory to use tmp_path
        test_storage = tmp_path / "storage"
        test_storage.mkdir(exist_ok=True)
        monkeypatch.setattr("config.PRESENTATIONS_STORAGE_DIR", str(test_storage))
        
        # Create a simple slide presentation
        slides = SlidePresentation(
            title="Test Presentation",
            slides=[
                Slide(
                    type="Content",
                    fields={
                        "title": "Introduction",
                        "content": ["Point 1", "Point 2", "Point 3"]
                    },
                    notes="These are speaker notes for slide 1"
                ),
                Slide(
                    type="Content",
                    fields={
                        "title": "Main Content",
                        "content": ["Main point 1", "Main point 2", "Main point 3"]
                    },
                    notes="These are speaker notes for slide 2"
                )
            ]
        )
        
        # Generate the PPTX file
        pptx_gen = await generate_pptx_from_slides(slides, "test")
        
        # Verify the PPTX file was created
        assert pptx_gen is not None
        assert_file_exists_and_valid(pptx_gen.pptx_path, min_size=10000, extensions=[".pptx"])
        assert pptx_gen.slide_count >= 4  # Welcome, 2 content, Thank You

    @pytest.mark.asyncio
    async def test_generate_pptx_with_images(self, tmp_path, monkeypatch):
        """Test generating a PPTX file from slides with images."""
        # Mock the storage directory
        test_storage = tmp_path / "storage" / "presentations"
        test_storage.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr("config.PRESENTATIONS_STORAGE_DIR", str(test_storage))
        
        # Create test image directory and file
        test_images_dir = test_storage / "test" / "images"
        test_images_dir.mkdir(parents=True, exist_ok=True)
        test_image_path = test_images_dir / "test_image.png"
        
        # Create a dummy image file
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(str(test_image_path))
        
        # Create a presentation with images
        slides = SlidePresentation(
            title="Template Test Presentation",
            slides=[
                Slide(
                    type="Content",
                    fields={
                        "title": "Slide 1",
                        "content": ["Point 1", "Point 2", "Point 3"]
                    },
                    notes="These are speaker notes for slide 1"
                ),
                Slide(
                    type="ContentImage",
                    fields={
                        "title": "Slide 2",
                        "content": ["Main point 1", "Main point 2", "Main point 3"],
                        "image": str(test_image_path)
                    },
                    notes="These are speaker notes for slide 2"
                )
            ]
        )
        
        # Generate the PPTX file
        pptx_gen = await generate_pptx_from_slides(slides, "test")
        
        # Verify the PPTX file was created
        assert pptx_gen is not None
        assert_file_exists_and_valid(pptx_gen.pptx_path, min_size=10000)
        assert pptx_gen.slide_count >= 4
    
    @pytest.mark.asyncio
    async def test_generate_pptx_empty_slides(self, tmp_path, monkeypatch):
        """Test handling of empty slides list."""
        # Mock the storage directory
        test_storage = tmp_path / "storage"
        test_storage.mkdir(exist_ok=True)
        monkeypatch.setattr("config.PRESENTATIONS_STORAGE_DIR", str(test_storage))
        
        slides = SlidePresentation(
            title="Empty Test",
            slides=[]  # Empty slides list
        )
        
        # Should still generate with just Welcome and Thank You slides
        result = await generate_pptx_from_slides(slides, "empty_test")
        assert result is not None
        assert result.slide_count >= 2  # At least Welcome and Thank You
    
    @pytest.mark.asyncio
    async def test_convert_pptx_to_png_fallback(self, tmp_path):
        """Test that convert_pptx_to_png handles missing files gracefully."""
        # Test with non-existent file
        output_dir = tmp_path / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Should create a fallback PNG when the PPTX doesn't exist
        result = await convert_pptx_to_png("non_existent.pptx", str(output_dir))
        
        # Should return at least the fallback PNG
        assert result is not None
        assert len(result) >= 1
        assert any("fallback" in path for path in result) 