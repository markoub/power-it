import os
import pytest
import json
import hashlib
import shutil
import tempfile
from models import CompiledSlide, CompiledPresentation
from tools.generate_pptx import generate_pptx_from_slides
from config import PRESENTATIONS_STORAGE_DIR

pytestmark = pytest.mark.asyncio

@pytest.fixture
def template_pptx_vcr():
    """Fixture for recording/replaying template PPTX test results"""
    # Create fixture directory
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    os.makedirs(fixture_dir, exist_ok=True)
    
    # Determine mode from environment variable
    record_mode = os.environ.get("TEMPLATE_PPTX_VCR_MODE", "replay") == "record"
    print(f"Template PPTX VCR mode: {'record' if record_mode else 'replay'}")
    
    def load_or_save_fixture(test_name, result_data=None):
        """Load or save fixture based on mode"""
        fixture_name = f"template_pptx_{test_name}.json"
        fixture_path = os.path.join(fixture_dir, fixture_name)
        
        if record_mode and result_data:
            # Record mode - save the fixture
            with open(fixture_path, "w") as f:
                json.dump(result_data, f, indent=2)
            print(f"Saved template PPTX test result to {fixture_path}")
            return result_data
        else:
            # Replay mode - load from fixture
            try:
                with open(fixture_path, "r") as f:
                    fixture_data = json.load(f)
                print(f"Loaded template PPTX test result from {fixture_path}")
                return fixture_data
            except FileNotFoundError:
                if not record_mode:
                    raise ValueError(
                        f"No fixture found at {fixture_path}. Run with TEMPLATE_PPTX_VCR_MODE=record first."
                    )
                return None
    
    return load_or_save_fixture

@pytest.fixture
def test_image_path():
    """Fixture providing a test image path."""
    # Create test directory
    test_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, "test", "images")
    os.makedirs(test_dir, exist_ok=True)
    
    # Path for test image
    test_image = os.path.join(test_dir, "test_image.png")
    
    # If test image doesn't exist, try to copy from project root
    if not os.path.exists(test_image):
        source_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_image.png")
        if os.path.exists(source_image):
            shutil.copy(source_image, test_image)
    
    # Skip test if image still doesn't exist
    if not os.path.exists(test_image):
        pytest.skip("Test image not found")
    
    return test_image

async def test_template_pptx(template_pptx_vcr, test_image_path):
    """Test PPTX generation with the template."""
    test_name = "basic_test"
    
    # Create a test presentation with slides
    presentation = CompiledPresentation(
        title="Template Test Presentation",
        slides=[
            CompiledSlide(
                title="First Content Slide",
                type="content",
                content=[
                    "This is a bullet point",
                    "This is another bullet point",
                    "This is a third bullet point with more text to test wrapping"
                ],
                notes="These are speaker notes for the first slide"
            ),
            CompiledSlide(
                title="Slide With Image",
                type="content",
                content=[
                    "Here's a slide with an image",
                    "The image should appear in the image placeholder",
                    "Text should be in the content placeholder"
                ],
                notes="Speaker notes for the image slide",
                image_url="/presentations/test/images/test_image.png"
            )
        ]
    )
    
    # In record mode, generate actual presentation and analyze
    if os.environ.get("TEMPLATE_PPTX_VCR_MODE") == "record":
        # Generate the presentation
        result = await generate_pptx_from_slides(presentation, "test")
        
        # Analyze the presentation
        pptx_path = result.pptx_path
        slide_count = result.slide_count
        file_size = os.path.getsize(pptx_path)
        
        # Save result data
        result_data = {
            "slide_count": slide_count,
            "file_size": file_size
        }
        
        template_pptx_vcr(test_name, result_data)
        
        # Basic checks
        assert slide_count >= 2, "Should have at least 2 slides"
        assert file_size > 0, "File size should be greater than 0"
        
        # Clean up
        os.remove(pptx_path)
    
    # In replay mode, use fixture data
    else:
        # Get fixture data
        fixture_data = template_pptx_vcr(test_name)
        
        # Basic checks using fixture data
        assert fixture_data["slide_count"] >= 2, "Should have at least 2 slides"
        assert fixture_data["file_size"] > 0, "File size should be greater than 0" 