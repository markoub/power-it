"""
Tools for modifying existing presentations based on user instructions.
This module now uses the new wizard system for better organization.
"""

from typing import Dict, Any, Optional, List, Union
import json
import re
import os
from prompts import get_prompt

# Use absolute imports
from config import MODIFY_MODEL, MODIFY_CONFIG
from utils.gemini import extract_json_from_text
import google.generativeai as genai
from models import CompiledPresentation, CompiledSlide, ResearchData
from .wizard.wizard_factory import WizardFactory

# Offline mode check
OFFLINE_MODE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes"}

# Global wizard factory instance
_wizard_factory = WizardFactory()

async def modify_single_slide(
    compiled_data: Dict[str, Any],
    research_data: Dict[str, Any],
    prompt: str,
    slide_index: int
) -> Dict[str, Any]:
    """
    Modify only a single slide in a presentation and return just that slide.

    Args:
        compiled_data: The compiled presentation data (slides and images)
        research_data: Research data for context
        prompt: User instructions for how to modify the slide
        slide_index: The index of the slide to modify

    Returns:
        A dictionary containing just the modified slide
    """

    if OFFLINE_MODE:
        # When offline, return a simple modified slide without calling Gemini
        if slide_index < 0 or slide_index >= len(compiled_data.get("slides", [])):
            raise ValueError(f"Invalid slide index: {slide_index}")

        target_slide = compiled_data["slides"][slide_index]
        modified_slide = json.loads(json.dumps(target_slide))

        fields = modified_slide.get("fields", {})
        title = fields.get("title", "Slide")
        fields["title"] = f"Modified: {title}"

        content = fields.get("content")
        if isinstance(content, list):
            content.append("Additional offline content")
        elif isinstance(content, str):
            fields["content"] = content + "\nAdditional offline content"
        else:
            fields["content"] = "Additional offline content"

        modified_slide["fields"] = fields

        return {"modified_slide": modified_slide, "slide_index": slide_index}
    # Create the model with configuration from config.py
    model = genai.GenerativeModel(
        model_name=MODIFY_MODEL,
        generation_config=MODIFY_CONFIG
    )
    
    # Extract the specific slide to modify
    if slide_index < 0 or slide_index >= len(compiled_data.get("slides", [])):
        raise ValueError(f"Invalid slide index: {slide_index}")
    
    target_slide = compiled_data["slides"][slide_index]
    
    # Get the system prompt from the centralized prompt system
    system_prompt = await get_prompt("modify_slide")
    
    # Create the input prompt with context
    try:
        # Convert the slide, presentation and research data to JSON strings
        slide_json = json.dumps(target_slide, indent=2)
        presentation_json = json.dumps(compiled_data, indent=2)
        research_json = json.dumps(research_data, indent=2)
        
        input_prompt = f"""
        # Current Slide to Modify (Slide {slide_index + 1})
        ```json
        {slide_json}
        ```

        # Full Presentation Context (For Reference Only)
        ```json
        {presentation_json}
        ```

        # Research Context
        ```json
        {research_json}
        ```

        # User Instructions
        {prompt}

        Please modify ONLY the specified slide according to the instructions. 
        Return ONLY the modified slide as a JSON object.
        Make sure to preserve all original fields in your response, even if you don't modify them.
        """
        
        # Generate a response with the model
        response = await model.generate_content_async(
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                },
                {
                    "role": "model",
                    "parts": [{"text": "I understand. I'll help you modify just the single specified slide according to the user's instructions while preserving its format and all original fields."}]
                },
                {
                    "role": "user",
                    "parts": [{"text": input_prompt}]
                }
            ]
        )
        
        # Extract the text from the response
        text_response = response.text
        
        # Use the extract_json_from_text utility function
        json_str = extract_json_from_text(text_response)
        
        # Parse JSON to get modified slide data
        modified_slide = json.loads(json_str)
        
        print(f"Successfully modified slide {slide_index} with prompt: {prompt}")
        
        # Ensure the modified slide preserves all properties from the original slide
        # This is a fallback in case the model forgets to include some fields
        for key, value in target_slide.items():
            if key not in modified_slide:
                modified_slide[key] = value
                print(f"Adding missing field '{key}' from original slide to modified slide")
        
        # Validate the modified slide matches expected structure
        CompiledSlide(**modified_slide)  # This will raise an exception if invalid
        
        # Return the modified slide as a dictionary
        return {
            "modified_slide": modified_slide,
            "slide_index": slide_index
        }
        
    except Exception as e:
        print(f"Error in modify_single_slide: {str(e)}")
        raise e

async def modify_presentation(
    compiled_data: Dict[str, Any],
    research_data: Dict[str, Any],
    prompt: str
) -> CompiledPresentation:
    """
    Modify a presentation based on user instructions using Gemini AI.
    
    Args:
        compiled_data: The compiled presentation data (slides and images)
        research_data: Research data for context
        prompt: User instructions for how to modify the presentation
        
    Returns:
        A CompiledPresentation with the modifications applied
    """
    # Offline mode returns the same presentation with minor changes
    if OFFLINE_MODE:
        modified = json.loads(json.dumps(compiled_data))
        if modified.get("slides"):
            for slide in modified["slides"]:
                fields = slide.get("fields", {})
                if "title" in fields:
                    fields["title"] = f"Modified: {fields['title']}"
        return CompiledPresentation(**modified)

    # Create the model with configuration from config.py
    model = genai.GenerativeModel(
        model_name=MODIFY_MODEL,
        generation_config=MODIFY_CONFIG
    )
    
    # Get the system prompt from the centralized prompt system
    system_prompt = await get_prompt("modify_presentation")
    
    # Create the input prompt with context
    try:
        # Convert the compiled data and research data to JSON strings
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

        Please modify the presentation according to the instructions. Return only the modified presentation JSON.
        """
        
        # Generate a response with the model
        response = await model.generate_content_async(
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                },
                {
                    "role": "model",
                    "parts": [{"text": "I understand. I'll help you modify PowerPoint presentations according to user instructions while preserving the original format."}]
                },
                {
                    "role": "user",
                    "parts": [{"text": input_prompt}]
                }
            ]
        )
        
        # Extract the text from the response
        text_response = response.text
        
        # Use the extract_json_from_text utility function
        json_str = extract_json_from_text(text_response)
        
        # Parse JSON to get modified data
        modified_data = json.loads(json_str)
        
        print(f"Successfully modified presentation with prompt: {prompt}")
        # Convert to Pydantic model and return
        return CompiledPresentation(**modified_data)

    except Exception as e:
        print(f"Error in modify_presentation: {str(e)}")
        raise e


async def process_wizard_request(
    prompt: str,
    presentation_data: Dict[str, Any],
    current_step: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a wizard request using the new wizard system.
    
    Args:
        prompt: User's request/question
        presentation_data: Current presentation data
        current_step: Current step in the presentation workflow
        context: Additional context (e.g., selected slide, mode)
        
    Returns:
        Dictionary containing response and any suggested changes
    """
    return await _wizard_factory.process_wizard_request(
        prompt, presentation_data, current_step, context
    )


async def modify_research(
    research_data: Dict[str, Any],
    prompt: str
) -> ResearchData:
    """Modify research content based on user instructions."""

    if OFFLINE_MODE:
        modified_content = research_data.get("content", "") + f"\n\nOffline modification: {prompt}"
        return ResearchData(content=modified_content, links=research_data.get("links", []))

    model = genai.GenerativeModel(
        model_name=MODIFY_MODEL,
        generation_config=MODIFY_CONFIG
    )

    try:
        research_json = json.dumps(research_data, indent=2)
        input_prompt = f"""
        # Current Research Content
        ```json
        {research_json}
        ```

        # User Instructions
        {prompt}

        Update the research according to the instructions and return only JSON with 'content' and 'links'.
        """

        response = await model.generate_content_async(
            contents=[
                {"role": "user", "parts": [{"text": "You improve existing research for presentations."}]},
                {"role": "user", "parts": [{"text": input_prompt}]},
            ]
        )

        text_response = response.text
        json_str = extract_json_from_text(text_response)
        modified = json.loads(json_str)

        return ResearchData(**modified)

    except Exception as e:
        print(f"Error in modify_research: {str(e)}")
        raise e
