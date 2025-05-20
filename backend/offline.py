import os
import importlib.util
from unittest.mock import patch, MagicMock

OFFLINE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes"}

if OFFLINE:
    print("Offline mode enabled - using recorded fixtures")

    base_dir = os.path.dirname(__file__)
    gemini_path = os.path.join(base_dir, "tests", "test_gemini_vcr.py")
    openai_path = os.path.join(base_dir, "tests", "test_openai_vcr.py")

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

    import google.generativeai as genai
    patch.object(
        genai.GenerativeModel,
        "generate_content_async",
        side_effect=gemini_vcr.mock_generate_content_async(
            genai.GenerativeModel.generate_content_async
        ),
    ).start()
    patch.object(
        genai.GenerativeModel,
        "generate_content",
        side_effect=gemini_vcr.mock_generate_content(
            genai.GenerativeModel.generate_content
        ),
    ).start()

    def _offline_openai(*args, **kwargs):
        client = MagicMock()
        images = MagicMock()
        images.generate = lambda **kw: openai_vcr.mock_openai_images_generate(**kw)
        client.images = images
        return client

    patch("openai.OpenAI", new=_offline_openai).start()

    from tools import logo_fetcher

    def _offline_search_logo(term):
        fixture = gemini_vcr.generate_fixture_name([term], {})
        data = gemini_vcr.load_recording(fixture)
        if data:
            return data
        return {"name": term, "url": "", "image_url": ""}

    def _offline_download_logo(term, filename=None):
        path = os.path.join(logo_fetcher.downloaded_logos_dir, f"{term.lower().replace(' ', '_')}.svg")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(
                    f"<svg xmlns='http://www.w3.org/2000/svg' width='200' height='100'><text x='10' y='50'>{term}</text></svg>"
                )
        return True, path

    patch("tools.logo_fetcher.search_logo", new=_offline_search_logo).start()
    patch("tools.logo_fetcher.download_logo", new=_offline_download_logo).start()
    patch.object(logo_fetcher.LogoFetcher, "search_logo", _offline_search_logo).start()
    patch.object(logo_fetcher.LogoFetcher, "download_logo", _offline_download_logo).start()

