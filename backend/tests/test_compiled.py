import pytest
import os
import sys
from typing import List, Dict, Any
import asyncio

# Add parent directory to path to import modules properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import SlidePresentation, Slide, ImageGeneration, CompiledPresentation
from tools.compiled import generate_compiled_presentation

@pytest.mark.asyncio
async def test_generate_compiled_presentation():
    """Test that compiled presentation handles slides with fields correctly"""
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
            image_path="/path/to/image1.png"
        ),
        ImageGeneration(
            slide_index=1,
            slide_title="Content Slide",
            prompt="Create content image",
            image_path="/path/to/image2.png"
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
    assert compiled.slides[0].image_url == "/presentations/1/images/image1.png"
    
    # Check second slide
    assert compiled.slides[1].type == "content"
    assert compiled.slides[1].fields["title"] == "Content Slide"
    assert compiled.slides[1].fields["content"] == "This is the main content"
    assert compiled.slides[1].image_url == "/presentations/1/images/image2.png"

@pytest.mark.asyncio
async def test_generate_compiled_presentation_legacy():
    """Test backward compatibility with old slide structure"""
    # Create a presentation with legacy structure (without fields)
    # This test simulates the case we're trying to fix
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
        def __init__(self, title, slides):
            self.title = title
            self.slides = slides
    
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
            image_path="/path/to/legacy_image1.png"
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
    assert compiled.slides[0].fields == {}  # Should have empty fields
    assert compiled.slides[0].image_url == "/presentations/2/images/legacy_image1.png" 