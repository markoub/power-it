import pytest
from models import ResearchData
from tools.research import research_topic, process_manual_research
from tests.utils import assert_valid_research_data

pytestmark = pytest.mark.asyncio

class TestResearchIntegration:
    """Integration tests for the research functionality."""

    async def test_research_topic_integration(self, mock_gemini_responses, mock_config):
        """Test the research_topic function with VCR recording/replaying."""
        topic = "Artificial Intelligence in Healthcare"
        
        # Call research_topic - the VCR fixture will handle record/replay automatically
        result = await research_topic(topic)
        
        # Use the validation helper
        assert_valid_research_data(result)
        
        # Check that the content contains relevant keywords (flexible for offline mode)
        content_lower = result.content.lower()
        has_ai_keywords = any(keyword in content_lower for keyword in [
            "artificial intelligence", "ai", "machine learning", "healthcare", "health"
        ])
        assert has_ai_keywords, f"Content should contain relevant keywords, got: {result.content[:200]}..."

    @pytest.mark.parametrize("topic", [
        "Blockchain Technology 2024",
        "Machine Learning in Finance", 
        "Quantum Computing Applications"
    ])
    async def test_research_topic_various_subjects(self, mock_gemini_responses, mock_config, topic):
        """Test research generation with different topics."""
        result = await research_topic(topic)
        
        # Use the validation helper
        assert_valid_research_data(result)
        
        # Check for general relevant keywords (flexible for offline mode)
        content_lower = result.content.lower()
        has_relevant_keywords = any(keyword in content_lower for keyword in [
            "blockchain", "machine learning", "quantum", "technology", "business", 
            "applications", "finance", "computing", "artificial intelligence", "ai"
        ])
        assert has_relevant_keywords, f"Content should contain relevant keywords for topic '{topic}'"

    async def test_research_topic_multiple_calls(self, mock_gemini_responses, mock_config):
        """Test that multiple research calls work properly."""
        topics = [
            "Artificial Intelligence Benefits",
            "Renewable Energy Solutions",
            "Digital Marketing Trends"
        ]
        
        results = []
        for topic in topics:
            result = await research_topic(topic)
            assert_valid_research_data(result)
            results.append(result)
        
        # Verify all results are valid
        assert len(results) == len(topics), "Should have results for all topics"
        
        # Each result should be substantial
        for i, result in enumerate(results):
            assert len(result.content) > 100, f"Result {i} should be substantial"

    async def test_manual_research_processing(self, mock_config):
        """Test manual research processing without API calls."""
        test_content = """# Manual Research Content

This is a comprehensive manual research about artificial intelligence.

## Key Points

- AI is transforming industries
- Machine learning is a subset of AI
- Neural networks are powerful tools

## Conclusion

AI will continue to evolve and impact our lives."""
        
        result = await process_manual_research(test_content)
        
        # Verify structure
        assert isinstance(result, ResearchData)
        assert result.content == test_content
        assert result.links == []  # Manual research doesn't generate links

    async def test_research_data_model_validation(self):
        """Test ResearchData model validation."""
        # Valid research data
        valid_data = ResearchData(
            content="# Test Research\n\nThis is valid research content with sufficient length.",
            links=[]
        )
        assert_valid_research_data(valid_data)
        
        # Research data with links
        valid_data_with_links = ResearchData(
            content="# Test Research\n\nThis research includes links for further reading.",
            links=[
                {"href": "https://example.com", "title": "Example Link"},
                {"href": "https://test.com", "title": "Test Link"}
            ]
        )
        assert_valid_research_data(valid_data_with_links)

    async def test_research_content_structure(self, mock_gemini_responses, mock_config):
        """Test that research content has proper markdown structure."""
        topic = "Cloud Computing Fundamentals"
        result = await research_topic(topic)
        
        assert_valid_research_data(result)
        
        # Check for markdown structure
        assert "#" in result.content, "Research should contain markdown headers"
        
        # Content should be well-structured
        lines = result.content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) >= 5, "Research should have multiple content lines"

    async def test_research_error_handling(self, mock_config):
        """Test research function handles errors gracefully."""
        # Test with empty topic
        with pytest.raises((ValueError, TypeError)):
            await research_topic("")
        
        # Test with None topic
        with pytest.raises((ValueError, TypeError)):
            await research_topic(None)

    async def test_manual_research_error_handling(self, mock_config):
        """Test manual research handles errors gracefully."""
        # Test with empty content
        with pytest.raises((ValueError, TypeError)):
            await process_manual_research("")
        
        # Test with None content
        with pytest.raises((ValueError, TypeError)):
            await process_manual_research(None) 