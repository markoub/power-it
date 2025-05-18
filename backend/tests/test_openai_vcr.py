import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import base64
from typing import Dict, Any, Optional, Callable
from dotenv import load_dotenv
import traceback

class OpenAIVCR:
    """
    A VCR-like class for recording and replaying OpenAI API responses.
    This allows integration tests to run without actually calling the OpenAI API.
    """
    def __init__(self, fixtures_dir: str = None, dummy_image_dir: str = None):
        # Use absolute path for fixtures directory
        if fixtures_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.fixtures_dir = os.path.join(current_dir, "fixtures")
        else:
            self.fixtures_dir = fixtures_dir
            
        # Use absolute path for dummy image directory
        if dummy_image_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.dummy_image_dir = os.path.join(current_dir, "test_data")
        else:
            self.dummy_image_dir = dummy_image_dir
            
        self.recordings: Dict[str, Any] = {}
        self.record_mode = os.environ.get("OPENAI_VCR_MODE", "replay") == "record"
        
        # Create directories if they don't exist
        print(f"OpenAI fixtures directory: {self.fixtures_dir}")
        print(f"OpenAI dummy image directory: {self.dummy_image_dir}")
        print(f"OpenAI record mode: {self.record_mode}")
        os.makedirs(self.fixtures_dir, exist_ok=True)
        os.makedirs(self.dummy_image_dir, exist_ok=True)
    
    def get_fixture_path(self, name: str) -> str:
        """Get the path to a fixture file."""
        path = os.path.join(self.fixtures_dir, f"{name}.json")
        return path
    
    def save_recording(self, name: str, data: Dict[str, Any]) -> None:
        """Save a recording to a fixture file."""
        fixture_path = self.get_fixture_path(name)
        print(f"Attempting to save OpenAI fixture to: {fixture_path}")
        try:
            with open(fixture_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Successfully saved OpenAI fixture to: {fixture_path}")
            # Verify the file was created
            if os.path.exists(fixture_path):
                print(f"Verified file exists: {fixture_path}")
                print(f"File size: {os.path.getsize(fixture_path)} bytes")
            else:
                print(f"ERROR: File was not created: {fixture_path}")
        except Exception as e:
            print(f"ERROR saving fixture: {str(e)}")
            traceback.print_exc()
    
    def load_recording(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a recording from a fixture file."""
        fixture_path = self.get_fixture_path(name)
        if os.path.exists(fixture_path):
            print(f"Loading OpenAI fixture from: {fixture_path}")
            with open(fixture_path, "r") as f:
                return json.load(f)
        return None
    
    def get_dummy_image(self) -> str:
        """Get a dummy base64 encoded image for testing."""
        # Load a dummy image from test_data directory
        dummy_images = [f for f in os.listdir(self.dummy_image_dir) 
                       if f.endswith(('jpg', 'jpeg', 'png', 'gif'))]
        
        if dummy_images:
            # Use the first image found
            dummy_image_path = os.path.join(self.dummy_image_dir, dummy_images[0])
            with open(dummy_image_path, "rb") as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        
        # If no dummy image is found, create a minimal one
        print("WARNING: No dummy images found, creating a minimal one")
        # Create a 1x1 black pixel PNG image
        dummy_image = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c````\x00\x00\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')
        return dummy_image
    
    def generate_fixture_name(self, kwargs: Dict[str, Any]) -> str:
        """Generate a unique fixture name based on the function arguments."""
        # Create a deterministic fixture name based on the prompt
        import hashlib
        
        # Extract prompt or use a default
        prompt = kwargs.get('prompt', 'image')
        
        # Take first few words of prompt for prefix
        if isinstance(prompt, str) and prompt:
            # Take first 30 chars of first word, removing special chars
            first_word = ''.join(c for c in prompt.split()[0][:30] if c.isalnum())
            prompt_prefix = first_word.lower() + "_"
        else:
            prompt_prefix = "image_"
        
        # Convert kwargs to a stable string representation for hashing
        kwargs_str = str(sorted(kwargs.items()))
        
        # Generate a hash of the combined string
        hash_obj = hashlib.md5(kwargs_str.encode())
        hash_str = hash_obj.hexdigest()
        
        fixture_name = f"{prompt_prefix}{hash_str[:12]}"
        print(f"Generated OpenAI fixture name: {fixture_name}")
        return fixture_name
    
    def mock_openai_images_generate(self, **kwargs):
        """Create a mock response for OpenAI images.generate."""
        fixture_name = self.generate_fixture_name(kwargs)
        
        # If we're in record mode, make the actual API call and save the response
        if self.record_mode:
            print(f"Recording OpenAI API response to fixture: {fixture_name}")
            try:
                # Import here to avoid circular imports
                from openai import OpenAI
                
                # Create a real client to make the API call
                client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                
                # Make the actual API call
                response = client.images.generate(**kwargs)
                
                # Extract and save b64_json image data
                recording = {
                    "b64_json": response.data[0].b64_json,
                    "prompt": kwargs.get('prompt', '')
                }
                
                self.save_recording(fixture_name, recording)
                
                # Return a mock that matches the structure of the real response
                mock_response = MagicMock()
                mock_data = MagicMock()
                mock_data.b64_json = response.data[0].b64_json
                mock_response.data = [mock_data]
                return mock_response
            except Exception as e:
                print(f"ERROR in OpenAI API call: {str(e)}")
                traceback.print_exc()
                raise
        
        # If we're in replay mode, load the response from a fixture
        recording = self.load_recording(fixture_name)
        if recording:
            print(f"Replaying OpenAI API response from fixture: {fixture_name}")
            
            # Create a mock response with the saved b64_json data
            mock_response = MagicMock()
            mock_data = MagicMock()
            mock_data.b64_json = recording["b64_json"]
            mock_response.data = [mock_data]
            return mock_response
        
        # If no fixture found, use a dummy image
        print(f"No fixture found for OpenAI API call: {fixture_name}, using dummy image")
        dummy_image = self.get_dummy_image()
        
        # Create a mock response with the dummy image
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.b64_json = dummy_image
        mock_response.data = [mock_data]
        return mock_response


@pytest.fixture
def openai_vcr():
    """Pytest fixture that provides an OpenAIVCR instance."""
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
    
    # Create a mock instance for openai_vcr to be used in tests
    mock_vcr = MagicMock()
    mock_vcr.mock_openai_images_generate = openai_vcr.mock_openai_images_generate
    
    # Now patch the OpenAI constructor in tools.images
    with patch('tools.images.OpenAI', return_value=mock_client):
        # Indicate the patching was successful for debug
        print("Successfully patched OpenAI client in tools.images module")
        yield mock_vcr 