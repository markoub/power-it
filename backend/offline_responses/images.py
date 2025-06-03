import os
import base64
from config import STORAGE_DIR
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Tuple, Optional

DUMMY_IMAGE_DIR = os.path.join(STORAGE_DIR, "offline_assets")
DUMMY_IMAGE_PATH = os.path.join(DUMMY_IMAGE_DIR, "dummy_image.png")

# Different placeholder sizes for different aspect ratios
PLACEHOLDER_SIZES = {
    "landscape": (1024, 576),  # 16:9 aspect ratio
    "portrait": (768, 1024),   # 3:4 aspect ratio
    "square": (1024, 1024),    # 1:1 aspect ratio
}

DUMMY_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

def create_placeholder_image(size: Tuple[int, int], text: str = "Placeholder Image") -> bytes:
    """Create a placeholder image with the given size and text."""
    width, height = size
    
    # Create a new image with a gradient background
    img = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Draw a subtle grid pattern
    grid_color = '#e0e0e0'
    grid_spacing = 40
    
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
    
    # Draw diagonal lines for texture
    for i in range(-height, width, grid_spacing * 2):
        draw.line([(i, 0), (i + height, height)], fill='#d8d8d8', width=1)
    
    # Draw a central icon area
    center_x, center_y = width // 2, height // 2
    icon_size = min(width, height) // 4
    icon_rect = [
        center_x - icon_size // 2, center_y - icon_size // 2,
        center_x + icon_size // 2, center_y + icon_size // 2
    ]
    
    # Draw image icon shape
    draw.rectangle(icon_rect, outline='#999999', width=3)
    # Draw mountain shapes inside (simple image icon)
    mountain_points = [
        (icon_rect[0] + icon_size // 4, icon_rect[3] - icon_size // 4),
        (icon_rect[0] + icon_size // 2, icon_rect[1] + icon_size // 2),
        (icon_rect[0] + 3 * icon_size // 4, icon_rect[3] - icon_size // 4)
    ]
    draw.polygon(mountain_points, fill='#cccccc', outline='#999999')
    
    # Draw sun circle
    sun_radius = icon_size // 8
    sun_center = (icon_rect[2] - icon_size // 4, icon_rect[1] + icon_size // 4)
    draw.ellipse(
        [sun_center[0] - sun_radius, sun_center[1] - sun_radius,
         sun_center[0] + sun_radius, sun_center[1] + sun_radius],
        fill='#cccccc', outline='#999999'
    )
    
    # Add text
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Calculate text position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = center_y + icon_size // 2 + 20
    
    # Draw text with shadow
    draw.text((text_x + 1, text_y + 1), text, fill='#cccccc', font=font)
    draw.text((text_x, text_y), text, fill='#666666', font=font)
    
    # Add size indicator
    size_text = f"{width} × {height}px"
    size_bbox = draw.textbbox((0, 0), size_text, font=font)
    size_width = size_bbox[2] - size_bbox[0]
    draw.text((width - size_width - 10, height - 30), size_text, fill='#999999', font=font)
    
    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def get_aspect_ratio_type(prompt: str) -> str:
    """Determine aspect ratio type from prompt keywords."""
    prompt_lower = prompt.lower()
    
    # Check for aspect ratio keywords
    if any(word in prompt_lower for word in ['portrait', 'vertical', 'tall']):
        return 'portrait'
    elif any(word in prompt_lower for word in ['square', 'logo', 'icon']):
        return 'square'
    else:
        return 'landscape'  # Default to landscape


def ensure_dummy_image_exists():
    """Create the dummy image file if it does not exist."""
    if not os.path.exists(DUMMY_IMAGE_PATH):
        os.makedirs(DUMMY_IMAGE_DIR, exist_ok=True)
        # Create a default landscape placeholder
        placeholder_data = create_placeholder_image(PLACEHOLDER_SIZES['landscape'])
        with open(DUMMY_IMAGE_PATH, "wb") as f:
            f.write(placeholder_data)


def load_dummy_image_b64(prompt: Optional[str] = None) -> str:
    """Load a dummy image as base64, creating one based on the prompt if provided."""
    if prompt:
        # Determine aspect ratio from prompt
        aspect_type = get_aspect_ratio_type(prompt)
        size = PLACEHOLDER_SIZES[aspect_type]
        
        # Create a custom placeholder with the prompt text
        short_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
        placeholder_data = create_placeholder_image(size, short_prompt)
        return base64.b64encode(placeholder_data).decode()
    else:
        # Use default placeholder
        ensure_dummy_image_exists()
        with open(DUMMY_IMAGE_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
