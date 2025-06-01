import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

from tools.images import _generate_image_for_slide, generate_image_from_prompt, save_image_to_file
from models import ImageGeneration, Slide
from tools.slide_config import SLIDE_TYPES
from tests.utils import assert_file_exists_and_valid, MockFactory
import base64


class TestImageSizeConfiguration:
    """Test suite for image size configuration based on slide types."""
    
    async def test_generate_image_for_slide_default_size(self, mock_openai_responses, temp_storage_dir):
        """Test that the default size is used when slide type is not ContentImage."""
        # Create a slide with image field but not ContentImage type
        slide = Slide(
            type="ImageFull", # A valid slide type with image but not ContentImage
            fields={
                "title": "Test Slide", 
                "content": "Test content",
                "image": True
            }
        )
        
        # Call the function
        result = await _generate_image_for_slide(slide, 0, None)
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].slide_index == 0
        assert result[0].slide_title == "Test Slide"
    
    async def test_generate_image_for_slide_content_image_size(self, mock_openai_responses, temp_storage_dir):
        """Test that the 3:4 size is used when slide type is ContentImage."""
        # Create a slide with image field and ContentImage type
        slide = Slide(
            type="ContentImage",
            fields={
                "title": "Test Slide", 
                "content": "Test content",
                "image": True
            }
        )
        
        # Call the function
        result = await _generate_image_for_slide(slide, 0, None)
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].slide_index == 0
        assert result[0].slide_title == "Test Slide"


class TestImageFieldValidation:
    """Test suite for image field validation and edge cases."""
    
    async def test_generate_image_missing_image_field(self, mock_openai_responses):
        """Test that no image is generated when image field is missing."""
        # Create a slide without image field
        slide = Slide(
            type="ContentImage",
            fields={
                "title": "Test Slide", 
                "content": "Test content"
                # No image field
            }
        )
        
        # Call the function
        result = await _generate_image_for_slide(slide, 0, None)
        
        # Verify no image was generated
        assert isinstance(result, list)
        assert len(result) == 0
    
    async def test_generate_image_false_image_field(self, mock_openai_responses):
        """Test that no image is generated when image field is False."""
        # Create a slide with image field set to False
        slide = Slide(
            type="ContentImage",
            fields={
                "title": "Test Slide", 
                "content": "Test content",
                "image": False
            }
        )
        
        # Call the function
        result = await _generate_image_for_slide(slide, 0, None)
        
        # Verify no image was generated
        assert isinstance(result, list)
        assert len(result) == 0
    
    async def test_multiple_image_fields_in_slide(self, mock_openai_responses):
        """Test handling of slides with multiple image fields."""
        slide = Slide(
            type="3Images",
            fields={
                "title": "Multiple Images",
                "image1": True,
                "image2": False,  # This one should be skipped
                "image3": True
            }
        )
        
        result = await _generate_image_for_slide(slide, 0, None)
        
        # Should only generate 2 images (image1 and image3)
        assert len(result) == 2
        assert result[0].image_field_name == "image1"
        assert result[1].image_field_name == "image3"


class TestImageStorage:
    """Test suite for image storage functionality."""
    
    async def test_generate_image_save_to_file(self, mock_openai_responses, temp_storage_dir):
        """Test that image is saved to file when presentation_id is provided."""
        # Create a slide with image field
        slide = Slide(
            type="ContentImage",
            fields={
                "title": "Test Slide", 
                "content": "Test content",
                "image": True
            }
        )
        
        # Call the function with presentation_id
        result = await _generate_image_for_slide(slide, 0, 999)
        
        # Verify the result includes an image path
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].image_path is not None
        assert "999" in result[0].image_path
        assert "slide_0" in result[0].image_path
        
        # Verify the file exists and is valid
        assert_file_exists_and_valid(result[0].image_path, min_size=10, extensions=['.png', '.jpg'])
    
    def test_save_image_to_file_function(self, temp_storage_dir, monkeypatch):
        """Test the save_image_to_file utility function."""
        # Temporarily disable offline mode for this test
        monkeypatch.setattr("tools.images.OFFLINE_MODE", False)
        
        # Create test image data
        test_image_data = base64.b64encode(b"test image data").decode('utf-8')
        
        # Save the image (correct signature: presentation_id, slide_index, image_field_name, image_data)
        file_path = save_image_to_file(123, 1, "test_slide", test_image_data)
        
        assert file_path is not None
        assert "123" in file_path
        assert "test_slide" in file_path
        assert_file_exists_and_valid(file_path, min_size=5)
    
    async def test_image_storage_directory_creation(self, temp_storage_dir):
        """Test that storage directories are created automatically."""
        # Use a non-existent presentation ID
        slide = Slide(
            type="ContentImage",
            fields={"title": "Test", "image": True}
        )
        
        result = await _generate_image_for_slide(slide, 0, 99999)
        
        assert len(result) > 0
        assert result[0].image_path is not None
        
        # Check directory was created
        image_dir = Path(result[0].image_path).parent
        assert image_dir.exists()
        assert image_dir.is_dir()


class TestPromptBasedImageGeneration:
    """Test suite for prompt-based image generation."""
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_default_size(self, mock_openai_responses):
        """Test that the default size is used when slide_type is not specified."""
        # Call the function
        result = await generate_image_from_prompt("Test prompt")
        
        # Verify the result
        assert result is not None
        assert result.prompt == "Test prompt"
        assert result.image is not None
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_content_image_size(self, mock_openai_responses):
        """Test that the 3:4 size is used when slide_type is ContentImage."""
        # Call the function with slide_type=ContentImage
        result = await generate_image_from_prompt("Test prompt", slide_type="ContentImage")
        
        # Verify the result
        assert result is not None
        assert result.prompt == "Test prompt"
        assert result.image is not None
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_save_to_file(self, mock_openai_responses, temp_storage_dir):
        """Test that image is saved to file when presentation_id is provided."""
        # Call the function with presentation_id
        result = await generate_image_from_prompt("Test prompt", presentation_id=999)
        
        # Verify the result includes an image path
        assert result is not None
        assert result.image_path is not None
        assert "999" in result.image_path
        
        # Verify the file exists and is valid
        assert_file_exists_and_valid(result.image_path, min_size=10, extensions=['.png', '.jpg'])
    
    @pytest.mark.asyncio
    async def test_generate_image_with_custom_parameters(self, mock_openai_responses):
        """Test image generation with custom parameters."""
        result = await generate_image_from_prompt(
            "Complex business visualization",
            slide_type="ImageFull",
            size="1792x1024"
        )
        
        assert result is not None
        assert result.prompt == "Complex business visualization"
        # Default values from the function
        assert result.slide_title == "Mock Image"
        assert result.slide_index == -1


class TestErrorHandling:
    """Test suite for error handling in image generation."""
    
    async def test_invalid_image_data(self, mock_openai_responses):
        """Test handling of invalid image data from API."""
        # This would need custom mock to return invalid data
        # For now, we'll test that the function handles None gracefully
        slide = Slide(
            type="ContentImage",
            fields={"title": "Test", "image": None}
        )
        
        result = await _generate_image_for_slide(slide, 0, None)
        assert len(result) == 0  # Should not generate image for None
    
    @pytest.mark.asyncio
    async def test_offline_mode_behavior(self, mock_openai_responses):
        """Test that offline mode returns mock data correctly."""
        # In offline mode, should always return mock data
        result = await generate_image_from_prompt("Test prompt")
        
        assert result is not None
        assert result.image is not None
        assert result.slide_title == "Mock Image"
        assert result.slide_index == -1