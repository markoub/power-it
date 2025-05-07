import unittest
import os
import tempfile
import shutil
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock

from models import SlidePresentation, Slide

@pytest.mark.asyncio
class TestPPTXIntegration:
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup_and_teardown(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.prs_dir = os.path.join(self.test_dir, "presentations")
        os.makedirs(self.prs_dir, exist_ok=True)
        
        # Mock the PRESENTATIONS_STORAGE_DIR constant
        self.patcher = patch('tools.generate_pptx.PRESENTATIONS_STORAGE_DIR', self.prs_dir)
        self.patcher.start()
        
        yield
        
        # Stop the patcher
        self.patcher.stop()
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    async def test_generate_presentation_with_section(self):
        """Test generating a presentation with a section slide."""
        # Import here to avoid import issues
        from tools.generate_pptx import generate_pptx_from_slides
        
        # Create a presentation with a section slide
        slides = SlidePresentation(
            title="Test Presentation",
            slides=[
                # Welcome slide
                Slide(
                    type="Welcome",
                    fields={
                        "title": "Welcome to Test Presentation",
                        "subtitle": "Testing Section Slides",
                        "author": "Test Author"
                    }
                ),
                # Section slide
                Slide(
                    type="Section",
                    fields={
                        "title": "Section One"
                    }
                ),
                # Content slide
                Slide(
                    type="Content",
                    fields={
                        "title": "Content Slide",
                        "content": ["Item 1", "Item 2", "Item 3"]
                    }
                )
            ]
        )
        
        # Mock the presentation template loading
        with patch('pptx.Presentation') as mock_prs_class:
            # Setup the mock presentation
            mock_prs = MagicMock()
            mock_prs_class.return_value = mock_prs
            
            # Mock the slide layouts
            mock_welcome_layout = MagicMock()
            mock_section_layout = MagicMock()
            mock_content_layout = MagicMock()
            mock_toc_layout = MagicMock()
            mock_thankyou_layout = MagicMock()
            
            # Mock the get_layout_by_name function
            with patch('tools.pptx_shapes.get_layout_by_name') as mock_get_layout:
                def mock_get_layout_side_effect(prs, name):
                    if name == "Welcome":
                        return mock_welcome_layout
                    elif name == "Section":
                        return mock_section_layout
                    elif name == "Content":
                        return mock_content_layout
                    elif name == "TableOfContents":
                        return mock_toc_layout
                    elif name == "ThankYou":
                        return mock_thankyou_layout
                    return None
                
                mock_get_layout.side_effect = mock_get_layout_side_effect
                
                # Mock finding shapes by name
                with patch('tools.pptx_slides.find_shape_by_name') as mock_find_shape:
                    # Create mock shapes
                    mock_title_shape = MagicMock()
                    mock_title_shape.text_frame = MagicMock()
                    
                    mock_section_title_shape = MagicMock()
                    mock_section_title_shape.text_frame = MagicMock()
                    
                    mock_section_number_shape = MagicMock()
                    mock_section_number_shape.text_frame = MagicMock()
                    
                    mock_content_title_shape = MagicMock()
                    mock_content_title_shape.text_frame = MagicMock()
                    
                    mock_content_body_shape = MagicMock()
                    mock_content_body_shape.text_frame = MagicMock()
                    
                    # Setup find_shape_by_name to return appropriate shapes
                    def find_shape_side_effect(slide, name):
                        if name == "Title":
                            if mock_prs.slides.add_slide.call_count == 1:  # Welcome slide
                                return mock_title_shape
                            elif mock_prs.slides.add_slide.call_count == 2:  # Section slide
                                return mock_section_title_shape
                            elif mock_prs.slides.add_slide.call_count == 3:  # Content slide
                                return mock_content_title_shape
                        elif name == "Number" and mock_prs.slides.add_slide.call_count == 2:  # Section slide
                            return mock_section_number_shape
                        elif name == "Content" and mock_prs.slides.add_slide.call_count == 3:  # Content slide
                            return mock_content_body_shape
                        return None
                    
                    mock_find_shape.side_effect = find_shape_side_effect
                    
                    # Generate the presentation
                    result = await generate_pptx_from_slides(slides)
                    
                    # Verify the presentation was saved
                    assert result is not None
                    assert os.path.exists(result.pptx_path)
                    
                    # Verify the section slide was created
                    mock_find_shape.assert_any_call(mock_prs.slides.add_slide.return_value, "Number")
                    mock_find_shape.assert_any_call(mock_prs.slides.add_slide.return_value, "Title")
                    
                    # Verify the correct text was set on the section slide shapes
                    assert mock_section_title_shape.text_frame.text == "Section One"
                    assert mock_section_number_shape.text_frame.text == "01"

if __name__ == '__main__':
    unittest.main() 