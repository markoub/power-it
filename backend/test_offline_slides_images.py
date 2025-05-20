#!/usr/bin/env python
import os
import asyncio
import json
from pathlib import Path
import sys

# Set offline mode
os.environ["POWERIT_OFFLINE"] = "1"

# Import necessary modules
from tools.slides import generate_slides, OFFLINE_SLIDES_RESPONSE
from tools.images import generate_slide_images
from models import ResearchData
from config import PRESENTATIONS_STORAGE_DIR

async def test_offline_image_generation():
    print("Testing offline slide image generation...")
    
    # First, let's check what slide types we have in the offline mock
    print("\nOffline mock slide types:")
    for i, slide in enumerate(OFFLINE_SLIDES_RESPONSE["slides"]):
        slide_type = slide["type"]
        slide_title = slide["fields"].get("title", "No title")
        has_image = any(field.startswith("image") for field in slide["fields"])
        print(f"Slide {i+1}: Type={slide_type}, Title='{slide_title}', Has image field: {has_image}")
    
    # Generate slides in offline mode
    print("\nGenerating slides in offline mode...")
    research = ResearchData(content="Test content")
    slides = await generate_slides(research)
    
    print(f"Generated {len(slides.slides)} slides")
    for i, slide in enumerate(slides.slides):
        slide_type = slide.type
        slide_title = getattr(slide.fields, "title", "No title")
        print(f"Slide {i+1}: Type={slide_type}, Title='{slide_title}'")
    
    # Generate images for the slides
    print("\nGenerating images for the slides...")
    test_presentation_id = 999
    
    # Create presentation directory if it doesn't exist
    presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(test_presentation_id))
    images_dir = os.path.join(presentation_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    images = await generate_slide_images(slides, test_presentation_id)
    
    print(f"\nGenerated {len(images)} images:")
    for i, img in enumerate(images):
        print(f"Image {i+1}:")
        print(f"  Slide index: {img.slide_index}")
        print(f"  Slide title: {img.slide_title}")
        print(f"  Image field: {img.image_field_name}")
        print(f"  Image path: {img.image_path}")
        print(f"  Has image data: {bool(img.image)}")
        
        # Verify the image file exists
        if img.image_path:
            image_exists = Path(img.image_path).exists()
            print(f"  Image file exists: {image_exists}")
        
    return len(images) > 0

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_offline_image_generation())
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1) 