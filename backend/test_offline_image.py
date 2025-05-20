#!/usr/bin/env python
import os
import asyncio
import sys
import shutil
from pathlib import Path

# Set offline mode for testing
os.environ["POWERIT_OFFLINE"] = "1"

# Import the function we want to test
from tools.images import generate_image_from_prompt
from config import PRESENTATIONS_STORAGE_DIR

async def test_offline_image_generation():
    """Test that image generation returns a dummy image in offline mode."""
    print("Testing image generation in OFFLINE mode...")
    
    # Test with a simple prompt without presentation ID
    print("\nTest 1: Single image generation without presentation ID")
    prompt = "Test prompt for image generation in offline mode"
    result = await generate_image_from_prompt(prompt)
    
    if result:
        print(f"✅ Successfully generated image in offline mode")
        print(f"Slide index: {result.slide_index}")
        print(f"Slide title: {result.slide_title}")
        print(f"Image path: {result.image_path}")
        
        # Verify image path exists if provided
        if result.image_path and Path(result.image_path).exists():
            print(f"✅ Image file was created successfully")
        elif result.image_path:
            print(f"❌ Image file was not created at path: {result.image_path}")
        
        # Verify base64 data was provided
        if result.image:
            print(f"✅ Base64 image data was returned ({len(result.image)} chars)")
        else:
            print(f"❌ No base64 image data was returned")
    else:
        print(f"❌ Failed to generate image in offline mode")
        return False
    
    # Test with presentation ID to verify file creation
    print("\nTest 2: Image generation with presentation ID")
    # Use test presentation ID 999 for testing
    test_presentation_id = 999
    
    # Create presentation directory if it doesn't exist
    presentation_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(test_presentation_id))
    images_dir = os.path.join(presentation_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    prompt = "Test prompt with presentation ID"
    result_with_id = await generate_image_from_prompt(prompt, presentation_id=test_presentation_id)
    
    if result_with_id:
        print(f"✅ Successfully generated image with presentation ID")
        print(f"Slide index: {result_with_id.slide_index}")
        print(f"Slide title: {result_with_id.slide_title}")
        print(f"Image path: {result_with_id.image_path}")
        
        # Verify image path exists
        if result_with_id.image_path and Path(result_with_id.image_path).exists():
            print(f"✅ Image file was created successfully at: {result_with_id.image_path}")
            
            # Verify it's in the correct directory
            expected_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(test_presentation_id), "images")
            actual_dir = os.path.dirname(result_with_id.image_path)
            
            if expected_dir == actual_dir:
                print(f"✅ Image was saved in the correct directory")
            else:
                print(f"❌ Image was saved in the wrong directory")
                print(f"   Expected: {expected_dir}")
                print(f"   Actual: {actual_dir}")
        elif result_with_id.image_path:
            print(f"❌ Image file was not created at path: {result_with_id.image_path}")
        
        # Verify base64 data
        if result_with_id.image:
            print(f"✅ Base64 image data was returned ({len(result_with_id.image)} chars)")
        else:
            print(f"❌ No base64 image data was returned")
            
        return True
    else:
        print(f"❌ Failed to generate image with presentation ID")
        return False

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_offline_image_generation()) 