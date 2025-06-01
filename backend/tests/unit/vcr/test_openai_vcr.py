import json
import pytest
from unittest.mock import patch, MagicMock
import base64
import os
from typing import Dict, Any
from pathlib import Path

from tests.utils.vcr_base import BaseVCR
from tests.utils.env_manager import EnvironmentManager
from tests.utils.module_manager import ModuleManager


class OpenAIVCR(BaseVCR):
    """
    VCR implementation for recording and replaying OpenAI API responses.
    """
    
    def __init__(self, fixtures_dir: str = None, dummy_image_dir: str = None):
        super().__init__(api_name="openai", fixtures_dir=fixtures_dir)
        
        # Set up dummy image directory
        if dummy_image_dir is None:
            self.dummy_image_dir = Path(__file__).parent / "test_data"
        else:
            self.dummy_image_dir = Path(dummy_image_dir)
        
        self.dummy_image_dir.mkdir(parents=True, exist_ok=True)
    
    def create_mock_response(self, recording: Dict[str, Any]) -> Any:
        """Create a mock OpenAI response from a recording."""
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.b64_json = recording["b64_json"]
        mock_response.data = [mock_data]
        return mock_response
    
    def get_dummy_image(self) -> str:
        """Get a dummy base64 encoded image for testing."""
        # Check for existing dummy images
        dummy_images = list(self.dummy_image_dir.glob("*.png")) + \
                      list(self.dummy_image_dir.glob("*.jpg")) + \
                      list(self.dummy_image_dir.glob("*.jpeg")) + \
                      list(self.dummy_image_dir.glob("*.gif"))
        
        if dummy_images:
            # Use the first image found
            with open(dummy_images[0], "rb") as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        
        # Create a minimal 1x1 black pixel PNG image
        dummy_image = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c````\x00'
            b'\x00\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82'
        ).decode('utf-8')
        return dummy_image
    
    def get_sample_image_b64(self) -> str:
        """Get a sample base64 encoded image for testing."""
        return self.get_dummy_image()
    
    def images_generate_mock(self, **kwargs):
        """Mock for OpenAI images.generate method."""
        prompt = kwargs.get('prompt', 'image')
        fixture_name = self.generate_fixture_name(prompt, kwargs)
        
        # Record or replay
        def api_call():
            # This would be the real API call in record mode
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            return client.images.generate(**kwargs)
        
        def response_processor(response):
            return {
                "b64_json": response.data[0].b64_json,
                "prompt": prompt
            }
        
        try:
            return self.record_or_replay(fixture_name, api_call, response_processor)
        except FileNotFoundError:
            # Fallback to dummy image if no fixture found
            dummy_image = self.get_dummy_image()
            mock_response = MagicMock()
            mock_data = MagicMock()
            mock_data.b64_json = dummy_image
            mock_response.data = [mock_data]
            return mock_response


class TestOpenAIVCR:
    """Test cases for OpenAIVCR functionality."""
    
    def test_generate_fixture_name(self):
        """Test fixture name generation."""
        vcr = OpenAIVCR()
        name = vcr.generate_fixture_name("test image", {"size": "1024x1024"})
        assert isinstance(name, str)
        assert len(name.split('_')) == 2
        assert name.startswith("test")
    
    def test_create_mock_response(self):
        """Test mock response creation."""
        vcr = OpenAIVCR()
        recording = {"b64_json": "base64data", "prompt": "test"}
        
        mock_response = vcr.create_mock_response(recording)
        assert mock_response.data[0].b64_json == "base64data"
    
    def test_get_dummy_image(self):
        """Test dummy image generation."""
        vcr = OpenAIVCR()
        dummy_image = vcr.get_dummy_image()
        
        assert isinstance(dummy_image, str)
        assert len(dummy_image) > 0
        
        # Should be valid base64
        try:
            base64.b64decode(dummy_image)
        except Exception:
            pytest.fail("Dummy image is not valid base64")
    
    def test_images_generate_mock(self):
        """Test images generate mock."""
        with EnvironmentManager.temporary_env(OPENAI_VCR_MODE="replay"):
            vcr = OpenAIVCR()
            
            # Create a test fixture
            test_recording = {"b64_json": "testdata", "prompt": "test"}
            vcr.save_recording("test_12345678", test_recording)
            
            # Mock the method
            with patch.object(vcr, 'generate_fixture_name', return_value="test_12345678"):
                response = vcr.images_generate_mock(prompt="test prompt")
                assert response.data[0].b64_json == "testdata"
    
    def test_images_generate_mock_fallback(self):
        """Test images generate mock with fallback to dummy image."""
        with EnvironmentManager.temporary_env(OPENAI_VCR_MODE="replay"):
            vcr = OpenAIVCR()
            
            # No fixture exists, should fall back to dummy image
            response = vcr.images_generate_mock(prompt="nonexistent prompt")
            assert response.data[0].b64_json is not None
            assert len(response.data[0].b64_json) > 0


@pytest.fixture
def openai_vcr():
    """Pytest fixture that provides an OpenAIVCR instance."""
    return OpenAIVCR()


@pytest.fixture
def mock_openai_api():
    """
    Setup OpenAI API configuration for testing.
    """
    with EnvironmentManager.temporary_env(
        OPENAI_API_KEY="fake-openai-key-for-testing",
        OPENAI_VCR_MODE="replay"
    ):
        yield


@pytest.fixture
def mock_openai_responses(openai_vcr, mock_openai_api):
    """
    Patch OpenAI client to use VCR.
    """
    mock_client = MagicMock()
    mock_images = MagicMock()
    mock_images.generate = openai_vcr.images_generate_mock
    mock_client.images = mock_images
    
    with patch('tools.images.OpenAI', return_value=mock_client):
        yield openai_vcr 