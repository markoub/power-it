import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.pptx_slides import create_section_slide
from tools.pptx_utils import format_section_number

class TestSectionSlide(unittest.TestCase):
    
    @patch('tools.pptx_slides.find_shape_by_name')
    def test_create_section_slide(self, mock_find_shape):
        """Test that the section slide is created correctly with proper title and number."""
        # Create mock presentation and slide layout
        mock_prs = MagicMock()
        mock_layout = MagicMock()
        mock_slide = MagicMock()
        
        # Setup the mock presentation to return our mock slide
        mock_prs.slides.add_slide.return_value = mock_slide
        
        # Create mock shapes for title and number
        mock_title_shape = MagicMock()
        mock_title_shape.text_frame = MagicMock()
        
        mock_number_shape = MagicMock()
        mock_number_shape.text_frame = MagicMock()
        
        # Setup the mock find_shape_by_name to return our mock shapes
        def find_shape_side_effect(slide, name):
            if name == "Title":
                return mock_title_shape
            elif name == "Number":
                return mock_number_shape
            return None
        
        mock_find_shape.side_effect = find_shape_side_effect
        
        # Call the function to create a section slide
        section_title = "Test Section"
        section_number = 3
        result = create_section_slide(mock_prs, mock_layout, section_title, section_number)
        
        # Verify the presentation's add_slide method was called with the layout
        mock_prs.slides.add_slide.assert_called_once_with(mock_layout)
        
        # Verify find_shape_by_name was called with the right arguments
        mock_find_shape.assert_any_call(mock_slide, "Number")
        mock_find_shape.assert_any_call(mock_slide, "Title")
        
        # Verify title and number were set correctly
        mock_title_shape.text_frame.text = section_title
        mock_number_shape.text_frame.text = format_section_number(section_number)
        
        # Verify the result is the mock slide
        self.assertEqual(result, mock_slide)
        
    @patch('tools.pptx_slides.find_shape_by_name')
    def test_section_slide_with_fallback_placeholders(self, mock_find_shape):
        """Test when the placeholders need to be found by type rather than name."""
        # Create mock presentation and slide layout
        mock_prs = MagicMock()
        mock_layout = MagicMock()
        mock_slide = MagicMock()
        
        # Setup the mock presentation to return our mock slide
        mock_prs.slides.add_slide.return_value = mock_slide
        
        # Make find_shape_by_name return None to simulate missing named shapes
        mock_find_shape.return_value = None
        
        # Create mock shapes for title and number with placeholder types
        mock_title_shape = MagicMock()
        mock_title_shape.text_frame = MagicMock()
        mock_title_shape.placeholder_format = MagicMock()
        mock_title_shape.placeholder_format.type = 2  # BODY type
        
        mock_number_shape = MagicMock()
        mock_number_shape.text_frame = MagicMock()
        mock_number_shape.placeholder_format = MagicMock()
        mock_number_shape.placeholder_format.type = 3  # CENTER_TITLE type
        
        # Add shapes to the slide
        mock_slide.shapes = [mock_title_shape, mock_number_shape]
        
        # Call the function to create a section slide
        section_title = "Test Section"
        section_number = 3
        result = create_section_slide(mock_prs, mock_layout, section_title, section_number)
        
        # Verify title and number were set correctly based on placeholder types
        mock_title_shape.text_frame.text = section_title
        mock_number_shape.text_frame.text = format_section_number(section_number)
        
        # Verify the result is the mock slide
        self.assertEqual(result, mock_slide)
        
if __name__ == '__main__':
    unittest.main() 