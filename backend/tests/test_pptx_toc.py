import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from tools.pptx_toc import _find_section_text_shapes, process_toc_slide


class TestPptxToc(unittest.TestCase):
    
    @patch('tools.pptx_toc.find_shape_by_name')
    def test_find_section_text_shapes_by_name(self, mock_find_shape):
        """Test that _find_section_text_shapes returns the correct dictionary when shapes have Section names."""
        # Create mock slide
        mock_slide = MagicMock()
        
        # Setup mock shapes to be returned by find_shape_by_name
        mock_shapes = {
            "Section1": MagicMock(name="Section1"),
            "Section2": MagicMock(name="Section2"),
            "Section4": MagicMock(name="Section4"),
            # Section3 is missing on purpose
            "Section5": MagicMock(name="Section5")
        }
        
        # Configure mock_find_shape to return appropriate mock shapes
        def side_effect(slide, name):
            return mock_shapes.get(name, None)
            
        mock_find_shape.side_effect = side_effect
        
        # Call the function
        result = _find_section_text_shapes(mock_slide)
        
        # Verify the results
        self.assertEqual(len(result), 4)  # Should find 4 shapes
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(4, result)
        self.assertIn(5, result)
        self.assertNotIn(3, result)  # Section3 should not be found
        
        # Verify correct shapes were returned
        self.assertEqual(result[1], mock_shapes["Section1"])
        self.assertEqual(result[2], mock_shapes["Section2"])
        self.assertEqual(result[4], mock_shapes["Section4"])
        self.assertEqual(result[5], mock_shapes["Section5"])
        
        # Verify find_shape_by_name was called with correct arguments
        expected_calls = [
            unittest.mock.call(mock_slide, "Section1"),
            unittest.mock.call(mock_slide, "Section2"),
            unittest.mock.call(mock_slide, "Section3"),
            unittest.mock.call(mock_slide, "Section4"),
            unittest.mock.call(mock_slide, "Section5"),
            unittest.mock.call(mock_slide, "Section6"),
            unittest.mock.call(mock_slide, "Section7"),
            unittest.mock.call(mock_slide, "Section8"),
        ]
        mock_find_shape.assert_has_calls(expected_calls)
        self.assertEqual(mock_find_shape.call_count, 8)
    
    @patch('tools.pptx_toc.find_shape_by_name')
    def test_find_section_text_shapes_by_placeholder(self, mock_find_shape):
        """Test that _find_section_text_shapes correctly identifies Text Placeholder shapes."""
        # Create mock slide
        mock_slide = MagicMock()
        
        # Make find_shape_by_name return None (no section shapes found by name)
        mock_find_shape.return_value = None
        
        # Create mock text placeholder shapes with proper names
        text_placeholders = []
        for i in range(9):
            if i == 0:
                name = "Title 1"
            else:
                name = f"Text Placeholder {i+1}"
                
            shape = MagicMock()
            # Set the name property correctly
            type(shape).name = PropertyMock(return_value=name)
            shape.text_frame = MagicMock()
            text_placeholders.append(shape)
        
        # Set the shapes on the slide
        mock_slide.shapes = text_placeholders
        
        # Call the function
        result = _find_section_text_shapes(mock_slide)
        
        # Verify results
        self.assertEqual(len(result), 8)  # Should find 8 section shapes
        
        # Section 1 should be Text Placeholder 2, and so on
        for i in range(1, 9):
            self.assertIn(i, result)
            self.assertEqual(result[i], text_placeholders[i])
        
        # Verify find_shape_by_name was called for each section name
        self.assertEqual(mock_find_shape.call_count, 8)
    
    @patch('tools.pptx_toc._find_section_text_shapes')
    def test_process_toc_slide(self, mock_find_sections):
        """Test that process_toc_slide correctly updates section text."""
        # Create mock slide and section shapes
        mock_slide = MagicMock()
        mock_section_shapes = {
            1: MagicMock(text_frame=MagicMock()),
            2: MagicMock(text_frame=MagicMock()),
            3: MagicMock(text_frame=MagicMock()),
            4: MagicMock(text_frame=MagicMock())
        }
        
        # Configure mock to return section shapes
        mock_find_sections.return_value = mock_section_shapes
        
        # Test data
        section_titles = ["First Section", "Second Section", "Third Section"]
        
        # Call the function
        process_toc_slide(mock_slide, section_titles)
        
        # Verify section texts were updated correctly
        self.assertEqual(mock_section_shapes[1].text_frame.text, "First Section")
        self.assertEqual(mock_section_shapes[2].text_frame.text, "Second Section")
        self.assertEqual(mock_section_shapes[3].text_frame.text, "Third Section")
        
        # Verify fourth section was hidden
        mock_section_shapes[4].element.getparent().remove.assert_called_once_with(
            mock_section_shapes[4].element
        )
        
        # Verify first call attempts to get the shapes
        mock_find_sections.assert_called_once_with(mock_slide) 