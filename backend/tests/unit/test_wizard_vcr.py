"""
Test file for recording VCR fixtures for wizard API calls.
Run with: ./record_tests.sh tests/unit/test_wizard_vcr.py
"""

import pytest
import json
import asyncio
from pathlib import Path
from tools.wizard.wizard_factory import WizardFactory
from tools.wizard.general_wizard import GeneralWizard
from tools.wizard.research_wizard import ResearchWizard
from tools.wizard.slides_wizard import SlidesWizard


class TestWizardVCR:
    """Test cases for recording wizard API calls with VCR."""
    
    @pytest.fixture
    def wizard_factory(self):
        """Create wizard factory instance."""
        return WizardFactory()
    
    @pytest.fixture
    def sample_presentation_data(self):
        """Sample presentation data for wizard context."""
        return {
            "id": 1,
            "title": "AI in Healthcare",
            "author": "Test Author",
            "steps": [
                {
                    "step": "research",
                    "status": "completed",
                    "result": {
                        "content": "# AI in Healthcare\n\n## Introduction\nAI is transforming healthcare...",
                        "links": []
                    }
                },
                {
                    "step": "slides",
                    "status": "completed",
                    "result": {
                        "title": "AI in Healthcare",
                        "slides": [
                            {
                                "type": "welcome",
                                "fields": {
                                    "title": "AI in Healthcare",
                                    "subtitle": "Transforming Patient Care",
                                    "author": "Test Author"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_general_wizard_vcr(self, wizard_factory, sample_presentation_data):
        """Test and record VCR fixture for general wizard."""
        prompt = "How can I make my presentation more engaging?"
        
        result = await wizard_factory.process_wizard_request(
            prompt=prompt,
            presentation_data=sample_presentation_data,
            current_step="pptx"
        )
        
        assert "response" in result
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
        
        # Save fixture
        fixture_path = Path("tests/fixtures/wizard_general_test.json")
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        with open(fixture_path, "w") as f:
            json.dump({
                "prompt": prompt,
                "current_step": "pptx",
                "response": result
            }, f, indent=2)
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_research_wizard_vcr(self, wizard_factory, sample_presentation_data):
        """Test and record VCR fixture for research wizard."""
        prompt = "Add more information about machine learning applications"
        
        result = await wizard_factory.process_wizard_request(
            prompt=prompt,
            presentation_data=sample_presentation_data,
            current_step="research"
        )
        
        assert "response" in result
        # Research wizard may suggest changes (in offline mode, uses 'suggestions')
        if "suggestions" in result:
            assert "research" in result["suggestions"]
        
        # Save fixture
        fixture_path = Path("tests/fixtures/wizard_research_test.json")
        with open(fixture_path, "w") as f:
            json.dump({
                "prompt": prompt,
                "current_step": "research",
                "response": result
            }, f, indent=2)
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_slides_wizard_vcr(self, wizard_factory, sample_presentation_data):
        """Test and record VCR fixture for slides wizard."""
        prompt = "Add a new slide about AI ethics"
        
        result = await wizard_factory.process_wizard_request(
            prompt=prompt,
            presentation_data=sample_presentation_data,
            current_step="slides",
            context={"current_slide": 0}
        )
        
        assert "response" in result
        # Slides wizard may suggest slide changes (in offline mode, uses 'suggestions')
        if "suggestions" in result:
            # Can be either single slide or presentation-level changes
            assert ("slides" in result["suggestions"] or 
                    "slide" in result["suggestions"] or 
                    "presentation" in result["suggestions"])
        
        # Save fixture
        fixture_path = Path("tests/fixtures/wizard_slides_test.json")
        with open(fixture_path, "w") as f:
            json.dump({
                "prompt": prompt,
                "current_step": "slides",
                "context": {"current_slide": 0},
                "response": result
            }, f, indent=2)
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_wizard_suggestions_vcr(self, wizard_factory, sample_presentation_data):
        """Test and record VCR fixture for wizard suggestions."""
        prompt = "What improvements can you suggest for this slide?"
        
        result = await wizard_factory.process_wizard_request(
            prompt=prompt,
            presentation_data=sample_presentation_data,
            current_step="slides",
            context={
                "current_slide": 0,
                "request_suggestions": True
            }
        )
        
        assert "response" in result
        # Should include suggestions
        if "suggestions" in result:
            # In offline mode, suggestions is a dict, not a list
            assert isinstance(result["suggestions"], (dict, list))
            if isinstance(result["suggestions"], list):
                assert len(result["suggestions"]) > 0
        
        # Save fixture
        fixture_path = Path("tests/fixtures/wizard_suggestions_test.json")
        with open(fixture_path, "w") as f:
            json.dump({
                "prompt": prompt,
                "current_step": "slides",
                "context": {
                    "current_slide": 0,
                    "request_suggestions": True
                },
                "response": result
            }, f, indent=2)