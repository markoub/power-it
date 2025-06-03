from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import logging

from database import get_db, Presentation, PresentationStepModel
from models import CompiledPresentation
from services.tts_service import TTSService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/presentations/{presentation_id}/tts", tags=["tts"])

@router.get("/slide/{slide_index}")
async def stream_slide_audio(
    presentation_id: int,
    slide_index: int,
    voice: Optional[str] = Query(None, description="Voice to use for TTS"),
    rate: str = Query("+0%", description="Speech rate adjustment"),
    pitch: str = Query("+0Hz", description="Pitch adjustment"),
    volume: str = Query("+0%", description="Volume adjustment"),
    db: AsyncSession = Depends(get_db)
):
    """
    Stream audio for speaker notes of a specific slide
    
    Args:
        presentation_id: ID of the presentation
        slide_index: Index of the slide (0-based)
        voice: Voice to use (defaults to en-US-AriaNeural)
        rate: Speech rate adjustment (e.g., "+10%", "-20%")
        pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
        volume: Volume adjustment (e.g., "+20%", "-10%")
        
    Returns:
        Audio stream in MP3 format
    """
    try:
        # Get presentation
        result = await db.execute(
            select(Presentation).where(Presentation.id == presentation_id)
        )
        presentation = result.scalar_one_or_none()
        
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
            
        # Get compiled presentation step
        step_result = await db.execute(
            select(PresentationStepModel).where(
                PresentationStepModel.presentation_id == presentation_id,
                PresentationStepModel.step == "compiled"
            )
        )
        compiled_step = step_result.scalar_one_or_none()
                
        if not compiled_step or not compiled_step.result:
            raise HTTPException(status_code=404, detail="Compiled presentation not found")
            
        # Parse compiled presentation
        import json
        result_data = compiled_step.result
        if isinstance(result_data, str):
            result_data = json.loads(result_data)
        compiled = CompiledPresentation(**result_data)
        
        # Check slide index
        if slide_index < 0 or slide_index >= len(compiled.slides):
            raise HTTPException(status_code=404, detail="Slide not found")
            
        # Get slide and its notes
        slide = compiled.slides[slide_index]
        notes = slide.fields.get("notes", "")
        
        if not notes:
            raise HTTPException(status_code=404, detail="No speaker notes found for this slide")
            
        # Initialize TTS service
        tts = TTSService(voice=voice)
        
        # Stream audio
        async def audio_generator():
            async for chunk in tts.text_to_speech_stream(notes, rate, pitch, volume):
                yield chunk
                
        return StreamingResponse(
            audio_generator(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"inline; filename=slide_{slide_index}_audio.mp3",
                "Cache-Control": "no-cache",
                "X-Content-Type-Options": "nosniff"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def get_available_voices(locale: Optional[str] = Query(None, description="Filter voices by locale")):
    """
    Get list of available TTS voices
    
    Args:
        locale: Optional locale filter (e.g., "en-US", "en-GB")
        
    Returns:
        List of available voices
    """
    try:
        voices = await TTSService.get_available_voices(locale)
        return {
            "voices": voices,
            "total": len(voices)
        }
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))