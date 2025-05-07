import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SlidePresentation, Slide
from tools.generate_pptx import generate_pptx_from_slides, convert_pptx_to_png
from config import PRESENTATIONS_STORAGE_DIR

async def test_3images_slide(test_id="test"):
    """
    Generate a test presentation with a 3Images slide and optionally convert to PNG
    
    Args:
        test_id: The presentation ID to use (defaults to "test")
    """
    print("Testing 3Images slide generation...")
    
    # Create a test slide presentation with a 3Images slide
    slides = SlidePresentation(
        title="3Images Test Presentation",
        slides=[
            # Welcome slide
            Slide(
                type="Welcome",
                fields={
                    "title": "3Images Test Presentation",
                    "subtitle": "Testing the 3Images slide type",
                    "author": "Test User"
                }
            ),
            # A 3Images slide
            Slide(
                type="3Images",
                fields={
                    "title": "Three Images Slide",
                    "image1subtitle": "Image 1 Subtitle",
                    "image2subtitle": "Image 2 Subtitle",
                    "image3subtitle": "Image 3 Subtitle"
                }
            )
        ]
    )
    
    # Set up test images directory
    test_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, test_id, "images")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test image paths (use existing test_image.png if available)
    source_image = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test_image.png")
    
    if os.path.exists(source_image):
        # Copy source image to test images for all three image placeholders
        for i in range(1, 4):
            dest_image = os.path.join(test_dir, f"slide_2_image{i}.png")
            if not os.path.exists(dest_image):
                import shutil
                print(f"Copying test image to: {dest_image}")
                shutil.copy(source_image, dest_image)
    
    # Generate the PowerPoint presentation
    result = await generate_pptx_from_slides(slides, test_id)
    
    print(f"\nGenerated PPTX file: {result.pptx_path}")
    print(f"Slide count: {result.slide_count}")
    
    # Ask if user wants to convert to PNG
    convert = input("\nConvert to PNG? (y/n): ").lower().strip()
    if convert.startswith('y'):
        print("Converting PPTX to PNG...")
        png_files = await convert_pptx_to_png(result.pptx_path)
        if png_files:
            print(f"\nGenerated {len(png_files)} PNG files:")
            for png_file in png_files:
                print(f"  {png_file}")
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test 3Images slide functionality")
    parser.add_argument("--id", default="test", help="Presentation ID to use for testing")
    args = parser.parse_args()
    
    # Run the test
    asyncio.run(test_3images_slide(args.id)) 