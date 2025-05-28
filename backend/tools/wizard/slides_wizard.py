"""
Slides wizard for handling slide-related requests.
"""

import json
from typing import Dict, Any, Optional, List
from .base_wizard import BaseWizard, OFFLINE_MODE
from utils import extract_json_from_text
from models import CompiledPresentation, CompiledSlide


class SlidesWizard(BaseWizard):
    """Wizard specialized for slides step assistance."""
    
    def get_system_prompt(self) -> str:
        return """
        You are an expert presentation slides assistant. You help users:
        
        1. Modify individual slide content (title, content, structure)
        2. Add new slides to presentations
        3. Remove slides from presentations
        4. Reorder slides for better flow
        5. Improve slide design and content quality
        6. Provide guidance on slide best practices
        
        You can work in two modes:
        - Single slide mode: Modify one specific slide
        - Presentation mode: Add/remove/reorder slides across the entire presentation
        
        When modifying slides, preserve the original format and structure.
        When adding slides, create them in the same format as existing slides.
        """
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "type": "slides",
            "can_modify_single": True,
            "can_modify_presentation": True,
            "can_add_slides": True,
            "can_remove_slides": True,
            "can_reorder_slides": True,
            "supported_actions": [
                "modify_slide_content",
                "improve_slide_design",
                "add_new_slide",
                "remove_slide",
                "reorder_slides",
                "enhance_presentation_flow"
            ]
        }
    
    async def process_request(
        self,
        prompt: str,
        presentation_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process slides-related requests."""
        
        if OFFLINE_MODE:
            return self._create_offline_response(prompt, context, presentation_data)
        
        # Extract slides data
        slides_data = self._extract_slides_data(presentation_data)
        research_data = self._extract_research_data(presentation_data)
        
        # Determine the type of request
        request_type = self._analyze_request_type(prompt, context)
        
        if request_type == "single_slide":
            return await self._handle_single_slide_modification(
                prompt, slides_data, research_data, context
            )
        elif request_type == "presentation_level":
            return await self._handle_presentation_modification(
                prompt, slides_data, research_data, presentation_data
            )
        else:
            return await self._handle_general_slides_question(
                prompt, slides_data, presentation_data
            )
    
    def _extract_slides_data(self, presentation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract slides data from presentation."""
        steps = presentation_data.get("steps", [])
        slides_step = next((s for s in steps if s.get("step") == "slides"), None)
        
        if slides_step and slides_step.get("result"):
            return slides_step["result"]
        
        return {"slides": [], "images": []}
    
    def _extract_research_data(self, presentation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract research data from presentation."""
        steps = presentation_data.get("steps", [])
        research_step = next((s for s in steps if s.get("step") == "research"), None)
        
        if research_step and research_step.get("result"):
            return research_step["result"]
        
        return {"content": "", "links": []}
    
    def _analyze_request_type(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Analyze what type of request this is."""
        prompt_lower = prompt.lower()
        
        # Check if context indicates single slide mode
        if context and context.get("mode") == "single" and context.get("slide_index") is not None:
            # But check if it's actually a presentation-level request
            if self._is_presentation_level_request(prompt):
                return "presentation_level"
            return "single_slide"
        
        # Check for presentation-level keywords
        if self._is_presentation_level_request(prompt):
            return "presentation_level"
        
        # Check for modification keywords
        modification_keywords = [
            "improve", "modify", "change", "update", "enhance", "refine", "edit"
        ]
        
        if any(keyword in prompt_lower for keyword in modification_keywords):
            return "single_slide" if context and context.get("slide_index") is not None else "presentation_level"
        
        return "general_question"
    
    def _is_presentation_level_request(self, prompt: str) -> bool:
        """Check if this is a presentation-level request (add/remove slides)."""
        prompt_lower = prompt.lower()
        
        presentation_keywords = [
            "add slide", "new slide", "another slide", "more slide", "extra slide",
            "remove slide", "delete slide", "take out slide", "delete this slide",
            "reorder", "rearrange", "move slide", "reorganize"
        ]
        
        return any(keyword in prompt_lower for keyword in presentation_keywords)
    
    async def _handle_single_slide_modification(
        self,
        prompt: str,
        slides_data: Dict[str, Any],
        research_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle single slide modification requests."""
        
        try:
            slide_index = context.get("slide_index") if context else None
            if slide_index is None or slide_index < 0:
                return {
                    "response": "Please select a specific slide to modify.",
                    "suggestions": None,
                    "capabilities": self.get_capabilities()
                }
            
            slides = slides_data.get("slides", [])
            if slide_index >= len(slides):
                return {
                    "response": f"Slide index {slide_index} is out of range. There are only {len(slides)} slides.",
                    "suggestions": None,
                    "capabilities": self.get_capabilities()
                }
            
            target_slide = slides[slide_index]
            
            # Create the modification prompt
            slide_json = json.dumps(target_slide, indent=2)
            research_json = json.dumps(research_data, indent=2)
            
            input_prompt = f"""
            # Current Slide to Modify (Slide {slide_index + 1})
            ```json
            {slide_json}
            ```

            # Research Context
            ```json
            {research_json}
            ```

            # User Instructions
            {prompt}

            Please modify ONLY this slide according to the instructions. 
            Return ONLY the modified slide as a JSON object.
            Preserve all original fields, even if you don't modify them.
            """
            
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": self.get_system_prompt()}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll help you modify the specific slide according to your instructions."}]},
                    {"role": "user", "parts": [{"text": input_prompt}]}
                ]
            )
            
            text_response = response.text
            json_str = extract_json_from_text(text_response)
            modified_slide = json.loads(json_str)
            
            # Ensure all original fields are preserved
            for key, value in target_slide.items():
                if key not in modified_slide:
                    modified_slide[key] = value
            
            # Validate the modified slide
            CompiledSlide(**modified_slide)
            
            return {
                "response": "I've created improvements for this slide. You can preview the changes below.",
                "suggestions": {
                    "slide": self._format_slide_for_frontend(modified_slide),
                    "slide_index": slide_index
                },
                "capabilities": self.get_capabilities()
            }
            
        except Exception as e:
            print(f"Error in single slide modification: {str(e)}")
            return {
                "response": "I encountered an error while trying to modify the slide. Please try rephrasing your request.",
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
    
    async def _handle_presentation_modification(
        self,
        prompt: str,
        slides_data: Dict[str, Any],
        research_data: Dict[str, Any],
        presentation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle presentation-level modifications (add/remove slides)."""
        
        try:
            compiled_data = {
                "slides": slides_data.get("slides", []),
                "images": slides_data.get("images", [])
            }
            
            compiled_json = json.dumps(compiled_data, indent=2)
            research_json = json.dumps(research_data, indent=2)
            
            input_prompt = f"""
            # Current Presentation Data
            ```json
            {compiled_json}
            ```

            # Research Context
            ```json
            {research_json}
            ```

            # User Instructions
            {prompt}

            Please modify the presentation according to the instructions. 
            You can add, remove, or reorder slides as needed.
            Return the complete modified presentation in the same format.
            """
            
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": self.get_system_prompt()}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll help you modify the entire presentation according to your instructions."}]},
                    {"role": "user", "parts": [{"text": input_prompt}]}
                ]
            )
            
            text_response = response.text
            json_str = extract_json_from_text(text_response)
            modified_data = json.loads(json_str)
            
            # Validate the modified presentation
            CompiledPresentation(**modified_data)
            
            # Format slides for frontend
            formatted_slides = [
                self._format_slide_for_frontend(slide) 
                for slide in modified_data.get("slides", [])
            ]
            
            return {
                "response": f"I've modified your presentation with {len(formatted_slides)} slides. You can preview the changes below.",
                "suggestions": {
                    "presentation": {
                        **presentation_data,
                        "slides": formatted_slides
                    }
                },
                "capabilities": self.get_capabilities()
            }
            
        except Exception as e:
            print(f"Error in presentation modification: {str(e)}")
            return {
                "response": "I encountered an error while trying to modify the presentation. Please try rephrasing your request.",
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
    
    async def _handle_general_slides_question(
        self,
        prompt: str,
        slides_data: Dict[str, Any],
        presentation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general questions about slides."""
        
        try:
            slides_count = len(slides_data.get("slides", []))
            topic = presentation_data.get("topic", "Unknown topic")
            
            input_prompt = f"""
            # Presentation Topic
            {topic}
            
            # Current Slides Count
            {slides_count} slides
            
            # User Question
            {prompt}

            Please provide helpful guidance about slides and presentation creation.
            Respond conversationally - do not return JSON for this type of request.
            """
            
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": self.get_system_prompt()}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll help answer questions about slides and provide guidance."}]},
                    {"role": "user", "parts": [{"text": input_prompt}]}
                ]
            )
            
            return {
                "response": response.text,
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
            
        except Exception as e:
            print(f"Error in slides question handling: {str(e)}")
            return {
                "response": "I encountered an error while processing your question. Please try again.",
                "suggestions": None,
                "capabilities": self.get_capabilities()
            }
    
    def _create_offline_response(self, prompt: str, context: Optional[Dict[str, Any]] = None, presentation_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an offline response with mock suggestions for testing."""
        
        # Determine request type for mock suggestions
        request_type = self._analyze_request_type(prompt, context) if context else "general_question"
        
        base_response = {
            "response": f"Offline mode: I understand your request '{prompt}'. In full mode, I would provide detailed assistance.",
            "capabilities": self.get_capabilities()
        }
        
        # Add mock suggestions for modification requests
        if request_type == "single_slide" and context and context.get("slide_index") is not None:
            # Mock single slide suggestion - get the current slide and modify it
            slide_index = context.get("slide_index")
            
            # Try to get the current slide from presentation data using the same extraction method
            current_slide = None
            if presentation_data:
                slides_data = self._extract_slides_data(presentation_data)
                slides = slides_data.get("slides", [])
                if 0 <= slide_index < len(slides):
                    current_slide = slides[slide_index]
            
            if current_slide:
                # Create a modified version of the current slide with substantial changes
                current_title = current_slide.get("title", "Slide Title")
                current_content = current_slide.get("content", "Slide content")
                
                # Make sure the suggested slide is definitely different
                suggested_title = f"Enhanced: {current_title}" if not current_title.startswith("Enhanced:") else f"Improved {current_title.replace('Enhanced: ', '')}"
                
                # Create substantially different content
                if "bullet points" in prompt.lower() or "engaging" in prompt.lower():
                    suggested_content = f"""• Key Point 1: Enhanced version of your content
• Key Point 2: Additional insights and details
• Key Point 3: Actionable takeaways for your audience

{current_content}

Additional engaging elements:
- Interactive examples
- Real-world applications
- Clear call-to-action"""
                else:
                    suggested_content = f"IMPROVED CONTENT: {current_content}\n\nAdditional enhancements:\n- Better structure\n- More engaging language\n- Clearer messaging"
                
                base_response["suggestions"] = {
                    "slide": {
                        "title": suggested_title,
                        "content": suggested_content,
                        "type": current_slide.get("type", "content"),
                        "imagePrompt": "Professional illustration that enhances the slide message"
                    }
                }
            else:
                # Fallback if no current slide found
                base_response["suggestions"] = {
                    "slide": {
                        "title": "Enhanced Slide Title",
                        "content": "• Improved bullet point 1\n• Enhanced bullet point 2\n• Engaging call-to-action",
                        "type": "content",
                        "imagePrompt": "Professional illustration"
                    }
                }
        elif request_type == "presentation_level":
            # Mock presentation-level suggestion
            base_response["suggestions"] = {
                "presentation": {
                    "slides": [
                        {
                            "id": "slide-0",
                            "type": "Content", 
                            "title": "Mock Slide 1 (Offline)",
                            "content": "Mock content for slide 1",
                            "order": 0,
                            "fields": {
                                "title": "Mock Slide 1 (Offline)",
                                "content": "Mock content for slide 1"
                            }
                        },
                        {
                            "id": "slide-1",
                            "type": "Content",
                            "title": "Mock Slide 2 (Offline)", 
                            "content": "Mock content for slide 2",
                            "order": 1,
                            "fields": {
                                "title": "Mock Slide 2 (Offline)",
                                "content": "Mock content for slide 2"
                            }
                        }
                    ]
                }
            }
        else:
            base_response["suggestions"] = None
            
        return base_response

    def _format_slide_for_frontend(self, slide: Dict[str, Any]) -> Dict[str, Any]:
        """Format a slide for frontend consumption."""
        fields = slide.get("fields", {})
        title = fields.get("title", "Untitled Slide")
        content = fields.get("content", "")
        
        # Handle content formatting
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content if item)
        elif not isinstance(content, str):
            content = str(content)
        
        return {
            "id": slide.get("id", ""),
            "type": slide.get("type", "Content"),
            "fields": fields,
            "title": title,
            "content": content,
            "notes": fields.get("notes", ""),
            "order": slide.get("order", 0),
            "imagePrompt": "",
            "imageUrl": slide.get("image_url", "")
        } 