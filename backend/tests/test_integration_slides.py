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

from models import ResearchData, SlidePresentation
from tools.slides import generate_slides
from dotenv import load_dotenv

# Mark all tests as async
pytestmark = pytest.mark.asyncio

class TestSlidesIntegration:
    """Integration tests for the slides generation functionality"""
    
    async def test_slides_generation_integration(self):
        """Test the generate_slides function with recording/replaying"""
        # Sample research data
        research_content = """
        # Artificial Intelligence in Healthcare
        
        ## Introduction
        Artificial Intelligence (AI) is revolutionizing healthcare by improving diagnosis, 
        treatment plans, and patient outcomes.
        
        ## Current Applications
        - Medical imaging analysis
        - Predictive analytics for patient outcomes
        - Virtual health assistants
        - Drug discovery
        
        ## Benefits
        - Faster and more accurate diagnoses
        - Reduced healthcare costs
        - Personalized treatment plans
        - Improved patient outcomes
        
        ## Challenges
        - Data privacy concerns
        - Regulatory hurdles
        - Integration with existing systems
        - Physician adoption
        
        ## Future Directions
        The future of AI in healthcare includes advanced robotics, 
        real-time monitoring, and fully personalized medicine.
        """
        
        research = ResearchData(content=research_content)
        author = "Test Author"
        target_slides = 5
        
        # Create fixture path
        fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        os.makedirs(fixture_dir, exist_ok=True)
        
        # Create a deterministic fixture name
        topic_hash = hashlib.md5("AI_Healthcare".encode()).hexdigest()[:12]
        fixture_name = f"slides_{topic_hash}"
        fixture_path = os.path.join(fixture_dir, f"{fixture_name}.json")
        
        # Check if we're in record mode or replay mode
        record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
        
        if record_mode:
            print(f"Recording mode: generating new slides")
            # Record: Make the actual API call
            result = await generate_slides(research, target_slides=target_slides, author=author)
            
            # Save the response
            fixture_data = result.model_dump()
            
            with open(fixture_path, "w") as f:
                json.dump(fixture_data, f, indent=2)
                
            print(f"Saved fixture to {fixture_path}")
        else:
            print(f"Replay mode: using saved response from {fixture_path}")
            # Replay: Load from fixture
            try:
                with open(fixture_path, "r") as f:
                    fixture_data = json.load(f)
                
                # Create a SlidePresentation object from the fixture
                result = SlidePresentation.model_validate(fixture_data)
            except FileNotFoundError:
                raise ValueError(
                    f"No fixture found at {fixture_path}. Run with GEMINI_VCR_MODE=record first."
                )
        
        # Verify we got a proper SlidePresentation object
        assert isinstance(result, SlidePresentation)
        assert result.title, "Presentation title should not be empty"
        assert result.author == author, "Author should match input"
        assert len(result.slides) >= 4, "Should have at least 4 slides"
        
        # Check that slides have the right types
        slide_types = [slide.type for slide in result.slides]
        assert "Welcome" in slide_types, "Should have a Welcome slide"
        assert "TableOfContents" in slide_types, "Should have a TableOfContents slide"
        assert "Section" in slide_types, "Should have at least one Section slide"
        # Check for either Content or ContentImage slide types
        assert any(slide_type in slide_types for slide_type in ["Content", "ContentImage"]), "Should have at least one Content or ContentImage slide"
        
        # Check that the slides contain relevant content
        slides_content = ' '.join([str(slide.fields) for slide in result.slides])
        assert "AI" in slides_content or "Artificial Intelligence" in slides_content
        assert "Healthcare" in slides_content or "health" in slides_content.lower() 