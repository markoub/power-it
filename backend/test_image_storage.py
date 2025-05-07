#!/usr/bin/env python3

import os
import base64
import asyncio
import sys
import json
import shutil
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append('.')

from tools.images import generate_image_from_prompt, save_image_to_file, load_image_from_file
from config import PRESENTATIONS_STORAGE_DIR
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_image_storage():
    """Test the image storage functionality"""
    # Check if OpenAI API key exists
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please add it to your .env file.")
        return
    
    print("Testing image storage functionality...")
    
    # Test presentation ID for this test
    test_presentation_id = 999
    
    # Create test folder
    test_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(test_presentation_id))
    os.makedirs(test_dir, exist_ok=True)
    print(f"Created test directory: {test_dir}")
    
    try:
        # Generate a test image
        prompt = "Create a simple test image of a pencil"
        print(f"Generating test image with prompt: '{prompt}'...")
        
        result = await generate_image_from_prompt(prompt, presentation_id=test_presentation_id)
        
        if not result:
            print("ERROR: Image generation failed")
            return
        
        print(f"Image generated successfully!")
        print(f"Image path: {result.image_path}")
        
        # Verify the image file exists
        if not os.path.exists(result.image_path):
            print(f"ERROR: Image file not found at {result.image_path}")
            return
        
        print(f"File exists and is {os.path.getsize(result.image_path)} bytes")
        
        # Test loading the image back
        loaded_image = load_image_from_file(result.image_path)
        if not loaded_image:
            print(f"ERROR: Failed to load image from {result.image_path}")
            return
        
        print(f"Successfully loaded image from file")
        
        # Verify the loaded image matches the original
        if loaded_image == result.image:
            print("SUCCESS: Loaded image matches the original")
        else:
            print("ERROR: Loaded image does not match the original")
        
        print("\nImage storage test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"Cleaned up test directory: {test_dir}")

if __name__ == "__main__":
    asyncio.run(test_image_storage()) 