import pytest
import sys
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

# Import VCR classes rather than fixtures
from tests.test_gemini_vcr import GeminiVCR
from tests.test_openai_vcr import OpenAIVCR

# Configure pytest.ini options programmatically
def pytest_addoption(parser):
    parser.addini("asyncio_mode", "default asyncio mode", default="auto")
    parser.addini("asyncio_default_fixture_loop_scope", "default event loop scope for asyncio fixtures", default="function")

# Set up fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)

@pytest.fixture
def gemini_vcr():
    """
    Return an instance of GeminiVCR that can record and replay Gemini API calls.
    - If GEMINI_VCR_MODE=record, make actual API calls and save responses.
    - If GEMINI_VCR_MODE=replay, use saved responses.
    """
    # Create and return the GeminiVCR instance directly
    return GeminiVCR()

@pytest.fixture
def mock_gemini_api():
    """
    Patch the Gemini API key for testing.
    """
    # Create environment patch for API key if not in recording mode
    record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
    print(f"mock_gemini_api: record_mode = {record_mode}")
    
    if record_mode:
        # In record mode, we need the real API key
        # If GEMINI_API_KEY isn't explicitly set, try to load from .env file
        from dotenv import load_dotenv
        if not os.environ.get("GEMINI_API_KEY"):
            print("Loading API key from .env file for recording mode")
            load_dotenv()
            
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable is required for recording mode")
            
        # Use the real API key in the environment
        yield
    else:
        # In replay mode, use fake key
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-gemini-key-for-testing"}):
            yield

@pytest.fixture
def openai_vcr():
    """
    Return an instance of OpenAIVCR that can record and replay OpenAI API calls.
    - If OPENAI_VCR_MODE=record, make actual API calls and save responses.
    - If OPENAI_VCR_MODE=replay, use saved responses.
    """
    # Create and return the OpenAIVCR instance directly
    return OpenAIVCR()

@pytest.fixture
def mock_openai_api():
    """
    Patch the OpenAI API key for testing.
    """
    # Create environment patch for API key if not in recording mode
    record_mode = os.environ.get("OPENAI_VCR_MODE", "replay") == "record"
    print(f"mock_openai_api: record_mode = {record_mode}")
    
    if record_mode:
        # In record mode, we need the real API key
        # If OPENAI_API_KEY isn't explicitly set, try to load from .env file
        from dotenv import load_dotenv
        if not os.environ.get("OPENAI_API_KEY"):
            print("Loading API key from .env file for recording mode")
            load_dotenv()
            
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required for recording mode")
            
        # Use the real API key in the environment
        yield
    else:
        # In replay mode, use fake key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-openai-key-for-testing"}):
            yield

@pytest.fixture
def mock_openai_responses(openai_vcr, mock_openai_api):
    """
    Pytest fixture that replaces the OpenAI client with a mocked version.
    """
    # Create a completely mocked OpenAI client
    mock_client = MagicMock()
    mock_images = MagicMock()
    
    # Mock the generate method
    def mock_generate(**kwargs):
        return openai_vcr.mock_openai_images_generate(**kwargs)
    
    # Attach the generate method
    mock_images.generate = mock_generate
    mock_client.images = mock_images
    
    # Now patch the OpenAI constructor in tools.images
    with patch('tools.images.OpenAI', return_value=mock_client):
        # Indicate the patching was successful for debug
        print("Successfully patched OpenAI client in tools.images module")
        yield openai_vcr  # Return the actual VCR instance

@pytest.fixture
def mock_gemini_responses(gemini_vcr, mock_gemini_api):
    """
    Pytest fixture that patches Google's generative AI with mocked responses.
    """
    import google.generativeai as genai
    
    # Patch the generate_content method
    with patch('google.generativeai.GenerativeModel.generate_content', 
               side_effect=gemini_vcr.mock_generate_content(genai.GenerativeModel.generate_content)), \
         patch('google.generativeai.GenerativeModel.generate_content_async',
               side_effect=gemini_vcr.mock_generate_content_async(genai.GenerativeModel.generate_content_async)):
        
        # Indicate the patching was successful for debug
        print("Successfully patched Gemini API methods")
        yield gemini_vcr  # Return the actual VCR instance

@pytest.fixture
def image_api_vcr():
    """
    Record and replay image API calls.
    - If IMAGE_API_VCR_MODE=record, make actual API calls and save responses.
    - If IMAGE_API_VCR_MODE=replay, use saved responses.
    """
    record_mode = os.environ.get("IMAGE_API_VCR_MODE", "replay") == "record"
    
    def load_or_save_fixture(prompt, response=None):
        """Load a fixture or save a new one."""
        # Create a filename from the prompt
        hash_value = hash(prompt) % 10000000
        filename = f"image_api_{hash_value:x}.json"
        fixture_path = FIXTURES_DIR / filename
        
        # If we're saving a response
        if response is not None:
            save_fixture(fixture_path, response)
            return response
        
        # If we're loading a response
        fixture_data = load_fixture(fixture_path)
        if fixture_data is None and not record_mode:
            pytest.skip(f"No fixture found for prompt: {prompt}")
        
        return fixture_data
    
    return load_or_save_fixture 