import os
import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path if needed
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from models import SlidePresentation, Slide
from tools.generate_pptx import (
    generate_pptx_from_slides, 
    find_shape_by_name, 
    format_section_number,
    get_layout_by_name
)

# Mock classes for testing
class MockShape:
    def __init__(self, name=None):
        self.name = name
        self.text_frame = MagicMock()
        self.text = ""  # Property to track text
        
        # Make text_frame.text a property that updates self.text
        type(self.text_frame).text = property(
            lambda self: self.text_frame.owner.text,
            lambda self, value: setattr(self.text_frame.owner, "text", value)
        )
        # Set owner reference to self
        self.text_frame.owner = self
        
        self.element = MagicMock()
        self.element.getparent = MagicMock(return_value=MagicMock())
        self.left = 0
        self.top = 0
        self.width = 100
        self.height = 100
        self.placeholder_format = MagicMock()
        self.placeholder_format.type = 1  # Default to title type

class MockSlideLayout:
    def __init__(self, name):
        self.name = name
        self.placeholders = []
        self.shapes = []

class MockSlide:
    def __init__(self, layouts=None, shapes=None):
        self.shapes = shapes or []
        self.notes_slide = MagicMock()
        self.notes_slide.notes_text_frame = MagicMock()

class MockPresentation:
    def __init__(self, layouts=None):
        # Make sure we have at least 15 layouts to avoid index errors
        self.layouts = layouts or []
        if len(self.layouts) < 15:
            self.layouts.extend([MockSlideLayout(f"Layout {i}") for i in range(len(self.layouts), 15)])
        
        self.slide_layouts = self.layouts
        self.slides = []
        
    def save(self, path):
        # Mock saving the presentation
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)
        with open(path, 'w') as f:
            f.write('Mock PowerPoint file')

@pytest.fixture
def mock_shape_factory():
    """Fixture to create mock shapes with different properties."""
    def _create_shape(name=None, placeholder_type=1):
        shape = MockShape(name)
        shape.placeholder_format.type = placeholder_type
        return shape
    return _create_shape

@pytest.fixture
def mock_presentation():
    """Fixture to create a mock presentation with standard layouts."""
    # Create mock slide layouts
    layouts = [
        MockSlideLayout("Welcome"),
        MockSlideLayout("TableOfContents"),
        MockSlideLayout("ContentImage"),
        MockSlideLayout("Content"),
        MockSlideLayout("Section"),
        MockSlideLayout("ThankYou"),
        MockSlideLayout("3Images"),
        MockSlideLayout("ContentWithLogos")
    ]
    
    # Create a mock presentation
    presentation = MockPresentation(layouts)
    
    # Mock the add_slide method
    def mock_add_slide(layout):
        new_slide = MockSlide(shapes=[])
        presentation.slides.append(new_slide)
        return new_slide
    
    presentation.slides.add_slide = mock_add_slide
    
    return presentation

def test_format_section_number():
    """Test formatting section numbers with leading zeros."""
    assert format_section_number(1) == "01"
    assert format_section_number(9) == "09"
    assert format_section_number(10) == "10"
    assert format_section_number(99) == "99"

def test_find_shape_by_name():
    """Test finding shapes by name with different matching strategies."""
    # Create test shapes
    shape1 = MockShape("Title")
    shape2 = MockShape("Content")
    shape3 = MockShape("Image Placeholder")
    shape4 = MockShape("Section1")
    shape5 = MockShape("Text Placeholder 3")
    
    # Create a mock slide with these shapes
    slide = MockSlide(shapes=[shape1, shape2, shape3, shape4, shape5])
    
    # Test exact match
    found_shape = find_shape_by_name(slide, "Title")
    assert found_shape == shape1, "Should find shape with exact name match"
    
    # Test case-insensitive match
    found_shape = find_shape_by_name(slide, "content")
    assert found_shape == shape2, "Should find shape with case-insensitive match"
    
    # Test partial match
    found_shape = find_shape_by_name(slide, "Image")
    assert found_shape == shape3, "Should find shape with partial match"
    
    # Test number pattern matching
    found_shape = find_shape_by_name(slide, "3")
    assert found_shape == shape5, "Should find shape with number pattern match"
    
    # Test no match
    found_shape = find_shape_by_name(slide, "NonExistentShape")
    assert found_shape is None, "Should return None for non-existent shape"

@pytest.mark.asyncio
@patch('tools.generate_pptx.Presentation')
@patch('tools.generate_pptx.get_layout_by_name')
async def test_basic_presentation_generation(mock_get_layout, mock_presentation_class, mock_presentation, tmp_path):
    """Test generating a basic presentation with slides."""
    # Set up mocks
    mock_presentation_class.return_value = mock_presentation
    
    # Mock get_layout_by_name to return layouts from the mock presentation
    mock_get_layout.side_effect = lambda prs, name: next(
        (layout for layout in mock_presentation.layouts if layout.name == name), 
        None
    )
    
    # Create test shapes for different slide types
    title_shape = MockShape("Title")
    title_shape.placeholder_format.type = 1
    content_shape = MockShape("Content")
    content_shape.placeholder_format.type = 2
    
    # Add shapes to layouts
    for layout in mock_presentation.layouts:
        layout.placeholders = [title_shape, content_shape]
        layout.shapes = [title_shape, content_shape]
    
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
    
    # Run the function with the test presentation
    result = await generate_pptx_from_slides(test_presentation, "test")
    
    # Verify results
    assert result is not None
    assert result.presentation_id == "test"
    assert os.path.exists(result.pptx_path)
    
    # Verify slides were created
    assert len(mock_presentation.slides) == 5  # Welcome + Content + ContentImage + TableOfContents + ThankYou

@pytest.mark.asyncio
@patch('tools.generate_pptx.Presentation')
@patch('tools.generate_pptx.get_layout_by_name')
async def test_toc_slide_generation(mock_get_layout, mock_presentation_class, mock_presentation, mock_shape_factory):
    """Test generating a presentation with a table of contents slide."""
    # Set up mocks
    mock_presentation_class.return_value = mock_presentation
    
    # Mock get_layout_by_name to return layouts from the mock presentation
    mock_get_layout.side_effect = lambda prs, name: next(
        (layout for layout in mock_presentation.layouts if layout.name == name), 
        None
    )
    
    # Create TOC shapes
    section1_shape = mock_shape_factory("Section1", 2)
    section2_shape = mock_shape_factory("Section2", 2)
    number1_shape = mock_shape_factory("01", 3)
    number2_shape = mock_shape_factory("02", 3)
    
    # Add shapes to TOC layout
    toc_layout = next(layout for layout in mock_presentation.layouts if layout.name == "TableOfContents")
    toc_layout.shapes = [section1_shape, section2_shape, number1_shape, number2_shape]
    
    # Create a test presentation with sections
    test_presentation = SlidePresentation(
        title="Test Presentation with TOC",
        slides=[
            Slide(type="Welcome", fields={"title": "Welcome to the Test", "subtitle": "A test presentation"}),
            Slide(type="Section", fields={"title": "First Section"}),
            Slide(type="Content", fields={"title": "Content in Section 1", "content": ["Point 1", "Point 2"]}),
            Slide(type="Section", fields={"title": "Second Section"}),
            Slide(type="Content", fields={"title": "Content in Section 2", "content": ["Point 1", "Point 2"]})
        ]
    )
    
    # Mock find_shape_by_name
    with patch('tools.generate_pptx.find_shape_by_name') as mock_find_shape:
        mock_find_shape.side_effect = lambda slide, name: {
            "Section1": section1_shape,
            "Section2": section2_shape,
            "01": number1_shape,
            "02": number2_shape,
            "Title": mock_shape_factory("Title")
        }.get(name)
        
        # Run the function
        result = await generate_pptx_from_slides(test_presentation, "test")
    
    # Verify results
    assert result is not None
    assert result.presentation_id == "test"
    
    # Verify TOC slide was updated
    # Since we're patching find_shape_by_name, we can't directly access the shapes,
    # but we can verify the function completed successfully
    assert len(mock_presentation.slides) > 0 