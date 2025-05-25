import os
import base64
from config import STORAGE_DIR

DUMMY_IMAGE_DIR = os.path.join(STORAGE_DIR, "offline_assets")
DUMMY_IMAGE_PATH = os.path.join(DUMMY_IMAGE_DIR, "dummy_image.png")

DUMMY_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

def ensure_dummy_image_exists():
    """Create the dummy image file if it does not exist."""
    if not os.path.exists(DUMMY_IMAGE_PATH):
        os.makedirs(DUMMY_IMAGE_DIR, exist_ok=True)
        with open(DUMMY_IMAGE_PATH, "wb") as f:
            f.write(base64.b64decode(DUMMY_BASE64_IMAGE))


def load_dummy_image_b64() -> str:
    ensure_dummy_image_exists()
    with open(DUMMY_IMAGE_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()
