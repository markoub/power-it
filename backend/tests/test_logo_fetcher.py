import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to sys.path to import the LogoFetcher
sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools.logo_fetcher import LogoFetcher

class TestLogoFetcher(unittest.TestCase):
    """Tests for the LogoFetcher class"""
    
    def setUp(self):
        """Create a temporary directory for storing downloaded logos"""
        self.temp_dir = tempfile.mkdtemp()
        self.fetcher = LogoFetcher(self.temp_dir)
        
    def tearDown(self):
        """Remove the temporary directory and its contents"""
        shutil.rmtree(self.temp_dir)
    
    def test_search_logo(self):
        """Test searching for a logo"""
        # Test with a known term that should return results
        result = self.fetcher.search_logo("aws")
        self.assertIsNotNone(result, "Should find a logo for 'aws'")
        self.assertIn('image_url', result, "Result should include an image URL")
        self.assertIn('name', result, "Result should include a name")
        self.assertIn('url', result, "Result should include a URL")
        
        # Note: worldvectorlogo.com might return unrelated results for non-existent terms
        # Instead of testing for None, we'll skip this part of the test
    
    def test_download_logo(self):
        """Test downloading a logo to a file"""
        # Test downloading a known logo
        success, result = self.fetcher.download_logo("aws")
        self.assertTrue(success, "Download should succeed")
        self.assertTrue(os.path.exists(result), "File should exist after download")
        self.assertTrue(os.path.getsize(result) > 0, "File should not be empty")
        
        # Verify the file is a valid SVG by checking for the SVG header
        with open(result, 'rb') as f:
            content = f.read(100)  # Read the first 100 bytes
            self.assertIn(b'<svg', content, "File should be a valid SVG")
    
    def test_in_memory_download(self):
        """Test downloading a logo without saving to disk"""
        # Create a fetcher with no storage directory
        memory_fetcher = LogoFetcher(None)
        
        # Test downloading a known logo
        success, image_data = memory_fetcher.download_logo("aws")
        self.assertTrue(success, "Download should succeed")
        self.assertIsInstance(image_data, bytes, "Result should be bytes")
        self.assertTrue(len(image_data) > 0, "Image data should not be empty")
        self.assertIn(b'<svg', image_data[:100], "Data should be a valid SVG")

if __name__ == '__main__':
    unittest.main() 