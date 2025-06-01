import os
from dotenv import load_dotenv
import google.generativeai as genai

# Check for offline mode
OFFLINE_MODE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes", "on"}

if OFFLINE_MODE:
    # Ensure VCR fixtures are used
    os.environ.setdefault("GEMINI_VCR_MODE", "replay")
    os.environ.setdefault("OPENAI_VCR_MODE", "replay")
    print(f"Config: OFFLINE_MODE is enabled - all external API calls will use fixtures")

# Load environment variables
load_dotenv()


def _load_secret(name: str, default: str | None = None) -> str | None:
    """Load a secret from environment or /run/secrets."""
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

# Only configure genai if not in offline mode to avoid unintended API calls
if not OFFLINE_MODE:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    # In offline mode, still set up the configuration but with the fake key
    genai.configure(api_key="fake-testing-key")
    print("Config: Configured genai with fake API key for offline mode")

# Check for OpenAI API key
OPENAI_API_KEY = _load_secret("OPENAI_API_KEY")
if not OPENAI_API_KEY or OFFLINE_MODE:
    OPENAI_API_KEY = "fake-openai-key"
    if not OFFLINE_MODE:
        print(
            "WARNING: OPENAI_API_KEY not provided via env or secrets. Image generation will not work."
        )
# Make sure the environment variable is set for other modules
if OFFLINE_MODE:
    os.environ["OPENAI_API_KEY"] = "fake-openai-key"
    print("Config: Set OPENAI_API_KEY environment variable to fake key for offline mode")

# Model configurations - use environment variables with defaults
RESEARCH_MODEL = os.getenv("RESEARCH_MODEL", "gemini-2.5-flash-preview-04-17")
SLIDES_MODEL = os.getenv("SLIDES_MODEL", "gemini-2.5-flash-preview-04-17")
MODIFY_MODEL = os.getenv("MODIFY_MODEL", "gemini-2.5-flash-preview-04-17")

# Generation configurations
RESEARCH_CONFIG = {
    "temperature": float(os.getenv("RESEARCH_TEMPERATURE", "0.2")),
    "top_p": float(os.getenv("RESEARCH_TOP_P", "0.95")),
    "top_k": int(os.getenv("RESEARCH_TOP_K", "40")),
    "max_output_tokens": int(os.getenv("RESEARCH_MAX_OUTPUT_TOKENS", "108192")),
    "response_mime_type": "application/json",
}

SLIDES_CONFIG = {
    "temperature": float(os.getenv("SLIDES_TEMPERATURE", "0.3")),
    "top_p": float(os.getenv("SLIDES_TOP_P", "0.95")),
    "top_k": int(os.getenv("SLIDES_TOP_K", "40")),
    "max_output_tokens": int(os.getenv("SLIDES_MAX_OUTPUT_TOKENS", "200000")),
}

MODIFY_CONFIG = {
    "temperature": float(os.getenv("MODIFY_TEMPERATURE", "0.25")),
    "top_p": float(os.getenv("MODIFY_TOP_P", "0.92")),
    "top_k": int(os.getenv("MODIFY_TOP_K", "50")),
    "max_output_tokens": int(os.getenv("MODIFY_MAX_OUTPUT_TOKENS", "108192")),
}

# Image generation provider configuration
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai").lower()  # Options: "openai" or "gemini"

# OpenAI Image generation configuration
OPENAI_IMAGE_CONFIG = {
    "model": os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
    "quality": os.getenv("OPENAI_IMAGE_QUALITY", "low"),
    "size": os.getenv("OPENAI_IMAGE_SIZE", "1024x1024"),
    "output_format": os.getenv("OPENAI_IMAGE_FORMAT", "png"),
}

# Gemini Image generation configuration
GEMINI_IMAGE_CONFIG = {
    "model": os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-002"),
    "safety_filter_level": os.getenv("GEMINI_IMAGE_SAFETY", "block_only_high"),
    "person_generation": os.getenv("GEMINI_IMAGE_PERSON", "allow_all"),
}

# Slides customization defaults
SLIDES_DEFAULTS = {
    "target_slides": int(os.getenv("SLIDES_DEFAULT_COUNT", "10")),
    "target_audience": os.getenv("SLIDES_DEFAULT_AUDIENCE", "general"),
    "content_density": os.getenv("SLIDES_DEFAULT_DENSITY", "medium"),  # low, medium, high
    "presentation_duration": int(os.getenv("SLIDES_DEFAULT_DURATION", "15")),  # minutes
}

# Storage configuration
# Get the project root directory (parent of the backend directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(PROJECT_ROOT, "storage"))
PRESENTATIONS_STORAGE_DIR = os.path.join(STORAGE_DIR, "presentations")
os.makedirs(PRESENTATIONS_STORAGE_DIR, exist_ok=True) 