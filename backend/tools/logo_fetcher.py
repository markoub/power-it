import os
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote
import shutil

logger = logging.getLogger(__name__)

# Check for offline mode
OFFLINE_MODE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes"}

# Dummy logo file for offline mode
downloaded_logos_dir = os.path.join(os.path.dirname(__file__), "downloaded_logos")
DUMMY_LOGO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "offline_assets")
DUMMY_LOGO_PATH = os.path.join(DUMMY_LOGO_DIR, "dummy_logo.svg")

# Ensure the directories exist
os.makedirs(downloaded_logos_dir, exist_ok=True)
os.makedirs(DUMMY_LOGO_DIR, exist_ok=True)

# Create a dummy logo file if it doesn't exist
if OFFLINE_MODE and not os.path.exists(DUMMY_LOGO_PATH):
    try:
        with open(DUMMY_LOGO_PATH, 'w') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><rect width="200" height="100" fill="#cccccc"/><text x="10" y="50" font-family="Arial" font-size="14">Dummy Logo</text></svg>')
        print(f"Created dummy logo file at {DUMMY_LOGO_PATH}")
    except Exception as e:
        print(f"Error creating dummy logo: {str(e)}")

class LogoFetcher:
    """
    A class for fetching logo images from worldvectorlogo.com
    """
    BASE_URL = "https://worldvectorlogo.com"
    SEARCH_URL = f"{BASE_URL}/search/"
    
    def __init__(self, storage_dir=None):
        """
        Initialize the LogoFetcher.
        
        Args:
            storage_dir (str, optional): Directory to store downloaded images.
                                         If None, images will not be saved to disk.
        """
        self.storage_dir = storage_dir
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
            logger.info(f"Created logo storage directory: {storage_dir}")
    
    def search_logo(self, term):
        """
        Search for a logo by term.
        
        Args:
            term (str): Search term for the logo.
            
        Returns:
            dict: Information about the first logo found, or None if not found.
                 Format: {'name': str, 'url': str, 'image_url': str}
        """
        if OFFLINE_MODE:
            print(f"OFFLINE MODE: Using dummy logo info for term: {term}")
            return {
                'name': term,
                'url': f"https://worldvectorlogo.com/logos/{term.lower().replace(' ', '-')}",
                'image_url': f"https://worldvectorlogo.com/logos/{term.lower().replace(' ', '-')}.svg"
            }
            
        try:
            # URL encode the search term
            encoded_term = quote(term)
            search_url = f"{self.BASE_URL}/search/{encoded_term}"
            
            print(f"LOGO DEBUG: Searching for logo at URL: {search_url}")
            response = requests.get(search_url)
            print(f"LOGO DEBUG: Search response status code: {response.status_code}")
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the first logo
            logo_div = soup.select_one('div.grid__col a.logo')
            
            if not logo_div:
                print(f"LOGO DEBUG: No logo found using selector 'div.grid__col a.logo'")
                # Try alternative selectors
                alternative_selectors = [
                    'a.logo', 
                    '.grid a.logo',
                    '.search-results a',
                    '.grid .grid__col a'
                ]
                
                for selector in alternative_selectors:
                    print(f"LOGO DEBUG: Trying alternative selector: '{selector}'")
                    logo_div = soup.select_one(selector)
                    if logo_div:
                        print(f"LOGO DEBUG: Found logo using alternative selector: '{selector}'")
                        break
                
                if not logo_div:
                    # Save the HTML for debugging
                    debug_html_path = os.path.join(self.storage_dir, f"debug_{term}.html")
                    with open(debug_html_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"LOGO DEBUG: Saved HTML for debugging to {debug_html_path}")
                    
                    print(f"LOGO DEBUG: No logo found for term: {term}")
                    return None
            
            # Extract logo info
            logo_url = self.BASE_URL + logo_div['href'] if logo_div['href'].startswith('/') else logo_div['href']
            print(f"LOGO DEBUG: Found logo URL: {logo_url}")
            
            # Try to get the image
            logo_img = logo_div.select_one('img.logo__img')
            if not logo_img:
                print(f"LOGO DEBUG: No image found with selector 'img.logo__img', trying alternative selectors")
                for img_selector in ['img', '.logo__img', 'svg']:
                    logo_img = logo_div.select_one(img_selector)
                    if logo_img:
                        print(f"LOGO DEBUG: Found image using alternative selector: '{img_selector}'")
                        break
            
            logo_name = logo_div.select_one('span.logo__name')
            if not logo_name:
                print(f"LOGO DEBUG: No logo name found with selector 'span.logo__name', using term as name")
            
            if not logo_img or not logo_img.get('src'):
                print(f"LOGO DEBUG: Logo found but image URL missing for term: {term}")
                # List all attributes of the logo_img
                if logo_img:
                    print(f"LOGO DEBUG: Logo image attributes: {logo_img.attrs}")
                    # Try to find src in different attributes
                    for attr in ['data-src', 'data-original', 'srcset']:
                        if logo_img.get(attr):
                            print(f"LOGO DEBUG: Found alternative image URL in '{attr}': {logo_img[attr]}")
                            # Use this as the src
                            logo_img['src'] = logo_img[attr]
                            break
                return None
            
            print(f"LOGO DEBUG: Found logo image URL: {logo_img['src']}")
                
            return {
                'name': logo_name.text if logo_name else term,
                'url': logo_url,
                'image_url': logo_img['src']
            }
            
        except Exception as e:
            logger.error(f"Error searching for logo '{term}': {str(e)}")
            return None
    
    def download_logo(self, term, filename=None):
        """
        Search for and download a logo.
        
        Args:
            term (str): Search term for the logo.
            filename (str, optional): Filename to save the logo. If None,
                                     the filename will be derived from the term.
                                     
        Returns:
            tuple: (success, result) where:
                  - success is a boolean indicating if download was successful
                  - result is either the local path to the saved file, the image data (bytes),
                    or an error message
        """
        if OFFLINE_MODE:
            print(f"OFFLINE MODE: Using dummy logo for term: {term}")
            
            # If no storage_dir, just return the dummy logo path
            if not self.storage_dir:
                return True, DUMMY_LOGO_PATH
                
            # Otherwise, copy the dummy logo to the appropriate location
            if not filename:
                filename = f"{term.lower().replace(' ', '_')}.svg"
                
            local_path = os.path.join(self.storage_dir, filename)
            try:
                shutil.copy(DUMMY_LOGO_PATH, local_path)
                logger.info(f"Copied dummy logo to: {local_path}")
                return True, local_path
            except Exception as e:
                error_msg = f"Error copying dummy logo for '{term}': {str(e)}"
                logger.error(error_msg)
                return False, error_msg
        
        # Search for the logo
        logo_info = self.search_logo(term)
        if not logo_info:
            return False, f"No logo found for '{term}'"
        
        try:
            # Download the image
            image_url = logo_info['image_url']
            logger.info(f"Downloading logo from: {image_url}")
            response = requests.get(image_url)
            response.raise_for_status()
            
            image_data = response.content
            
            # If no storage_dir, just return the image data
            if not self.storage_dir:
                return True, image_data
            
            # Save the file
            if not filename:
                # Sanitize the filename
                filename = f"{term.lower().replace(' ', '_')}.svg"
            
            local_path = os.path.join(self.storage_dir, filename)
            with open(local_path, 'wb') as f:
                f.write(image_data)
                
            logger.info(f"Logo saved to: {local_path}")
            return True, local_path
            
        except Exception as e:
            error_msg = f"Error downloading logo for '{term}': {str(e)}"
            logger.error(error_msg)
            return False, error_msg

# Create a default instance with storage in 'downloaded_logos' directory
# Ensure the directory exists
if not os.path.exists(downloaded_logos_dir):
    os.makedirs(downloaded_logos_dir, exist_ok=True)
    logger.info(f"Created default logo storage directory: {downloaded_logos_dir}")

_default_fetcher = LogoFetcher(downloaded_logos_dir)

# Standalone functions that use the default LogoFetcher instance
def search_logo(term):
    """
    Search for a logo by term using the default LogoFetcher instance.
    
    Args:
        term (str): Search term for the logo.
        
    Returns:
        dict: Information about the first logo found, or None if not found.
             Format: {'name': str, 'url': str, 'image_url': str}
    """
    return _default_fetcher.search_logo(term)

def download_logo(term, filename=None):
    """
    Search for and download a logo using the default LogoFetcher instance.
    
    Args:
        term (str): Search term for the logo.
        filename (str, optional): Filename to save the logo. If None,
                                 the filename will be derived from the term.
                                 
    Returns:
        tuple: (success, result) where:
              - success is a boolean indicating if download was successful
              - result is either the local path to the saved file or an error message
    """
    return _default_fetcher.download_logo(term, filename)

# Example usage
if __name__ == "__main__":
    # Test the logo fetcher
    fetcher = LogoFetcher("./downloaded_logos")
    success, result = fetcher.download_logo("aws")
    
    if success:
        print(f"Downloaded logo: {result}")
    else:
        print(f"Failed to download logo: {result}") 