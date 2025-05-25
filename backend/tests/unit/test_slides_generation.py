import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from tools.slides import generate_slides
from models import ResearchData


@pytest.mark.asyncio
async def test_slides_generation_without_tool_choice_error():
    """Test that slides generation doesn't fail with tool_choice parameter error"""
    
    # Mock research data
    research_data = ResearchData(
        content="Test research content about artificial intelligence and machine learning applications in business.",
        sources=["https://example.com/ai-research"]
    )
    
    # Mock the Gemini API response
    mock_response = Mock()
    mock_response.text = '''```json
{
    "title": "AI in Business",
    "author": "Test Author",
    "slides": [
        {
            "type": "Welcome",
            "fields": {
                "title": "AI in Business",
                "subtitle": "Modern Applications",
                "author": "Test Author"
            }
        },
        {
            "type": "Content",
            "fields": {
                "title": "Introduction",
                "content": ["AI is transforming business operations"]
            }
        }
    ]
}
```'''
    
    # Mock the GenerativeModel
    with patch('tools.slides.genai.GenerativeModel') as mock_model_class:
        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model
        
        # Test that slides generation works without tool_choice error
        result = await generate_slides(research_data, target_slides=2, author="Test Author")
        
        # Verify the result
        assert result is not None
        assert result is not None
        if os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes"}:
            assert result.title is not None
        else:
            assert result.title == "AI in Business"
        assert result.author == "Test Author"
        assert len(result.slides) >= 2
        
        if os.environ.get("POWERIT_OFFLINE", "0").lower() not in {"1", "true", "yes"}:
            # Verify that generate_content_async was called without tool_choice parameter
            mock_model.generate_content_async.assert_called_once()
            call_args = mock_model.generate_content_async.call_args

            # Check that tool_choice is not in the keyword arguments
            assert 'tool_choice' not in call_args.kwargs

            # Check that required parameters are present
            assert 'generation_config' in call_args.kwargs
            assert 'tools' in call_args.kwargs
            assert 'safety_settings' in call_args.kwargs


@pytest.mark.asyncio
async def test_slides_generation_handles_api_errors_gracefully():
    """Test that slides generation handles API errors gracefully and falls back"""
    
    research_data = ResearchData(
        content="Test research content",
        sources=["https://example.com"]
    )
    
    # Mock the GenerativeModel to raise an exception
    with patch('tools.slides.genai.GenerativeModel') as mock_model_class:
        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(side_effect=Exception("API Error"))
        mock_model_class.return_value = mock_model
        
        # Test that slides generation falls back gracefully
        result = await generate_slides(research_data, target_slides=2, author="Test Author")
        
        # Verify that we get a fallback result
        assert result is not None
        assert result.title is not None
        assert result.author == "Test Author"
        assert len(result.slides) > 0
