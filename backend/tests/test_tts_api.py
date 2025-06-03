"""
API tests for TTS endpoints
"""
import pytest
import httpx
import asyncio


BASE_URL = "http://localhost:8000"


def test_tts_endpoint_exists():
    """Test that TTS endpoints are registered"""
    # Check the OpenAPI spec instead of the HTML
    response = httpx.get(f"{BASE_URL}/api/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    
    # Check that TTS endpoints are in the API spec
    paths = openapi.get("paths", {})
    assert "/presentations/{presentation_id}/tts/slide/{slide_index}" in paths
    assert "/presentations/{presentation_id}/tts/voices" in paths


def test_get_voices():
    """Test getting available TTS voices"""
    response = httpx.get(f"{BASE_URL}/presentations/0/tts/voices")
    assert response.status_code == 200
    
    data = response.json()
    assert "voices" in data
    assert "total" in data
    assert isinstance(data["voices"], list)
    assert isinstance(data["total"], int)
    
    # Should have at least some voices
    assert data["total"] > 0
    assert len(data["voices"]) > 0
    
    # Check voice structure
    if data["voices"]:
        voice = data["voices"][0]
        assert "Name" in voice or "name" in voice
        assert "Locale" in voice or "locale" in voice


def test_get_voices_with_locale():
    """Test getting voices filtered by locale"""
    response = httpx.get(f"{BASE_URL}/presentations/0/tts/voices?locale=en-US")
    assert response.status_code == 200
    
    data = response.json()
    assert "voices" in data
    assert isinstance(data["voices"], list)
    
    # All voices should be en-US
    for voice in data["voices"]:
        locale = voice.get("Locale") or voice.get("locale", "")
        assert locale.startswith("en-US")


def test_tts_slide_not_found():
    """Test TTS with non-existent presentation"""
    response = httpx.get(f"{BASE_URL}/presentations/99999/tts/slide/0")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_tts_slide_no_compiled():
    """Test TTS when presentation has no compiled step"""
    # Create a test presentation without compiled step
    presentation_data = {
        "name": "Test Presentation for TTS",
        "topic": "Testing TTS",
        "author": "Test Author"
    }
    
    create_response = httpx.post(
        f"{BASE_URL}/presentations",
        json=presentation_data
    )
    
    if create_response.status_code == 201:
        presentation_id = create_response.json()["id"]
        
        # Try to get TTS for this presentation (should fail as no compiled step)
        response = httpx.get(f"{BASE_URL}/presentations/{presentation_id}/tts/slide/0")
        assert response.status_code == 404
        assert "compiled" in response.json()["detail"].lower()


def test_tts_slide_with_existing_presentation():
    """Test TTS with an existing presentation that has compiled data"""
    # First, check if presentation 3 exists and has compiled data
    check_response = httpx.get(f"{BASE_URL}/presentations/3")
    
    if check_response.status_code == 200:
        presentation = check_response.json()
        
        # Check if it has compiled step
        has_compiled = any(
            step.get("step") == "compiled" and step.get("status") == "completed"
            for step in presentation.get("steps", [])
        )
        
        if has_compiled:
            # Test TTS for first slide
            response = httpx.get(f"{BASE_URL}/presentations/3/tts/slide/0")
            
            if response.status_code == 200:
                # Check response headers
                assert response.headers["content-type"] == "audio/mpeg"
                assert "cache-control" in response.headers
                assert response.headers["cache-control"] == "no-cache"
                
                # Check that we got audio data
                assert len(response.content) > 0
                
                # MP3 files typically start with ID3 tag or MPEG sync
                # edge-tts might use different MPEG header
                assert response.content[:3] == b'ID3' or response.content[0] == 0xff
            elif response.status_code == 404:
                # Slide might not have speaker notes
                assert "notes" in response.json()["detail"].lower()


def test_tts_slide_invalid_index():
    """Test TTS with invalid slide index"""
    # Check if presentation 3 exists
    check_response = httpx.get(f"{BASE_URL}/presentations/3")
    
    if check_response.status_code == 200:
        # Try to access slide 999 (should not exist)
        response = httpx.get(f"{BASE_URL}/presentations/3/tts/slide/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_tts_slide_with_custom_parameters():
    """Test TTS with custom voice parameters"""
    # Check if presentation 3 exists and has compiled data
    check_response = httpx.get(f"{BASE_URL}/presentations/3")
    
    if check_response.status_code == 200:
        presentation = check_response.json()
        
        # Check if it has compiled step
        has_compiled = any(
            step.get("step") == "compiled" and step.get("status") == "completed"
            for step in presentation.get("steps", [])
        )
        
        if has_compiled:
            # Test with custom parameters
            params = {
                "voice": "en-GB-RyanNeural",
                "rate": "+10%",
                "pitch": "-5Hz",
                "volume": "+20%"
            }
            
            response = httpx.get(
                f"{BASE_URL}/presentations/3/tts/slide/0",
                params=params
            )
            
            # Should either succeed or fail with no notes
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                assert response.headers["content-type"] == "audio/mpeg"
                assert len(response.content) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])