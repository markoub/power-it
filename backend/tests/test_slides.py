import unittest
import json
import sys
import os
import asyncio
from unittest.mock import patch, MagicMock
import pytest

# Add parent directory to path so we can import properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import ResearchData, SlidePresentation, Slide
from tools.slides import generate_slides
from tools.slide_config import SLIDE_TYPES, PRESENTATION_STRUCTURE

# Create a simple async mock class since AsyncMock might not be available
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
    
    async def generate_content_async(self, *args, **kwargs):
        return super(AsyncMock, self).generate_content_async(*args, **kwargs)

class MockResponse:
    def __init__(self, text):
        self.text = text

class TestSlideGeneration(unittest.TestCase):
    
    @patch('google.generativeai.GenerativeModel')
    def test_generate_slides_with_new_model(self, mock_model_class):
        """Test generating slides with the new Slide model structure using type and fields"""
        # Create mock response from Gemini
        mock_response = MockResponse(json.dumps({
            "title": "Test Presentation",
            "author": "Test Author",
            "slides": [
                {
                    "type": "Welcome",
                    "fields": {
                        "title": "Welcome to Test",
                        "subtitle": "A Test Presentation",
                        "author": "Test Author"
                    }
                },
                {
                    "type": "Section",
                    "fields": {
                        "title": "First Section"
                    }
                },
                {
                    "type": "Content",
                    "fields": {
                        "title": "Content Slide",
                        "content": ["Content point 1", "Content point 2"]
                    }
                },
                {
                    "type": "ContentImage",
                    "fields": {
                        "title": "Content with Image",
                        "content": ["Image point 1", "Image point 2"],
                        "subtitle": "Image subtitle",
                        "image": "A description of the image needed"
                    }
                },
                {
                    "type": "Content",
                    "fields": {
                        "title": "Summary",
                        "content": ["Summary point 1", "Summary point 2"]
                    }
                }
            ]
        }))
        
        # Set up mock model
        mock_model = MagicMock()
        mock_model.generate_content_async.return_value = asyncio.Future()
        mock_model.generate_content_async.return_value.set_result(mock_response)
        mock_model_class.return_value = mock_model
        
        # Create research data
        research = ResearchData(content="Test research content")
        
        # Run the generate_slides function
        result = asyncio.run(generate_slides(research, target_slides=5, author="Test Author"))
        
        # Verify the model was called with the correct prompt
        mock_model.generate_content_async.assert_called_once()
        
        # Assert that the result is a SlidePresentation object with the expected properties
        self.assertIsInstance(result, SlidePresentation)
        self.assertEqual(result.title, "Test Presentation")
        self.assertEqual(result.author, "Test Author")
        
        # Should have 6 slides (5 from the mock response + 1 auto-generated TableOfContents)
        self.assertEqual(len(result.slides), 6)
        
        # Check slide types
        slide_types = [slide.type for slide in result.slides]
        self.assertEqual(slide_types[0], "Welcome")
        self.assertEqual(slide_types[1], "TableOfContents")  # Auto-generated
        self.assertEqual(slide_types[2], "Section")
        
        # Verify first slide fields (Welcome)
        welcome_slide = result.slides[0]
        self.assertEqual(welcome_slide.type, "Welcome")
        self.assertEqual(welcome_slide.fields["title"], "Welcome to Test")
        self.assertEqual(welcome_slide.fields["subtitle"], "A Test Presentation")
        self.assertEqual(welcome_slide.fields["author"], "Test Author")
        self.assertNotIn("content", welcome_slide.fields)  # Welcome slide should not have content
        
        # Verify auto-generated TableOfContents slide
        toc_slide = result.slides[1]
        self.assertEqual(toc_slide.type, "TableOfContents")
        self.assertEqual(toc_slide.fields["title"], "Table of Contents")
        self.assertEqual(toc_slide.fields["sections"], ["First Section"])
        
        # Verify Section slide
        section_slide = result.slides[2]
        self.assertEqual(section_slide.type, "Section")
        self.assertEqual(section_slide.fields["title"], "First Section")
        self.assertNotIn("content", section_slide.fields)  # Section slide should not have content
        
        # Verify ContentImage slide
        image_slide = result.slides[4]
        self.assertEqual(image_slide.type, "ContentImage")
        self.assertEqual(image_slide.fields["image"], "A description of the image needed")
        self.assertEqual(image_slide.fields["subtitle"], "Image subtitle")
        self.assertIn("content", image_slide.fields)
        
        # Verify that only the appropriate fields are included for each slide type
        for slide in result.slides:
            slide_type = slide.type
            # Check that the fields are valid for this slide type
            if slide_type in SLIDE_TYPES:
                required_components = SLIDE_TYPES[slide_type]["components"]
                
                # Check that all required components are present
                for component in required_components:
                    # Skip sections check for auto-generated TOC
                    if slide_type == "TableOfContents" and component == "sections" and PRESENTATION_STRUCTURE.get("auto_generate_toc", True):
                        continue
                    self.assertIn(component, slide.fields)
                
                # Check that no extra fields are present
                for field in slide.fields:
                    # Special case for auto-generated TableOfContents which includes content and title
                    if slide_type == "TableOfContents" and field in ["content", "title", "sections"]:
                        continue
                        
                    # Title is allowed for all slides
                    if field == "title":
                        continue
                        
                    # Check that the field is in the required components
                    self.assertIn(field, required_components, 
                                  f"Field '{field}' should not be in {slide_type} slide")

    @patch('google.generativeai.GenerativeModel')
    def test_slide_field_removal(self, mock_model_class):
        """Test that the slide fields are properly filtered to only include required fields"""
        # Create mock response with extra fields
        mock_response = MockResponse(json.dumps({
            "title": "Test Presentation",
            "author": "Test Author",
            "slides": [
                {
                    "type": "Welcome",
                    "fields": {
                        "title": "Welcome to Test",
                        "subtitle": "A Test Presentation",
                        "author": "Test Author",
                        "content": ["This should be removed"],  # Extra field
                        "notes": "Speaker notes that should be removed",  # Extra field
                        "visual_suggestions": "Visual suggestions to remove"  # Extra field
                    }
                },
                {
                    "type": "Section",
                    "fields": {
                        "title": "First Section",
                        "content": ["This content should be removed"],  # Extra field
                        "extra_field": "This should be removed"  # Extra field
                    }
                }
            ]
        }))
        
        # Set up mock model - use a loop policy to avoid event loop issues
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        mock_model = MagicMock()
        future = loop.create_future()
        future.set_result(mock_response)
        mock_model.generate_content_async.return_value = future
        mock_model_class.return_value = mock_model
        
        try:
            # Create research data
            research = ResearchData(content="Test research content")
            
            # Run the generate_slides function
            result = loop.run_until_complete(generate_slides(research, target_slides=2, author="Test Author"))
            
            # Assert that the result is a SlidePresentation object with the expected properties
            self.assertIsInstance(result, SlidePresentation)
            
            # Verify Welcome slide has only required fields
            welcome_slide = result.slides[0]
            self.assertEqual(welcome_slide.type, "Welcome")
            self.assertEqual(welcome_slide.fields["title"], "Welcome to Test")
            self.assertEqual(welcome_slide.fields["subtitle"], "A Test Presentation")
            self.assertEqual(welcome_slide.fields["author"], "Test Author")
            self.assertNotIn("content", welcome_slide.fields)
            self.assertNotIn("notes", welcome_slide.fields)
            self.assertNotIn("visual_suggestions", welcome_slide.fields)
            
            # Verify Section slide has only required fields
            section_slide = result.slides[2]  # Index 2 because TableOfContents is inserted at 1
            self.assertEqual(section_slide.type, "Section")
            self.assertEqual(section_slide.fields["title"], "First Section")
            self.assertNotIn("content", section_slide.fields)
            self.assertNotIn("extra_field", section_slide.fields)
        finally:
            loop.close()

@pytest.mark.asyncio
async def test_welcome_and_section_slides_fallback():
    """Test that when Gemini doesn't provide Welcome and Section slides, 
    the code adds them automatically"""
    
    # Mock research data
    research = ResearchData(content="This is test research content")
    
    # Mock the Gemini API response to only return Content slides
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "title": "Test Presentation",
        "author": "Test Author",
        "slides": [
            {
                "type": "Content",
                "fields": {
                    "title": "Slide 1",
                    "content": ["Point 1", "Point 2"]
                }
            },
            {
                "type": "Content",
                "fields": {
                    "title": "Slide 2",
                    "content": ["Point 3", "Point 4"]
                }
            }
        ]
    })
    
    # Create a simple mock class that returns our response
    class MockGenerativeModel:
        async def generate_content_async(self, *args, **kwargs):
            return mock_response
    
    # Patch the genai.GenerativeModel to return our mock
    with patch('google.generativeai.GenerativeModel', return_value=MockGenerativeModel()):
        # Generate slides
        presentation = await generate_slides(research, target_slides=5)
        
        # Verify that Welcome and Section slides were added
        assert len(presentation.slides) >= 4  # Should include Welcome, TOC, Section, and original Content slides
        
        # Check that we have at least one slide of each required type
        slide_types = [slide.type for slide in presentation.slides]
        assert "Welcome" in slide_types
        assert "TableOfContents" in slide_types
        assert "Section" in slide_types
        assert "Content" in slide_types

@pytest.mark.asyncio
async def test_3images_conversion():
    """Test that 3Images with 'images' array is properly converted to the required format"""
    
    # Mock research data
    research = ResearchData(content="This is test research content")
    
    # Mock the Gemini API response with a 3Images slide using an 'images' array
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "title": "Test Presentation",
        "author": "Test Author",
        "slides": [
            {
                "type": "Welcome",
                "fields": {
                    "title": "Welcome Slide",
                    "subtitle": "Test Presentation",
                    "author": "Test Author"
                }
            },
            {
                "type": "3Images",
                "fields": {
                    "title": "3 Images Slide",
                    "images": [
                        {
                            "image": "image1.jpg",
                            "subtitle": "Image 1 Caption"
                        },
                        {
                            "image": "image2.jpg",
                            "subtitle": "Image 2 Caption"
                        },
                        {
                            "image": "image3.jpg",
                            "subtitle": "Image 3 Caption"
                        }
                    ]
                }
            }
        ]
    })
    
    # Create a simple mock class that returns our response
    class MockGenerativeModel:
        async def generate_content_async(self, *args, **kwargs):
            return mock_response
    
    # Patch the genai.GenerativeModel to return our mock
    with patch('google.generativeai.GenerativeModel', return_value=MockGenerativeModel()):
        # Generate slides
        presentation = await generate_slides(research, target_slides=5)
        
        # Find the 3Images slide
        three_images_slide = None
        for slide in presentation.slides:
            if slide.type == "3Images":
                three_images_slide = slide
                break
        
        # Verify that the 3Images slide was properly converted
        assert three_images_slide is not None
        assert "image1" in three_images_slide.fields
        assert "image2" in three_images_slide.fields
        assert "image3" in three_images_slide.fields
        assert "image1subtitle" in three_images_slide.fields
        assert "image2subtitle" in three_images_slide.fields
        assert "image3subtitle" in three_images_slide.fields
        assert three_images_slide.fields["image1"] == "image1.jpg"
        assert three_images_slide.fields["image2"] == "image2.jpg"
        assert three_images_slide.fields["image3"] == "image3.jpg"
        assert three_images_slide.fields["image1subtitle"] == "Image 1 Caption"
        assert three_images_slide.fields["image2subtitle"] == "Image 2 Caption"
        assert three_images_slide.fields["image3subtitle"] == "Image 3 Caption"

if __name__ == "__main__":
    unittest.main() 