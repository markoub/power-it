import pytest
import asyncio
from typing import List
from pathlib import Path
from unittest.mock import patch, MagicMock

from models import SlidePresentation, Slide, ImageGeneration
from tools.images import _generate_image_for_slide, generate_slide_images, generate_image_from_prompt
from tools.slide_config import SLIDE_TYPES
from tests.utils import assert_file_exists_and_valid, MockFactory


class TestSlideImageGeneration:
    """Test suite for slide image generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_slide_images_with_image_field(self, mock_openai_responses, temp_storage_dir):
        """Test that generate_slide_images only processes slides with 'image' field."""
        # Create test slides with valid slide types from the SLIDE_TYPES config
        slides = [
            Slide(
                type="ContentImage",  # This is a valid slide type with an image component
                fields={
                    "title": "Slide with Image",
                    "content": ["This slide has an image field"],
                    "image": True
                }
            ),
            Slide(
                type="Content",  # This is a valid slide type without an image component
                fields={
                    "title": "Slide without Image",
                    "content": ["This slide does not have an image field"]
                }
            ),
            Slide(
                type="ContentImage",  # Another slide with image
                fields={
                    "title": "Another Slide with Image",
                    "content": ["This is another slide with an image field"],
                    "image": True
                }
            )
        ]
        
        presentation = SlidePresentation(
            title="Test Presentation",
            slides=slides
        )
        
        # Use mocked responses
        images = await generate_slide_images(presentation, presentation_id=123)
        
        # Verify results
        assert len(images) == 2  # Should have 2 images for the 2 ContentImage slides
        
        # Check the slide indices
        slide_indices = [img.slide_index for img in images]
        assert 0 in slide_indices  # First slide has image field
        assert 1 not in slide_indices  # Second slide doesn't have image field
        assert 2 in slide_indices  # Third slide has image field
        
        # Verify image data
        for img in images:
            assert img.image is not None
            assert img.prompt is not None

    def test_generate_image_for_slide_with_image(self, mock_openai_responses, temp_storage_dir):
        """Test the _generate_image_for_slide function directly using OpenAI VCR."""
        # Create test slides with valid slide types
        slide_with_image = Slide(
            type="ContentImage",  # Valid slide type with image component
            fields={
                "title": "Slide With Image",
                "content": ["This is content for a slide with an image"],
                "image": True
            }
        )
        
        # Test slide with image field - will use VCR fixture
        results_with_image = _generate_image_for_slide(slide_with_image, 0, None)
        assert results_with_image is not None
        assert isinstance(results_with_image, list)
        assert len(results_with_image) > 0
        
        # Check the first result
        image_result = results_with_image[0]
        assert image_result.slide_index == 0
        assert image_result.slide_title == "Slide With Image"
        assert image_result.image is not None, "Should have an image"

    def test_generate_image_for_slide_without_image(self, mock_openai_responses):
        """Test that slides without image field return empty list."""
        # Create a valid slide without image component
        slide_without_image = Slide(
            type="Content",  # Valid slide type without image component
            fields={
                "title": "Slide Without Image",
                "content": ["This is content for a slide without an image"]
            }
        )
        
        # Test slide without image field
        results_without_image = _generate_image_for_slide(slide_without_image, 1, None)
        assert results_without_image is not None
        assert isinstance(results_without_image, list)
        assert len(results_without_image) == 0  # Should be empty list
    
    def test_generate_image_for_slide_with_presentation_id(self, mock_openai_responses, temp_storage_dir):
        """Test image generation saves to file when presentation_id is provided."""
        slide = Slide(
            type="ContentImage",
            fields={
                "title": "Test Slide",
                "content": ["Test content"],
                "image": True
            }
        )
        
        # Generate with presentation_id
        results = _generate_image_for_slide(slide, 0, 123)
        
        assert len(results) > 0
        result = results[0]
        assert result.image_path is not None
        assert "123" in result.image_path
        assert_file_exists_and_valid(result.image_path, min_size=10, extensions=['.png', '.jpg'])


class TestImagePromptGeneration:
    """Test suite for direct image generation from prompts."""
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_basic(self, mock_openai_responses):
        """Test basic image generation from prompt."""
        # Call the function with a test prompt
        result = await generate_image_from_prompt("Test image for presentation")
        
        # Verify results
        assert result is not None
        assert isinstance(result, ImageGeneration)
        assert result.prompt == "Test image for presentation"
        assert result.image is not None, "Should have an image"
        assert len(result.image) > 0, "Image data should not be empty"
    
    @pytest.mark.asyncio
    async def test_generate_image_with_slide_type(self, mock_openai_responses):
        """Test image generation with specific slide type."""
        result = await generate_image_from_prompt(
            "Business chart",
            slide_type="ContentImage"
        )
        
        assert result is not None
        assert result.prompt == "Business chart"
        assert result.image is not None
    
    @pytest.mark.asyncio
    async def test_generate_image_saves_to_file(self, mock_openai_responses, temp_storage_dir):
        """Test that image is saved to file when presentation_id is provided."""
        result = await generate_image_from_prompt(
            "Test image",
            presentation_id=456
        )
        
        assert result.image_path is not None
        assert "456" in result.image_path
        assert_file_exists_and_valid(result.image_path, min_size=10, extensions=['.png', '.jpg'])
    
    @pytest.mark.asyncio
    async def test_generate_image_offline_mode(self, mock_openai_responses):
        """Test image generation behavior in offline mode."""
        # In offline mode, should always succeed with mock data
        result = await generate_image_from_prompt("Test prompt")
        
        assert result is not None
        assert result.image is not None
        assert result.slide_title == "Mock Image"
        assert result.slide_index == -1
    
    @pytest.mark.asyncio
    async def test_generate_image_empty_prompt(self, mock_openai_responses):
        """Test handling of empty prompt."""
        # Empty prompt should still work but might generate generic image
        result = await generate_image_from_prompt("")
        assert result is not None
        assert result.prompt == ""
        assert result.image is not None


class TestSlideTypeImageGeneration:
    """Test suite for slide type specific image generation."""
    
    def test_three_images_slide_generation(self, mock_openai_responses):
        """Test image generation for 3Images slide type."""
        slide = Slide(
            type="3Images",
            fields={
                "title": "Three Images",
                "image1": True,
                "subtitleimage1": "First image",
                "image2": True,
                "subtitleimage2": "Second image",
                "image3": True,
                "subtitleimage3": "Third image"
            }
        )
        
        results = _generate_image_for_slide(slide, 0, None)
        
        # Should generate 3 images
        assert len(results) == 3
        
        # Check each image
        for i, result in enumerate(results):
            assert result.image_field_name == f"image{i+1}"
            assert result.slide_title == "Three Images"
            assert result.image is not None
    
    def test_image_full_slide_generation(self, mock_openai_responses):
        """Test image generation for ImageFull slide type."""
        slide = Slide(
            type="ImageFull",
            fields={
                "title": "Full Image Slide",
                "image": True
            }
        )
        
        results = _generate_image_for_slide(slide, 0, None)
        
        assert len(results) == 1
        assert results[0].slide_title == "Full Image Slide"
        assert results[0].image_field_name == "image"
    
    def test_invalid_slide_type(self, mock_openai_responses):
        """Test handling of invalid slide type."""
        slide = Slide(
            type="InvalidType",
            fields={
                "title": "Invalid",
                "image": True
            }
        )
        
        results = _generate_image_for_slide(slide, 0, None)
        
        # Should return empty list for invalid slide type
        assert isinstance(results, list)
        assert len(results) == 0