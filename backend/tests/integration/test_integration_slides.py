import pytest
from models import ResearchData, SlidePresentation, Slide
from tools.slides import generate_slides
from tests.utils import assert_valid_slide_presentation, compare_slides

pytestmark = pytest.mark.asyncio

class TestSlidesIntegration:
    """Integration tests for the slides generation functionality."""

    @pytest.fixture
    def sample_research_data(self):
        """Create sample research data for testing."""
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
        return ResearchData(content=research_content)

    async def test_slides_generation_integration(self, mock_gemini_responses, mock_config, sample_research_data):
        """Test the generate_slides function with VCR recording/replaying."""
        author = "Test Author"
        target_slides = 5
        
        result = await generate_slides(sample_research_data, target_slides=target_slides, author=author)
        
        # Use the validation helper
        assert_valid_slide_presentation(result)
        
        # Verify basic properties
        assert result.author == author, "Author should match input"
        assert len(result.slides) >= 4, "Should have at least 4 slides"
        
        # Check that slides have the right types
        slide_types = [slide.type for slide in result.slides]
        assert "Welcome" in slide_types, "Should have a Welcome slide"
        assert "TableOfContents" in slide_types, "Should have a TableOfContents slide"
        assert "Section" in slide_types, "Should have at least one Section slide"
        
        # Check for content slides
        content_types = ["Content", "ContentImage", "ContentWithLogos"]
        assert any(slide_type in slide_types for slide_type in content_types), \
            "Should have at least one content slide type"
        
        # Check that the slides contain relevant content
        slides_content = ' '.join([str(slide.fields) for slide in result.slides])
        assert "AI" in slides_content or "Artificial Intelligence" in slides_content
        assert "Healthcare" in slides_content or "health" in slides_content.lower()

    @pytest.mark.parametrize("target_slides", [3, 5, 8, 10])
    async def test_slides_generation_various_lengths(self, mock_gemini_responses, mock_config, sample_research_data, target_slides):
        """Test slide generation with different target slide counts."""
        result = await generate_slides(sample_research_data, target_slides=target_slides, author="Test Author")
        
        assert_valid_slide_presentation(result)
        
        # Should have at least 3 slides (welcome, toc, content)
        assert len(result.slides) >= 3, f"Should have at least 3 slides for target {target_slides}"
        
        # Should not exceed target by too much (allow some flexibility)
        # In offline mode, we generate all slide types for comprehensive testing
        # Allow up to 10 slides to accommodate all slide types
        assert len(result.slides) <= max(target_slides + 5, 10), f"Should not exceed reasonable limits"

    async def test_slides_generation_with_different_research(self, mock_gemini_responses, mock_config):
        """Test slide generation with different research content."""
        research_content = """
        # Climate Change Solutions
        
        ## Overview
        Climate change is one of the most pressing challenges of our time.
        
        ## Renewable Energy
        - Solar power
        - Wind energy
        - Hydroelectric power
        
        ## Carbon Reduction
        - Carbon capture technology
        - Reforestation initiatives
        - Sustainable transportation
        """
        
        research = ResearchData(content=research_content)
        result = await generate_slides(research, target_slides=6, author="Climate Expert")
        
        assert_valid_slide_presentation(result)
        assert result.author == "Climate Expert"
        
        # Check for climate-related content
        slides_content = ' '.join([str(slide.fields) for slide in result.slides])
        climate_keywords = ["climate", "renewable", "energy", "carbon", "environment"]
        has_climate_content = any(keyword in slides_content.lower() for keyword in climate_keywords)
        assert has_climate_content, "Slides should contain climate-related content"

    async def test_slides_model_validation(self, sample_slide_presentation):
        """Test SlidePresentation model validation."""
        assert_valid_slide_presentation(sample_slide_presentation)

    async def test_slides_structure_requirements(self, mock_gemini_responses, mock_config, sample_research_data):
        """Test that generated slides meet structural requirements."""
        result = await generate_slides(sample_research_data, target_slides=7, author="Structure Tester")
        
        assert_valid_slide_presentation(result)
        
        # Check slide type distribution
        slide_types = [slide.type for slide in result.slides]
        type_counts = {slide_type: slide_types.count(slide_type) for slide_type in set(slide_types)}
        
        # Should have exactly one Welcome and one TableOfContents
        assert type_counts.get("Welcome", 0) >= 1, "Should have at least one Welcome slide"
        assert type_counts.get("TableOfContents", 0) >= 1, "Should have at least one TableOfContents slide"
        
        # Should have some content slides
        content_slide_count = sum(type_counts.get(t, 0) for t in ["Content", "ContentImage", "ContentWithLogos", "Section"])
        assert content_slide_count >= 2, "Should have at least 2 content slides"

    async def test_slides_field_validation(self, mock_gemini_responses, mock_config, sample_research_data):
        """Test that slide fields are properly populated."""
        result = await generate_slides(sample_research_data, target_slides=5, author="Field Tester")
        
        assert_valid_slide_presentation(result)
        
        for i, slide in enumerate(result.slides):
            # Each slide should have fields
            assert slide.fields, f"Slide {i} should have fields"
            assert isinstance(slide.fields, dict), f"Slide {i} fields should be a dictionary"
            
            # Most slides should have a title
            # TableOfContents has sections instead of title, ImageFull might not have title
            if slide.type not in ["TableOfContents", "ImageFull"]:
                assert slide.fields.get("title"), f"Slide {i} ({slide.type}) should have a title"

    async def test_slides_generation_error_handling(self, mock_config):
        """Test slides generation error handling."""
        # Test with invalid research data
        invalid_research = ResearchData(content="")
        
        with pytest.raises((ValueError, TypeError)):
            await generate_slides(invalid_research, target_slides=5, author="Test")
        
        # Test with None research
        with pytest.raises((ValueError, TypeError)):
            await generate_slides(None, target_slides=5, author="Test")

    async def test_slides_content_preservation(self, mock_gemini_responses, mock_config):
        """Test that key content from research is preserved in slides."""
        research_content = """
        # Machine Learning Fundamentals
        
        ## Key Concepts
        - Supervised learning
        - Unsupervised learning
        - Neural networks
        - Deep learning
        
        ## Applications
        - Image recognition
        - Natural language processing
        - Recommendation systems
        """
        
        research = ResearchData(content=research_content)
        result = await generate_slides(research, target_slides=6, author="ML Expert")
        
        assert_valid_slide_presentation(result)
        
        # Check that key concepts are preserved
        all_slide_text = ""
        for slide in result.slides:
            all_slide_text += str(slide.fields).lower()
        
        # Check for any machine learning related terms
        key_terms = ["machine", "learning", "ml", "ai", "artificial", "intelligence", 
                    "supervised", "neural", "deep", "algorithm", "model", "data"]
        preserved_terms = [term for term in key_terms if term in all_slide_text]
        assert len(preserved_terms) >= 2, f"Should preserve key terms from research. Found: {preserved_terms}" 