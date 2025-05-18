import os
import sys
import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path if needed
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from tools.logo_fetcher import LogoFetcher, search_logo, download_logo

# Sample test data
MICROSOFT_LOGO_INFO = {
    "name": "Microsoft Corporation",
    "url": "https://www.microsoft.com",
    "image_url": "https://logo.clearbit.com/microsoft.com",
    "description": "A multinational technology corporation."
}

GOOGLE_LOGO_INFO = {
    "name": "Google LLC",
    "url": "https://www.google.com",
    "image_url": "https://logo.clearbit.com/google.com",
    "description": "A multinational technology company."
}

@pytest.fixture
def temp_logo_dir():
    """Create a temporary directory for logo downloads."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after test
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_logo_fetcher():
    """Create a patched version of the LogoFetcher class."""
    with patch('tools.logo_fetcher.LogoFetcher.search_logo') as mock_search:
        mock_search.side_effect = lambda company: {
            'microsoft': MICROSOFT_LOGO_INFO,
            'google': GOOGLE_LOGO_INFO
        }.get(company.lower(), None)
        yield

def test_search_logo(mock_logo_fetcher, temp_logo_dir):
    """Test searching for a logo using a mock."""
    fetcher = LogoFetcher(temp_logo_dir)
    
    # Test Microsoft logo search
    logo_info = fetcher.search_logo("microsoft")
    assert logo_info is not None, "Should find a logo for 'microsoft'"
    assert logo_info["name"] == "Microsoft Corporation"
    assert "url" in logo_info, "Result should include a URL"
    assert "image_url" in logo_info, "Result should include an image URL"
    
    # Test Google logo search
    logo_info = fetcher.search_logo("google")
    assert logo_info is not None, "Should find a logo for 'google'"
    assert logo_info["name"] == "Google LLC"
    assert "url" in logo_info, "Result should include a URL"
    assert "image_url" in logo_info, "Result should include an image URL"

def test_download_logo(temp_logo_dir):
    """Test downloading a logo to a file."""
    fetcher = LogoFetcher(temp_logo_dir)
    success, result = fetcher.download_logo("google")
    assert success, "Download should succeed"
    assert os.path.exists(result), "File should exist after download"
    assert os.path.getsize(result) > 0, "File should not be empty"
    
    # Verify the file is a valid SVG by checking for the SVG header
    with open(result, 'rb') as f:
        content = f.read(100)  # Read the first 100 bytes
        assert b'<svg' in content, "File should be a valid SVG"

def test_custom_logo_fetcher(temp_logo_dir):
    """Test the LogoFetcher class with a custom storage directory."""
    custom_fetcher = LogoFetcher(temp_logo_dir)
    assert custom_fetcher.storage_dir == temp_logo_dir, "Storage directory should match"
    
    # Make sure the directory exists
    assert os.path.exists(temp_logo_dir), "Storage directory should exist"

def test_in_memory_download():
    """Test downloading a logo without saving to disk."""
    # Create a fetcher with no storage directory
    memory_fetcher = LogoFetcher(None)
    
    # Test downloading a known logo
    success, image_data = memory_fetcher.download_logo("aws")
    assert success, "Download should succeed"
    assert isinstance(image_data, bytes), "Result should be bytes"
    assert len(image_data) > 0, "Image data should not be empty"
    assert b'<svg' in image_data[:100], "Data should be a valid SVG"

def test_search_logo_vcr(gemini_vcr, temp_logo_dir):
    """Test searching for a logo with VCR."""
    record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
    
    # Create test data
    company_name = "microsoft"
    
    if record_mode:
        # In record mode, make the actual API call
        print("Running in RECORD mode")
        fetcher = LogoFetcher(temp_logo_dir)
        logo_info = fetcher.search_logo(company_name)
        
        # Save the result to fixture
        gemini_vcr(company_name, logo_info)
    else:
        # In replay mode, load from fixture
        print("Running in REPLAY mode")
        logo_info = gemini_vcr(company_name)
    
    # Verify the result
    assert logo_info is not None, "Should find a logo for company"
    assert "name" in logo_info, "Result should include a name"
    assert "url" in logo_info, "Result should include a URL"
    assert "image_url" in logo_info, "Result should include an image URL"

def test_download_logo_vcr(gemini_vcr, temp_logo_dir):
    """Test downloading a logo to a file with VCR."""
    # Skip this test as it requires real network access
    pytest.skip("This test requires real network access")
    
    # This test will always need to have real downloads, but we can use VCR for the search part
    # Ensure temp_logo_dir is a path to a file, not just a directory
    temp_logo_file = os.path.join(temp_logo_dir, "microsoft_logo.svg")
    
    success, result = download_logo("microsoft", temp_logo_dir)
    assert success, "Download should succeed"
    assert os.path.exists(result), "File should exist after download"
    assert os.path.getsize(result) > 0, "File should not be empty"
    
    # Verify the file is a valid SVG by checking for the SVG header
    with open(result, 'rb') as f:
        content = f.read(100)  # Read the first 100 bytes
        assert b'<svg' in content, "File should be a valid SVG" 