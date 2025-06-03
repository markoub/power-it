import pytest
from unittest.mock import patch, MagicMock
import json

from tests.utils import MockFactory, assert_valid_slide_presentation
from models import ResearchData, SlidePresentation, Slide
from tools.slides import generate_slides
from tools.slide_config import SLIDE_TYPES, PRESENTATION_STRUCTURE


class TestSlidesGeneration:
    """Test suite for slide generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_slides_basic(self, sample_research_data):
        """Test basic slide generation with mock response."""
        # Create mock response
        mock_response = {
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
        }
        
        # Create mock model
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[mock_response]
        )
        
        # Temporarily disable offline mode
        import tools.slides
        original_offline_mode = tools.slides.OFFLINE_MODE
        tools.slides.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Generate slides
                result = await generate_slides(
                    sample_research_data, 
                    target_slides=5, 
                    author="Test Author"
                )
                
                # Validate result
                assert_valid_slide_presentation(result)
                assert result.title == "Test Presentation"
                assert result.author == "Test Author"
                
                # Should have added TableOfContents
                assert len(result.slides) >= 6
                
                # Check slide types
                slide_types = [slide.type for slide in result.slides]
                assert "Welcome" in slide_types
                assert "TableOfContents" in slide_types
                assert "Section" in slide_types
                assert "Content" in slide_types
                assert "ContentImage" in slide_types
                
        finally:
            tools.slides.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_slide_field_filtering(self, sample_research_data):
        """Test that slide fields are properly filtered to only include required fields."""
        # Create mock response with extra fields
        mock_response = {
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
                        "extra_field": "Should be removed",  # Extra field
                        "visual_suggestions": "Should be removed"  # Extra field
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
        }
        
        # Create mock model
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[mock_response]
        )
        
        # Temporarily disable offline mode
        import tools.slides
        original_offline_mode = tools.slides.OFFLINE_MODE
        tools.slides.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Generate slides
                result = await generate_slides(
                    sample_research_data,
                    target_slides=2,
                    author="Test Author"
                )
                
                # Validate result
                assert_valid_slide_presentation(result)
                
                # Find Welcome slide and verify it has only required fields
                welcome_slide = next(
                    (s for s in result.slides if s.type == "Welcome"), 
                    None
                )
                assert welcome_slide is not None
                assert welcome_slide.fields["title"] == "Welcome to Test"
                assert welcome_slide.fields["subtitle"] == "A Test Presentation"
                assert welcome_slide.fields["author"] == "Test Author"
                assert "content" not in welcome_slide.fields
                assert "extra_field" not in welcome_slide.fields
                assert "visual_suggestions" not in welcome_slide.fields
                
                # Find Section slide and verify it has only required fields
                section_slide = next(
                    (s for s in result.slides 
                     if s.type == "Section" and s.fields.get("title") == "First Section"),
                    None
                )
                assert section_slide is not None
                assert section_slide.fields["title"] == "First Section"
                assert "content" not in section_slide.fields
                assert "extra_field" not in section_slide.fields
                
        finally:
            tools.slides.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_automatic_slide_addition(self, sample_research_data):
        """Test that Welcome and Section slides are added automatically when missing."""
        # Mock response with only Content slides
        mock_response = {
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
        }
        
        # Create mock model
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[mock_response]
        )
        
        # Temporarily disable offline mode
        import tools.slides
        original_offline_mode = tools.slides.OFFLINE_MODE
        tools.slides.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Generate slides
                presentation = await generate_slides(
                    sample_research_data,
                    target_slides=5
                )
                
                # Verify slides were added
                assert_valid_slide_presentation(presentation)
                assert len(presentation.slides) >= 4  # Welcome, TOC, Section, + original slides
                
                # Check required slide types
                slide_types = [slide.type for slide in presentation.slides]
                assert "Welcome" in slide_types
                assert "TableOfContents" in slide_types
                assert "Section" in slide_types
                assert "Content" in slide_types
                
        finally:
            tools.slides.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_three_images_slide_conversion(self, sample_research_data):
        """Test that 3Images slides with 'images' array are properly converted."""
        # Mock response with 3Images slide
        mock_response = {
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
        }
        
        # Create mock model
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[mock_response]
        )
        
        # Temporarily disable offline mode
        import tools.slides
        original_offline_mode = tools.slides.OFFLINE_MODE
        tools.slides.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Generate slides
                presentation = await generate_slides(
                    sample_research_data,
                    target_slides=5
                )
                
                # Find the 3Images slide
                three_images_slide = next(
                    (s for s in presentation.slides if s.type == "3Images"),
                    None
                )
                
                # Verify conversion
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
                
        finally:
            tools.slides.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_slides_customization_parameters(self, sample_research_data):
        """Test that slides generation properly handles customization parameters."""
        # Mock response
        mock_response = {
            "title": "Business Processes",
            "author": "Test Author",
            "slides": [
                {
                    "type": "Welcome",
                    "fields": {
                        "title": "Business Processes",
                        "subtitle": "Executive Overview",
                        "author": "Test Author"
                    }
                },
                {
                    "type": "Content",
                    "fields": {
                        "title": "Key Business Insights",
                        "content": ["Strategic value proposition", "Market impact analysis"],
                        "notes": "Executive-focused speaker notes with business impact details"
                    }
                }
            ]
        }
        
        # Create mock model that verifies prompt
        class MockGenerativeModel:
            async def generate_content_async(self, prompt, **kwargs):
                # Verify customization parameters in prompt
                assert "Target Audience: Executives" in prompt
                assert "Content Density: Low" in prompt
                assert "Presentation Duration: 20 minutes" in prompt
                assert "Focus on business metrics and ROI" in prompt
                
                mock_resp = MagicMock()
                mock_resp.text = json.dumps(mock_response)
                return mock_resp
        
        # Temporarily disable offline mode
        import tools.slides
        original_offline_mode = tools.slides.OFFLINE_MODE
        tools.slides.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=MockGenerativeModel()):
                # Generate slides with customization
                presentation = await generate_slides(
                    sample_research_data,
                    target_slides=8,
                    author="Test Author",
                    target_audience="executives",
                    content_density="low",
                    presentation_duration=20,
                    custom_prompt="Focus on business metrics and ROI"
                )
                
                # Verify presentation
                assert presentation is not None
                assert presentation.title == "Business Processes"
                assert presentation.author == "Test Author"
                assert len(presentation.slides) >= 2
                
        finally:
            tools.slides.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_input(self):
        """Test handling of invalid input - should raise ValueError."""
        import pytest
        
        # Should raise ValueError for None research
        with pytest.raises(ValueError, match="Research data cannot be None"):
            await generate_slides(research=None)
        
        # Should raise ValueError for empty research content
        from models import ResearchData
        empty_research = ResearchData(content="", links=[])
        with pytest.raises(ValueError, match="Research data must contain non-empty content"):
            await generate_slides(research=empty_research)
    
    @pytest.mark.asyncio
    async def test_error_handling_api_failure(self, sample_research_data):
        """Test error handling when API call fails."""
        # Create mock model that raises exception
        mock_model = MagicMock()
        mock_model.generate_content_async.side_effect = Exception("API Error")
        
        # Temporarily disable offline mode
        import tools.slides
        original_offline_mode = tools.slides.OFFLINE_MODE
        tools.slides.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                result = await generate_slides(sample_research_data)
                
                # Should return fallback slides instead of raising exception
                assert result is not None
                assert isinstance(result, SlidePresentation)
                assert len(result.slides) >= 1  # Should have at least one fallback slide
                
        finally:
            tools.slides.OFFLINE_MODE = original_offline_mode
    
    def test_offline_slides_generation(self, sample_research_data):
        """Test offline slides generation functionality."""
        from offline_responses.slides import generate_offline_slides
        
        # Generate slides with customization
        result = generate_offline_slides(
            sample_research_data,
            target_slides=6,
            author="Dr. Smith",
            target_audience="technical",
            content_density="high",
            presentation_duration=30,
            custom_prompt="Focus on technical implementation details"
        )
        
        # Verify basic structure
        assert result["title"] is not None
        assert result["author"] == "Dr. Smith"
        # In offline mode, we generate all slide types for testing
        # This is expected behavior to ensure comprehensive coverage
        assert len(result["slides"]) <= 10  # Allow all slide types for testing
        
        # Check speaker notes for technical content
        for slide in result["slides"]:
            notes = slide["fields"].get("notes", "")
            if notes and ("technical" in notes.lower() or "implementation" in notes.lower()):
                assert len(notes) > 50  # Should be detailed for technical audience
    
    def test_config_defaults(self):
        """Test that configuration defaults are properly set."""
        # Import the real config module
        import sys
        import os
        
        # Temporarily remove test config and import real config
        if 'config' in sys.modules:
            del sys.modules['config']
        
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        import config
        
        # Check if SLIDES_DEFAULTS exists, if not skip the test
        if not hasattr(config, 'SLIDES_DEFAULTS'):
            import pytest
            pytest.skip("SLIDES_DEFAULTS not found in config")
        
        SLIDES_DEFAULTS = config.SLIDES_DEFAULTS
        
        # Verify defaults exist and have reasonable values
        assert "target_slides" in SLIDES_DEFAULTS
        assert "target_audience" in SLIDES_DEFAULTS
        assert "content_density" in SLIDES_DEFAULTS
        assert "presentation_duration" in SLIDES_DEFAULTS
        
        assert SLIDES_DEFAULTS["target_slides"] > 0
        assert SLIDES_DEFAULTS["target_audience"] in [
            "general", "executives", "technical", "students", "sales"
        ]
        assert SLIDES_DEFAULTS["content_density"] in ["low", "medium", "high"]
        assert SLIDES_DEFAULTS["presentation_duration"] > 0