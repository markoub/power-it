import pytest
import os
import sys
import asyncio
from typing import Dict, Any, List

# Add parent directory to path to import modules properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import SlidePresentation, Slide, ImageGeneration
from tools.images import _generate_image_for_slide, generate_slide_images, generate_image_from_prompt
from tools.slide_config import SLIDE_TYPES
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Original MockOpenAI class kept for backward compatibility 
# but tests should use the VCR approach instead
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
async def test_generate_slide_images_with_image_field(mock_openai_responses):
    """Test that generate_slide_images only processes slides with 'image' field"""
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
    
    # Mock the executor to run synchronously
    import tools.images
    original_executor = tools.images.image_executor
    
    try:
        # Replace the executor with a simple function that runs synchronously
        tools.images.image_executor = None
        
        # Create a synchronous version of _generate_image_for_slide for testing
        def mock_generate_image_for_slide(slide, index, presentation_id):
            """Custom implementation for testing that respects slide types and configs"""
            slide_type = getattr(slide, 'type', None)
            if not slide_type or slide_type not in SLIDE_TYPES:
                return []
                
            slide_config = SLIDE_TYPES[slide_type]
            image_fields = [comp for comp in slide_config.get("components", []) if comp.startswith("image")]
            
            if not hasattr(slide, 'fields') or not slide.fields:
                return []
                
            generated_images = []
            for image_field in image_fields:
                if slide.fields.get(image_field):
                    generated_images.append(ImageGeneration(
                        slide_index=index,
                        slide_title=slide.fields.get('title', ''),
                        prompt="mock prompt",
                        image_field_name=image_field,
                        image_path=f"/mock/path/image_{index}_{image_field}.png",
                        image="mockbase64data"
                    ))
            
            return generated_images
        
        # Replace the async run_in_executor call with our mock function
        async def mock_run_in_executor(executor, func, *args, **kwargs):
            return mock_generate_image_for_slide(*args, **kwargs)
        
        # Save original function
        original_run_in_executor = asyncio.get_event_loop().run_in_executor
        asyncio.get_event_loop().run_in_executor = mock_run_in_executor
        
        # Run the test
        images = await generate_slide_images(presentation, presentation_id=123)
        
        # Verify results
        assert len(images) == 2  # Should have 2 images for the 2 ContentImage slides
        
        # Check the slide indices
        slide_indices = [img.slide_index for img in images]
        assert 0 in slide_indices  # First slide has image field
        assert 1 not in slide_indices  # Second slide doesn't have image field
        assert 2 in slide_indices  # Third slide has image field
        
    finally:
        # Restore original functions
        tools.images.image_executor = original_executor
        asyncio.get_event_loop().run_in_executor = original_run_in_executor


def test_generate_image_for_slide(mock_openai_responses):
    """Test the _generate_image_for_slide function directly using OpenAI VCR"""
    # Create test slides with valid slide types
    slide_with_image = Slide(
        type="ContentImage",  # Valid slide type with image component
        fields={
            "title": "Slide With Image",
            "content": ["This is content for a slide with an image"],
            "image": True
        }
    )
    
    slide_without_image = Slide(
        type="Content",  # Valid slide type without image component
        fields={
            "title": "Slide Without Image",
            "content": ["This is content for a slide without an image"]
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
    
    # Test slide without image field
    results_without_image = _generate_image_for_slide(slide_without_image, 1, None)
    assert results_without_image is not None
    assert isinstance(results_without_image, list)
    assert len(results_without_image) == 0  # Should be empty list


@pytest.mark.asyncio
async def test_generate_image_from_prompt(mock_openai_responses):
    """Test the generate_image_from_prompt function using OpenAI VCR"""
    # Call the function with a test prompt
    result = await generate_image_from_prompt("Test image for presentation")
    
    # Verify results
    assert result is not None
    assert result.prompt == "Test image for presentation"
    assert result.image is not None, "Should have an image" 