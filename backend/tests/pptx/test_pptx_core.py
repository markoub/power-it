import os
import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
from pptx import Presentation as PptxPresentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# Add parent directory to path if needed
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from models import SlidePresentation, Slide
from tools.generate_pptx import (
    generate_pptx_from_slides, 
    find_shape_by_name, 
    format_section_number,
    get_layout_by_name
)

def test_format_section_number():
    """Test formatting section numbers with leading zeros."""
    assert format_section_number(1) == "01"
    assert format_section_number(9) == "09"
    assert format_section_number(10) == "10"
    assert format_section_number(99) == "99"

@pytest.fixture
def real_presentation():
    """Create a real presentation for testing."""
    # Create a new presentation using python-pptx
    presentation = PptxPresentation()
    
    # Add slide layouts with names we use in the application
    # We'll set titles to match our needed layouts
    layouts = []
    
    # Add some slides to test with
    for layout_name in ["Welcome", "TableOfContents", "ContentImage", "Content", 
                        "Section", "ThankYou", "3Images", "ContentWithLogos"]:
        # Get the default layout
        layout = presentation.slide_layouts[0]
        # Add a slide using this layout
        slide = presentation.slides.add_slide(layout)
        
        # Add a title shape to identify the slide
        title_shape = slide.shapes.title
        if title_shape:
            title_shape.text = layout_name
        
        # Store the reference
        layouts.append((layout_name, layout))
    
    return presentation

def test_find_shape_by_name():
    """Test finding shapes by name with different matching strategies."""
    # Create a real slide
    prs = PptxPresentation()
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    
    # Get the title shape
    title_shape = slide.shapes.title
    title_shape.name = "Title"
    
    # Add some other shapes
    content_shape = slide.shapes.add_textbox(0, 0, 100, 100)
    content_shape.name = "Content"
    
    image_shape = slide.shapes.add_textbox(0, 0, 100, 100)
    image_shape.name = "Image Placeholder"
    
    section_shape = slide.shapes.add_textbox(0, 0, 100, 100)
    section_shape.name = "Section1"
    
    number_shape = slide.shapes.add_textbox(0, 0, 100, 100)
    number_shape.name = "Text Placeholder 3"
    
    # Test exact match
    found_shape = find_shape_by_name(slide, "Title")
    assert found_shape.name == "Title", "Should find shape with exact name match"
    
    # Test case-insensitive match
    found_shape = find_shape_by_name(slide, "content")
    assert found_shape.name == "Content", "Should find shape with case-insensitive match"
    
    # Test partial match
    found_shape = find_shape_by_name(slide, "Image")
    assert found_shape.name == "Image Placeholder", "Should find shape with partial match"
    
    # Test number pattern matching
    found_shape = find_shape_by_name(slide, "3")
    assert found_shape.name == "Text Placeholder 3", "Should find shape with number pattern match"
    
    # Test no match
    found_shape = find_shape_by_name(slide, "NonExistentShape")
    assert found_shape is None, "Should return None for non-existent shape"

@pytest.mark.asyncio
async def test_basic_presentation_generation(tmp_path):
    """Test generating a basic presentation with slides using a real presentation object."""
    # Create a test presentation
    test_presentation = SlidePresentation(
        title="Test Presentation",
        slides=[
            Slide(type="Welcome", fields={"title": "Welcome to the Test", "subtitle": "A test presentation"}),
            Slide(type="Content", fields={"title": "Content Slide", "content": ["Point 1", "Point 2"]}),
            Slide(type="ContentImage", fields={"title": "Image Slide", "content": ["Image Content"], "image": "image.png"})
        ]
    )
    
    # Create output directory
    output_dir = tmp_path / "presentations" / "test"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Patch content_slide function to avoid requiring real images
    with patch('tools.pptx_slides.create_content_slide') as mock_content_slide:
        # Set up the mock to do the actual function work but ignore image
        mock_content_slide.side_effect = lambda prs, layout, title, content, add_image=False, image_path=None: \
            create_content_slide_without_image(prs, layout, title, content)
        
        # Run the function with the test presentation
        result = await generate_pptx_from_slides(test_presentation, "test")
    
    # Verify results
    assert result is not None
    assert result.presentation_id == "test"
    assert os.path.exists(result.pptx_path)
    
    # Verify the file was created with some content
    assert os.path.getsize(result.pptx_path) > 0, "PPTX file should have content"
    
    # Load the generated presentation to verify structure
    generated_pptx = PptxPresentation(result.pptx_path)
    
    # A basic presentation without sections should have:
    # - Welcome slide
    # - Content slide
    # - ContentImage slide
    # - ThankYou slide
    # No table of contents since there are no sections
    assert len(generated_pptx.slides) >= 4, "Should have at least 4 slides"

# Helper function for testing
def create_content_slide_without_image(prs, layout, title, content):
    """Create a content slide without an image for testing."""
    slide = prs.slides.add_slide(layout)
    
    # Add title
    title_shape = slide.shapes.title
    if title_shape:
        title_shape.text = title
    
    # Add content placeholder
    content_shape = None
    for shape in slide.placeholders:
        if shape.placeholder_format.type == 2:  # Body
            content_shape = shape
            break
    
    if content_shape:
        content_text = "\n".join([f"• {item}" for item in content])
        content_shape.text = content_text
    
    return slide