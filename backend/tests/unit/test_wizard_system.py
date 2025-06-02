"""Tests for the wizard system functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from tests.utils import MockFactory, assert_valid_research_data
from tools.wizard.wizard_factory import WizardFactory
from tools.wizard.research_wizard import ResearchWizard
from tools.wizard.slides_wizard import SlidesWizard
from tools.wizard.general_wizard import GeneralWizard


class TestWizardFactory:
    """Test the wizard factory routing logic."""
    
    def test_wizard_factory_initialization(self):
        """Test that wizard factory initializes correctly."""
        factory = WizardFactory()
        assert "research" in factory._wizards
        assert "slides" in factory._wizards
        assert "general" in factory._wizards
        assert isinstance(factory._wizards["research"], ResearchWizard)
        assert isinstance(factory._wizards["slides"], SlidesWizard)
        assert isinstance(factory._wizards["general"], GeneralWizard)
    
    def test_determine_wizard_type_research(self):
        """Test that research step routes to research wizard."""
        factory = WizardFactory()
        wizard_type = factory._determine_wizard_type("research", {})
        assert wizard_type == "research"
        
        wizard_type = factory._determine_wizard_type("Research", {})
        assert wizard_type == "research"
    
    def test_determine_wizard_type_slides(self):
        """Test that slides step routes to slides wizard."""
        factory = WizardFactory()
        wizard_type = factory._determine_wizard_type("slides", {})
        assert wizard_type == "slides"
        
        wizard_type = factory._determine_wizard_type("Slides", {})
        assert wizard_type == "slides"
    
    def test_determine_wizard_type_general(self):
        """Test that other steps route to general wizard."""
        factory = WizardFactory()
        
        for step in ["illustrations", "pptx", "unknown", "other"]:
            wizard_type = factory._determine_wizard_type(step, {})
            assert wizard_type == "general"
    
    @pytest.mark.asyncio
    async def test_process_request_routing(self):
        """Test that requests are routed to correct wizard."""
        factory = WizardFactory()
        
        # Test research routing
        response = await factory.process_wizard_request(
            "Add more information about AI",
            {"id": 1},
            "research"
        )
        assert response["type"] == "research_modification"
        
        # Test slides routing
        response = await factory.process_wizard_request(
            "Add a new slide",
            {"id": 1},
            "slides"
        )
        assert response["type"] in ["slide_modification", "presentation_modification"]
        
        # Test general routing
        response = await factory.process_wizard_request(
            "What is this step?",
            {"id": 1},
            "pptx"
        )
        assert response["type"] == "explanation"


class TestResearchWizard:
    """Test the research wizard functionality."""
    
    def test_research_wizard_capabilities(self):
        """Test research wizard capabilities."""
        wizard = ResearchWizard()
        caps = wizard.get_capabilities()
        
        assert caps["type"] == "research"
        assert caps["can_modify"] is True
        assert caps["can_add_content"] is True
        assert caps["can_answer_questions"] is True
        assert "refine_research" in caps["supported_actions"]
        assert "add_information" in caps["supported_actions"]
    
    def test_extract_research_data(self):
        """Test extracting research data from presentation."""
        wizard = ResearchWizard()
        
        # Test with valid research data
        presentation_data = {
            "steps": [
                {
                    "step": "research",
                    "result": {"content": "Test research", "links": ["http://example.com"]}
                }
            ]
        }
        
        research_data = wizard._extract_research_data(presentation_data)
        assert research_data["content"] == "Test research"
        assert research_data["links"] == ["http://example.com"]
        
        # Test with no research data
        presentation_data = {"steps": []}
        research_data = wizard._extract_research_data(presentation_data)
        assert research_data["content"] == ""
        assert research_data["links"] == []
    
    def test_is_modification_request(self):
        """Test identifying modification requests."""
        wizard = ResearchWizard()
        
        # Test modification keywords
        assert wizard._is_modification_request("add more information") is True
        assert wizard._is_modification_request("improve the research") is True
        assert wizard._is_modification_request("modify this content") is True
        assert wizard._is_modification_request("expand on this topic") is True
        
        # Test non-modification requests
        assert wizard._is_modification_request("what is this about?") is False
        assert wizard._is_modification_request("explain the topic") is False
        assert wizard._is_modification_request("how does this work?") is False
    
    @pytest.mark.asyncio
    async def test_process_research_modification(self, sample_research_data):
        """Test processing research modification requests."""
        wizard = ResearchWizard()
        
        presentation_data = {
            "id": 1,
            "topic": "AI in Healthcare",
            "steps": [
                {
                    "step": "research",
                    "result": sample_research_data.model_dump()
                }
            ]
        }
        
        response = await wizard.process_request(
            "Add more information about machine learning applications",
            presentation_data
        )
        
        assert response["type"] == "research_modification"
        changes = response.get("changes") or response.get("suggestions")
        assert changes is not None
        assert "research" in changes
        assert "content" in changes["research"]
    
    @pytest.mark.asyncio
    async def test_process_research_question(self):
        """Test processing research questions."""
        wizard = ResearchWizard()
        
        presentation_data = {
            "id": 1,
            "topic": "AI in Healthcare",
            "steps": [
                {
                    "step": "research",
                    "result": {"content": "AI is transforming healthcare...", "links": []}
                }
            ]
        }
        
        response = await wizard.process_request(
            "What are the main benefits mentioned?",
            presentation_data
        )
        
        assert response["type"] == "explanation"
        assert "response" in response
        assert len(response["response"]) > 0


class TestSlidesWizard:
    """Test the slides wizard functionality."""
    
    def test_slides_wizard_capabilities(self):
        """Test slides wizard capabilities."""
        wizard = SlidesWizard()
        caps = wizard.get_capabilities()
        
        assert caps["type"] == "slides"
        assert caps["can_modify_single"] is True
        assert caps["can_modify_presentation"] is True
        assert caps["can_add_slides"] is True
        assert caps["can_remove_slides"] is True
        assert "modify_slide_content" in caps["supported_actions"]
        assert "add_new_slide" in caps["supported_actions"]
    
    def test_is_presentation_level_request(self):
        """Test identifying presentation-level requests."""
        wizard = SlidesWizard()
        
        # Test presentation-level keywords
        assert wizard._is_presentation_level_request("add a new slide") is True
        assert wizard._is_presentation_level_request("remove slide about") is True
        assert wizard._is_presentation_level_request("delete this slide") is True
        assert wizard._is_presentation_level_request("reorder the slides") is True
        
        # Test non-presentation-level requests
        assert wizard._is_presentation_level_request("improve this content") is False
        assert wizard._is_presentation_level_request("make it better") is False
        assert wizard._is_presentation_level_request("what is this about?") is False
    
    @pytest.mark.asyncio
    async def test_process_slide_modification(self, sample_slide_presentation):
        """Test processing single slide modification."""
        wizard = SlidesWizard()
        
        presentation_data = {
            "id": 1,
            "steps": [
                {
                    "step": "slides",
                    "result": sample_slide_presentation.model_dump()
                }
            ]
        }
        
        # Add selectedSlide to simulate UI selection
        presentation_data["selectedSlide"] = 3
        
        response = await wizard.process_request(
            "Make this slide more engaging",
            presentation_data
        )
        
        assert response["type"] == "slide_modification"
        assert "slide" in response["changes"]
        assert response["changes"]["slide"]["index"] == 3
    
    @pytest.mark.asyncio
    async def test_process_presentation_modification(self, sample_slide_presentation):
        """Test processing presentation-level modification."""
        wizard = SlidesWizard()
        
        presentation_data = {
            "id": 1,
            "steps": [
                {
                    "step": "slides",
                    "result": sample_slide_presentation.model_dump()
                }
            ]
        }
        
        response = await wizard.process_request(
            "Add a new slide about future trends",
            presentation_data
        )
        
        assert response["type"] == "presentation_modification"
        assert "presentation" in response["changes"]
        assert "slides" in response["changes"]["presentation"]


class TestGeneralWizard:
    """Test the general wizard functionality."""
    
    def test_general_wizard_capabilities(self):
        """Test general wizard capabilities."""
        wizard = GeneralWizard()
        caps = wizard.get_capabilities()
        
        assert caps["type"] == "general"
        assert caps["can_modify"] is False
        assert caps["can_provide_guidance"] is True
        assert caps["can_answer_questions"] is True
        assert "answer_questions" in caps["supported_actions"]
        assert "provide_guidance" in caps["supported_actions"]
    
    @pytest.mark.asyncio
    async def test_process_general_request(self):
        """Test processing general requests."""
        wizard = GeneralWizard()
        
        presentation_data = {
            "id": 1,
            "topic": "Test Topic"
        }
        
        response = await wizard.process_request(
            "What does this step do?",
            presentation_data
        )
        
        assert response["type"] == "explanation"
        assert "response" in response
        assert len(response["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_empty_request(self):
        """Test error handling with empty request."""
        wizard = GeneralWizard()
        
        response = await wizard.process_request("", {})
        
        assert response["type"] == "error"
        assert "error" in response
        assert "empty" in response["error"].lower()