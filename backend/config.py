import os
from dotenv import load_dotenv
import google.generativeai as genai


def _load_secret(secret_name: str) -> str | None:
    """Load a secret from `/run/secrets` if it exists."""
    secret_path = os.path.join("/run/secrets", secret_name)
    if os.path.exists(secret_path):
        with open(secret_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or _load_secret("gemini_api_key")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "fake-testing-key"
    print(
        "WARNING: GEMINI_API_KEY not found in environment or /run/secrets. "
        "Using a fake key for testing purposes."
    )

genai.configure(api_key=GEMINI_API_KEY)

# Check for OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or _load_secret("openai_api_key")
if not OPENAI_API_KEY:
    print(
        "WARNING: OPENAI_API_KEY not found in environment or /run/secrets. "
        "Image generation will not work."
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