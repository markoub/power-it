"""
Unit tests for TTS service
"""
import pytest
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add the backend directory to the path to avoid import issues
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path setup
from services.tts_service import TTSService


class TestTTSService:
    """Test the TTS service functionality"""
    
    @pytest.mark.asyncio
    async def test_tts_service_initialization(self):
        """Test TTS service initialization with default and custom voice"""
        # Default voice
        service = TTSService()
        assert service.voice == TTSService.DEFAULT_VOICE
        
        # Custom voice
        custom_voice = "en-GB-RyanNeural"
        service = TTSService(voice=custom_voice)
        assert service.voice == custom_voice
    
    @pytest.mark.asyncio
    async def test_text_to_speech_stream(self):
        """Test text to speech streaming"""
        service = TTSService()
        
        with patch('edge_tts.Communicate') as mock_communicate_class:
            # Mock the communicate instance
            mock_communicate = MagicMock()
            mock_communicate_class.return_value = mock_communicate
            
            # Mock the stream method to return audio chunks
            async def mock_stream():
                yield {"type": "audio", "data": b"chunk1"}
                yield {"type": "audio", "data": b"chunk2"}
                yield {"type": "metadata", "data": {}}  # Should be ignored
                yield {"type": "audio", "data": b"chunk3"}
            
            mock_communicate.stream.return_value = mock_stream()
            
            # Collect chunks
            chunks = []
            async for chunk in service.text_to_speech_stream("Test text"):
                chunks.append(chunk)
            
            # Verify
            assert len(chunks) == 3
            assert chunks[0] == b"chunk1"
            assert chunks[1] == b"chunk2"
            assert chunks[2] == b"chunk3"
            
            # Verify Communicate was called correctly
            mock_communicate_class.assert_called_once_with(
                text="Test text",
                voice=service.voice,
                rate="+0%",
                pitch="+0Hz",
                volume="+0%"
            )
    
    @pytest.mark.asyncio
    async def test_text_to_speech_stream_with_parameters(self):
        """Test text to speech streaming with custom parameters"""
        service = TTSService(voice="en-GB-SoniaNeural")
        
        with patch('edge_tts.Communicate') as mock_communicate_class:
            mock_communicate = MagicMock()
            mock_communicate_class.return_value = mock_communicate
            
            async def mock_stream():
                yield {"type": "audio", "data": b"test_audio"}
            
            mock_communicate.stream.return_value = mock_stream()
            
            # Test with custom parameters
            chunks = []
            async for chunk in service.text_to_speech_stream(
                "Test text", 
                rate="+10%", 
                pitch="-5Hz", 
                volume="+20%"
            ):
                chunks.append(chunk)
            
            # Verify parameters were passed correctly
            mock_communicate_class.assert_called_once_with(
                text="Test text",
                voice="en-GB-SoniaNeural",
                rate="+10%",
                pitch="-5Hz",
                volume="+20%"
            )
    
    @pytest.mark.asyncio
    async def test_text_to_speech_bytes(self):
        """Test converting text to complete audio bytes"""
        service = TTSService()
        
        with patch('edge_tts.Communicate') as mock_communicate_class:
            mock_communicate = MagicMock()
            mock_communicate_class.return_value = mock_communicate
            
            async def mock_stream():
                yield {"type": "audio", "data": b"part1"}
                yield {"type": "audio", "data": b"part2"}
                yield {"type": "audio", "data": b"part3"}
            
            mock_communicate.stream.return_value = mock_stream()
            
            # Get complete audio
            audio_bytes = await service.text_to_speech_bytes("Test text")
            
            # Verify
            assert audio_bytes == b"part1part2part3"
    
    @pytest.mark.asyncio
    async def test_get_available_voices(self):
        """Test getting available voices"""
        mock_voices = [
            {"Name": "en-US-AriaNeural", "Locale": "en-US"},
            {"Name": "en-GB-SoniaNeural", "Locale": "en-GB"},
            {"Name": "en-US-GuyNeural", "Locale": "en-US"}
        ]
        
        with patch('edge_tts.list_voices') as mock_list_voices:
            mock_list_voices.return_value = mock_voices
            
            # Get all voices
            voices = await TTSService.get_available_voices()
            assert len(voices) == 3
            assert voices == mock_voices
            
            # Get filtered voices
            us_voices = await TTSService.get_available_voices("en-US")
            assert len(us_voices) == 2
            assert all(v["Locale"].startswith("en-US") for v in us_voices)
    
    @pytest.mark.asyncio
    async def test_tts_service_error_handling(self):
        """Test error handling in TTS service"""
        service = TTSService()
        
        with patch('edge_tts.Communicate') as mock_communicate_class:
            mock_communicate = MagicMock()
            mock_communicate_class.return_value = mock_communicate
            
            # Mock stream to raise an error
            mock_communicate.stream.side_effect = Exception("TTS error")
            
            # Should propagate the error
            with pytest.raises(Exception) as exc_info:
                async for _ in service.text_to_speech_stream("Test"):
                    pass
            
            assert "TTS error" in str(exc_info.value)