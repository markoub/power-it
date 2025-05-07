import pytest
import os
import sys
import asyncio
from typing import Dict, Any, List

# Add parent directory to path to import modules properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import SlidePresentation, Slide, ImageGeneration
from tools.images import _generate_image_for_slide, generate_slide_images
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock OpenAI client to avoid actual API calls
class MockOpenAI:
    def __init__(self, *args, **kwargs):
        pass
    
    class Images:
        def generate(self, *args, **kwargs):
            class MockResult:
                def __init__(self):
                    class MockData:
                        def __init__(self):
                            self.b64_json = "mockbase64data"
                    self.data = [MockData()]
            return MockResult()
    
    def __init__(self, *args, **kwargs):
        self.images = self.Images()

@pytest.mark.asyncio
async def test_generate_slide_images_with_image_field():
    """Test that generate_slide_images only processes slides with 'image' field"""
    # Create test slides
    slides = [
        Slide(
            type="content",
            fields={
                "title": "Slide with Image",
                "content": ["This slide has an image field set to True"],
                "image": True
            }
        ),
        Slide(
            type="content",
            fields={
                "title": "Slide without Image",
                "content": ["This slide does not have an image field"]
            }
        ),
        Slide(
            type="content",
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
    
    # Mock the OpenAI API call to avoid actual API calls during testing
    # Save original function to restore later
    import tools.images
    original_executor = tools.images.image_executor
    original_openai = tools.images.OpenAI
    
    try:
        # Replace the executor with a simple function that runs synchronously
        tools.images.image_executor = None
        tools.images.OpenAI = MockOpenAI
        
        # Create a synchronous version of _generate_image_for_slide for testing
        def mock_generate_image_for_slide(slide, index, presentation_id):
            """Mock function that only returns data for slides with 'image' field"""
            if not (hasattr(slide, 'fields') and slide.fields.get('image')):
                return None
            
            return ImageGeneration(
                slide_index=index,
                slide_title=slide.fields.get('title', ''),
                prompt="mock prompt",
                image_path=f"/mock/path/image_{index}.png",
                image="mockbase64data"
            )
        
        # Replace the async run_in_executor call with our mock function
        async def mock_run_in_executor(executor, func, *args, **kwargs):
            return mock_generate_image_for_slide(*args, **kwargs)
        
        # Save original function
        original_run_in_executor = asyncio.get_event_loop().run_in_executor
        asyncio.get_event_loop().run_in_executor = mock_run_in_executor
        
        # Run the test
        images = await generate_slide_images(presentation, presentation_id=123)
        
        # Verify results
        assert len(images) == 2  # Should have 2 images for the 2 slides with 'image' field
        
        # Check the slide indices
        slide_indices = [img.slide_index for img in images]
        assert 0 in slide_indices  # First slide has image field
        assert 1 not in slide_indices  # Second slide doesn't have image field
        assert 2 in slide_indices  # Third slide has image field
        
    finally:
        # Restore original functions
        tools.images.image_executor = original_executor
        tools.images.OpenAI = original_openai
        asyncio.get_event_loop().run_in_executor = original_run_in_executor

def test_generate_image_for_slide():
    """Test the _generate_image_for_slide function directly"""
    # Create test slides
    slide_with_image = Slide(
        type="content",
        fields={
            "title": "Slide With Image",
            "content": ["This is content for a slide with an image"],
            "image": True
        }
    )
    
    slide_without_image = Slide(
        type="content",
        fields={
            "title": "Slide Without Image",
            "content": ["This is content for a slide without an image"]
        }
    )
    
    # Save and mock OpenAI
    import tools.images
    original_openai = tools.images.OpenAI
    
    try:
        # Mock OpenAI to avoid actual API calls
        tools.images.OpenAI = MockOpenAI
        
        # Test slide with image field
        result_with_image = _generate_image_for_slide(slide_with_image, 0, None)
        assert result_with_image is not None
        assert result_with_image.slide_index == 0
        assert result_with_image.slide_title == "Slide With Image"
        
        # Test slide without image field
        result_without_image = _generate_image_for_slide(slide_without_image, 1, None)
        assert result_without_image is None
        
    finally:
        # Restore original OpenAI
        tools.images.OpenAI = original_openai 