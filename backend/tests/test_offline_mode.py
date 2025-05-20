import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pytest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestOfflineMode(unittest.TestCase):
    """Test that the offline mode correctly prevents real API calls."""
    
    def setUp(self):
        # Save original environment
        self.original_powerit_offline = os.environ.get("POWERIT_OFFLINE")
        
        # Set offline mode
        os.environ["POWERIT_OFFLINE"] = "1"
        
        # Reset modules to force reloading with new environment
        if "offline" in sys.modules:
            del sys.modules["offline"]
        if "config" in sys.modules:
            del sys.modules["config"]
        if "tools.research" in sys.modules:
            del sys.modules["tools.research"]
        
        # Create a default fixture for Gemini API calls
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        os.makedirs(fixtures_dir, exist_ok=True)
        
        # Create default test fixture
        test_fixture = {
            "text": "This is a mocked response for offline mode testing.",
            "prompt": "Test prompt in offline mode"
        }
        with open(os.path.join(fixtures_dir, "test_0864ba19df1d.json"), "w") as f:
            json.dump(test_fixture, f)
    
    def tearDown(self):
        # Restore original environment
        if self.original_powerit_offline is not None:
            os.environ["POWERIT_OFFLINE"] = self.original_powerit_offline
        else:
            del os.environ["POWERIT_OFFLINE"]
        
        # Clean up test fixture
        test_fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "test_0864ba19df1d.json")
        if os.path.exists(test_fixture_path):
            os.unlink(test_fixture_path)
    
    def test_gemini_api_mocked(self):
        """Test that Gemini API calls are mocked in offline mode."""
        # Import after setting environment
        import offline
        import google.generativeai as genai
        
        # Create a model
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Call generate_content
        response = model.generate_content("Test prompt in offline mode")
        
        # Verify response is mocked
        self.assertIsNotNone(response)
        self.assertTrue(hasattr(response, "text"))
        self.assertEqual(response.text, "This is a mocked response for offline mode testing.")
    
    def test_openai_api_mocked(self):
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
        self.assertIsNotNone(response)
        self.assertTrue(hasattr(response, "data"))
        self.assertTrue(len(response.data) > 0)
        self.assertTrue(hasattr(response.data[0], "b64_json"))
    
    def test_logo_fetcher_mocked(self):
        """Test that logo fetcher calls are mocked in offline mode."""
        # Import after setting environment
        import offline
        from tools import logo_fetcher
        
        # Call search_logo
        result = logo_fetcher.search_logo("Test Company")
        
        # Verify response is mocked
        self.assertIsNotNone(result)
        
        # Call download_logo
        success, path = logo_fetcher.download_logo("Test Company")
        
        # Verify response is mocked
        self.assertTrue(success)
        self.assertTrue(os.path.exists(path))
        
        # Clean up
        if os.path.exists(path):
            os.unlink(path)
    
    def test_requests_mocked(self):
        """Test that requests.get is mocked in offline mode."""
        # Import after setting environment
        import offline
        import requests
        
        # We can't use unittest's patch because offline.py already applied its own patch
        # Call requests.get and verify it doesn't make a real request
        response = requests.get("https://example.com")
        
        # Verify mocked response properties
        self.assertEqual(response.status_code, 200)
        self.assertIn("Mocked HTML", response.text)
        
    def test_research_offline_mode(self):
        """Test that research_topic returns mock data in offline mode."""
        # Import after setting environment
        import offline
        from tools.research import research_topic, OFFLINE_RESEARCH_RESPONSE
        import asyncio
        
        # Call research_topic and get result
        result = asyncio.run(research_topic("Test Topic"))
        
        # Verify we got a ResearchData object with the expected content from the mock response
        self.assertIsNotNone(result)
        self.assertIn("Artificial Intelligence in Modern Business", result.content)
        
        # Test with manual research mode
        manual_result = asyncio.run(research_topic("Test Topic", mode="manual"))
        
        # Verify we get a template response back with the correct title for manual mode
        self.assertIn("# Test Topic", manual_result.content)
        self.assertIn("## Introduction", manual_result.content)
        
    def test_process_manual_research(self):
        """Test that process_manual_research works correctly."""
        # Import after setting environment
        import offline
        from tools.research import process_manual_research
        import asyncio
        
        # Test with some content
        test_content = "This is a test content\nWith multiple lines\nFor testing purposes"
        result = asyncio.run(process_manual_research(test_content))
        
        # Verify structure
        self.assertEqual(result.content, test_content)
        self.assertEqual(len(result.links), 0)


if __name__ == "__main__":
    unittest.main() 