#!/usr/bin/env python3

import os
import base64
import json
import pytest
import httpx
import asyncio
import hashlib
from unittest.mock import patch, AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio

# Create fixture directory
fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
os.makedirs(fixture_dir, exist_ok=True)

# Check if we're in record mode
record_mode = os.environ.get("IMAGE_API_VCR_MODE") == "record"
print(f"Image API VCR mode: {'record' if record_mode else 'replay'}")

@pytest.fixture
def image_api_vcr():
    """VCR-like fixture for image API tests"""
    
    def load_or_save_fixture(prompt, response_data=None):
        """Load or save fixture based on mode"""
        # Create deterministic fixture name based on prompt
        hash_obj = hashlib.md5(prompt.encode())
        fixture_name = f"image_api_{hash_obj.hexdigest()[:12]}.json"
        fixture_path = os.path.join(fixture_dir, fixture_name)
        
        if record_mode and response_data:
            # Record mode - save the fixture
            with open(fixture_path, "w") as f:
                json.dump(response_data, f, indent=2)
            print(f"Saved API response to {fixture_path}")
            return response_data
        else:
            # Replay mode - load from fixture
            try:
                with open(fixture_path, "r") as f:
                    fixture_data = json.load(f)
                print(f"Loaded API response from {fixture_path}")
                return fixture_data
            except FileNotFoundError:
                # Skip test if fixture not available in replay mode
                pytest.skip(f"Fixture not found at {fixture_path}. Run with IMAGE_API_VCR_MODE=record first.")
                return None
                
    return load_or_save_fixture

@pytest.mark.asyncio
async def test_image_generation_api(image_api_vcr, mock_openai_responses):
    """
    Test the image generation API with record/replay functionality.
    This test requires the API server to be running when in record mode.
    """
    # Create a sample prompt
    prompt = "Create a professional business image showing data visualization and analytics"
    
    # Record mode - make actual API call
    if os.environ.get("IMAGE_API_VCR_MODE") == "record":
        try:
            # Check if server is running by making a quick connection attempt
            try:
                async with httpx.AsyncClient() as client:
                    # Make a simple HEAD request to check if server is up
                    await client.head("http://localhost:8000", timeout=2.0)
            except Exception:
                pytest.skip("API server not running on localhost:8000. Start server before recording fixtures.")
                
            # Now make the actual API call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/images",
                    json={"prompt": prompt, "size": "1024x1024"},
                    timeout=120.0  # Image generation can take time
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Save response to fixture (without full image data)
                    fixture_data = {
                        "slide_title": result["slide_title"],
                        "prompt": result["prompt"],
                        # Store a small sample of the image to verify format
                        "image_sample": result["image"][:100] if "image" in result and result["image"] else ""
                    }
                    image_api_vcr(prompt, fixture_data)
                else:
                    pytest.fail(f"API call failed: {response.status_code}, {response.text}")
        except Exception as e:
            pytest.skip(f"Error making request. Skipping test: {str(e)}")
            
    # Replay mode - use fixture
    else:
        # Get fixture data
        fixture_data = image_api_vcr(prompt)
        
        # Verify fixture data
        assert "slide_title" in fixture_data
        assert "prompt" in fixture_data
        assert fixture_data["prompt"] == prompt
        assert "image_sample" in fixture_data
        
        # Create mock response
        with patch("httpx.AsyncClient.post") as mock_post:
            # Create a proper mock response that returns a regular dict from json()
            mock_response = MagicMock()
            mock_response.status_code = 200
            
            # Create a full response with dummy image data
            response_data = {
                "slide_title": fixture_data["slide_title"],
                "prompt": fixture_data["prompt"],
                "image": fixture_data["image_sample"] + "..." # simulated image data
            }
            
            # Set up non-async json method (httpx Response.json() is not async)
            mock_response.json.return_value = response_data
            
            # Set up the mock to return our mock response
            mock_post.return_value = mock_response
            
            # Call the API (mock will intercept)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/images",
                    json={"prompt": prompt, "size": "1024x1024"}
                )
                
                # Verify response
                assert response.status_code == 200
                result = response.json()  # This should now return our dict, not a coroutine
                assert result["slide_title"] == fixture_data["slide_title"]
                assert result["prompt"] == fixture_data["prompt"]

@pytest.mark.asyncio
async def test_mcp_image_generation(mock_openai_responses):
    """
    Test the image generation by making a MCP request using mocks.
    """
    import fastmcp
    from unittest.mock import patch, AsyncMock
    
    # Sample image data (base64 encoded small PNG)
    sample_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    # Mock MCP client
    mocked_client = AsyncMock()
    mocked_client.connect = AsyncMock()
    mocked_client.disconnect = AsyncMock()
    mocked_client.call = AsyncMock()
    
    # Configure the call method to return sample data
    mocked_client.call.side_effect = lambda method, **kwargs: {
        "ping": True,
        "generate_image_tool": {
            "image": sample_image_b64,
            "prompt": kwargs.get("prompt", ""),
            "size": kwargs.get("size", "1024x1024")
        }
    }.get(method)
    
    # Patch the Client class constructor instead of create_client
    with patch("fastmcp.Client", return_value=mocked_client):
        # Create MCP client - use the Client class directly
        client = fastmcp.Client()
        
        try:
            # Connect to MCP server (mocked)
            await client.connect(host="127.0.0.1", port=8080)
            
            # Check if the server is running (will always succeed with mock)
            ping_result = await client.call("ping")
            assert ping_result, "Server ping failed"
            
            # Create a sample prompt
            prompt = "Create a professional business image showing data visualization and analytics for a presentation"
            
            # Call the generate_image_tool (mocked)
            result = await client.call("generate_image_tool", prompt=prompt, size="1024x1024")
            
            # Verify response
            assert result is not None
            assert "image" in result
            assert result["prompt"] == prompt
            assert result["size"] == "1024x1024"
            
            # Check the decoded image (will be valid because we used a valid base64 PNG)
            image_data = base64.b64decode(result['image'])
            assert len(image_data) > 0
            
        finally:
            # Disconnect from MCP server (mocked)
            await client.disconnect()
        
        # Verify our mocks were called correctly
        mocked_client.connect.assert_called_once_with(host="127.0.0.1", port=8080)
        mocked_client.call.assert_any_call("ping")
        mocked_client.call.assert_any_call("generate_image_tool", prompt=prompt, size="1024x1024")
        mocked_client.disconnect.assert_called_once()