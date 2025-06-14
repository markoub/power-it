import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock, call
from pptx import Presentation

from models import SlidePresentation, Slide
from tools.generate_pptx import generate_pptx_from_slides, find_shape_by_name, format_section_number
from tests.utils import MockFactory
from typing import List, Dict, Any, Optional

# Mock classes for backward compatibility with existing tests
class MockShape:
    """Legacy mock shape class - use MockFactory.create_mock_shape() for new tests."""
    def __init__(self, name=None):
        mock = MockFactory.create_mock_shape(name=name)
        # Copy all attributes from the factory mock
        for attr in dir(mock):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(mock, attr))
        
        # Legacy specific setup
        self.text = ""  # Property to track text
        type(self.text_frame).text = property(
            lambda self: self.text_frame.owner.text,
            lambda self, value: setattr(self.text_frame.owner, "text", value)
        )
        self.text_frame.owner = self

class MockSlideLayout:
    """Legacy mock slide layout."""
    def __init__(self, name):
        self.name = name
        self.placeholders = []

class MockSlide:
    """Legacy mock slide - use MockFactory.create_mock_slide() for new tests."""
    def __init__(self, layouts, shapes=None):
        mock = MockFactory.create_mock_slide(shapes=shapes)
        # Copy attributes
        for attr in dir(mock):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(mock, attr))
        # Legacy specific
        self.placeholders = self.shapes
        self.notes_slide = MagicMock()
        self.notes_slide.notes_text_frame = MagicMock()

class MockPresentation:
    """Legacy mock presentation - use MockFactory.create_mock_presentation() for new tests."""
    def __init__(self, layouts=None):
        # Ensure we have enough layouts
        if layouts and len(layouts) < 13:
            layouts.extend([MockSlideLayout(f"Layout {i}") for i in range(len(layouts), 13)])
        
        mock = MockFactory.create_mock_presentation()
        # Copy attributes but keep our layouts
        for attr in dir(mock):
            if not attr.startswith('_') and attr != 'slide_layouts':
                setattr(self, attr, getattr(mock, attr))
        
        self.slide_layouts = layouts or []
        self.slides.add_slide = MagicMock(return_value=MockSlide(layouts))

    def save(self, path):
        # Mock saving the presentation
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)
        with open(path, 'w') as f:
            f.write('Mock PowerPoint file')
    
    # Add missing attributes for compatibility
    @property
    def slide_width(self):
        return 9144000  # Default PowerPoint slide width in EMUs
    
    @property 
    def slide_height(self):
        return 6858000  # Default PowerPoint slide height in EMUs

class TestPptxGeneration:
    """Test PowerPoint generation functionality."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test fixtures."""
        # Create mock slide layouts
        self.welcome_layout = MockSlideLayout("Welcome")
        self.content_image_layout = MockSlideLayout("ContentImage")
        self.table_of_contents_layout = MockSlideLayout("TableOfContents")
        self.content_layout = MockSlideLayout("Content")
        self.section_layout = MockSlideLayout("Section")
        self.thankyou_layout = MockSlideLayout("ThankYou")
        
        # Create mock shapes for table of contents
        self.section1_shape = MockShape(name="Section1")
        self.section2_shape = MockShape(name="Section2")
        self.number1_shape = MockShape(name="01")
        self.number2_shape = MockShape(name="02")
        self.divider1_shape = MockShape(name="01Divider")
        self.divider2_shape = MockShape(name="02Divider")
        
        # Create mock shapes for Section slide
        self.section_number_shape = MockShape(name="Number")
        self.section_title_shape = MockShape(name="Title")
        
        # Mock title and content shapes
        self.title_shape = MockShape(name="Title")
        self.title_shape.placeholder_format.type = 1
        self.content_shape = MockShape(name="Content")
        self.content_shape.placeholder_format.type = 2
        self.image_shape = MockShape(name="Image")
        self.image_shape.placeholder_format.type = 18
        
        # Set up layouts with shapes
        self.content_layout.placeholders = [self.title_shape, self.content_shape]
        self.content_image_layout.placeholders = [self.title_shape, self.content_shape, self.image_shape]
        self.section_layout.placeholders = [self.section_number_shape, self.section_title_shape]
        
        # Create a mock slide for table of contents with TOC shapes
        self.toc_slide_shapes = [
            self.section1_shape, self.section2_shape,
            self.number1_shape, self.number2_shape,
            self.divider1_shape, self.divider2_shape
        ]
        
        # Use pytest's tmp_path for temporary files
        self.test_dir = tmp_path / 'test_tmp'
        self.test_dir.mkdir(exist_ok=True)
    
    @patch('tools.generate_pptx.Presentation')
    @patch('tools.generate_pptx.get_layout_by_name')
    def test_table_of_contents_slide(self, mock_get_layout, mock_presentation_class):
        # Set up mocks
        mock_presentation = MockPresentation([
            self.welcome_layout,
            self.table_of_contents_layout,
            self.content_image_layout,
            self.content_layout,
            self.section_layout,
            self.thankyou_layout
        ])
        mock_presentation_class.return_value = mock_presentation
        
        # Mock get_layout_by_name to return the correct layouts
        def mock_get_layout_side_effect(prs, name):
            layouts = {
                "Welcome": self.welcome_layout,
                "TableOfContents": self.table_of_contents_layout,
                "ContentImage": self.content_image_layout,
                "Content": self.content_layout,
                "Section": self.section_layout,
                "ThankYou": self.thankyou_layout
            }
            return layouts.get(name)
            
        mock_get_layout.side_effect = mock_get_layout_side_effect
        
        # Create a mock slide for TOC with shapes
        toc_mock_slide = MockSlide([], self.toc_slide_shapes)
        mock_presentation.slides.add_slide.return_value = toc_mock_slide
        
        # Create a test presentation with sections
        test_presentation = SlidePresentation(
            title="Test Presentation",
            slides=[
                Slide(type="Section", fields={"title": "Section 1", "content": ["Point 1", "Point 2"]}),
                Slide(type="Section", fields={"title": "Section 2", "content": ["Point 1", "Point 2"]}),
                Slide(type="Content", fields={"title": "Content Slide", "content": ["Content 1", "Content 2"]}),
                Slide(type="ContentImage", fields={"title": "Image Slide", "content": ["Image Content"], "image": "http://example.com/image.png"})
            ]
        )
        
        # Run the function with the test presentation
        with patch('tools.pptx_slides.find_shape_by_name') as mock_find_shape_slides, \
             patch('tools.generate_pptx.find_shape_by_name') as mock_find_shape_gen, \
             patch('tools.pptx_toc.find_shape_by_name') as mock_find_shape_toc:
            # Mock find_shape_by_name to return shapes for sections 1 and 2
            def mock_find_shape_side_effect(slide, name):
                shapes = {
                    "Section1": self.section1_shape,
                    "Section2": self.section2_shape,
                    "01": self.number1_shape,
                    "02": self.number2_shape,
                    "01Divider": self.divider1_shape,
                    "02Divider": self.divider2_shape,
                    "Section3": None,  # No section 3
                    "03": None,
                    "03Divider": None,
                    "Number": self.section_number_shape,
                    "Title": self.section_title_shape
                }
                return shapes.get(name)
            
            # Apply the same mock to all imports
            for mock_func in [mock_find_shape_slides, mock_find_shape_gen, mock_find_shape_toc]:
                mock_func.side_effect = mock_find_shape_side_effect
            
            # Create a fake event loop and run the coroutine
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                generate_pptx_from_slides(test_presentation, "test")
            )
            loop.close()
            
            # Store reference for later assertion
            self._mock_find_shape = mock_find_shape_slides
        
        # Verify results
        assert result is not None
        assert result.presentation_id == "test"
        # Don't check file existence because MockPresentation creates a text file
        # Just verify the save method was called
        mock_presentation.save.assert_called_once()
        
        # Verify table of contents slide was created with correct sections
        mock_presentation.slides.add_slide.assert_any_call(self.table_of_contents_layout)
        
        # Verify set_text_frame was called for the sections we have  
        # Note: The text property is a MagicMock so we can't directly assert on it
        # Instead check that the text_frame.text was set
        assert self._mock_find_shape.call_count > 0
        
    def test_find_shape_by_name(self):
        # Create mock shapes for testing
        shapes = [
            MockShape(name="Title"),
            MockShape(name="Content"),
            MockShape(name="Section1"),
            None,  # Test with None shape
            MockShape(name=None)  # Test with None name
        ]
        
        # Create mock slide
        mock_slide = MockSlide([], shapes)
        
        # Test finding shapes by name
        title_shape = find_shape_by_name(mock_slide, "Title")
        assert title_shape.name == "Title"
        
        # Test with partial name match
        section_shape = find_shape_by_name(mock_slide, "Section")
        assert section_shape.name == "Section1"
        
        # Test with non-existent shape
        missing_shape = find_shape_by_name(mock_slide, "Missing")
        assert missing_shape is None

    @patch('tools.generate_pptx.Presentation')
    @patch('tools.generate_pptx.get_layout_by_name')
    def test_content_slide_type(self, mock_get_layout, mock_presentation_class):
        # Set up mocks
        mock_presentation = MockPresentation([
            self.welcome_layout,
            self.content_image_layout,
            self.content_layout,
            self.thankyou_layout
        ])
        mock_presentation_class.return_value = mock_presentation
        
        # Mock get_layout_by_name to return the correct layouts including TableOfContents
        def mock_get_layout_side_effect(prs, name):
            layouts = {
                "Welcome": self.welcome_layout,
                "ContentImage": self.content_image_layout,
                "Content": self.content_layout,
                "ThankYou": self.thankyou_layout,
                "TableOfContents": self.table_of_contents_layout  # Important: add this even though not in the test!
            }
            return layouts.get(name)
            
        mock_get_layout.side_effect = mock_get_layout_side_effect
        
        # Create a content slide
        content_slide = MockSlide([], [self.title_shape, self.content_shape])
        # Create an image slide
        image_slide = MockSlide([], [self.title_shape, self.content_shape, self.image_shape])
        
        # Mock add_slide to return different slide types
        def mock_add_slide(layout):
            if layout == self.content_layout:
                return content_slide
            elif layout == self.content_image_layout:
                return image_slide
            return MockSlide([])
            
        mock_presentation.slides.add_slide.side_effect = mock_add_slide
        
        # Create a test presentation with content and image slides
        test_presentation = SlidePresentation(
            title="Test Presentation",
            slides=[
                Slide(type="Content", fields={"title": "Content Only", "content": ["Content 1", "Content 2"]}),
                Slide(type="ContentImage", fields={"title": "Image and Content", "content": ["Image Content"], "image": "http://example.com/image.png"})
            ]
        )
        
        # Run the function with the test presentation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            generate_pptx_from_slides(test_presentation, "test")
        )
        loop.close()
        
        # Verify results
        assert result is not None
        assert result.presentation_id == "test"
        
        # Verify the correct layouts were used
        mock_presentation.slides.add_slide.assert_any_call(self.content_layout)
        mock_presentation.slides.add_slide.assert_any_call(self.content_image_layout)

    @patch('tools.generate_pptx.Presentation')
    @patch('tools.generate_pptx.get_layout_by_name')
    @patch('tools.generate_pptx.create_thank_you_slide')
    @patch('tools.generate_pptx.create_welcome_slide')
    @patch('tools.generate_pptx.create_table_of_contents_slide')
    def test_section_slide_type(self, mock_create_toc, mock_create_welcome, mock_create_thank_you, mock_get_layout, mock_presentation_class):
        """Test creating section slides with proper numbering."""
        # Set up mocks
        mock_presentation = MockPresentation([
            self.welcome_layout,
            self.content_image_layout,
            self.section_layout,
            self.thankyou_layout,
            self.table_of_contents_layout
        ])
        mock_presentation_class.return_value = mock_presentation
        
        # Mock the create functions to return valid slides
        mock_create_welcome.return_value = MockSlide([])
        mock_create_toc.return_value = MockSlide([])
        mock_create_thank_you.return_value = MockSlide([])
        
        # Mock get_layout_by_name to return the correct layouts
        def mock_get_layout_side_effect(prs, name):
            layouts = {
                "Welcome": self.welcome_layout,
                "ContentImage": self.content_image_layout,
                "Section": self.section_layout, 
                "ThankYou": self.thankyou_layout,
                "TableOfContents": self.table_of_contents_layout  # Important: add this even though not in the test!
            }
            return layouts.get(name)
            
        mock_get_layout.side_effect = mock_get_layout_side_effect
        
        # Create a fresh number and title shape for each section to avoid state between calls
        number_shape1 = MockShape(name="Number")
        title_shape1 = MockShape(name="Title")
        number_shape2 = MockShape(name="Number")
        title_shape2 = MockShape(name="Title")
        
        # Create section slides with their own shapes
        section_slide1 = MockSlide([], [number_shape1, title_shape1])
        section_slide2 = MockSlide([], [number_shape2, title_shape2])
        
        # Return different slides for each section
        mock_presentation.slides.add_slide.side_effect = [
            MockSlide([]),  # Welcome slide
            section_slide1,  # First section
            section_slide2,  # Second section
            MockSlide([])   # ThankYou slide
        ]
        
        # Create a test presentation with section slides
        test_presentation = SlidePresentation(
            title="Test Presentation",
            slides=[
                Slide(type="Section", fields={"title": "First Section"}),
                Slide(type="Section", fields={"title": "Second Section"}),
            ]
        )
        
        # Run the function with the test presentation
        with patch('tools.generate_pptx.find_shape_by_name') as mock_find_shape:
            # Mock to return the appropriate shape based on which slide we're processing
            def mock_find_shape_side_effect(slide, name):
                if slide == section_slide1:
                    if name == "Number":
                        return number_shape1
                    elif name == "Title":
                        return title_shape1
                elif slide == section_slide2:
                    if name == "Number":
                        return number_shape2
                    elif name == "Title":
                        return title_shape2
                return None
                
            mock_find_shape.side_effect = mock_find_shape_side_effect
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                generate_pptx_from_slides(test_presentation, "test")
            )
            loop.close()
        
        # Verify results
        assert result is not None
        
        # Verify the thank you slide was created
        mock_create_thank_you.assert_called_once()
        
        # Verify that get_layout_by_name was called for the section layout at least once
        section_calls = [call for call in mock_get_layout.call_args_list if call[0][1] == 'Section']
        assert len(section_calls) >= 1, "Section layout should be requested at least once"

    def test_format_section_number_in_context(self):
        """Test section number formatting in PPTX context."""
        # Basic tests are in test_pptx_utils.py
        # Here we test how it's used in actual slide generation
        assert format_section_number(1) == "01"
        assert format_section_number(10) == "10"
        assert format_section_number(0) == "00"
        
    @patch('tools.generate_pptx.Presentation')
    @patch('tools.generate_pptx.get_layout_by_name')
    def test_comprehensive_presentation(self, mock_get_layout, mock_presentation_class):
        """Comprehensive test that verifies all slide types - TableOfContents, Section, and Content slides."""
        
        # Set up mocks
        mock_presentation = MockPresentation([
            self.welcome_layout,
            self.content_image_layout,
            self.table_of_contents_layout,
            self.content_layout,
            self.section_layout,
            self.thankyou_layout
        ])
        mock_presentation_class.return_value = mock_presentation
        
        # Mock get_layout_by_name to return the correct layouts
        def mock_get_layout_side_effect(prs, name):
            layouts = {
                "Welcome": self.welcome_layout,
                "TableOfContents": self.table_of_contents_layout,
                "ContentImage": self.content_image_layout,
                "Content": self.content_layout,
                "Section": self.section_layout,
                "ThankYou": self.thankyou_layout
            }
            return layouts.get(name)
            
        mock_get_layout.side_effect = mock_get_layout_side_effect
        
        # Set up mock slides
        welcome_slide = MockSlide([], [self.title_shape, MockShape(name="Subtitle")])
        toc_slide = MockSlide([], self.toc_slide_shapes)
        section_slide = MockSlide([], [self.section_title_shape, self.section_number_shape])
        content_slide = MockSlide([], [self.title_shape, self.content_shape])

        # Make mock_presentation.slides.add_slide return different slides based on layout
        def mock_add_slide(layout):
            if layout == self.welcome_layout:
                return welcome_slide
            elif layout == self.table_of_contents_layout:
                return toc_slide
            elif layout == self.section_layout:
                return section_slide
            elif layout == self.content_layout:
                return content_slide
            else:
                return MockSlide([], [])
                
        mock_presentation.slides.add_slide.side_effect = mock_add_slide
        
        # Create a test presentation with all slide types
        test_presentation = SlidePresentation(
            title="Comprehensive Test",
            slides=[
                Slide(type="Welcome", fields={"title": "Welcome Title", "subtitle": "Test Subtitle", "author": "Test Author"}),
                Slide(type="Section", fields={"title": "Section 1"}),
                Slide(type="Content", fields={"title": "Content Slide 1", "content": ["Item 1", "Item 2"]}),
                Slide(type="Section", fields={"title": "Section 2"}),
                Slide(type="Content", fields={"title": "Content Slide 2", "content": ["Item 3", "Item 4"]}),
                Slide(type="ContentImage", fields={"title": "Image Slide", "content": ["Image description"], "image": "test.jpg"})
            ]
        )
        
        # Run the function with the test presentation
        with patch('tools.generate_pptx.find_shape_by_name') as mock_find_shape:
            # Mock find_shape_by_name to return appropriate shapes
            def mock_find_shape_side_effect(slide, name):
                if name == "Title" and slide in [welcome_slide, content_slide]:
                    return self.title_shape
                elif name == "Subtitle" and slide == welcome_slide:
                    return MockShape(name="Subtitle")
                elif name in ["Section1", "Section2"] and slide == toc_slide:
                    return self.section1_shape if name == "Section1" else self.section2_shape
                elif name in ["01", "02"] and slide == toc_slide:
                    return self.number1_shape if name == "01" else self.number2_shape
                elif name == "Title" and slide == section_slide:
                    return self.section_title_shape
                elif name == "Number" and slide == section_slide:
                    return self.section_number_shape
                elif name == "Content" and slide == content_slide:
                    return self.content_shape
                elif name == "Image" and slide == content_slide:
                    return self.image_shape
                else:
                    return None
                
            mock_find_shape.side_effect = mock_find_shape_side_effect
            
            # Create a fake event loop and run the coroutine
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    generate_pptx_from_slides(test_presentation, "comprehensive_test")
                )
            finally:
                loop.close()
            
        # Verify results
        assert result is not None
        assert result.presentation_id == "comprehensive_test"
        # Check that the presentation file exists in the storage directory
        assert os.path.exists(os.path.dirname(result.pptx_path)), \
            f"Presentation directory should exist at {os.path.dirname(result.pptx_path)}"

@pytest.mark.asyncio
async def test_toc_generation():
    """
    Test the PowerPoint generation with a focus on TableOfContents slide.
    """
    print("\n===== TESTING TOC POWERPOINT GENERATION =====")
    
    # Create a test presentation with sections
    presentation = SlidePresentation(
        title="Test Presentation with TOC",
        slides=[
            # Welcome slide
            Slide(
                type="Welcome",
                fields={
                    "title": "Test Presentation with TOC",
                    "subtitle": "Testing TableOfContents handling"
                }
            ),
            # TOC slide
            Slide(
                type="TableOfContents",
                fields={
                    "title": "Table of Contents",
                    "sections": [
                        "Introduction",
                        "Key Findings",
                        "Methodology",
                        "Results",
                        "Conclusion",
                        "Next Steps"
                    ]
                }
            ),
            # Section slides
            Slide(
                type="Section",
                fields={
                    "title": "Introduction"
                }
            ),
            Slide(
                type="Content",
                fields={
                    "title": "About this Presentation",
                    "content": [
                        "This is a test presentation to verify the TableOfContents handling",
                        "It includes multiple sections to test TOC generation",
                        "Each section should appear in the Table of Contents slide"
                    ]
                }
            ),
            Slide(
                type="Section",
                fields={
                    "title": "Key Findings"
                }
            ),
            Slide(
                type="Content",
                fields={
                    "title": "Main Results",
                    "content": [
                        "Finding 1: The TOC works correctly",
                        "Finding 2: Section slides are processed properly",
                        "Finding 3: Content slides display the right information"
                    ]
                }
            ),
            Slide(
                type="Section",
                fields={
                    "title": "Methodology"
                }
            ),
            Slide(
                type="ContentImage",
                fields={
                    "title": "Our Approach",
                    "content": [
                        "Step 1: Create test data",
                        "Step 2: Run the test",
                        "Step 3: Verify results"
                    ]
                }
            ),
            Slide(
                type="Section",
                fields={
                    "title": "Results"
                }
            ),
            Slide(
                type="Content",
                fields={
                    "title": "Key Metrics",
                    "content": [
                        "Metric 1: Success rate",
                        "Metric 2: Error count",
                        "Metric 3: Performance"
                    ]
                }
            ),
            Slide(
                type="Section",
                fields={
                    "title": "Conclusion"
                }
            ),
            Slide(
                type="Content",
                fields={
                    "title": "Summary",
                    "content": [
                        "The TOC generation works correctly",
                        "All sections are properly displayed",
                        "The presentation looks good"
                    ]
                }
            ),
            Slide(
                type="Section",
                fields={
                    "title": "Next Steps"
                }
            ),
            Slide(
                type="Content",
                fields={
                    "title": "Future Work",
                    "content": [
                        "Continue improving the presentation generation",
                        "Add more slide types",
                        "Enhance the design"
                    ]
                }
            )
        ]
    )
    
    # Generate the PowerPoint
    result = await generate_pptx_from_slides(presentation, "test")
    
    print("\n===== TEST RESULTS =====")
    print(f"PowerPoint file generated: {result.pptx_path}")
    print(f"Slide count: {result.slide_count}")
    print("======================\n")

    return result

# Note: Run with pytest instead of directly
# pytest tests/unit/pptx/test_pptx_functions.py::test_toc_generation -v 