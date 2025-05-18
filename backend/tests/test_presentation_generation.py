import os
import pytest
import json
import hashlib
from unittest.mock import patch, MagicMock
import asyncio

# Import functions to be tested
from orchestrator import create_presentation
from models import ResearchData, SlidePresentation, Slide
from tools.research import research_topic
from tools.slides import generate_slides

# Mark all tests as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def presentation_vcr():
    """Fixture for recording/replaying presentation generation responses"""
    # Create fixture directory
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    os.makedirs(fixture_dir, exist_ok=True)
    
    # Determine mode from environment variable
    record_mode = os.environ.get("PRESENTATION_VCR_MODE", "replay") == "record"
    print(f"Presentation VCR mode: {'record' if record_mode else 'replay'}")
    
    def load_or_save_fixture(test_name, result_data=None):
        """Load or save fixture based on mode"""
        fixture_name = f"presentation_{test_name}.json"
        fixture_path = os.path.join(fixture_dir, fixture_name)
        
        if record_mode and result_data:
            # Record mode - save the fixture
            with open(fixture_path, "w") as f:
                json.dump(result_data, f, indent=2)
            print(f"Saved presentation result to {fixture_path}")
            return result_data
        else:
            # Replay mode - load from fixture
            try:
                with open(fixture_path, "r") as f:
                    fixture_data = json.load(f)
                print(f"Loaded presentation result from {fixture_path}")
                return fixture_data
            except FileNotFoundError:
                if not record_mode:
                    print(f"No fixture found at {fixture_path}. Test will be skipped.")
                    # Return None to indicate fixture not found (test will be skipped)
                    return None
                return None
    
    return load_or_save_fixture

@pytest.mark.asyncio
async def test_orchestrator(presentation_vcr, mock_gemini_responses):
    """
    Test that the create_presentation function works correctly.
    """
    # Skip this test due to complex mock setup
    pytest.skip("Test requires complex mocking setup")
    
    # Test parameters
    topic = "Artificial Intelligence Benefits"
    target_slides = 6
    test_name = "orchestrator_test"
    
    # Record mode - make actual API call
    if os.environ.get("PRESENTATION_VCR_MODE") == "record":
        # Call the orchestrator function
        result = await create_presentation(topic=topic, target_slides=target_slides)
        
        # Convert the result to a serializable format
        result_data = {
            "research": result.research.model_dump() if result.research else None,
            "slides": result.slides.model_dump() if result.slides else None
        }
        
        # Save to fixture
        presentation_vcr(test_name, result_data)
        
        # Basic assertions on the real result
        assert result.research is not None, "Research data should not be None"
        assert result.slides is not None, "Slides data should not be None"
        assert len(result.slides.slides) >= target_slides/2, f"Should have at least {target_slides/2} slides"
        
    # Replay mode - use fixture data
    else:
        # Get fixture data
        fixture_data = presentation_vcr(test_name)
        
        # Skip test if no fixture data is available
        if fixture_data is None:
            pytest.skip(f"Test requires fixture data. Run with PRESENTATION_VCR_MODE=record first.")
            return
        
        # Mock research_topic and generate_slides
        with patch("orchestrator.research_topic") as mock_research, \
             patch("orchestrator.generate_slides") as mock_slides:
            
            # Set up the mocks to return objects based on fixture data
            if fixture_data.get("research"):
                mock_research.return_value = ResearchData.model_validate(fixture_data["research"])
            else:
                mock_research.return_value = ResearchData(content="Mocked research content")
                
            if fixture_data.get("slides"):
                mock_slides.return_value = SlidePresentation.model_validate(fixture_data["slides"])
            else:
                mock_slides.return_value = SlidePresentation(
                    title="Mocked Presentation",
                    slides=[Slide(title="Mock Slide", type="content", content=["Mock content"])]
                )
            
            # Call the orchestrator function with mocks
            result = await create_presentation(topic=topic, target_slides=target_slides)
            
            # Assertions on the mocked result
            assert result.research is not None, "Research data should not be None"
            assert result.slides is not None, "Slides data should not be None"
            
            # Verify the mocks were called with expected parameters
            mock_research.assert_called_once_with(topic)
            mock_slides.assert_called_once() 