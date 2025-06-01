"""Common test helper functions and assertions."""

import asyncio
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import json
from models import ResearchData, SlidePresentation, Slide


async def wait_for_condition(
    condition_func: Callable[[], bool],
    timeout: float = 5.0,
    interval: float = 0.1,
    error_msg: str = "Condition not met within timeout"
) -> bool:
    """
    Wait for a condition to become true.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds
        error_msg: Error message if timeout occurs
        
    Returns:
        True if condition was met
        
    Raises:
        TimeoutError: If condition not met within timeout
    """
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        if condition_func():
            return True
        await asyncio.sleep(interval)
    
    raise TimeoutError(error_msg)


def assert_api_error(response: Any, status_code: int, error_contains: str) -> None:
    """
    Assert that an API response is an error with expected status and message.
    
    Args:
        response: API response object
        status_code: Expected HTTP status code
        error_contains: String that should be contained in error message
    """
    assert response.status_code == status_code, \
        f"Expected status {status_code}, got {response.status_code}"
    
    error_data = response.json()
    assert "detail" in error_data, "Error response missing 'detail' field"
    
    error_detail = error_data["detail"]
    if isinstance(error_detail, str):
        assert error_contains.lower() in error_detail.lower(), \
            f"Expected error to contain '{error_contains}', got '{error_detail}'"
    elif isinstance(error_detail, list):
        # Handle validation errors
        error_messages = " ".join(str(e.get("msg", "")) for e in error_detail)
        assert error_contains.lower() in error_messages.lower(), \
            f"Expected error to contain '{error_contains}', got '{error_messages}'"


async def create_test_presentation(
    api_client: Any,
    name: Optional[str] = None,
    topic: str = "Test Topic",
    author: str = "Test Author",
    research_type: str = "research",
    **kwargs
) -> Dict[str, Any]:
    """
    Create a test presentation via API.
    
    Args:
        api_client: Test client for API calls
        name: Presentation name (auto-generated if None)
        topic: Presentation topic
        author: Presentation author
        research_type: Type of research
        **kwargs: Additional fields
        
    Returns:
        Created presentation data
    """
    if name is None:
        import uuid
        name = f"Test Presentation {uuid.uuid4().hex[:8]}"
    
    payload = {
        "name": name,
        "topic": topic,
        "author": author,
        "research_type": research_type,
        **kwargs
    }
    
    response = api_client.post("/presentations", json=payload)
    assert response.status_code == 201, f"Failed to create presentation: {response.text}"
    
    return response.json()


def assert_valid_research_data(data: ResearchData) -> None:
    """
    Assert that research data is valid and complete.
    
    Args:
        data: Research data to validate
    """
    assert isinstance(data, ResearchData), "Data must be ResearchData instance"
    assert data.content, "Research content cannot be empty"
    assert len(data.content) > 100, "Research content seems too short"
    
    # Check for basic markdown structure
    assert "#" in data.content, "Research should contain markdown headers"
    
    # Validate links if present
    if data.links:
        assert isinstance(data.links, list), "Links must be a list"
        for link in data.links:
            assert isinstance(link, dict), "Each link must be a dictionary"
            assert "href" in link, "Link missing 'href' field"
            assert "title" in link, "Link missing 'title' field"
            assert link["href"].startswith(("http://", "https://")), \
                f"Invalid URL: {link['href']}"


def assert_valid_slide_presentation(presentation: SlidePresentation) -> None:
    """
    Assert that a slide presentation is valid and complete.
    
    Args:
        presentation: Slide presentation to validate
    """
    assert isinstance(presentation, SlidePresentation), \
        "Presentation must be SlidePresentation instance"
    assert presentation.title, "Presentation must have a title"
    assert presentation.slides, "Presentation must have slides"
    assert len(presentation.slides) >= 3, \
        f"Presentation should have at least 3 slides, got {len(presentation.slides)}"
    
    # Check required slide types
    assert_has_required_slide_types(presentation)
    
    # Validate each slide
    for i, slide in enumerate(presentation.slides):
        assert isinstance(slide, Slide), f"Slide {i} must be Slide instance"
        assert slide.type, f"Slide {i} missing type"
        assert slide.fields, f"Slide {i} missing fields"
        assert isinstance(slide.fields, dict), f"Slide {i} fields must be dict"


def assert_has_required_slide_types(presentation: SlidePresentation) -> None:
    """
    Assert that presentation has required slide types.
    
    Args:
        presentation: Slide presentation to check
    """
    slide_types = [slide.type for slide in presentation.slides]
    
    # Check for welcome/title slide
    has_welcome = any(t in ["Welcome", "welcome", "Title"] for t in slide_types)
    assert has_welcome, "Presentation missing Welcome/Title slide"
    
    # Check for content slides
    content_slides = [t for t in slide_types if "Content" in t or "content" in t]
    assert len(content_slides) >= 1, "Presentation should have at least one content slide"


def assert_file_exists_and_valid(
    file_path: str,
    min_size: int = 100,
    extensions: Optional[List[str]] = None
) -> None:
    """
    Assert that a file exists and meets basic validity criteria.
    
    Args:
        file_path: Path to the file
        min_size: Minimum file size in bytes
        extensions: Allowed file extensions
    """
    path = Path(file_path)
    
    assert path.exists(), f"File does not exist: {file_path}"
    assert path.is_file(), f"Path is not a file: {file_path}"
    
    size = path.stat().st_size
    assert size >= min_size, \
        f"File too small: {size} bytes (minimum: {min_size})"
    
    if extensions:
        assert any(file_path.endswith(ext) for ext in extensions), \
            f"Invalid file extension. Expected one of: {extensions}"


def load_test_fixture(fixture_name: str, fixtures_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a test fixture JSON file.
    
    Args:
        fixture_name: Name of the fixture file (without .json extension)
        fixtures_dir: Directory containing fixtures (defaults to tests/fixtures)
        
    Returns:
        Loaded fixture data
    """
    if fixtures_dir is None:
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
    else:
        fixtures_dir = Path(fixtures_dir)
    
    fixture_path = fixtures_dir / f"{fixture_name}.json"
    
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")
    
    with open(fixture_path, "r") as f:
        return json.load(f)


def compare_slides(actual: List[Slide], expected: List[Dict[str, Any]]) -> None:
    """
    Compare actual slides with expected slide data.
    
    Args:
        actual: List of actual Slide objects
        expected: List of expected slide dictionaries
    """
    assert len(actual) == len(expected), \
        f"Slide count mismatch: expected {len(expected)}, got {len(actual)}"
    
    for i, (actual_slide, expected_slide) in enumerate(zip(actual, expected)):
        assert actual_slide.type == expected_slide["type"], \
            f"Slide {i} type mismatch: expected {expected_slide['type']}, got {actual_slide.type}"
        
        # Compare fields
        for key, expected_value in expected_slide.get("fields", {}).items():
            assert key in actual_slide.fields, \
                f"Slide {i} missing field '{key}'"
            
            actual_value = actual_slide.fields[key]
            if isinstance(expected_value, list) and isinstance(actual_value, list):
                assert len(actual_value) == len(expected_value), \
                    f"Slide {i} field '{key}' list length mismatch"
            else:
                assert actual_value == expected_value, \
                    f"Slide {i} field '{key}' mismatch: expected {expected_value}, got {actual_value}"


def extract_slide_text(slide: Any) -> List[str]:
    """
    Extract all text from a PowerPoint slide.
    
    Args:
        slide: python-pptx slide object
        
    Returns:
        List of text strings found in the slide
    """
    texts = []
    
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text:
            texts.append(shape.text.strip())
        elif hasattr(shape, "text_frame") and shape.text_frame:
            text = shape.text_frame.text.strip()
            if text:
                texts.append(text)
    
    return texts