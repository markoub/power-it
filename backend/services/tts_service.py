import edge_tts
import asyncio
import io
from typing import AsyncGenerator, Optional
import logging

logger = logging.getLogger(__name__)

class TTSService:
    """Service for converting text to speech using edge-tts"""
    
    DEFAULT_VOICE = "en-US-AriaNeural"
    VOICE_OPTIONS = {
        "en-US": {
            "female": ["en-US-AriaNeural", "en-US-JennyNeural"],
            "male": ["en-US-GuyNeural", "en-US-ChristopherNeural"]
        },
        "en-GB": {
            "female": ["en-GB-SoniaNeural", "en-GB-LibbyNeural"],
            "male": ["en-GB-RyanNeural", "en-GB-ThomasNeural"]
        }
    }
    
    def __init__(self, voice: Optional[str] = None):
        self.voice = voice or self.DEFAULT_VOICE
        
    async def text_to_speech_stream(
        self, 
        text: str, 
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> AsyncGenerator[bytes, None]:
        """
        Convert text to speech and yield audio chunks
        
        Args:
            text: The text to convert to speech
            rate: Speech rate adjustment (e.g., "+10%", "-20%")
            pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
            volume: Volume adjustment (e.g., "+20%", "-10%")
            
        Yields:
            Audio data chunks in MP3 format
        """
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=rate,
                pitch=pitch,
                volume=volume
            )
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]
                    
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            raise
            
    async def text_to_speech_bytes(
        self, 
        text: str, 
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> bytes:
        """
        Convert text to speech and return complete audio data
        
        Args:
            text: The text to convert to speech
            rate: Speech rate adjustment
            pitch: Pitch adjustment
            volume: Volume adjustment
            
        Returns:
            Complete audio data in MP3 format
        """
        audio_data = io.BytesIO()
        
        async for chunk in self.text_to_speech_stream(text, rate, pitch, volume):
            audio_data.write(chunk)
            
        audio_data.seek(0)
        return audio_data.read()
    
    @classmethod
    async def get_available_voices(cls, locale: Optional[str] = None) -> list:
        """Get list of available voices, optionally filtered by locale"""
        voices = await edge_tts.list_voices()
        
        if locale:
            return [v for v in voices if v["Locale"].startswith(locale)]
        return voices