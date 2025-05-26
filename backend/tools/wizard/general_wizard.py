"""
General wizard for handling general questions and guidance.
"""

from typing import Dict, Any, Optional
from .base_wizard import BaseWizard, OFFLINE_MODE


class GeneralWizard(BaseWizard):
    """Wizard for general assistance and guidance."""
    
    def get_system_prompt(self) -> str:
        return """
        You are a helpful presentation creation assistant. You help users:
        
        1. Understand the presentation creation process
        2. Navigate between different steps
        3. Provide general guidance on presentations
        4. Answer questions about the application features
        5. Suggest next steps in the workflow
        
        You provide guidance but cannot modify content directly on steps other than Research and Slides.
        You can suggest when users should go back to previous steps or move forward.
        
        Be helpful, encouraging, and provide clear direction on how to proceed.
        """
    
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
            
            input_prompt = f"""
            # Current Step
            {current_step}
            
            # Presentation State
            Topic: {presentation_data.get('topic', 'Not set')}
            Research Status: {presentation_state['research_status']}
            Slides Status: {presentation_state['slides_status']}
            Images Status: {presentation_state['images_status']}
            PPTX Status: {presentation_state['pptx_status']}
            
            # User Question
            {prompt}

            Please provide helpful guidance to the user. You can:
            - Answer questions about the presentation creation process
            - Suggest which step to go to next
            - Explain what each step does
            - Provide general presentation advice
            - Help troubleshoot issues
            
            If the user needs to modify content, direct them to the appropriate step.
            Respond conversationally and be encouraging.
            """
            
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": self.get_system_prompt()}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll help guide you through the presentation creation process."}]},
                    {"role": "user", "parts": [{"text": input_prompt}]}
                ]
            )
            
            return {
                "response": response.text,
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
            
        except Exception as e:
            print(f"Error in general wizard: {str(e)}")
            return {
                "response": "I'm here to help! I can answer questions about the presentation creation process, guide you through the steps, and provide general assistance. What would you like to know?",
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