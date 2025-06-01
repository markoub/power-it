import json
import pytest
from unittest.mock import patch, MagicMock
import google.generativeai as genai
from typing import Dict, Any

from tests.utils.vcr_base import BaseVCR
from tests.utils.env_manager import EnvironmentManager
from tests.utils.module_manager import ModuleManager


class GeminiVCR(BaseVCR):
    """
    VCR implementation for recording and replaying Gemini API responses.
    """
    
    def __init__(self, fixtures_dir: str = None):
        super().__init__(api_name="gemini", fixtures_dir=fixtures_dir)
    
    def create_mock_response(self, recording: Dict[str, Any]) -> Any:
        """Create a mock Gemini response from a recording."""
        mock_response = MagicMock()
        mock_response.text = recording["text"]
        return mock_response
    
    def _extract_prompt_from_content(self, content: Any) -> str:
        """Extract prompt text from various content formats."""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "parts" in item:
                    for part in item["parts"]:
                        if isinstance(part, dict) and "text" in part:
                            return part["text"]
        return str(content)
    
    def generate_content_mock(self, *args, **kwargs):
        """Mock for generate_content method."""
        # Extract content from various argument patterns
        contents = None
        
        if args and isinstance(args[0], genai.GenerativeModel):
            # Standard pattern: model.generate_content(content)
            if len(args) > 1:
                contents = args[1]
            elif 'contents' in kwargs:
                contents = kwargs['contents']
        elif args:
            # Direct content pattern
            contents = args[0]
        elif 'contents' in kwargs:
            contents = kwargs['contents']
            
        if contents is None:
            raise TypeError("No 'contents' parameter found in generate_content call")
        
        # Generate fixture name
        prompt = self._extract_prompt_from_content(contents)
        fixture_name = self.generate_fixture_name(prompt, kwargs)
        
        # Record or replay
        def api_call():
            # This would be the real API call in record mode
            import os
            api_key = os.environ.get("GEMINI_API_KEY", "fake-key-for-testing")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            return model.generate_content(contents, **kwargs)
        
        def response_processor(response):
            return {
                "text": response.text,
                "prompt": prompt
            }
        
        return self.record_or_replay(fixture_name, api_call, response_processor)
    
    async def generate_content_async_mock(self, *args, **kwargs):
        """Mock for generate_content_async method."""
        # Extract content from various argument patterns
        contents = None
        
        if args and isinstance(args[0], genai.GenerativeModel):
            # Standard pattern: model.generate_content_async(content)
            if len(args) > 1:
                contents = args[1]
            elif 'contents' in kwargs:
                contents = kwargs['contents']
        elif args:
            # Direct content pattern
            contents = args[0]
        elif 'contents' in kwargs:
            contents = kwargs['contents']
            
        if contents is None:
            raise TypeError("No 'contents' parameter found in generate_content_async call")
        
        # Generate fixture name
        prompt = self._extract_prompt_from_content(contents)
        fixture_name = self.generate_fixture_name(prompt, kwargs)
        
        # Record or replay
        async def api_call():
            # This would be the real API call in record mode
            import os
            api_key = os.environ.get("GEMINI_API_KEY", "fake-key-for-testing")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            return await model.generate_content_async(contents, **kwargs)
        
        def response_processor(response):
            return {
                "text": response.text,
                "prompt": prompt
            }
        
        return self.record_or_replay(fixture_name, api_call, response_processor)

    def mock_generate_content(self, original_method):
        """
        Factory method to create a mock for generate_content.
        This is the method expected by conftest.py.
        """
        return self.generate_content_mock

    def mock_generate_content_async(self, original_method):
        """
        Factory method to create a mock for generate_content_async.
        This is the method expected by conftest.py.
        """
        return self.generate_content_async_mock


class TestGeminiVCR:
    """Test cases for GeminiVCR functionality."""
    
    def test_generate_fixture_name(self):
        """Test fixture name generation."""
        vcr = GeminiVCR()
        name = vcr.generate_fixture_name("test prompt", {"temperature": 0.5})
        assert isinstance(name, str)
        assert len(name.split('_')) == 2
        assert name.startswith("test")
    
    def test_create_mock_response(self):
        """Test mock response creation."""
        vcr = GeminiVCR()
        recording = {"text": "Test response", "prompt": "Test prompt"}
        
        mock_response = vcr.create_mock_response(recording)
        assert mock_response.text == "Test response"
    
    def test_extract_prompt_from_content(self):
        """Test prompt extraction from various content formats."""
        vcr = GeminiVCR()
        
        # String content
        assert vcr._extract_prompt_from_content("Simple prompt") == "Simple prompt"
        
        # List content with parts
        content = [{"parts": [{"text": "Complex prompt"}]}]
        assert vcr._extract_prompt_from_content(content) == "Complex prompt"
        
        # Fallback
        assert vcr._extract_prompt_from_content(123) == "123"
    
    @pytest.mark.asyncio
    async def test_generate_content_async_mock(self):
        """Test async generate content mock."""
        with EnvironmentManager.temporary_env(GEMINI_VCR_MODE="replay"):
            vcr = GeminiVCR()
            
            # Create a test fixture
            test_recording = {"text": "Test response", "prompt": "test"}
            vcr.save_recording("test_12345678", test_recording)
            
            # Mock the method
            with patch.object(vcr, 'generate_fixture_name', return_value="test_12345678"):
                response = await vcr.generate_content_async_mock("test prompt")
                assert response.text == "Test response"
    
    def test_generate_content_mock(self):
        """Test sync generate content mock."""
        with EnvironmentManager.temporary_env(GEMINI_VCR_MODE="replay"):
            vcr = GeminiVCR()
            
            # Create a test fixture
            test_recording = {"text": "Test response", "prompt": "test"}
            vcr.save_recording("test_12345678", test_recording)
            
            # Mock the method
            with patch.object(vcr, 'generate_fixture_name', return_value="test_12345678"):
                response = vcr.generate_content_mock("test prompt")
                assert response.text == "Test response"


@pytest.fixture
def gemini_vcr():
    """Pytest fixture that provides a GeminiVCR instance."""
    return GeminiVCR()


@pytest.fixture
def mock_gemini_api():
    """
    Setup Gemini API configuration for testing.
    """
    with EnvironmentManager.temporary_env(
        GEMINI_API_KEY="fake-api-key-for-testing",
        GEMINI_VCR_MODE="replay"
    ):
        with patch('google.generativeai.configure') as mock_configure:
            mock_configure.return_value = None
            yield


@pytest.fixture
def mock_gemini_responses(gemini_vcr, mock_gemini_api):
    """
    Patch Gemini API methods to use VCR.
    """
    with patch.object(
        genai.GenerativeModel,
        'generate_content_async',
        side_effect=gemini_vcr.generate_content_async_mock
    ) as async_mock, patch.object(
        genai.GenerativeModel,
        'generate_content',
        side_effect=gemini_vcr.generate_content_mock
    ) as sync_mock:
        yield gemini_vcr 