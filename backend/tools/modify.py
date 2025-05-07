"""
Tools for modifying existing presentations based on user instructions.
"""

from typing import Dict, Any, Optional, List, Union
import json
import re

# Use absolute imports
from config import MODIFY_MODEL, MODIFY_CONFIG
from utils import extract_json_from_text
import google.generativeai as genai
from models import CompiledPresentation, CompiledSlide

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
    # Create the model with configuration from config.py
    model = genai.GenerativeModel(
        model_name=MODIFY_MODEL,
        generation_config=MODIFY_CONFIG
    )
    
    # Extract the specific slide to modify
    if slide_index < 0 or slide_index >= len(compiled_data.get("slides", [])):
        raise ValueError(f"Invalid slide index: {slide_index}")
    
    target_slide = compiled_data["slides"][slide_index]
    
    # Create the system prompt that explains how to modify a single slide
    system_prompt = """
    You are an expert presentation assistant that can modify and improve individual slides in PowerPoint-style presentations.
    
    You will be given:
    1. The current slide content to modify
    2. The full presentation context (for reference)
    3. Research data for context
    4. User instructions for how to modify the slide
    
    Analyze the content and modify ONLY the specified slide according to the user's instructions.
    Do not change any other slides or the presentation structure.
    
    Return ONLY the modified slide in the EXACT SAME FORMAT as the input slide,
    with any necessary changes applied. The response should be a JSON object representing 
    just the single slide - not the full presentation.
    
    IMPORTANT: Preserve all original fields in your response, even if you don't modify them.
    This includes 'title', 'content', 'type', 'notes', 'image' and any other fields present in the original slide.
    """
    
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
    # Create the model with configuration from config.py
    model = genai.GenerativeModel(
        model_name=MODIFY_MODEL,
        generation_config=MODIFY_CONFIG
    )
    
    # Create the system prompt that explains how to modify presentations
    system_prompt = """
    You are an expert presentation assistant that can modify and improve PowerPoint-style presentations.
    You will be given:
    1. A compiled presentation (with slides and images combined)
    2. Research data for context
    3. User instructions for how to modify the presentation
    
    Analyze the content and structure, then modify it according to the user's instructions.
    You can:
    - Add, remove, or reorder slides
    - Change slide content, titles, or image descriptions
    - Restructure presentations for better flow
    - Simplify or expand content
    - Change tone or style
    
    Return the modified presentation in the EXACT SAME FORMAT as the input compiled presentation,
    with any necessary changes applied.
    """
    
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