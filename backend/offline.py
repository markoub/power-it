import os
import importlib.util
from unittest.mock import patch, MagicMock
import base64
import json

OFFLINE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes", "on"}

if OFFLINE:
    print("Offline mode enabled - using recorded fixtures")

    base_dir = os.path.dirname(__file__)
    gemini_path = os.path.join(base_dir, "tests", "unit", "vcr", "test_gemini_vcr.py")
    openai_path = os.path.join(base_dir, "tests", "unit", "vcr", "test_openai_vcr.py")

    spec_g = importlib.util.spec_from_file_location("gemini_vcr", gemini_path)
    gemini_vcr_module = importlib.util.module_from_spec(spec_g)
    spec_g.loader.exec_module(gemini_vcr_module)
    GeminiVCR = gemini_vcr_module.GeminiVCR

    spec_o = importlib.util.spec_from_file_location("openai_vcr", openai_path)
    openai_vcr_module = importlib.util.module_from_spec(spec_o)
    spec_o.loader.exec_module(openai_vcr_module)
    OpenAIVCR = openai_vcr_module.OpenAIVCR

    gemini_vcr = GeminiVCR()
    openai_vcr = OpenAIVCR()

    # Create fixtures directory if it doesn't exist
    fixtures_dir = os.path.join(base_dir, "tests", "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)

    # Patch Gemini API
    import google.generativeai as genai
    patch.object(
        genai.GenerativeModel,
        "generate_content_async",
        side_effect=gemini_vcr.generate_content_async_mock,
    ).start()
    patch.object(
        genai.GenerativeModel,
        "generate_content",
        side_effect=gemini_vcr.generate_content_mock,
    ).start()

    # Create a more comprehensive mock for OpenAI
    mock_client = MagicMock()
    mock_images = MagicMock()

    # Setup the mock image generation
    def mock_images_generate(**kwargs):
        response = openai_vcr.images_generate_mock(**kwargs)
        print(f"Mock OpenAI images.generate called with prompt: {kwargs.get('prompt', 'no prompt')}")
        return response

    mock_images.generate = mock_images_generate
    mock_client.images = mock_images

    # Patch both the OpenAI class and the existing instances
    patch("openai.OpenAI", return_value=mock_client).start()
    
    # Directly patch the tools.images module
    try:
        from tools import images
        patch.object(images, 'OpenAI', return_value=mock_client).start()
        print("Successfully patched OpenAI in tools.images module")
    except ImportError:
        print("Warning: Could not patch tools.images module directly")

    # Create a more robust mock for the requests module (used by logo_fetcher)
    class MockResponse:
        def __init__(self, text="<html>Mocked HTML response</html>", status_code=200, content=None):
            self.text = text
            self.status_code = status_code
            self.content = content or b"Mocked binary content"
            
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP Error: {self.status_code}")
            return None
            
        def json(self):
            return {"mocked": True, "data": "Mocked JSON data"}
    
    def mock_requests_get(url, *args, **kwargs):
        print(f"Intercepted request to: {url}")
        
        # Create a default SVG mock for logo URLs
        if "worldvectorlogo.com" in url:
            mock_html = """
            <html>
                <body>
                    <div class="grid__col">
                        <a class="logo" href="/logos/company-name">
                            <img class="logo__img" src="/svg/company-logo.svg" />
                            <span class="logo__name">Company Name</span>
                        </a>
                    </div>
                </body>
            </html>
            """
            return MockResponse(text=mock_html)
        
        # For SVG image URLs
        if url.endswith(".svg"):
            mock_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><text x="10" y="50">Mocked Logo</text></svg>'
            return MockResponse(content=mock_svg.encode('utf-8'))
            
        return MockResponse()
    
    # Patch the requests module
    import requests
    patch.object(requests, "get", side_effect=mock_requests_get).start()
    
    # Patch logo_fetcher more comprehensively
    from tools import logo_fetcher

    def _offline_search_logo(term):
        print(f"Mock search_logo called for: {term}")
        # Try to load from fixture first
        fixture_name = f"logo_search_{term.lower().replace(' ', '_')}"
        fixture_path = os.path.join(fixtures_dir, f"{fixture_name}.json")
        
        if os.path.exists(fixture_path):
            with open(fixture_path, 'r') as f:
                return json.load(f)
                
        # Create a mock response
        return {
            'name': term,
            'url': f"https://worldvectorlogo.com/logos/{term.lower().replace(' ', '-')}",
            'image_url': f"https://worldvectorlogo.com/svg/{term.lower().replace(' ', '-')}.svg"
        }

    def _offline_download_logo(term, filename=None):
        print(f"Mock download_logo called for: {term}")
        path = os.path.join(logo_fetcher.downloaded_logos_dir, f"{term.lower().replace(' ', '_')}.svg")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><text x="10" y="50">{term}</text></svg>'
                )
        return True, path

    # Patch both the module functions and the class methods
    patch("tools.logo_fetcher.search_logo", new=_offline_search_logo).start()
    patch("tools.logo_fetcher.download_logo", new=_offline_download_logo).start()
    patch.object(logo_fetcher.LogoFetcher, "search_logo", _offline_search_logo).start()
    patch.object(logo_fetcher.LogoFetcher, "download_logo", _offline_download_logo).start()
    
    # Ensure requests is patched within the logo_fetcher module
    patch.object(logo_fetcher, "requests", MagicMock()).start()
    logo_fetcher.requests.get = mock_requests_get
    
    # Add a dummy base64 image for cases where we need one
    DUMMY_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    print("Offline patching complete - all external API calls will be mocked")

