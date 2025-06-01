import pytest
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

# Import test utilities
from tests.utils import (
    EnvironmentManager,
    ModuleManager,
    MockFactory,
    create_test_presentation,
    assert_api_error,
    assert_valid_research_data,
    assert_valid_slide_presentation,
)

# Import VCR classes
from tests.unit.vcr.test_gemini_vcr import GeminiVCR
from tests.unit.vcr.test_openai_vcr import OpenAIVCR

# Configure pytest.ini options programmatically
def pytest_addoption(parser):
    parser.addini("asyncio_mode", "default asyncio mode", default="auto")
    parser.addini("asyncio_default_fixture_loop_scope", "default event loop scope for asyncio fixtures", default="function")

# Set up fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)

# ==================== Environment and Configuration Fixtures ====================

@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    """Configure test environment once for all tests."""
    # Import test config module
    ModuleManager.import_test_config()
    yield
    # Cleanup
    ModuleManager.cleanup_imports("tests.", "tools.", "routers.", "services.")

@pytest.fixture
def temp_storage_dir():
    """Create a temporary storage directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix="powerit_test_")
    storage_dir = Path(temp_dir) / "storage"
    presentations_dir = storage_dir / "presentations"
    presentations_dir.mkdir(parents=True, exist_ok=True)
    
    yield str(storage_dir)
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_config(temp_storage_dir, monkeypatch):
    """Mock configuration for tests."""
    monkeypatch.setattr("config.STORAGE_DIR", temp_storage_dir)
    monkeypatch.setattr("config.PRESENTATIONS_STORAGE_DIR", 
                       os.path.join(temp_storage_dir, "presentations"))
    monkeypatch.setattr("config.OFFLINE_MODE", True)
    monkeypatch.setattr("config.GEMINI_API_KEY", "fake-test-key")
    monkeypatch.setattr("config.OPENAI_API_KEY", "fake-test-key")
    
    yield

# ==================== VCR and API Mocking Fixtures ====================

@pytest.fixture
def gemini_vcr():
    """
    Return an instance of GeminiVCR that can record and replay Gemini API calls.
    - If GEMINI_VCR_MODE=record, make actual API calls and save responses.
    - If GEMINI_VCR_MODE=replay, use saved responses.
    """
    return GeminiVCR()

@pytest.fixture
def mock_gemini_api():
    """Patch the Gemini API key for testing."""
    record_mode = EnvironmentManager.get_bool_env("GEMINI_VCR_MODE", False)
    
    if record_mode:
        # In record mode, we need the real API key
        from dotenv import load_dotenv
        if not os.environ.get("GEMINI_API_KEY"):
            load_dotenv()
            
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable is required for recording mode")
        yield
    else:
        # In replay mode, use fake key
        with EnvironmentManager.temporary_env(GEMINI_API_KEY="fake-gemini-key-for-testing"):
            yield

@pytest.fixture
def openai_vcr():
    """
    Return an instance of OpenAIVCR that can record and replay OpenAI API calls.
    - If OPENAI_VCR_MODE=record, make actual API calls and save responses.
    - If OPENAI_VCR_MODE=replay, use saved responses.
    """
    return OpenAIVCR()

@pytest.fixture
def mock_openai_api():
    """Patch the OpenAI API key for testing."""
    record_mode = EnvironmentManager.get_bool_env("OPENAI_VCR_MODE", False)
    
    if record_mode:
        # In record mode, we need the real API key
        from dotenv import load_dotenv
        if not os.environ.get("OPENAI_API_KEY"):
            load_dotenv()
            
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required for recording mode")
        yield
    else:
        # In replay mode, use fake key
        with EnvironmentManager.temporary_env(OPENAI_API_KEY="fake-openai-key-for-testing"):
            yield

@pytest.fixture
def mock_openai_responses(openai_vcr, mock_openai_api):
    """
    Pytest fixture that replaces the OpenAI client with a mocked version.
    """
    # Create a completely mocked OpenAI client
    mock_client = MagicMock()
    mock_images = MagicMock()
    
    # Mock the generate method
    def mock_generate(**kwargs):
        return openai_vcr.mock_openai_images_generate(**kwargs)
    
    # Attach the generate method
    mock_images.generate = mock_generate
    mock_client.images = mock_images
    
    # Now patch the OpenAI constructor in tools.images
    with patch('tools.images.OpenAI', return_value=mock_client):
        # Indicate the patching was successful for debug
        print("Successfully patched OpenAI client in tools.images module")
        yield openai_vcr  # Return the actual VCR instance

@pytest.fixture
def mock_gemini_responses(gemini_vcr, mock_gemini_api):
    """
    Pytest fixture that patches Google's generative AI with mocked responses.
    """
    import google.generativeai as genai
    
    # Patch the generate_content method
    with patch('google.generativeai.GenerativeModel.generate_content', 
               side_effect=gemini_vcr.mock_generate_content(genai.GenerativeModel.generate_content)), \
         patch('google.generativeai.GenerativeModel.generate_content_async',
               side_effect=gemini_vcr.mock_generate_content_async(genai.GenerativeModel.generate_content_async)):
        
        # Indicate the patching was successful for debug
        print("Successfully patched Gemini API methods")
        yield gemini_vcr  # Return the actual VCR instance

@pytest.fixture
def image_api_vcr():
    """
    Record and replay image API calls.
    - If IMAGE_API_VCR_MODE=record, make actual API calls and save responses.
    - If IMAGE_API_VCR_MODE=replay, use saved responses.
    """
    record_mode = os.environ.get("IMAGE_API_VCR_MODE", "replay") == "record"
    
    def load_or_save_fixture(prompt, response=None):
        """Load a fixture or save a new one."""
        # Create a filename from the prompt
        hash_value = hash(prompt) % 10000000
        filename = f"image_api_{hash_value:x}.json"
        fixture_path = FIXTURES_DIR / filename
        
        # If we're saving a response
        if response is not None:
            save_fixture(fixture_path, response)
            return response
        
        # If we're loading a response
        fixture_data = load_fixture(fixture_path)
        if fixture_data is None and not record_mode:
            pytest.skip(f"No fixture found for prompt: {prompt}")
        
        return fixture_data
    
    return load_or_save_fixture

# ==================== Mock Object Fixtures ====================

@pytest.fixture
def mock_presentation():
    """Mock PowerPoint presentation object."""
    return MockFactory.create_mock_presentation()

@pytest.fixture
def mock_slide():
    """Mock PowerPoint slide object."""
    return MockFactory.create_mock_slide()

@pytest.fixture
def mock_shape():
    """Mock PowerPoint shape object."""
    return MockFactory.create_mock_shape()

# ==================== Test Data Fixtures ====================

@pytest.fixture
def sample_research_data():
    """Sample research data for testing."""
    from models import ResearchData
    return ResearchData(
        content="""# AI in Healthcare

## Introduction
Artificial Intelligence (AI) is revolutionizing healthcare by improving diagnostics, 
treatment planning, and patient care.

## Key Applications
- Medical imaging analysis
- Drug discovery
- Personalized medicine
- Clinical decision support

## Benefits
1. Improved accuracy in diagnosis
2. Reduced healthcare costs
3. Better patient outcomes
4. Accelerated research

## Challenges
- Data privacy concerns
- Regulatory compliance
- Integration with existing systems
- Training healthcare professionals

## Future Outlook
The future of AI in healthcare looks promising with continued advancements in 
machine learning algorithms and increased adoption across medical institutions.""",
        links=[
            {"href": "https://example.com/ai-healthcare", "title": "AI in Healthcare Overview"},
            {"href": "https://example.com/medical-ai", "title": "Medical AI Applications"}
        ]
    )

@pytest.fixture
def sample_slide_presentation():
    """Sample slide presentation for testing."""
    from models import SlidePresentation, Slide
    return SlidePresentation(
        title="AI in Healthcare",
        author="Test Author",
        slides=[
            Slide(
                type="Welcome",
                fields={
                    "title": "AI in Healthcare",
                    "subtitle": "Transforming Medical Care",
                    "author": "Test Author"
                }
            ),
            Slide(
                type="TableOfContents",
                fields={
                    "title": "Table of Contents",
                    "sections": [
                        "Introduction",
                        "Key Applications",
                        "Benefits",
                        "Challenges",
                        "Future Outlook"
                    ]
                }
            ),
            Slide(
                type="Section",
                fields={"title": "Introduction"}
            ),
            Slide(
                type="Content",
                fields={
                    "title": "What is AI in Healthcare?",
                    "content": [
                        "AI revolutionizes medical diagnostics",
                        "Improves treatment planning",
                        "Enhances patient care quality",
                        "Accelerates medical research"
                    ]
                }
            ),
            Slide(
                type="ContentImage",
                fields={
                    "title": "AI Applications",
                    "content": [
                        "Medical imaging analysis",
                        "Drug discovery",
                        "Personalized medicine"
                    ],
                    "image": True
                }
            )
        ]
    )

@pytest.fixture
def test_image_path(temp_storage_dir):
    """Create and return path to test image."""
    from PIL import Image
    image_path = os.path.join(temp_storage_dir, "test_image.png")
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image_path)
    return image_path

# ==================== Database Fixtures ====================

@pytest.fixture
async def test_db():
    """Initialize test database."""
    from database import init_db
    await init_db()
    yield

@pytest.fixture
async def clean_db(test_db):
    """Ensure database is clean before and after each test."""
    from database import SessionLocal
    from sqlalchemy import text
    
    async with SessionLocal() as db:
        # Clean all tables
        await db.execute(text("DELETE FROM presentation_steps"))
        await db.execute(text("DELETE FROM presentations"))
        await db.commit()
    
    yield
    
    # Clean again after test
    async with SessionLocal() as db:
        await db.execute(text("DELETE FROM presentation_steps"))
        await db.execute(text("DELETE FROM presentations"))
        await db.commit()

# ==================== API Testing Fixtures ====================

@pytest.fixture
def api_client():
    """Create FastAPI test client."""
    from fastapi.testclient import TestClient
    from api import app
    return TestClient(app)

@pytest.fixture
async def create_presentation(api_client, clean_db):
    """Factory fixture to create test presentations."""
    created_ids = []
    
    async def _create(**kwargs):
        presentation = await create_test_presentation(api_client, **kwargs)
        created_ids.append(presentation["id"])
        return presentation
    
    yield _create
    
    # Cleanup all created presentations
    for presentation_id in created_ids:
        api_client.delete(f"/presentations/{presentation_id}")

# ==================== Helper Function Fixtures ====================

@pytest.fixture
def load_fixture():
    """Load a fixture file."""
    def _load(fixture_path: Path) -> Optional[Dict[str, Any]]:
        if fixture_path.exists():
            with open(fixture_path, "r") as f:
                return json.load(f)
        return None
    return _load

@pytest.fixture
def save_fixture():
    """Save data to a fixture file."""
    def _save(fixture_path: Path, data: Dict[str, Any]) -> None:
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        with open(fixture_path, "w") as f:
            json.dump(data, f, indent=2)
    return _save 