"""
Wizard factory for routing requests to appropriate wizard types.
"""

from typing import Dict, Any, Optional
from .research_wizard import ResearchWizard
from .slides_wizard import SlidesWizard
from .general_wizard import GeneralWizard


class WizardFactory:
    """Factory for creating and routing to appropriate wizard types."""
    
    def __init__(self):
        self._wizards = {
            "research": ResearchWizard(),
            "slides": SlidesWizard(),
            "general": GeneralWizard()
        }
    
    async def process_wizard_request(
        self,
        prompt: str,
        presentation_data: Dict[str, Any],
        current_step: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route a wizard request to the appropriate wizard type.
        
        Args:
            prompt: User's request/question
            presentation_data: Current presentation data
            current_step: Current step in the presentation workflow
            context: Additional context (e.g., selected slide, mode)
            
        Returns:
            Dictionary containing response and any suggested changes
        """
        
        # Determine which wizard to use based on the current step
        wizard_type = self._determine_wizard_type(current_step, context)
        wizard = self._wizards.get(wizard_type, self._wizards["general"])
        
        # Add step information to context
        if context is None:
            context = {}
        context["step"] = current_step
        
        # Process the request
        result = await wizard.process_request(prompt, presentation_data, context)
        
        # Add metadata about which wizard was used
        result["wizard_type"] = wizard_type
        result["step"] = current_step
        
        return result
    
    def _determine_wizard_type(self, current_step: str, context: Optional[Dict[str, Any]]) -> str:
        """Determine which wizard type to use based on step and context."""
        
        # Research step uses research wizard
        if current_step.lower() == "research":
            return "research"
        
        # Slides step uses slides wizard
        elif current_step.lower() == "slides":
            return "slides"
        
        # All other steps use general wizard
        else:
            return "general"
    
    def get_wizard_capabilities(self, wizard_type: str) -> Dict[str, Any]:
        """Get capabilities for a specific wizard type."""
        wizard = self._wizards.get(wizard_type)
        if wizard:
            return wizard.get_capabilities()
        return {}
    
    def get_all_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities for all wizard types."""
        return {
            wizard_type: wizard.get_capabilities()
            for wizard_type, wizard in self._wizards.items()
        } 