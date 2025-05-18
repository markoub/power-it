"""
Test configuration module - replaces the real config.py during tests
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set testing api key - use the real key for recording, fake key for replay
record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
if record_mode:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required for recording mode")
    genai.configure(api_key=GEMINI_API_KEY)
else:
    # For replay mode, we use a fake key (actual API calls will be intercepted)
    GEMINI_API_KEY = "fake-testing-api-key"
    # Don't actually configure the API in replay mode

# For testing, use models that are guaranteed to exist
RESEARCH_MODEL = "gemini-2.0-flash"
SLIDES_MODEL = "gemini-2.0-flash"
MODIFY_MODEL = "gemini-2.0-flash"

# Testing configurations with lower token limits for faster tests
RESEARCH_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,  # Lower token limit for testing
}

SLIDES_CONFIG = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,  # Lower token limit for testing
}

MODIFY_CONFIG = {
    "temperature": 0.25,
    "top_p": 0.92,
    "top_k": 50,
    "max_output_tokens": 4096,  # Lower token limit for testing
}

# OpenAI Image generation configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "fake-testing-openai-key")
OPENAI_IMAGE_CONFIG = {
    "model": "gpt-image-1",
    "quality": "low",
    "size": "1024x1536",
    "output_format": "png",
}

# Test data storage configuration - use temporary directories
import tempfile
TEMP_DIR = tempfile.mkdtemp(prefix="powerit_test_")
STORAGE_DIR = os.path.join(TEMP_DIR, "storage")
PRESENTATIONS_STORAGE_DIR = os.path.join(STORAGE_DIR, "presentations")

# Create storage directories
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(PRESENTATIONS_STORAGE_DIR, exist_ok=True) 