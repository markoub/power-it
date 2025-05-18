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

# Import and register fixtures from test_gemini_vcr.py and test_openai_vcr.py
from tests.test_gemini_vcr import gemini_vcr, mock_gemini_api, mock_gemini_responses
from tests.test_openai_vcr import openai_vcr, mock_openai_api, mock_openai_responses

# Make them available to pytest
__all__ = [
    'gemini_vcr', 'mock_gemini_api', 'mock_gemini_responses',
    'openai_vcr', 'mock_openai_api', 'mock_openai_responses'
]

# Configure pytest.ini options programmatically
def pytest_addoption(parser):
    parser.addini("asyncio_mode", "default asyncio mode", default="auto")
    parser.addini("asyncio_default_fixture_loop_scope", "default event loop scope for asyncio fixtures", default="function")

# Set up fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)

def load_fixture(fixture_path):
    """Load a fixture from the fixtures directory."""
    if not fixture_path.exists():
        return None
    with open(fixture_path, "r") as f:
        return json.load(f)

def save_fixture(fixture_path, data):
    """Save a fixture to the fixtures directory."""
    with open(fixture_path, "w") as f:
        json.dump(data, f, indent=2)

@pytest.fixture
def gemini_vcr():
    """
    Record and replay Gemini API calls.
    - If GEMINI_VCR_MODE=record, make actual API calls and save responses.
    - If GEMINI_VCR_MODE=replay, use saved responses.
    """
    record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
    
    def load_or_save_fixture(prompt, response=None):
        """Load a fixture or save a new one."""
        # Create a filename from the prompt
        hash_value = hash(prompt) % 10000000
        filename = f"gemini_{hash_value:x}.json"
        fixture_path = FIXTURES_DIR / filename
        
        print(f"Debug: Using fixture file {fixture_path} for prompt '{prompt}' (hash: {hash_value:x})")
        
        # If we're saving a response
        if response is not None:
            print(f"Debug: Saving response to {fixture_path}")
            save_fixture(fixture_path, response)
            return response
        
        # If we're loading a response
        fixture_data = load_fixture(fixture_path)
        
        if fixture_data is None:
            print(f"Debug: No fixture found at {fixture_path}")
            if not record_mode:
                pytest.skip(f"No fixture found for prompt: {prompt}")
        else:
            print(f"Debug: Loaded fixture from {fixture_path}")
        
        return fixture_data
    
    # Return the load_or_save_fixture function
    yield load_or_save_fixture

@pytest.fixture
def openai_vcr():
    """
    Record and replay OpenAI API calls.
    - If OPENAI_VCR_MODE=record, make actual API calls and save responses.
    - If OPENAI_VCR_MODE=replay, use saved responses.
    """
    record_mode = os.environ.get("OPENAI_VCR_MODE", "replay") == "record"
    
    def load_or_save_fixture(prompt, response=None):
        """Load a fixture or save a new one."""
        # Create a filename from the prompt
        hash_value = hash(prompt) % 10000000
        filename = f"openai_{hash_value:x}.json"
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
    
    # If we're in record mode, return the fixture loader
    if record_mode:
        yield load_or_save_fixture
    else:
        # Patch OpenAI client
        openai_patcher = patch("openai.OpenAI")
        mock_openai = openai_patcher.start()
        
        # Create mock client and completion
        mock_client = MagicMock()
        mock_completion = MagicMock()
        
        def mock_completion_create(*args, **kwargs):
            """Mock the completion.create method."""
            prompt = kwargs.get("prompt", "")
            fixture_data = load_or_save_fixture(prompt)
            
            # Create a mock response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].text = fixture_data.get("text", "")
            
            return mock_response
        
        mock_completion.create.side_effect = mock_completion_create
        mock_client.completions = mock_completion
        mock_openai.return_value = mock_client
        
        yield load_or_save_fixture
        
        # Clean up
        openai_patcher.stop()

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