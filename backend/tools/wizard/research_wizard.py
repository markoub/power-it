"""
Research wizard for handling research-related requests.
"""

import json
from typing import Dict, Any, Optional
from .base_wizard import BaseWizard, OFFLINE_MODE
from utils.gemini import extract_json_from_text
from models import ResearchData
from prompts import get_prompt
from tools.research import check_clarifications


class ResearchWizard(BaseWizard):
    """Wizard specialized for research step assistance."""
    
    async def get_system_prompt(self) -> str:
        return await get_prompt("wizard_research_system")
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "type": "research",
            "can_modify": True,
            "can_add_content": True,
            "can_answer_questions": True,
            "can_suggest_improvements": True,
            "can_clarify": True,
            "supported_actions": [
                "refine_research",
                "add_information", 
                "answer_questions",
                "suggest_topics",
                "improve_quality",
                "clarify_ambiguities"
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
            return self._create_offline_response(prompt, presentation_data)
        
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
            
            prompt_template = await get_prompt("wizard_research_modify")
            input_prompt = prompt_template.format(
                research_json=research_json,
                prompt=prompt
            )
            
            system_prompt = await self.get_system_prompt()
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt}]},
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
            
            system_prompt = await self.get_system_prompt()
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt}]},
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
    
    async def check_topic_clarifications(self, topic: str) -> Optional[Dict[str, Any]]:
        """Check if a topic needs clarification before research."""
        
        # Use the research tool's clarification check (works in both online and offline modes)
        result = await check_clarifications(topic)
        
        # If we got a result with needs_clarification=True, return it
        if result and result.get("needs_clarification"):
            return result
        
        # Otherwise return None (no clarification needed)
        return None
    
    def _create_offline_response(self, prompt: str, presentation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create realistic offline responses for testing."""
        
        # Extract current research data
        research_data = self._extract_research_data(presentation_data)
        current_content = research_data.get("content", "")
        current_links = research_data.get("links", [])
        
        # Determine request type
        is_modification = self._is_modification_request(prompt)
        prompt_lower = prompt.lower()
        
        if is_modification:
            # Create mock modified research based on request type
            modified_content = current_content
            
            if "ethics" in prompt_lower or "privacy" in prompt_lower:
                # Add ethics section
                ethics_section = """

## Ethical Considerations and Privacy Concerns

### Data Privacy
- Implementation of robust data encryption and anonymization techniques
- Compliance with GDPR, HIPAA, and other regulatory frameworks
- Patient consent management and data ownership rights

### AI Ethics in Healthcare
- Addressing algorithmic bias in medical AI systems
- Ensuring transparency and explainability of AI decisions
- Maintaining human oversight in critical medical decisions
- Equitable access to AI-powered healthcare solutions

### Key Challenges
1. Balancing innovation with patient privacy protection
2. Ensuring AI systems don't perpetuate healthcare disparities
3. Managing liability and accountability in AI-assisted diagnoses
4. Protecting sensitive health data from breaches and misuse"""
                
                modified_content = current_content + ethics_section
                
            elif "future" in prompt_lower or "trends" in prompt_lower:
                # Add future trends section
                trends_section = """

## Future Trends and Developments

### Emerging Technologies
- Integration of quantum computing for drug discovery
- Advanced natural language processing for patient interactions
- Federated learning for privacy-preserving AI training
- Digital twins for personalized treatment planning

### Expected Developments (2024-2030)
1. AI-powered preventive medicine becoming mainstream
2. Fully automated diagnostic laboratories
3. Virtual health assistants for 24/7 patient support
4. Precision medicine tailored to individual genetics

### Investment and Growth
- Projected market growth to $150 billion by 2030
- Increased venture capital funding in health tech
- Government initiatives supporting AI in healthcare"""
                
                modified_content = current_content + trends_section
                
            elif "introduction" in prompt_lower or "engaging" in prompt_lower:
                # Improve introduction
                new_intro = """# Artificial Intelligence in Healthcare: Transforming Medicine

> "AI is not just changing healthcare—it's revolutionizing how we understand, prevent, and treat disease." - Dr. Eric Topol

## Introduction

Imagine a world where diseases are detected before symptoms appear, where treatment plans are tailored to your unique genetic makeup, and where AI assistants help doctors make life-saving decisions in seconds. This isn't science fiction—it's the reality of AI in healthcare today.

The integration of artificial intelligence in healthcare represents one of the most significant technological shifts in modern medicine. From diagnostic imaging that catches cancer earlier than ever before, to predictive algorithms that identify at-risk patients, AI is fundamentally changing how we deliver and receive medical care.

"""
                # Replace or prepend the introduction
                if current_content.startswith("#"):
                    # Find the first paragraph after the title
                    lines = current_content.split("\n")
                    title_index = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith("#"):
                            title_index = i
                            break
                    modified_content = new_intro + "\n".join(lines[title_index:])
                else:
                    modified_content = new_intro + current_content
            
            elif "section" in prompt_lower or "add" in prompt_lower:
                # Generic section addition
                new_section = """

## Additional Insights

### Recent Developments
- Breakthrough AI models achieving human-level performance in specific medical tasks
- Successful clinical trials of AI-assisted surgical systems
- Growing adoption of AI in rural and underserved healthcare settings

### Best Practices
- Ensuring diverse training data to reduce bias
- Continuous monitoring and validation of AI systems
- Maintaining strong physician-AI collaboration
- Regular updates based on new medical research"""
                
                modified_content = current_content + new_section
            
            # Add some mock links if needed
            if len(current_links) < 3:
                new_links = current_links + [
                    "https://www.nature.com/articles/ai-healthcare-2024",
                    "https://www.who.int/health-topics/artificial-intelligence",
                    "https://jamanetwork.com/journals/jama/ai-medicine"
                ]
            else:
                new_links = current_links
            
            return {
                "type": "research_modification",
                "response": "I've updated the research content based on your request. The changes include the specific information you asked for.",
                "suggestions": {
                    "research": {
                        "content": modified_content,
                        "links": new_links
                    }
                },
                "capabilities": self.get_capabilities(),
                "wizard_type": "research",
                "step": "research"
            }
        
        else:
            # Handle questions and guidance requests
            if "what" in prompt_lower and "about" in prompt_lower:
                response = """Based on the research content, this presentation covers comprehensive information about the topic. The research includes:

1. **Main themes**: The core concepts and current state of the field
2. **Key challenges**: Current limitations and obstacles
3. **Applications**: Real-world use cases and implementations
4. **Future outlook**: Emerging trends and potential developments

The research appears well-structured with clear sections and supporting evidence. Would you like me to elaborate on any specific aspect?"""
            
            elif "improve" in prompt_lower or "quality" in prompt_lower:
                response = """Here are some suggestions to improve the research quality:

1. **Add more recent data**: Include statistics and studies from 2023-2024
2. **Expand case studies**: Add 2-3 specific real-world examples
3. **Include expert quotes**: Add perspectives from industry leaders
4. **Strengthen the conclusion**: Summarize key takeaways more clearly
5. **Add visual data**: Mention relevant charts or infographics that could support the points

The current research provides a solid foundation. These enhancements would make it more comprehensive and engaging."""
            
            elif "main" in prompt_lower and ("challenge" in prompt_lower or "concern" in prompt_lower):
                response = """Based on the research, the main challenges and concerns include:

1. **Technical challenges**: Integration with existing systems, data quality, and algorithm accuracy
2. **Ethical considerations**: Privacy, bias, transparency, and accountability
3. **Regulatory hurdles**: Compliance with healthcare regulations and approval processes
4. **Economic factors**: High implementation costs and ROI uncertainty
5. **Human factors**: Resistance to change and need for training

These challenges are significant but not insurmountable with proper planning and implementation strategies."""
            
            else:
                # Generic helpful response
                response = """I understand your question about the research. The current research provides comprehensive coverage of the topic with well-structured sections and relevant information.

To provide more specific assistance, I can help you:
- Add new sections or expand existing ones
- Improve the clarity and engagement of the content
- Include more recent developments or case studies
- Strengthen the introduction or conclusion
- Add more supporting evidence or expert perspectives

What specific aspect would you like to focus on?"""
            
            return {
                "type": "explanation",
                "response": response,
                "suggestions": None,
                "capabilities": self.get_capabilities(),
                "wizard_type": "research",
                "step": "research"
            } 