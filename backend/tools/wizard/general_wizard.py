"""
General wizard for handling general questions and guidance.
"""

from typing import Dict, Any, Optional
from .base_wizard import BaseWizard, OFFLINE_MODE
from prompts import get_prompt


class GeneralWizard(BaseWizard):
    """Wizard for general assistance and guidance."""
    
    async def get_system_prompt(self) -> str:
        return await get_prompt("wizard_general_system")
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "type": "general",
            "can_modify": False,
            "can_provide_guidance": True,
            "can_answer_questions": True,
            "can_suggest_navigation": True,
            "supported_actions": [
                "answer_questions",
                "provide_guidance",
                "suggest_next_steps",
                "explain_features",
                "help_navigation"
            ]
        }
    
    async def process_request(
        self,
        prompt: str,
        presentation_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process general assistance requests."""
        
        if OFFLINE_MODE:
            return self._create_offline_response(prompt)
        
        current_step = context.get("step") if context else "unknown"
        
        try:
            # Analyze the presentation state
            presentation_state = self._analyze_presentation_state(presentation_data)
            
            prompt_template = await get_prompt("wizard_general_guidance")
            input_prompt = prompt_template.format(
                current_step=current_step,
                topic=presentation_data.get('topic', 'Not set'),
                research_status=presentation_state['research_status'],
                slides_status=presentation_state['slides_status'],
                images_status=presentation_state['images_status'],
                pptx_status=presentation_state['pptx_status'],
                prompt=prompt
            )
            
            system_prompt = await self.get_system_prompt()
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll help guide you through the presentation creation process."}]},
                    {"role": "user", "parts": [{"text": input_prompt}]}
                ]
            )
            
            return {
                "type": "explanation",
                "response": response.text,
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
            
        except Exception as e:
            print(f"Error in general wizard: {str(e)}")
            return {
                "type": "explanation",
                "response": "I'm here to help! I can answer questions about the presentation creation process, guide you through the steps, and provide general assistance. What would you like to know?",
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
    
    def _create_offline_response(self, prompt: str) -> Dict[str, Any]:
        """Create offline response for testing."""
        if not prompt or not prompt.strip():
            return {
                "type": "error",
                "error": "Empty request received. Please provide a question or instruction.",
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
        
        return {
            "type": "explanation",
            "response": f"Offline mode: I understand your request '{prompt}'. In full mode, I would provide detailed assistance about the presentation creation process.",
            "suggestions": None,
            "capabilities": self.get_capabilities()
        }
    
    def _analyze_presentation_state(self, presentation_data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze the current state of the presentation."""
        steps = presentation_data.get("steps", [])
        
        def get_step_status(step_name: str) -> str:
            step = next((s for s in steps if s.get("step") == step_name), None)
            if not step:
                return "not_started"
            return step.get("status", "unknown")
        
        return {
            "research_status": get_step_status("research"),
            "slides_status": get_step_status("slides"),
            "images_status": get_step_status("images"),
            "pptx_status": get_step_status("pptx")
        } 