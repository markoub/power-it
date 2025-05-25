import os
import pytest
import sys
import json
from unittest.mock import patch, MagicMock
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use the test_config instead of the real config
import tests.test_config as test_config
sys.modules['config'] = test_config

from models import ResearchData
from tools.research import research_topic, RESEARCH_SCHEMA
from dotenv import load_dotenv

# Mark all tests as async
pytestmark = pytest.mark.asyncio

class TestStructuredOutput:
    """Tests for structured output implementation in research functionality"""
    
    async def test_research_schema_structure(self):
        """Test that the research schema follows Google AI structured output format"""
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
    
    @patch('tools.research.OFFLINE_MODE', False)
    @patch('google.generativeai.GenerativeModel')
    async def test_structured_output_configuration(self, mock_model_class):
        """Test that the model is configured with structured output schema"""
        # Mock the model and response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "content": "# Test Topic\n\nThis is test content.",
            "links": [{"href": "https://example.com", "title": "Example"}]
        })
        mock_model.generate_content.return_value = mock_response
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
        assert isinstance(result, ResearchData)
        assert result.content == "# Test Topic\n\nThis is test content."
        assert len(result.links) == 1
        assert result.links[0]["href"] == "https://example.com"
        assert result.links[0]["title"] == "Example"
    
    @patch('tools.research.OFFLINE_MODE', False)
    @patch('google.generativeai.GenerativeModel')
    async def test_structured_output_json_parsing(self, mock_model_class):
        """Test that structured output JSON is parsed correctly"""
        # Mock the model and response with valid JSON
        mock_model = MagicMock()
        mock_response = MagicMock()
        test_data = {
            "content": "# AI in Healthcare\n\n## Introduction\n\nAI is transforming healthcare...",
            "links": [
                {"href": "https://healthcare.ai", "title": "Healthcare AI"},
                {"href": "https://medical.research", "title": "Medical Research"}
            ]
        }
        mock_response.text = json.dumps(test_data)
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Call research_topic
        result = await research_topic("AI in Healthcare", mode="ai")
        
        # Verify the result structure
        assert isinstance(result, ResearchData)
        assert result.content == test_data["content"]
        assert len(result.links) == 2
        assert result.links[0]["href"] == "https://healthcare.ai"
        assert result.links[0]["title"] == "Healthcare AI"
        assert result.links[1]["href"] == "https://medical.research"
        assert result.links[1]["title"] == "Medical Research"
    
    @patch('tools.research.OFFLINE_MODE', False)
    @patch('google.generativeai.GenerativeModel')
    async def test_structured_output_error_handling(self, mock_model_class):
        """Test error handling when structured output fails"""
        # Mock the model to raise an exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        # Call research_topic
        result = await research_topic("Test Topic", mode="ai")
        
        # Verify fallback response
        assert isinstance(result, ResearchData)
        assert "error" in result.content.lower()
        assert "Test Topic" in result.content
        assert len(result.links) == 0
    
    async def test_offline_mode_bypass(self):
        """Test that offline mode bypasses structured output and returns fixed response"""
        # This test runs in offline mode by default due to test_config
        result = await research_topic("Any Topic", mode="ai")
        
        # Verify we get the fixed offline response
        assert isinstance(result, ResearchData)
        assert "Artificial Intelligence in Modern Business" in result.content
        assert len(result.links) == 0  # Offline mode returns empty links
    
    async def test_manual_mode_bypass(self):
        """Test that manual mode bypasses structured output"""
        result = await research_topic("Manual Topic", mode="manual")
        
        # Verify we get a template response
        assert isinstance(result, ResearchData)
        assert "Manual Topic" in result.content
        assert "template" in result.content.lower()
        assert len(result.links) == 0
    
    @patch('tools.research.OFFLINE_MODE', False)
    @patch('google.generativeai.GenerativeModel')
    async def test_structured_output_with_empty_links(self, mock_model_class):
        """Test structured output with empty links array"""
        # Mock the model and response with empty links
        mock_model = MagicMock()
        mock_response = MagicMock()
        test_data = {
            "content": "# Test Content\n\nThis is a test with no external sources.",
            "links": []
        }
        mock_response.text = json.dumps(test_data)
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Call research_topic
        result = await research_topic("Test Topic", mode="ai")
        
        # Verify the result structure
        assert isinstance(result, ResearchData)
        assert result.content == test_data["content"]
        assert len(result.links) == 0
    
    @patch('tools.research.OFFLINE_MODE', False)
    @patch('google.generativeai.GenerativeModel')
    async def test_structured_output_malformed_json_handling(self, mock_model_class):
        """Test handling of malformed JSON response"""
        # Mock the model to return malformed JSON
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"content": "Test", "links": [malformed'  # Malformed JSON
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Call research_topic
        result = await research_topic("Test Topic", mode="ai")
        
        # Verify fallback response
        assert isinstance(result, ResearchData)
        assert "error" in result.content.lower()
        assert len(result.links) == 0 