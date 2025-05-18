#!/usr/bin/env python3

import os
import base64
import pytest
import shutil
from pathlib import Path

from tools.images import generate_image_from_prompt, save_image_to_file, load_image_from_file
from config import PRESENTATIONS_STORAGE_DIR

@pytest.mark.asyncio
async def test_image_storage(mock_openai_responses):
    """Test the image storage functionality"""
    # Test presentation ID for this test
    test_presentation_id = 999
    
    # Create test folder
    test_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, str(test_presentation_id))
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Generate a test image
        prompt = "Create a simple test image of a pencil"
        
        result = await generate_image_from_prompt(prompt, presentation_id=test_presentation_id)
        
        assert result is not None, "Image generation failed"
        assert result.image_path is not None, "No image path returned"
        
        # Verify the image file exists
        assert os.path.exists(result.image_path), f"Image file not found at {result.image_path}"
        assert os.path.getsize(result.image_path) > 0, "Image file is empty"
        
        # Test loading the image back
        loaded_image = load_image_from_file(result.image_path)
        assert loaded_image is not None, f"Failed to load image from {result.image_path}"
        
        # Verify the loaded image matches the original
        assert loaded_image == result.image, "Loaded image does not match the original"
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir) 