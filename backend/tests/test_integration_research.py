import os
import pytest
import sys
import json
import hashlib
from unittest.mock import patch, MagicMock
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use the test_config instead of the real config
# We need to patch this before importing other modules
import tests.test_config as test_config
sys.modules['config'] = test_config

from models import ResearchData
from tools.research import research_topic
from dotenv import load_dotenv

# Mark all tests as async
pytestmark = pytest.mark.asyncio

class TestResearchIntegration:
    """Integration tests for the research functionality"""
    
    async def test_research_topic_integration(self):
        """Test the research_topic function with recording/replaying"""
        # Run the research function
        topic = "Artificial Intelligence in Healthcare"
        
        # Create fixture path
        fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        os.makedirs(fixture_dir, exist_ok=True)
        
        # Create a deterministic fixture name
        hash_obj = hashlib.md5(topic.encode())
        fixture_name = f"research_{hash_obj.hexdigest()[:12]}"
        fixture_path = os.path.join(fixture_dir, f"{fixture_name}.json")
        
        # Check if we're in record mode or replay mode
        record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
        
        if record_mode:
            print(f"Recording mode: generating new response for topic '{topic}'")
            # Record: Make the actual API call
            result = await research_topic(topic)
            
            # Save the response
            fixture_data = {
                "content": result.content,
                "links": [link.model_dump() for link in result.links] if result.links else []
            }
            
            with open(fixture_path, "w") as f:
                json.dump(fixture_data, f, indent=2)
                
            print(f"Saved fixture to {fixture_path}")
        else:
            print(f"Replay mode: using saved response from {fixture_path}")
            # Replay: Load from fixture
            try:
                with open(fixture_path, "r") as f:
                    fixture_data = json.load(f)
                
                # Create a ResearchData object from the fixture
                result = ResearchData(
                    content=fixture_data["content"],
                    links=fixture_data["links"]
                )
            except FileNotFoundError:
                raise ValueError(
                    f"No fixture found at {fixture_path}. Run with GEMINI_VCR_MODE=record first."
                )
        
        # Verify we got a proper ResearchData object
        assert isinstance(result, ResearchData)
        assert result.content, "Research content should not be empty"
        
        # Basic validation of content
        assert len(result.content) > 100, "Research content should be substantial"
        
        # Check that the content contains the topic keywords
        assert "Artificial Intelligence" in result.content or "AI" in result.content
        assert "Healthcare" in result.content or "health" in result.content.lower()
        
        # Verify links if present
        if result.links:
            assert isinstance(result.links, list)
            for link in result.links:
                assert hasattr(link, "href"), "Each link should have an href"
                assert hasattr(link, "title"), "Each link should have a title" 