"""
Test file for recording VCR fixtures for research clarification API calls.
Run with: ./record_tests.sh tests/unit/test_research_clarification_vcr.py
"""

import pytest
import json
from pathlib import Path
from tools.research import check_clarifications
from routers.research_clarification import check_topic_clarification
from schemas.presentations import ClarificationCheckRequest
from unittest.mock import Mock
from tools.wizard.research_wizard import ResearchWizard


class TestResearchClarificationVCR:
    """Test cases for recording research clarification API calls with VCR."""
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_ambiguous_topic_adk_vcr(self):
        """Test and record VCR fixture for ambiguous topic 'ADK'."""
        topic = "Google ADK"
        
        # Test the direct function
        result = await check_clarifications(topic)
        
        assert result is not None
        assert result.get("needs_clarification") == True
        assert "ADK" in result.get("initial_message", "")
        
        # Save fixture reference
        fixture_path = Path("tests/fixtures/research_clarification_adk.json")
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        with open(fixture_path, "w") as f:
            json.dump({
                "topic": topic,
                "result": result
            }, f, indent=2)
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_ambiguous_topic_sdk_vcr(self):
        """Test and record VCR fixture for ambiguous topic 'SDK'."""
        topic = "Google SDK"
        
        result = await check_clarifications(topic)
        
        assert result is not None
        assert result.get("needs_clarification") == True
        assert "SDK" in result.get("initial_message", "")
        
        # Save fixture reference
        fixture_path = Path("tests/fixtures/research_clarification_sdk.json")
        with open(fixture_path, "w") as f:
            json.dump({
                "topic": topic,
                "result": result
            }, f, indent=2)
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_clear_topic_vcr(self):
        """Test and record VCR fixture for clear topic that doesn't need clarification."""
        topic = "Machine Learning in Healthcare"
        
        result = await check_clarifications(topic)
        
        # Clear topics should return None (no clarification needed)
        assert result is None
        
        # Save fixture reference
        fixture_path = Path("tests/fixtures/research_clarification_clear.json")
        with open(fixture_path, "w") as f:
            json.dump({
                "topic": topic,
                "result": result
            }, f, indent=2)
    
    @pytest.mark.asyncio
    @pytest.mark.vcr_record
    async def test_wizard_clarification_check_vcr(self):
        """Test the wizard's clarification check method."""
        wizard = ResearchWizard()
        
        # Test ambiguous topic
        topic = "API integration"
        result = await wizard.check_topic_clarifications(topic)
        
        assert result is not None
        assert result.get("needs_clarification") == True
        assert "API" in result.get("initial_message", "")
        
        # Test clear topic
        clear_topic = "Python programming tutorial"
        clear_result = await wizard.check_topic_clarifications(clear_topic)
        
        assert clear_result is None
        
        # Save fixture reference
        fixture_path = Path("tests/fixtures/research_wizard_clarification.json")
        with open(fixture_path, "w") as f:
            json.dump({
                "ambiguous_topic": topic,
                "ambiguous_result": result,
                "clear_topic": clear_topic,
                "clear_result": clear_result
            }, f, indent=2)