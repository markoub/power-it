"""
Research wizard for handling research-related requests.
"""

import json
from typing import Dict, Any, Optional
from .base_wizard import BaseWizard, OFFLINE_MODE
from utils import extract_json_from_text
from models import ResearchData


class ResearchWizard(BaseWizard):
    """Wizard specialized for research step assistance."""
    
    def get_system_prompt(self) -> str:
        return """
        You are an expert research assistant for presentation creation. You help users:
        
        1. Refine and improve research content
        2. Answer questions about research topics
        3. Suggest additional research directions
        4. Help with research methodology
        5. Provide guidance on research quality and completeness
        
        You can:
        - Modify existing research content based on user feedback
        - Add new information to research
        - Restructure research for better presentation flow
        - Suggest additional research questions or topics
        - Provide general research guidance
        
        When modifying research, return JSON with 'content' and 'links' fields.
        When providing guidance, return conversational responses.
        """
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "type": "research",
            "can_modify": True,
            "can_add_content": True,
            "can_answer_questions": True,
            "can_suggest_improvements": True,
            "supported_actions": [
                "refine_research",
                "add_information", 
                "answer_questions",
                "suggest_topics",
                "improve_quality"
            ]
        }
    
    async def process_request(
        self,
        prompt: str,
        presentation_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process research-related requests."""
        
        if OFFLINE_MODE:
            return self._create_offline_response(prompt)
        
        # Get current research data
        research_data = self._extract_research_data(presentation_data)
        
        # Determine if this is a modification request or a question
        is_modification_request = self._is_modification_request(prompt)
        
        if is_modification_request:
            return await self._handle_research_modification(prompt, research_data)
        else:
            return await self._handle_research_question(prompt, research_data, presentation_data)
    
    def _extract_research_data(self, presentation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract research data from presentation."""
        steps = presentation_data.get("steps", [])
        research_step = next((s for s in steps if s.get("step") == "research"), None)
        
        if research_step and research_step.get("result"):
            return research_step["result"]
        
        return {"content": "", "links": []}
    
    def _is_modification_request(self, prompt: str) -> bool:
        """Determine if the prompt is asking for research modification."""
        modification_keywords = [
            "add", "include", "expand", "improve", "modify", "change", "update",
            "refine", "enhance", "extend", "elaborate", "more information",
            "more details", "additional", "extra", "supplement"
        ]
        
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in modification_keywords)
    
    async def _handle_research_modification(
        self, 
        prompt: str, 
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle requests to modify research content."""
        
        try:
            research_json = json.dumps(research_data, indent=2)
            
            input_prompt = f"""
            # Current Research Content
            ```json
            {research_json}
            ```

            # User Instructions
            {prompt}

            Please modify the research according to the instructions. Return only JSON with 'content' and 'links' fields.
            The 'content' should be the updated research text, and 'links' should be an array of relevant URLs.
            """
            
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": self.get_system_prompt()}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll help you modify research content according to your instructions."}]},
                    {"role": "user", "parts": [{"text": input_prompt}]}
                ]
            )
            
            text_response = response.text
            json_str = extract_json_from_text(text_response)
            modified_research = json.loads(json_str)
            
            # Validate the modified research
            ResearchData(**modified_research)
            
            return {
                "response": "I've updated the research content based on your request. You can preview the changes below.",
                "suggestions": {
                    "research": modified_research
                },
                "capabilities": self.get_capabilities()
            }
            
        except Exception as e:
            print(f"Error in research modification: {str(e)}")
            return {
                "response": "I encountered an error while trying to modify the research. Please try rephrasing your request.",
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
    
    async def _handle_research_question(
        self, 
        prompt: str, 
        research_data: Dict[str, Any],
        presentation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general questions about research."""
        
        try:
            research_json = json.dumps(research_data, indent=2)
            topic = presentation_data.get("topic", "Unknown topic")
            
            input_prompt = f"""
            # Presentation Topic
            {topic}
            
            # Current Research Content
            ```json
            {research_json}
            ```

            # User Question
            {prompt}

            Please provide a helpful response to the user's question about the research.
            You can suggest improvements, answer questions about the content, or provide guidance.
            Respond conversationally - do not return JSON for this type of request.
            """
            
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": self.get_system_prompt()}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll help answer questions about research and provide guidance."}]},
                    {"role": "user", "parts": [{"text": input_prompt}]}
                ]
            )
            
            return {
                "response": response.text,
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
            
        except Exception as e:
            print(f"Error in research question handling: {str(e)}")
            return {
                "response": "I encountered an error while processing your question. Please try again.",
                "suggestions": None,
                "capabilities": self.get_capabilities()
            } 