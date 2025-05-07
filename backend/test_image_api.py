#!/usr/bin/env python3

import os
import base64
import json
import argparse
import httpx
import asyncio

# Set OpenAI API key from .env file
from dotenv import load_dotenv
load_dotenv()

async def test_image_generation_api():
    """
    Test the image generation API by making a direct HTTP request.
    """
    # Check if OpenAI API key exists
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please add it to your .env file.")
        return
    
    # Create a sample prompt
    prompt = "Create a professional business image showing data visualization and analytics for a presentation"
    
    # Make request to the API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/images",
                json={"prompt": prompt, "size": "1024x1024"},
                timeout=120.0  # Image generation can take time
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Image generated successfully!")
                print(f"Slide title: {result['slide_title']}")
                print(f"Prompt used: {result['prompt']}")
                
                # Save the image to a file
                image_data = base64.b64decode(result['image'])
                with open("test_image.png", "wb") as f:
                    f.write(image_data)
                print(f"Image saved to 'test_image.png'")
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error making request: {str(e)}")

async def test_mcp_image_generation():
    """
    Test the image generation by making a direct MCP request.
    """
    # Check if OpenAI API key exists
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please add it to your .env file.")
        return
    
    import fastmcp
    
    # Create MCP client
    print("Creating MCP client...")
    client = fastmcp.create_client()
    
    try:
        # Connect to MCP server
        print("Connecting to MCP server...")
        await client.connect(host="127.0.0.1", port=8080)
        
        # Check if the server is running
        ping_result = await client.call("ping")
        print(f"Ping result: {ping_result}")
        
        # Create a sample prompt
        prompt = "Create a professional business image showing data visualization and analytics for a presentation"
        
        # Call the generate_image_tool
        print("Generating image...")
        result = await client.call("generate_image_tool", prompt=prompt, size="1024x1024")
        
        # Save the image to a file
        if result and "image" in result:
            image_data = base64.b64decode(result['image'])
            with open("test_mcp_image.png", "wb") as f:
                f.write(image_data)
            print(f"Image saved to 'test_mcp_image.png'")
        else:
            print(f"Error: {result}")
    except Exception as e:
        print(f"Error during MCP request: {str(e)}")
    finally:
        # Disconnect from MCP server
        print("Disconnecting from MCP server...")
        await client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test image generation API")
    parser.add_argument("--method", choices=["api", "mcp"], default="api", help="Test method (api or mcp)")
    args = parser.parse_args()
    
    if args.method == "api":
        asyncio.run(test_image_generation_api())
    else:
        asyncio.run(test_mcp_image_generation()) 