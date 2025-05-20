import os
from dotenv import load_dotenv
import google.generativeai as genai

# Check for offline mode
OFFLINE_MODE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes"}

if OFFLINE_MODE:
    # Ensure VCR fixtures are used
    os.environ.setdefault("GEMINI_VCR_MODE", "replay")
    os.environ.setdefault("OPENAI_VCR_MODE", "replay")

# Load environment variables
load_dotenv()


def _load_secret(name: str, default: str | None = None) -> str | None:
    """Load a secret from an environment variable or /run/secrets file."""
    value = os.getenv(name)
    if value:
        return value
    secret_path = f"/run/secrets/{name}"
    if os.path.exists(secret_path):
        with open(secret_path) as fh:
            return fh.read().strip()
    return default

# Configure Gemini API
GEMINI_API_KEY = _load_secret("GEMINI_API_KEY")
if not GEMINI_API_KEY or OFFLINE_MODE:
    GEMINI_API_KEY = "fake-testing-key"
    if not OFFLINE_MODE:
        print(
            "WARNING: GEMINI_API_KEY not provided via env or secrets. "
            "Using a fake key for testing purposes."
        )

genai.configure(api_key=GEMINI_API_KEY)

# Check for OpenAI API key
OPENAI_API_KEY = _load_secret("OPENAI_API_KEY")
if not OPENAI_API_KEY or OFFLINE_MODE:
    OPENAI_API_KEY = "fake-openai-key"
    if not OFFLINE_MODE:
        print(
            "WARNING: OPENAI_API_KEY not provided via env or secrets. Image generation will not work."
        )

# Model configurations
RESEARCH_MODEL = "gemini-2.5-flash-preview-04-17"
SLIDES_MODEL = "gemini-2.5-flash-preview-04-17"
MODIFY_MODEL = "gemini-2.5-flash-preview-04-17"

# Generation configurations
RESEARCH_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 108192,
}

SLIDES_CONFIG = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 104096,
}

MODIFY_CONFIG = {
    "temperature": 0.25,
    "top_p": 0.92,
    "top_k": 50,
    "max_output_tokens": 108192,
}

# OpenAI Image generation configuration
OPENAI_IMAGE_CONFIG = {
    "model": "gpt-image-1",
    "quality": "low",
    "size": "1024x1536",
    "output_format": "png",
}

# Image storage configuration
STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "storage")
PRESENTATIONS_STORAGE_DIR = os.path.join(STORAGE_DIR, "presentations")
# Create storage directories if they don't exist
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(PRESENTATIONS_STORAGE_DIR, exist_ok=True) 