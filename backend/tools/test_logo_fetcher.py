#!/usr/bin/env python
"""
Test script for the standalone logo fetcher functions.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path if needed
sys.path.append(str(Path(__file__).parent.parent))

# Import the standalone functions
from tools import search_logo, download_logo, LogoFetcher

def test_standalone_functions():
    """Test the standalone logo fetcher functions."""
    print("Testing search_logo function...")
    logo_info = search_logo("microsoft")
    
    if not logo_info:
        print("❌ search_logo failed to find a logo for 'microsoft'")
        return False
    
    print(f"✅ Found logo: {logo_info['name']}")
    print(f"   URL: {logo_info['url']}")
    print(f"   Image URL: {logo_info['image_url']}")
    
    print("\nTesting download_logo function...")
    success, result = download_logo("microsoft")
    
    if not success:
        print(f"❌ download_logo failed: {result}")
        return False
    
    print(f"✅ Downloaded logo to: {result}")
    
    # Verify the file exists and is not empty
    if not os.path.exists(result):
        print(f"❌ Downloaded file does not exist: {result}")
        return False
    
    if os.path.getsize(result) == 0:
        print(f"❌ Downloaded file is empty: {result}")
        return False
    
    print(f"✅ File exists and has content: {os.path.getsize(result)} bytes")
    
    # Verify it's an SVG by checking the first few bytes
    with open(result, 'rb') as f:
        content = f.read(100)
        if b'<svg' not in content:
            print("❌ Downloaded file does not appear to be a valid SVG")
            return False
    
    print("✅ Downloaded file is a valid SVG")
    return True

def test_class_instantiation():
    """Test creating a LogoFetcher instance with custom storage dir."""
    print("\nTesting LogoFetcher class instantiation...")
    
    # Create a temporary directory for this test
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a LogoFetcher instance with the temp directory
        fetcher = LogoFetcher(temp_dir)
        print(f"✅ Created LogoFetcher instance with storage dir: {temp_dir}")
        
        # Test downloading a logo
        success, result = fetcher.download_logo("facebook")
        
        if not success:
            print(f"❌ Custom LogoFetcher download failed: {result}")
            return False
        
        print(f"✅ Downloaded logo to: {result}")
        
        # Verify the file exists in the custom directory
        if not os.path.exists(result):
            print(f"❌ Downloaded file does not exist: {result}")
            return False
        
        if not result.startswith(temp_dir):
            print(f"❌ Downloaded file not in correct directory: {result}")
            return False
        
        print(f"✅ File exists in custom directory: {result}")
        return True
    
    finally:
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("=== Testing Logo Fetcher Standalone Functions ===")
    
    if test_standalone_functions() and test_class_instantiation():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1) 