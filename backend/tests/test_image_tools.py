import pytest
import sys
import os
import asyncio
from unittest.mock import patch, MagicMock
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.images import _generate_image_for_slide, generate_image_from_prompt

# Mock models for testing
@dataclass
class MockSlide:
    fields: Dict = field(default_factory=dict)
    type: Optional[str] = None

@dataclass
class MockResponse:
    data: List[MagicMock]

@dataclass
class MockData:
    b64_json: str = "mockbase64data"

class TestImageTools:
    
    @patch('tools.images.OpenAI')
    def test_generate_image_for_slide_default_size(self, mock_openai):
        """Test that the default size is used when slide type is not ContentImage"""
        # Setup
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Create mock response
        mock_response = MockResponse(data=[MockData()])
        mock_client.images.generate.return_value = mock_response
        
        # Create a slide with image field but not ContentImage type
        slide = MockSlide(fields={"image": True, "title": "Test", "content": "Test content"})
        
        # Call the function
        result = _generate_image_for_slide(slide, 0, None)
        
        # Verify client was called with default size
        mock_client.images.generate.assert_called_once()
        call_args = mock_client.images.generate.call_args[1]
        assert call_args["size"] == "1024x1024"
    
    @patch('tools.images.OpenAI')
    def test_generate_image_for_slide_content_image_size(self, mock_openai):
        """Test that the 3:4 size is used when slide type is ContentImage"""
        # Setup
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Create mock response
        mock_response = MockResponse(data=[MockData()])
        mock_client.images.generate.return_value = mock_response
        
        # Create a slide with image field and ContentImage type
        slide = MockSlide(
            fields={"image": True, "title": "Test", "content": "Test content"},
            type="ContentImage"
        )
        
        # Call the function
        result = _generate_image_for_slide(slide, 0, None)
        
        # Verify client was called with 3:4 size
        mock_client.images.generate.assert_called_once()
        call_args = mock_client.images.generate.call_args[1]
        assert call_args["size"] == "1024x1536"
    
    @patch('tools.images.OpenAI')
    def test_prompt_does_not_include_title_text(self, mock_openai):
        """Test that the prompt doesn't include the slide title and explicitly mentions no text"""
        # Setup
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Create mock response
        mock_response = MockResponse(data=[MockData()])
        mock_client.images.generate.return_value = mock_response
        
        # Create a slide with image field and a title
        slide_title = "Important slide title"
        slide = MockSlide(
            fields={"image": True, "title": slide_title, "content": "Test content"}
        )
        
        # Call the function
        result = _generate_image_for_slide(slide, 0, None)
        
        # Verify the prompt does not contain the slide title text
        mock_client.images.generate.assert_called_once()
        call_args = mock_client.images.generate.call_args[1]
        prompt = call_args["prompt"]
        
        # Checks
        assert slide_title not in prompt  # Title should not be in prompt
        assert "ABSOLUTELY NO TEXT OR TITLES" in prompt  # Strong no-text directive
        assert "The title will be added separately" in prompt  # Explanation
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_default_size(self):
        """Test that the default size is used when slide_type is not specified"""
        # Setup for mocking the runner function
        mock_runner = MagicMock()
        mock_runner.return_value = MockResponse(data=[MockData()])
        
        # Patch the _generate_single_image function inside generate_image_from_prompt
        with patch('asyncio.get_event_loop') as mock_loop, \
             patch('tools.images.OpenAI') as mock_openai:
            
            # Setup the event loop to return our mocked response
            mock_loop.return_value.run_in_executor.side_effect = lambda executor, func, *args, **kwargs: \
                asyncio.Future()
                
            # Setup the future to return our mocked response
            future = asyncio.Future()
            future.set_result(mock_runner.return_value)
            mock_loop.return_value.run_in_executor.return_value = future
            
            # Call the function
            result = await generate_image_from_prompt("Test prompt")
            
            # Get the function that was passed to run_in_executor
            func_called = mock_loop.return_value.run_in_executor.call_args[0][1]
            
            # Now manually call that function to check the OpenAI call
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.images.generate.return_value = mock_runner.return_value
            
            # Call the function manually to set up the OpenAI client and check size
            with patch.object(asyncio, 'sleep', return_value=None):
                func_called()
                
                # Verify the size parameter
                mock_client.images.generate.assert_called_once()
                call_args = mock_client.images.generate.call_args[1]
                assert call_args["size"] == "1024x1024"
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt_content_image_size(self):
        """Test that the 3:4 size is used when slide_type is ContentImage"""
        # Setup for mocking the runner function
        mock_runner = MagicMock()
        mock_runner.return_value = MockResponse(data=[MockData()])
        
        # Patch the _generate_single_image function inside generate_image_from_prompt
        with patch('asyncio.get_event_loop') as mock_loop, \
             patch('tools.images.OpenAI') as mock_openai:
            
            # Setup the event loop to return our mocked response
            mock_loop.return_value.run_in_executor.side_effect = lambda executor, func, *args, **kwargs: \
                asyncio.Future()
                
            # Setup the future to return our mocked response
            future = asyncio.Future()
            future.set_result(mock_runner.return_value)
            mock_loop.return_value.run_in_executor.return_value = future
            
            # Call the function with ContentImage slide_type
            result = await generate_image_from_prompt("Test prompt", slide_type="ContentImage")
            
            # Get the function that was passed to run_in_executor
            func_called = mock_loop.return_value.run_in_executor.call_args[0][1]
            
            # Now manually call that function to check the OpenAI call
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.images.generate.return_value = mock_runner.return_value
            
            # Call the function manually to set up the OpenAI client and check size
            with patch.object(asyncio, 'sleep', return_value=None):
                func_called()
                
                # Verify the size parameter
                mock_client.images.generate.assert_called_once()
                call_args = mock_client.images.generate.call_args[1]
                assert call_args["size"] == "1024x1536" 