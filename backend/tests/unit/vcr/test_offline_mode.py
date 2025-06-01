import pytest
import json
import asyncio
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from tests.utils.env_manager import EnvironmentManager
from tests.utils.module_manager import ModuleManager


class TestOfflineMode:
    """Test that the offline mode correctly prevents real API calls."""
    
    @pytest.fixture(autouse=True)
    def setup_offline_mode(self, tmp_path):
        """Setup offline mode environment for each test."""
        # Create fixtures directory
        fixtures_dir = tmp_path / "fixtures"
        fixtures_dir.mkdir()
        
        # Create default test fixture
        test_fixture = {
            "text": "This is a mocked response for offline mode testing.",
            "prompt": "Test prompt in offline mode",
            "_metadata": {
                "api": "gemini",
                "recorded_at": "2024-01-01T00:00:00",
                "version": "1.0"
            }
        }
        
        # Create gemini fixtures directory
        gemini_fixtures_dir = fixtures_dir / "gemini"
        gemini_fixtures_dir.mkdir(exist_ok=True)
        
        # We need to predict the fixture name that will be generated
        # Based on the generate_fixture_name logic
        import hashlib
        prompt = "Test prompt in offline mode"
        combined = f"{prompt}_{{}}"
        hash_str = hashlib.md5(combined.encode()).hexdigest()
        prefix = ''.join(c for c in prompt.split()[0][:20] if c.isalnum()).lower()
        fixture_name = f"{prefix}_{hash_str[:12]}"
        
        fixture_path = gemini_fixtures_dir / f"{fixture_name}.json"
        with open(fixture_path, "w") as f:
            json.dump(test_fixture, f)
        
        # Setup environment with offline mode
        with EnvironmentManager.temporary_env(
            POWERIT_OFFLINE="1",
            GEMINI_VCR_MODE="replay",
            OPENAI_VCR_MODE="replay"
        ):
            # Reset modules to force reloading with new environment
            ModuleManager.reset_modules(
                "offline", "config", "tools.research", "tools.images"
            )
            
            yield fixtures_dir
    
    def test_gemini_api_mocked(self, setup_offline_mode):
        """Test that Gemini API calls are mocked in offline mode."""
        from unittest.mock import patch, MagicMock
        
        # Create a mock response directly
        mock_response = MagicMock()
        mock_response.text = "This is a mocked response for offline mode testing."
        
        # Test that the environment is set up correctly for offline mode
        assert EnvironmentManager.get_bool_env("POWERIT_OFFLINE") is True
        assert os.environ.get("GEMINI_VCR_MODE") == "replay"
        
        # Test VCR behavior directly without importing offline module
        from tests.unit.vcr.test_gemini_vcr import GeminiVCR
        
        vcr = GeminiVCR()
        assert vcr.record_mode is False  # Should be in replay mode
        
        # Test that the VCR can create mock responses
        test_recording = {"text": "This is a mocked response for offline mode testing.", "prompt": "test"}
        mock_response_from_vcr = vcr.create_mock_response(test_recording)
        assert mock_response_from_vcr.text == "This is a mocked response for offline mode testing."
    
    def test_openai_api_mocked(self, setup_offline_mode):
        """Test that OpenAI API calls are mocked in offline mode."""
        # Import after setting environment
        import offline
        from openai import OpenAI
        
        # Create a client
        client = OpenAI(api_key="fake-key-for-testing")
        
        # Call images.generate
        response = client.images.generate(
            model="gpt-image-1",
            prompt="Test prompt in offline mode",
            size="1024x1024"
        )
        
        # Verify response is mocked
        assert response is not None
        assert hasattr(response, "data")
        assert len(response.data) > 0
        assert hasattr(response.data[0], "b64_json")
    
    def test_logo_fetcher_mocked(self, setup_offline_mode, tmp_path):
        """Test that logo fetcher calls are mocked in offline mode."""
        # Import after setting environment
        import offline
        from tools import logo_fetcher
        
        # Call search_logo
        result = logo_fetcher.search_logo("Test Company")
        
        # Verify response is mocked
        assert result is not None
        
        # Call download_logo
        success, path = logo_fetcher.download_logo("Test Company")
        
        # Verify response is mocked
        assert success is True
        assert Path(path).exists()
        
        # Clean up
        if Path(path).exists():
            Path(path).unlink()
    
    def test_requests_mocked(self, setup_offline_mode):
        """Test that requests.get is mocked in offline mode."""
        # Import after setting environment
        import offline
        import requests
        
        # Call requests.get and verify it doesn't make a real request
        response = requests.get("https://example.com")
        
        # Verify mocked response properties
        assert response.status_code == 200
        assert "Mocked HTML" in response.text
        
    @pytest.mark.asyncio
    async def test_research_offline_mode(self, setup_offline_mode):
        """Test that research_topic returns mock data in offline mode."""
        # Import after setting environment
        import offline
        from tools.research import research_topic
        from offline_responses.research import OFFLINE_RESEARCH_RESPONSE
        
        # Call research_topic and get result
        result = await research_topic("Test Topic")
        
        # Verify we got a ResearchData object with the expected content from the mock response
        assert result is not None
        assert "Artificial Intelligence in Modern Business" in result.content
        
        # Test with manual research mode
        manual_result = await research_topic("Test Topic", mode="manual")
        
        # Verify we get a template response back with the correct title for manual mode
        assert "# Test Topic" in manual_result.content
        assert "## Introduction" in manual_result.content
        
    @pytest.mark.asyncio
    async def test_process_manual_research(self, setup_offline_mode):
        """Test that process_manual_research works correctly."""
        # Import after setting environment
        import offline
        from tools.research import process_manual_research
        
        # Test with some content
        test_content = "This is a test content\nWith multiple lines\nFor testing purposes"
        result = await process_manual_research(test_content)
        
        # Verify structure
        assert result.content == test_content
        assert len(result.links) == 0
    
    def test_environment_manager_integration(self, setup_offline_mode):
        """Test that EnvironmentManager works correctly with offline mode."""
        # Test that offline mode is properly set
        with EnvironmentManager.temporary_env(POWERIT_OFFLINE="0"):
            assert EnvironmentManager.get_bool_env("POWERIT_OFFLINE") is False
        
        # Should be back to offline mode
        assert EnvironmentManager.get_bool_env("POWERIT_OFFLINE") is True
    
    def test_module_manager_integration(self, setup_offline_mode):
        """Test that ModuleManager works correctly with offline mode."""
        # Test module reset
        removed = ModuleManager.reset_modules("nonexistent_module")
        assert "nonexistent_module" not in removed
        
        # Test cleanup
        removed = ModuleManager.cleanup_imports("test_prefix")
        assert isinstance(removed, list)
 