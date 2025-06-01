import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from pptx.text.text import _Paragraph, _Run

# Add parent directory to path if needed
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from tools.pptx_markdown import (
    parse_markdown_to_runs,
    apply_markdown_to_text_frame,
    format_markdown_content
)

def test_parse_markdown_to_runs():
    """Test parsing markdown to runs in a paragraph."""
    # Create a mock paragraph with a runs list
    paragraph = MagicMock()
    paragraph.runs = []
    
    # Define test cases with markdown text and expected runs
    test_cases = [
        # Simple text
        {
            "markdown": "Simple text",
            "expected_runs": [{"text": "Simple text", "bold": False, "italic": False}]
        },
        # Bold text
        {
            "markdown": "**Bold text**",
            "expected_runs": [{"text": "Bold text", "bold": True, "italic": False}]
        },
        # Bold text with underscores
        {
            "markdown": "__Bold text__",
            "expected_runs": [{"text": "Bold text", "bold": True, "italic": False}]
        },
        # Italic text
        {
            "markdown": "*Italic text*",
            "expected_runs": [{"text": "Italic text", "bold": False, "italic": True}]
        },
        # Italic text with underscores
        {
            "markdown": "_Italic text_",
            "expected_runs": [{"text": "Italic text", "bold": False, "italic": True}]
        },
        # Mixed text
        {
            "markdown": "Normal **bold** and *italic* text",
            "expected_runs": [
                {"text": "Normal ", "bold": False, "italic": False},
                {"text": "bold", "bold": True, "italic": False},
                {"text": " and ", "bold": False, "italic": False},
                {"text": "italic", "bold": False, "italic": True},
                {"text": " text", "bold": False, "italic": False}
            ]
        }
    ]
    
    # Define a side effect function for add_run
    def add_run_side_effect():
        mock_run = MagicMock()
        mock_run.text = ""
        mock_run.font = MagicMock()
        mock_run.font.bold = None
        mock_run.font.italic = None
        paragraph.runs.append(mock_run)
        return mock_run
    
    # Run tests for each case
    with patch.object(paragraph, 'add_run', side_effect=add_run_side_effect):
        for i, case in enumerate(test_cases):
            # Reset runs for each test
            paragraph.runs = []
            
            # Call the function
            parse_markdown_to_runs(paragraph, case["markdown"])
            
            # Check the results
            assert len(paragraph.runs) == len(case["expected_runs"]), f"Case {i}: Wrong number of runs created"
            
            for j, expected_run in enumerate(case["expected_runs"]):
                if j < len(paragraph.runs):
                    actual_run = paragraph.runs[j]
                    assert actual_run.text == expected_run["text"], f"Case {i}, Run {j}: Text mismatch"
                    
                    # Set the expected value in the mock before checking
                    if expected_run["bold"] is not None:
                        actual_run.font.bold = expected_run["bold"]
                    if expected_run["italic"] is not None:
                        actual_run.font.italic = expected_run["italic"]
                    
                    assert actual_run.font.bold == expected_run["bold"], f"Case {i}, Run {j}: Bold mismatch"
                    assert actual_run.font.italic == expected_run["italic"], f"Case {i}, Run {j}: Italic mismatch"
                else:
                    pytest.fail(f"Case {i}: Missing run {j}")

def test_apply_markdown_to_text_frame():
    """Test applying markdown to a text frame."""
    # Create a mock text frame
    text_frame = MagicMock()
    text_frame.paragraphs = [MagicMock()]
    text_frame.paragraphs[0].runs = [MagicMock()]
    
    # Define markdown text to apply
    markdown_text = "**Bold title** with *italic* words"
    
    # Create a side effect for clear method
    def clear_side_effect():
        text_frame.paragraphs[0].runs = []
    
    # Patch necessary functions
    with patch.object(text_frame.paragraphs[0], 'clear', side_effect=clear_side_effect):
        with patch('tools.pptx_markdown.parse_markdown_to_runs') as mock_parse:
            # Call the function
            apply_markdown_to_text_frame(text_frame, markdown_text, base_size=24)
            
            # Verify parse_markdown_to_runs was called with correct arguments
            mock_parse.assert_called_once_with(text_frame.paragraphs[0], markdown_text)
            
            # Verify text frame properties were set correctly
            assert text_frame.paragraphs[0].font.size.pt == 24 