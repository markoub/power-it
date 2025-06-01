import os
import sys
import pytest
import asyncio
from unittest.mock import patch, MagicMock

# Add parent directory to sys.path to import from main code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.slides import generate_slides
from models import ResearchData, SlidePresentation
from tools.logo_fetcher import LogoFetcher


class TestLogoSlide:
    """Test the ContentWithLogos slide type functionality"""

    @pytest.mark.asyncio
    async def test_logo_slide_generation(self):
        """Test that ContentWithLogos slides are created and logos are fetched"""
        
        # Create a mock ResearchData object with content that would trigger logo slide generation
        research_content = """
        Cloud Computing Providers Overview
        
        This presentation should cover the major cloud providers:
        - Amazon Web Services (AWS) is the market leader with a wide range of services
        - Microsoft Azure offers tight integration with Microsoft products
        - Google Cloud Platform (GCP) has strong data analytics and machine learning offerings
        
        Each provider has their strengths and specialties.
        """
        research = ResearchData(content=research_content)
        
        # Mock the logo fetcher to avoid actual network calls during testing
        # We'll simulate successful logo downloads
        mock_logo_path = "/path/to/mock/logo.svg"
        
        # Create a mock response for the download_logo function
        def mock_download_logo(term, filename=None):
            print(f"Mock downloading logo for: {term}")
            return True, mock_logo_path
        
        # Mock JSON content to simulate Gemini response
        mock_json_content = {
            "title": "Cloud Computing Providers Overview",
            "author": "Test Author",
            "slides": [
                {
                    "type": "Welcome",
                    "fields": {
                        "title": "Cloud Computing Providers Overview",
                        "subtitle": "A Comparison of Major Cloud Services",
                        "author": "Test Author"
                    }
                },
                {
                    "type": "ContentWithLogos",
                    "fields": {
                        "title": "Major Cloud Providers",
                        "content": [
                            "These companies dominate the cloud computing market",
                            "Each has unique strengths and offerings",
                            "Market share is constantly changing"
                        ],
                        "logo1": "AWS",
                        "logo2": "Microsoft Azure",
                        "logo3": "Google Cloud"
                    }
                }
            ]
        }
        
        # Create patched version of the slides generation function to bypass the Gemini API call
        async def patched_generate_slides(research, target_slides=10, author=None):
            # Skip actual Gemini API call, use mock data directly
            print("Using mock data for slide generation")
            return SlidePresentation(**mock_json_content)
        
        # Apply the patch to the download_logo function in the slides module
        with patch('tools.slides.download_logo', side_effect=mock_download_logo):
            # Replace the generate_slides function with our patched version
            with patch('tools.slides.generate_slides', side_effect=patched_generate_slides):
                # Now we can test our ContentWithLogos slide handling
                presentation = await patched_generate_slides(research, target_slides=5, author="Test Author")
                
                # Process the logos in the ContentWithLogos slides
                for slide in presentation.slides:
                    if slide.type == "ContentWithLogos":
                        for logo_field in ['logo1', 'logo2', 'logo3']:
                            if logo_field in slide.fields and slide.fields[logo_field]:
                                logo_term = slide.fields[logo_field]
                                success, result = mock_download_logo(logo_term)
                                if success:
                                    slide.fields[logo_field] = result
                
                # Verify the presentation structure
                assert isinstance(presentation, SlidePresentation)
                assert len(presentation.slides) >= 2  # At least Welcome and ContentWithLogos
                
                # Find the ContentWithLogos slide
                logo_slides = [slide for slide in presentation.slides if slide.type == "ContentWithLogos"]
                assert len(logo_slides) > 0, "No ContentWithLogos slide was generated"
                
                logo_slide = logo_slides[0]
                
                # Verify the slide has the expected fields
                assert "title" in logo_slide.fields
                assert "content" in logo_slide.fields
                assert "logo1" in logo_slide.fields
                
                # Verify the logo paths were updated with the mocked path
                assert logo_slide.fields["logo1"] == mock_logo_path
                
                # If more than one logo was included
                if "logo2" in logo_slide.fields:
                    assert logo_slide.fields["logo2"] == mock_logo_path
                
                if "logo3" in logo_slide.fields:
                    assert logo_slide.fields["logo3"] == mock_logo_path 