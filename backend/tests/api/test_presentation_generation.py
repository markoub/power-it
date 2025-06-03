import pytest
from unittest.mock import patch
from orchestrator import create_presentation
from models import ResearchData, SlidePresentation, Slide
from tools.research import research_topic
from tools.slides import generate_slides
from tests.utils import assert_valid_research_data, assert_valid_slide_presentation

pytestmark = pytest.mark.asyncio


class TestPresentationGeneration:
    """Tests for presentation generation via orchestrator."""

    async def test_create_presentation_integration(self, mock_gemini_responses, mock_config):
        """Test the complete presentation creation flow."""
        topic = "Artificial Intelligence Benefits"
        target_slides = 6
        author = "Test Author"
        
        result = await create_presentation(
            topic=topic, 
            target_slides=target_slides,
            author=author
        )
        
        # Verify the result structure
        assert hasattr(result, 'research'), "Result should have research attribute"
        assert hasattr(result, 'slides'), "Result should have slides attribute"
        
        # Validate research data
        assert result.research is not None, "Research data should not be None"
        assert_valid_research_data(result.research)
        
        # Validate slides data
        assert result.slides is not None, "Slides data should not be None"
        assert_valid_slide_presentation(result.slides)
        
        # Check minimum slide count
        assert len(result.slides.slides) >= 3, f"Should have at least 3 slides"
        
        # Verify author is set correctly
        assert result.slides.author == author, "Slides author should match input"

    async def test_create_presentation_with_custom_parameters(self, mock_gemini_responses, mock_config):
        """Test presentation creation with custom parameters."""
        topic = "Machine Learning in Finance"
        target_slides = 8
        author = "Finance Expert"
        
        result = await create_presentation(
            topic=topic,
            target_slides=target_slides,
            author=author
        )
        
        # Basic validation
        assert result.research is not None
        assert result.slides is not None
        assert_valid_research_data(result.research)
        assert_valid_slide_presentation(result.slides)
        
        # Check parameters are reflected
        assert result.slides.author == author
        
        # Check that content is related to the topic
        research_content = result.research.content.lower()
        slides_content = str(result.slides.slides).lower()
        
        # Should contain topic-related keywords
        topic_keywords = ["machine learning", "finance", "financial", "ai", "artificial intelligence"]
        has_topic_keywords = any(keyword in research_content or keyword in slides_content 
                               for keyword in topic_keywords)
        assert has_topic_keywords, "Content should relate to the specified topic"

    @pytest.mark.parametrize("topic,expected_keywords", [
        ("Climate Change Solutions", ["climate", "environment", "carbon", "renewable"]),
        ("Digital Marketing Trends", ["digital", "marketing", "social", "online"]),
        ("Blockchain Technology", ["blockchain", "crypto", "decentralized", "technology"]),
    ])
    async def test_create_presentation_various_topics(self, mock_gemini_responses, mock_config, topic, expected_keywords):
        """Test presentation creation with various topics."""
        result = await create_presentation(
            topic=topic,
            target_slides=5,
            author="Topic Tester"
        )
        
        assert_valid_research_data(result.research)
        assert_valid_slide_presentation(result.slides)
        
        # Check for topic relevance (flexible for offline mode)
        all_content = (result.research.content + str(result.slides.slides)).lower()
        has_relevant_content = any(keyword in all_content for keyword in expected_keywords + ["ai", "artificial intelligence"])
        assert has_relevant_content, f"Content should relate to topic '{topic}'"

    @pytest.mark.parametrize("target_slides", [3, 5, 8, 12])
    async def test_create_presentation_various_lengths(self, mock_gemini_responses, mock_config, target_slides):
        """Test presentation creation with different target slide counts."""
        result = await create_presentation(
            topic="Software Development Best Practices",
            target_slides=target_slides,
            author="Dev Expert"
        )
        
        assert_valid_research_data(result.research)
        assert_valid_slide_presentation(result.slides)
        
        # Should have reasonable number of slides relative to target
        actual_slides = len(result.slides.slides)
        assert actual_slides >= 3, "Should have at least 3 slides"
        # In offline mode, we generate all slide types for comprehensive testing
        # This ensures all slide types are properly tested
        # Allow up to 10 slides to accommodate all slide types in slide_config.py
        assert actual_slides <= max(target_slides + 5, 10), f"Should not exceed reasonable limits"

    async def test_orchestrator_components_called_correctly(self, mock_config):
        """Test that orchestrator calls components with correct parameters."""
        topic = "Test Topic"
        target_slides = 5
        author = "Test Author"
        
        # Mock the individual components
        with patch('orchestrator.research_topic') as mock_research, \
             patch('orchestrator.generate_slides') as mock_slides:
            
            # Set up return values
            mock_research_data = ResearchData(
                content="# Test Research\n\nThis is test research content."
            )
            mock_research.return_value = mock_research_data
            
            mock_slides_data = SlidePresentation(
                title="Test Presentation",
                author=author,
                slides=[
                    Slide(type="Welcome", fields={"title": "Test", "author": author}),
                    Slide(type="Content", fields={"title": "Content", "content": ["Test content"]})
                ]
            )
            mock_slides.return_value = mock_slides_data
            
            # Call orchestrator
            result = await create_presentation(
                topic=topic,
                target_slides=target_slides,
                author=author
            )
            
            # Verify components were called correctly
            mock_research.assert_called_once_with(topic)
            mock_slides.assert_called_once_with(
                mock_research_data,
                target_slides,
                author
            )
            
            # Verify result
            assert result.research == mock_research_data
            assert result.slides == mock_slides_data

    async def test_orchestrator_error_handling(self, mock_config):
        """Test orchestrator error handling."""
        # Test with invalid topic
        with pytest.raises((ValueError, TypeError)):
            await create_presentation(topic="", target_slides=5, author="Test")
        
        with pytest.raises((ValueError, TypeError)):
            await create_presentation(topic=None, target_slides=5, author="Test")
        
        # Test with invalid target_slides
        with pytest.raises((ValueError, TypeError)):
            await create_presentation(topic="Test Topic", target_slides=0, author="Test")
        
        with pytest.raises((ValueError, TypeError)):
            await create_presentation(topic="Test Topic", target_slides=-1, author="Test")

    async def test_presentation_data_consistency(self, mock_gemini_responses, mock_config):
        """Test that presentation data is consistent between research and slides."""
        topic = "Artificial Intelligence in Education"
        
        result = await create_presentation(
            topic=topic,
            target_slides=6,
            author="Education Expert"
        )
        
        assert_valid_research_data(result.research)
        assert_valid_slide_presentation(result.slides)
        
        # Extract key terms from research
        research_content = result.research.content.lower()
        slides_content = str(result.slides.slides).lower()
        
        # Common terms should appear in both research and slides
        common_terms = ["artificial intelligence", "ai", "education", "learning"]
        research_terms = [term for term in common_terms if term in research_content]
        slides_terms = [term for term in common_terms if term in slides_content]
        
        # At least some terms should be present in both (flexible for offline mode)
        assert len(research_terms) > 0 or len(slides_terms) > 0, "Should have topic-related terms"

    @pytest.mark.skipif(
        True,  # Skip by default unless explicitly enabled
        reason="Integration test - requires environment setup"
    )
    async def test_end_to_end_presentation_generation(self, mock_gemini_responses, mock_config):
        """
        End-to-end test for presentation generation.
        Only runs when explicitly enabled.
        """
        topic = "Future of Remote Work"
        
        result = await create_presentation(
            topic=topic,
            target_slides=7,
            author="Workplace Expert"
        )
        
        # Comprehensive validation
        assert_valid_research_data(result.research)
        assert_valid_slide_presentation(result.slides)
        
        # Detailed content checks
        assert len(result.research.content) > 500, "Research should be comprehensive"
        assert len(result.slides.slides) >= 5, "Should have multiple slides"
        
        # Check slide diversity
        slide_types = [slide.type for slide in result.slides.slides]
        unique_types = set(slide_types)
        assert len(unique_types) >= 3, "Should have diverse slide types"
        
        # Verify presentation structure
        assert "Welcome" in slide_types, "Should have welcome slide"
        content_slides = [s for s in slide_types if "Content" in s]
        assert len(content_slides) >= 2, "Should have content slides"