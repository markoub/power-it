import os
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
from pptx import Presentation as PptxPresentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from models import SlidePresentation, Slide
from tools.generate_pptx import (
    generate_pptx_from_slides, 
    find_shape_by_name, 
    format_section_number,
    get_layout_by_name
)
from tests.utils import MockFactory, assert_file_exists_and_valid

class TestPPTXCore:
    """Test core PPTX functionality."""
    
    def test_format_section_number_core_functionality(self):
        """Test core section number formatting."""
        # Note: Basic tests are in test_pptx_utils.py
        # Here we test integration with PPTX generation
        assert format_section_number(1) == "01"
        assert format_section_number(50) == "50"

    @pytest.fixture
    def real_presentation(self):
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

    def test_find_shape_by_name_with_real_presentation(self):
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
    
    def test_find_shape_by_name_with_mocks(self):
        """Test find_shape_by_name using mock objects."""
        # Create mock shapes
        title_shape = MockFactory.create_mock_shape(name="Title", text="Test Title")
        content_shape = MockFactory.create_mock_shape(name="Content", text="Test Content")
        image_shape = MockFactory.create_mock_shape(name="Image Placeholder")
        
        # Create mock slide with shapes
        slide = MockFactory.create_mock_slide(shapes=[title_shape, content_shape, image_shape])
        
        # Test exact match
        found = find_shape_by_name(slide, "Title")
        assert found == title_shape
        
        # Test partial match
        found = find_shape_by_name(slide, "Image")
        assert found == image_shape
        
        # Test no match
        found = find_shape_by_name(slide, "NotFound")
        assert found is None

    @pytest.mark.asyncio
    async def test_basic_presentation_generation(self, tmp_path):
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
        assert_file_exists_and_valid(result.pptx_path, min_size=10000, extensions=[".pptx"])
        
        # Load the generated presentation to verify structure
        generated_pptx = PptxPresentation(result.pptx_path)
        
        # A basic presentation without sections should have:
        # - Welcome slide
        # - Content slide
        # - ContentImage slide
        # - ThankYou slide
        # No table of contents since there are no sections
        assert len(generated_pptx.slides) >= 4, "Should have at least 4 slides"
    
    @pytest.mark.asyncio
    async def test_presentation_generation_with_sections(self, tmp_path):
        """Test generating presentation with sections and TOC."""
        test_presentation = SlidePresentation(
            title="Test with Sections",
            slides=[
                Slide(type="Section", fields={"title": "Introduction"}),
                Slide(type="Content", fields={"title": "Intro Content", "content": ["Point 1"]}),
                Slide(type="Section", fields={"title": "Main Topic"}),
                Slide(type="Content", fields={"title": "Main Content", "content": ["Point 2"]}),
            ]
        )
        
        output_dir = tmp_path / "presentations" / "test_sections"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result = await generate_pptx_from_slides(test_presentation, "test_sections")
        
        assert result is not None
        assert_file_exists_and_valid(result.pptx_path, min_size=10000)
        
        # Should have more slides due to TOC
        generated_pptx = PptxPresentation(result.pptx_path)
        assert len(generated_pptx.slides) >= 6  # Welcome, TOC, 2 sections, 2 content, ThankYou
    
    def test_get_layout_by_name_error_handling(self):
        """Test error handling in get_layout_by_name."""
        mock_prs = MockFactory.create_mock_presentation()
        
        # Test with non-existent layout
        layout = get_layout_by_name(mock_prs, "NonExistentLayout")
        assert layout is None


# Helper function for testing (kept outside class for backward compatibility)
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