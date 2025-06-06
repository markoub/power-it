from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.presentations import (
    ClarificationCheckRequest,
    ClarificationCheckResponse
)
from tools.research import check_clarifications
from tools.wizard.research_wizard import ResearchWizard

router = APIRouter(
    prefix="/research",
    tags=["research"],
)

@router.post("/clarification/check",
           response_model=ClarificationCheckResponse,
           summary="Check if a research topic needs clarification",
           description="Analyzes a topic for ambiguities and returns clarification questions if needed")
async def check_topic_clarification(
    request: ClarificationCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    """Check if a topic needs clarification before research."""
    
    wizard = ResearchWizard()
    clarification_data = await wizard.check_topic_clarifications(request.topic)
    
    if clarification_data:
        return ClarificationCheckResponse(
            needs_clarification=True,
            initial_message=clarification_data.get("initial_message", "")
        )
    
    return ClarificationCheckResponse(
        needs_clarification=False,
        initial_message=""
    )