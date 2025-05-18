import pytest
import os
import sys
import asyncio
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions we're testing
from tools.images import _generate_image_for_slide, generate_image_from_prompt
from models import ImageGeneration, Slide
from tools.slide_config import SLIDE_TYPES

# Mock classes for testing
class MockSlide:
    def __init__(self, fields=None, type=None):
        self.fields = fields or {}
        self.type = type or "ContentImage"

class MockData:
    def __init__(self):
        self.b64_json = "mockbase64data"

class MockResponse:
    def __init__(self, data=None):
        self.data = data or []

class TestImageTools:
    
    def test_generate_image_for_slide_default_size(self, mock_openai_responses):
        """Test that the default size is used when slide type is not ContentImage"""
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
        result = _generate_image_for_slide(slide, 0, None)
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].slide_index == 0
        assert result[0].slide_title == "Test Slide"
    
    def test_generate_image_for_slide_content_image_size(self, mock_openai_responses):
        """Test that the 3:4 size is used when slide type is ContentImage"""
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
        result = _generate_image_for_slide(slide, 0, None)
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].slide_index == 0
        assert result[0].slide_title == "Test Slide"
    
    def test_generate_image_missing_image_field(self, mock_openai_responses):
        """Test that no image is generated when image field is missing"""
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
        result = _generate_image_for_slide(slide, 0, None)
        
        # Verify no image was generated
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_generate_image_false_image_field(self, mock_openai_responses):
        """Test that no image is generated when image field is False"""
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
        result = _generate_image_for_slide(slide, 0, None)
        
        # Verify no image was generated
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_generate_image_save_to_file(self, mock_openai_responses):
        """Test that image is saved to file when presentation_id is provided"""
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
        result = _generate_image_for_slide(slide, 0, 999)
        
        # Verify the result includes an image path
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].image_path is not None
        assert "999" in result[0].image_path
        assert "slide_0" in result[0].image_path
        
        # Verify the file exists
        assert os.path.exists(result[0].image_path)
        
        # Clean up the file
        if os.path.exists(result[0].image_path):
            os.remove(result[0].image_path)
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_default_size(self, mock_openai_responses):
        """Test that the default size is used when slide_type is not specified"""
        # Call the function
        result = await generate_image_from_prompt("Test prompt")
        
        # Verify the result
        assert result is not None
        assert result.prompt == "Test prompt"
        assert result.image is not None
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_content_image_size(self, mock_openai_responses):
        """Test that the 3:4 size is used when slide_type is ContentImage"""
        # Call the function with slide_type=ContentImage
        result = await generate_image_from_prompt("Test prompt", slide_type="ContentImage")
        
        # Verify the result
        assert result is not None
        assert result.prompt == "Test prompt"
        assert result.image is not None
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_save_to_file(self, mock_openai_responses):
        """Test that image is saved to file when presentation_id is provided"""
        # Call the function with presentation_id
        result = await generate_image_from_prompt("Test prompt", presentation_id=999)
        
        # Verify the result includes an image path
        assert result is not None
        assert result.image_path is not None
        assert "999" in result.image_path
        
        # Verify the file exists
        assert os.path.exists(result.image_path)
        
        # Clean up the file
        if os.path.exists(result.image_path):
            os.remove(result.image_path) 