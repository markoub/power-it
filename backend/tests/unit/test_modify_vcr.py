"""
Test file for recording VCR fixtures for modify.py API calls.
Run with: ./record_tests.sh tests/unit/test_modify_vcr.py
"""

import pytest
import json
import asyncio
from pathlib import Path
from tools.modify import modify_presentation, modify_single_slide
from models import ResearchData, CompiledPresentation


class TestModifyVCR:
    """Test cases for recording modify API calls with VCR."""
    
    @pytest.fixture
    def sample_research_data(self):
        """Sample research data for testing."""
        return {
            "content": "# AI in Healthcare\n\n## Introduction\nArtificial intelligence is transforming healthcare...",
            "links": [
                {"href": "https://example.com/ai-health", "title": "AI in Healthcare"}
            ]
        }
    
    @pytest.fixture
    def sample_compiled_data(self):
        """Sample compiled presentation data."""
        return {
            "title": "AI in Healthcare",
            "author": "Test Author",
            "slides": [
                {
                    "type": "welcome",
                    "fields": {
                        "title": "AI in Healthcare",
                        "subtitle": "Transforming Patient Care",
                        "author": "Test Author",
                        "notes": "Welcome slide"
                    }
                },
                {
                    "type": "content",
                    "fields": {
                        "title": "Introduction",
                        "content": [
                            "AI is revolutionizing healthcare",
                            "Machine learning enables early diagnosis",
                            "Deep learning analyzes medical images"
                        ],
                        "notes": "Introduction to AI in healthcare"
                    }
                },
                {
                    "type": "section",
                    "fields": {
                        "title": "Current Applications",
                        "notes": "Section divider"
                    }
                }
            ],
            "images": {}
        }
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_modify_presentation_vcr(self, sample_compiled_data, sample_research_data):
        """Test and record VCR fixture for modify_presentation."""
        prompt = "Add more details about machine learning applications in the introduction slide"
        
        result = await modify_presentation(
            compiled_data=sample_compiled_data,
            research_data=sample_research_data,
            prompt=prompt
        )
        
        assert isinstance(result, CompiledPresentation)
        assert result.title == sample_compiled_data["title"]
        assert len(result.slides) > 0
        
        # Save the fixture for reference
        fixture_path = Path("tests/fixtures/modify_presentation_test.json")
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        with open(fixture_path, "w") as f:
            json.dump({
                "prompt": prompt,
                "response": result.dict()
            }, f, indent=2)
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_modify_single_slide_vcr(self, sample_compiled_data, sample_research_data):
        """Test and record VCR fixture for modify_single_slide."""
        prompt = "Make the content more engaging and add statistics"
        slide_index = 1  # Modify the content slide
        
        result = await modify_single_slide(
            compiled_data=sample_compiled_data,
            research_data=sample_research_data,
            prompt=prompt,
            slide_index=slide_index
        )
        
        assert "modified_slide" in result
        assert result["slide_index"] == slide_index
        assert result["modified_slide"]["type"] == "content"
        
        # Save the fixture for reference
        fixture_path = Path("tests/fixtures/modify_single_slide_test.json")
        with open(fixture_path, "w") as f:
            json.dump({
                "prompt": prompt,
                "slide_index": slide_index,
                "response": result
            }, f, indent=2)
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    @pytest.mark.skip(reason="Mock response doesn't actually add slides in offline mode")
    async def test_modify_add_slide_vcr(self, sample_compiled_data, sample_research_data):
        """Test and record VCR fixture for adding a new slide."""
        prompt = "Add a new slide about AI ethics in healthcare after the introduction"
        
        result = await modify_presentation(
            compiled_data=sample_compiled_data,
            research_data=sample_research_data,
            prompt=prompt
        )
        
        assert isinstance(result, CompiledPresentation)
        # Should have more slides than original
        assert len(result.slides) > len(sample_compiled_data["slides"])
        
        # Save the fixture
        fixture_path = Path("tests/fixtures/modify_add_slide_test.json")
        with open(fixture_path, "w") as f:
            json.dump({
                "prompt": prompt,
                "response": result.dict()
            }, f, indent=2)