#!/usr/bin/env python3

import os
import base64
import asyncio
import sys

# Add the current directory to Python path for imports
sys.path.append('.')

from tools.images import generate_image_from_prompt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_image_generation():
    """Test the image generation tool directly"""
    # Check if OpenAI API key exists
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please add it to your .env file.")
        return
    
    print("Generating test image...")
    prompt = "Create a professional business image showing data visualization and analytics for a presentation"
    
    try:
        # Generate the image
        result = await generate_image_from_prompt(prompt)
        
        if result:
            print(f"Image generated successfully!")
            print(f"Prompt used: {result.prompt}")
            
            # Save the image to a file
            image_data = base64.b64decode(result.image)
            with open("direct_test_image.png", "wb") as f:
                f.write(image_data)
            print(f"Image saved to 'direct_test_image.png'")
        else:
            print("Image generation failed.")
    except Exception as e:
        print(f"Error during image generation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_image_generation()) 