"""Tests for compiled presentation functionality."""

import pytest
from typing import List

from tests.utils import MockFactory, assert_valid_slide_presentation
from models import SlidePresentation, Slide, ImageGeneration, CompiledPresentation
from tools.compiled import generate_compiled_presentation


class TestCompiledPresentation:
    """Test suite for compiled presentation generation."""
    
    @pytest.mark.asyncio
    async def test_generate_compiled_presentation_basic(self):
        """Test that compiled presentation handles slides with fields correctly."""
        # Create test presentation with slides using the fields structure
        slides = [
            Slide(
                type="welcome",
                fields={
                    "title": "Welcome Slide",
                    "content": ["Welcome to the presentation", "Today we will discuss..."]
                }
            ),
            Slide(
                type="content",
                fields={
                    "title": "Content Slide",
                    "content": "This is the main content"
                }
            )
        ]
        
        presentation = SlidePresentation(
            title="Test Presentation",
            slides=slides
        )
        
        # Create test images
        images = [
            ImageGeneration(
                slide_index=0,
                slide_title="Welcome Slide",
                prompt="Create welcome image",
                image_field_name="image",
                image_path="/path/to/welcome_slide_123.png"
            ),
            ImageGeneration(
                slide_index=1,
                slide_title="Content Slide",
                prompt="Create content image",
                image_field_name="image",
                image_path="/path/to/content_slide_456.png"
            )
        ]
        
        # Generate compiled presentation
        compiled = await generate_compiled_presentation(presentation, images, 1)
        
        # Verify the results
        assert isinstance(compiled, CompiledPresentation)
        assert compiled.title == "Test Presentation"
        assert len(compiled.slides) == 2
        
        # Check first slide
        assert compiled.slides[0].type == "welcome"
        assert compiled.slides[0].fields["title"] == "Welcome Slide"
        assert compiled.slides[0].fields["content"] == ["Welcome to the presentation", "Today we will discuss..."]
        assert compiled.slides[0].fields.get("image_url") == "/presentations/1/images/welcome_slide_123.png"
        assert compiled.slides[0].image_url == "/presentations/1/images/welcome_slide_123.png"
        
        # Check second slide
        assert compiled.slides[1].type == "content"
        assert compiled.slides[1].fields["title"] == "Content Slide"
        assert compiled.slides[1].fields["content"] == "This is the main content"
        assert compiled.slides[1].fields.get("image_url") == "/presentations/1/images/content_slide_456.png"
        assert compiled.slides[1].image_url == "/presentations/1/images/content_slide_456.png"
    
    @pytest.mark.asyncio
    async def test_generate_compiled_presentation_no_images(self):
        """Test compiled presentation without images."""
        # Create test presentation
        slides = [
            Slide(
                type="section",
                fields={
                    "title": "Introduction"
                }
            ),
            Slide(
                type="content",
                fields={
                    "title": "Overview",
                    "content": ["Point 1", "Point 2", "Point 3"]
                }
            )
        ]
        
        presentation = SlidePresentation(
            title="No Images Presentation",
            author="Test Author",
            slides=slides
        )
        
        # Generate compiled presentation with empty images list
        compiled = await generate_compiled_presentation(presentation, [], 2)
        
        # Verify results
        assert isinstance(compiled, CompiledPresentation)
        assert compiled.title == "No Images Presentation"
        assert compiled.author == "Test Author"
        assert len(compiled.slides) == 2
        
        # Check slides have no image URLs
        for slide in compiled.slides:
            assert slide.image_url is None
            assert "image_url" not in slide.fields
    
    @pytest.mark.asyncio
    async def test_generate_compiled_presentation_partial_images(self):
        """Test compiled presentation with images for only some slides."""
        # Create test presentation
        slides = [
            Slide(
                type="welcome",
                fields={
                    "title": "Welcome",
                    "subtitle": "Test Presentation"
                }
            ),
            Slide(
                type="content",
                fields={
                    "title": "Content with Image",
                    "content": ["This slide has an image"]
                }
            ),
            Slide(
                type="section",
                fields={
                    "title": "Section without Image"
                }
            )
        ]
        
        presentation = SlidePresentation(
            title="Partial Images",
            slides=slides
        )
        
        # Create image only for second slide
        images = [
            ImageGeneration(
                slide_index=1,
                slide_title="Content with Image",
                prompt="Create content image",
                image_field_name="image",
                image_path="/path/to/content_789.png"
            )
        ]
        
        # Generate compiled presentation
        compiled = await generate_compiled_presentation(presentation, images, 3)
        
        # Verify results
        assert len(compiled.slides) == 3
        
        # First slide - no image
        assert compiled.slides[0].image_url is None
        assert "image_url" not in compiled.slides[0].fields
        
        # Second slide - has image
        assert compiled.slides[1].image_url == "/presentations/3/images/content_789.png"
        assert compiled.slides[1].fields["image_url"] == "/presentations/3/images/content_789.png"
        
        # Third slide - no image
        assert compiled.slides[2].image_url is None
        assert "image_url" not in compiled.slides[2].fields
    
    @pytest.mark.asyncio
    async def test_generate_compiled_presentation_legacy_format(self):
        """Test backward compatibility with old slide structure."""
        # Create a presentation with legacy structure (without fields)
        class LegacySlide:
            def __init__(self, title, type, content):
                self.title = title
                self.type = type
                self.content = content
                # These are required by the CompiledSlide constructor
                self.fields = {}
        
        slides = [
            LegacySlide(
                title="Legacy Welcome",
                type="welcome",
                content=["Welcome point 1", "Welcome point 2"]
            ),
            LegacySlide(
                title="Legacy Content",
                type="content",
                content="Legacy content text"
            )
        ]
        
        # Create a presentation object that has the slides attribute
        class LegacyPresentation:
            def __init__(self, title, slides, author=None):
                self.title = title
                self.slides = slides
                self.author = author
        
        presentation = LegacyPresentation(
            title="Legacy Test Presentation",
            slides=slides
        )
        
        # Create test images
        images = [
            ImageGeneration(
                slide_index=0,
                slide_title="Legacy Welcome",
                prompt="Create welcome image",
                image_field_name="image",
                image_path="/path/to/legacy_welcome_789.png"
            )
        ]
        
        # Generate compiled presentation
        compiled = await generate_compiled_presentation(presentation, images, 2)
        
        # Verify the results
        assert isinstance(compiled, CompiledPresentation)
        assert compiled.title == "Legacy Test Presentation"
        assert len(compiled.slides) == 2
        
        # Check first slide
        assert compiled.slides[0].type == "welcome"
        assert compiled.slides[0].fields.get("image_url") == "/presentations/2/images/legacy_welcome_789.png"
        assert compiled.slides[0].image_url == "/presentations/2/images/legacy_welcome_789.png"
    
    @pytest.mark.asyncio
    async def test_generate_compiled_presentation_multiple_images_per_slide(self):
        """Test handling slides with multiple image fields."""
        # Create test presentation with three images slide
        slides = [
            Slide(
                type="three_images",
                fields={
                    "title": "Three Images Gallery",
                    "image1": True,
                    "image1subtitle": "First Image",
                    "image2": True,
                    "image2subtitle": "Second Image",
                    "image3": True,
                    "image3subtitle": "Third Image"
                }
            )
        ]
        
        presentation = SlidePresentation(
            title="Multi-Image Presentation",
            slides=slides
        )
        
        # Create multiple images for the same slide
        images = [
            ImageGeneration(
                slide_index=0,
                slide_title="Three Images Gallery",
                prompt="Create first image",
                image_field_name="image1",
                image_path="/path/to/image1_abc.png"
            ),
            ImageGeneration(
                slide_index=0,
                slide_title="Three Images Gallery",
                prompt="Create second image",
                image_field_name="image2",
                image_path="/path/to/image2_def.png"
            ),
            ImageGeneration(
                slide_index=0,
                slide_title="Three Images Gallery",
                prompt="Create third image",
                image_field_name="image3",
                image_path="/path/to/image3_ghi.png"
            )
        ]
        
        # Generate compiled presentation
        compiled = await generate_compiled_presentation(presentation, images, 4)
        
        # Verify results
        assert len(compiled.slides) == 1
        slide = compiled.slides[0]
        
        # Check all images are added
        assert slide.fields["image1_url"] == "/presentations/4/images/image1_abc.png"
        assert slide.fields["image2_url"] == "/presentations/4/images/image2_def.png"
        assert slide.fields["image3_url"] == "/presentations/4/images/image3_ghi.png"
        
        # Main image_url should be the first image
        assert slide.image_url == "/presentations/4/images/image1_abc.png"
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_presentation(self):
        """Test error handling with invalid presentation data."""
        # Test with None presentation
        with pytest.raises(AttributeError):
            await generate_compiled_presentation(None, [], 1)
        
        # Test with presentation without slides
        class InvalidPresentation:
            def __init__(self):
                self.title = "Invalid"
                # Missing slides attribute
        
        with pytest.raises(AttributeError):
            await generate_compiled_presentation(InvalidPresentation(), [], 1)
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_images(self):
        """Test error handling with invalid image data."""
        # Create valid presentation
        presentation = SlidePresentation(
            title="Test",
            slides=[
                Slide(type="welcome", fields={"title": "Welcome"})
            ]
        )
        
        # Test with None images
        compiled = await generate_compiled_presentation(presentation, None, 1)
        assert len(compiled.slides) == 1
        assert compiled.slides[0].image_url is None
        
        # Test with invalid image object
        invalid_images = [{"not": "an_image_generation_object"}]
        with pytest.raises(AttributeError):
            await generate_compiled_presentation(presentation, invalid_images, 1)