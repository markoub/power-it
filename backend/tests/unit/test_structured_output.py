"""Tests for structured output implementation in research functionality."""

import pytest
import json
from unittest.mock import patch, MagicMock

from tests.utils import MockFactory, assert_valid_research_data, EnvironmentManager
from models import ResearchData
from tools.research import research_topic, RESEARCH_SCHEMA


class TestStructuredOutput:
    """Tests for structured output implementation in research functionality."""
    
    def test_research_schema_structure(self):
        """Test that the research schema follows Google AI structured output format."""
        # Verify schema has required structure
        assert "type" in RESEARCH_SCHEMA
        assert RESEARCH_SCHEMA["type"] == "object"
        assert "properties" in RESEARCH_SCHEMA
        assert "required" in RESEARCH_SCHEMA
        
        # Verify content property
        assert "content" in RESEARCH_SCHEMA["properties"]
        content_prop = RESEARCH_SCHEMA["properties"]["content"]
        assert content_prop["type"] == "string"
        assert "description" in content_prop
        
        # Verify links property
        assert "links" in RESEARCH_SCHEMA["properties"]
        links_prop = RESEARCH_SCHEMA["properties"]["links"]
        assert links_prop["type"] == "array"
        assert "items" in links_prop
        
        # Verify links items structure
        link_item = links_prop["items"]
        assert link_item["type"] == "object"
        assert "properties" in link_item
        assert "href" in link_item["properties"]
        assert "title" in link_item["properties"]
        assert "required" in link_item
        
        # Verify required fields
        assert "content" in RESEARCH_SCHEMA["required"]
        assert "links" in RESEARCH_SCHEMA["required"]
    
    @pytest.mark.asyncio
    async def test_structured_output_configuration(self):
        """Test that the model is configured with structured output schema."""
        # Mock the model and response
        mock_response = {
            "content": "# Test Topic\n\nThis is comprehensive test content for research validation. " +
                      "It includes multiple sections and detailed information to ensure the " +
                      "research data meets the minimum length requirements for proper validation. " +
                      "This content is structured to provide meaningful research output that can " +
                      "be used for generating high-quality presentation slides.",
            "links": [{"href": "https://example.com", "title": "Example"}]
        }
        
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[mock_response]
        )
        
        # Temporarily disable offline mode
        import tools.research
        original_offline_mode = tools.research.OFFLINE_MODE
        tools.research.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model_class.return_value = mock_model
                
                # Call research_topic
                result = await research_topic("Test Topic", mode="ai")
                
                # Verify model was created with structured output configuration
                mock_model_class.assert_called_once()
                call_args = mock_model_class.call_args
                
                # Check that generation_config includes response_schema
                generation_config = call_args[1]['generation_config']
                assert 'response_schema' in generation_config
                assert generation_config['response_schema'] == RESEARCH_SCHEMA
                
                # Verify the result
                assert_valid_research_data(result)
                assert "Test Topic" in result.content
                
        finally:
            tools.research.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_structured_output_json_parsing(self):
        """Test that structured output JSON is parsed correctly."""
        # Mock response with valid JSON
        test_data = {
            "content": "# AI in Healthcare\n\n## Introduction\n\nAI is transforming healthcare " +
                      "through advanced machine learning algorithms, predictive analytics, and " +
                      "automated diagnostic systems. These technologies are revolutionizing patient " +
                      "care, medical research, and healthcare administration by providing more " +
                      "accurate diagnoses, personalized treatment plans, and efficient resource " +
                      "management across healthcare institutions worldwide.",
            "links": [
                {"href": "https://healthcare.ai", "title": "Healthcare AI"},
                {"href": "https://medical.research", "title": "Medical Research"}
            ]
        }
        
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[test_data]
        )
        
        # Temporarily disable offline mode
        import tools.research
        original_offline_mode = tools.research.OFFLINE_MODE
        tools.research.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Call research_topic
                result = await research_topic("AI in Healthcare", mode="ai")
                
                # Verify the result structure
                assert_valid_research_data(result)
                assert result.content == test_data["content"]
                assert len(result.links) == 2
                assert result.links[0]["href"] == "https://healthcare.ai"
                assert result.links[0]["title"] == "Healthcare AI"
                assert result.links[1]["href"] == "https://medical.research"
                assert result.links[1]["title"] == "Medical Research"
                
        finally:
            tools.research.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_structured_output_error_handling(self):
        """Test error handling when structured output fails."""
        # Mock the model to raise an exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        
        # Temporarily disable offline mode
        import tools.research
        original_offline_mode = tools.research.OFFLINE_MODE
        tools.research.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Call research_topic
                result = await research_topic("Test Topic", mode="ai")
                
                # Verify fallback response
                assert isinstance(result, ResearchData)
                assert "error" in result.content.lower()
                assert "Test Topic" in result.content
                assert len(result.links) == 0
                
        finally:
            tools.research.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_offline_mode_bypass(self):
        """Test that offline mode bypasses structured output and returns fixed response."""
        # Enable offline mode
        import tools.research
        original_offline_mode = tools.research.OFFLINE_MODE
        tools.research.OFFLINE_MODE = True
        
        try:
            result = await research_topic("Any Topic", mode="ai")
            
            # Verify we get the fixed offline response
            assert isinstance(result, ResearchData)
            assert "Artificial Intelligence in Modern Business" in result.content
            assert len(result.links) == 0  # Offline mode returns empty links
            
        finally:
            tools.research.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_manual_mode_bypass(self):
        """Test that manual mode bypasses structured output."""
        result = await research_topic("Manual Topic", mode="manual")
        
        # Verify we get a template response
        assert isinstance(result, ResearchData)
        assert "Manual Topic" in result.content
        assert "template" in result.content.lower()
        assert len(result.links) == 0
    
    @pytest.mark.asyncio
    async def test_structured_output_with_empty_links(self):
        """Test structured output with empty links array."""
        # Mock response with empty links
        test_data = {
            "content": "# Test Content\n\nThis is comprehensive test content that demonstrates " +
                      "research capabilities without requiring external sources. It includes " +
                      "detailed analysis, multiple perspectives, and thorough explanations that " +
                      "provide value even without reference links. This content serves as an " +
                      "example of self-contained research that meets quality standards.",
            "links": []
        }
        
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[test_data]
        )
        
        # Temporarily disable offline mode
        import tools.research
        original_offline_mode = tools.research.OFFLINE_MODE
        tools.research.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Call research_topic
                result = await research_topic("Test Topic", mode="ai")
                
                # Verify the result structure
                assert_valid_research_data(result)
                assert result.content == test_data["content"]
                assert len(result.links) == 0
                
        finally:
            tools.research.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_structured_output_malformed_json_handling(self):
        """Test handling of malformed JSON response."""
        # Mock the model to return malformed JSON
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"content": "Test", "links": [malformed'  # Malformed JSON
        mock_model.generate_content.return_value = mock_response
        
        # Temporarily disable offline mode
        import tools.research
        original_offline_mode = tools.research.OFFLINE_MODE
        tools.research.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Call research_topic
                result = await research_topic("Test Topic", mode="ai")
                
                # Verify fallback response
                assert isinstance(result, ResearchData)
                assert "error" in result.content.lower()
                assert len(result.links) == 0
                
        finally:
            tools.research.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_structured_output_with_invalid_links(self):
        """Test handling of invalid link objects."""
        # Mock response with invalid links
        test_data = {
            "content": "# Test Content\n\nThis is comprehensive test content that includes " +
                      "detailed research analysis with mixed quality reference links. The content " +
                      "itself provides substantial value through thorough examination of the topic, " +
                      "comprehensive coverage of key points, and detailed explanations that meet " +
                      "the minimum content length requirements for proper validation testing.",
            "links": [
                {"href": "https://valid.com", "title": "Valid Link"},
                {"missing": "href field"},  # Invalid link
                {"href": "not-a-url", "title": "Invalid URL"}  # Invalid URL format
            ]
        }
        
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[test_data]
        )
        
        # Temporarily disable offline mode
        import tools.research
        original_offline_mode = tools.research.OFFLINE_MODE
        tools.research.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Call research_topic
                result = await research_topic("Test Topic", mode="ai")
                
                # Should handle gracefully and return valid content
                assert isinstance(result, ResearchData)
                assert "Test Content" in result.content
                # Links validation is handled by assert_valid_research_data
                
        finally:
            tools.research.OFFLINE_MODE = original_offline_mode
    
    @pytest.mark.asyncio
    async def test_structured_output_large_content(self):
        """Test handling of large content responses."""
        # Create large content
        large_content = "# Large Document\n\n" + "\n".join([
            f"## Section {i}\n\nThis is paragraph {i} with lots of content." * 10
            for i in range(20)
        ])
        
        test_data = {
            "content": large_content,
            "links": [
                {"href": f"https://source{i}.com", "title": f"Source {i}"}
                for i in range(10)
            ]
        }
        
        mock_model = MockFactory.create_gemini_mock_model(
            responses=[test_data]
        )
        
        # Temporarily disable offline mode
        import tools.research
        original_offline_mode = tools.research.OFFLINE_MODE
        tools.research.OFFLINE_MODE = False
        
        try:
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                # Call research_topic
                result = await research_topic("Large Topic", mode="ai")
                
                # Verify large content is handled
                assert_valid_research_data(result)
                assert len(result.content) > 1000
                assert len(result.links) == 10
                
        finally:
            tools.research.OFFLINE_MODE = original_offline_mode