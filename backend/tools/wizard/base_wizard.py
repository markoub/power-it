"""
Base wizard class that defines the common interface for all wizard types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import google.generativeai as genai
from config import MODIFY_MODEL, MODIFY_CONFIG

# Offline mode check
OFFLINE_MODE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes"}


class BaseWizard(ABC):
    """Base class for all wizard types."""
    
    def __init__(self):
        if not OFFLINE_MODE:
            self.model = genai.GenerativeModel(
                model_name=MODIFY_MODEL,
                generation_config=MODIFY_CONFIG
            )
        else:
            self.model = None
    
    @abstractmethod
    async def process_request(
        self,
        prompt: str,
        presentation_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a wizard request and return the response.
        
        Args:
            prompt: User's request/question
            presentation_data: Current presentation data
            context: Additional context (e.g., current slide, step)
            
        Returns:
            Dictionary containing response and any suggested changes
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this wizard type."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities description for this wizard type."""
        pass
    
    def _create_offline_response(self, prompt: str) -> Dict[str, Any]:
        """Create a simple offline response."""
        return {
            "response": f"Offline mode: I understand your request '{prompt}'. In full mode, I would provide detailed assistance.",
            "suggestions": None,
            "capabilities": self.get_capabilities()
        } 