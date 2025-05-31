import google.generativeai as genai
import json
import re
import sys
import traceback
import os
from typing import Dict, Any, List, Optional

# Use absolute imports
from config import SLIDES_MODEL, SLIDES_CONFIG
from utils import extract_json_from_text
from models import ResearchData, SlidePresentation, Slide
from tools.slide_config import SLIDE_TYPES, PRESENTATION_STRUCTURE
from tools.logo_fetcher import search_logo, download_logo
from offline_responses.slides import generate_offline_slides
from default_prompts import DEFAULT_SLIDES_PROMPT
from prompts import get_prompt

# Check for offline mode
OFFLINE_MODE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes"}


async def generate_slides(
    research: ResearchData, 
    target_slides: int = 10, 
    author: str = None,
    target_audience: str = "general",
    content_density: str = "medium",
    presentation_duration: int = 15,
    custom_prompt: str = None
) -> SlidePresentation:
    """
    Generate presentation slides based on research data.
    
    Args:
        research: Research data about the topic
        target_slides: Approximate number of slides to generate
        author: Author name for the presentation (defaults to PRESENTATION_STRUCTURE's default_author)
        target_audience: Target audience for the presentation (e.g., 'executives', 'technical', 'general')
        content_density: Content density level ('low', 'medium', 'high')
        presentation_duration: Total presentation duration in minutes (affects speaker notes)
        custom_prompt: Additional custom prompt to influence slide generation
        
    Returns:
        A SlidePresentation object with slide content
    """
    if OFFLINE_MODE:
        print(f"OFFLINE MODE: Generating dynamic slides response based on research content")
        offline_response = generate_offline_slides(research, target_slides, author, target_audience, content_density, presentation_duration, custom_prompt)
        print(f"OFFLINE MODE: Generated {len(offline_response['slides'])} slides with title: {offline_response['title']}")
        
        # Log the slide types for debugging
        slide_types = [slide['type'] for slide in offline_response['slides']]
        print(f"OFFLINE MODE: Slide types generated: {slide_types}")
        
        # Count slides that should have images
        image_slide_types = ['ContentImage', 'ImageFull', '3Images', 'ContentWithLogos']
        image_slides = [slide for slide in offline_response['slides'] if slide['type'] in image_slide_types]
        print(f"OFFLINE MODE: {len(image_slides)} slides require images")
        
        return SlidePresentation(**offline_response)

    print(f"\n===== DEBUG: Starting slide generation =====")
    print(f"Target slides: {target_slides}")
    print(f"Author: {author}")
    print(f"Research content length: {len(research.content) if research and research.content else 'None'}")
    
    # Format the research content for the prompt
    research_content = research.content
    
    # Use default author if none provided
    if author is None:
        author = PRESENTATION_STRUCTURE.get("default_author", "Marko Milosevic")
        print(f"DEBUG: Using default author: {author}")
    
    # Generate slide type information for the prompt, filtering by include_in_prompt flag
    slide_types_info = "\n".join([
        f"- '{slide_type}': {info['description']}" 
        for slide_type, info in SLIDE_TYPES.items()
        if info.get('include_in_prompt', True)  # Only include slide types marked for prompt inclusion
    ])
    
    prompt_slide_types = [slide_type for slide_type, info in SLIDE_TYPES.items() 
                          if info.get('include_in_prompt', True)]
    print(f"DEBUG: Slide types included in prompt: {', '.join(prompt_slide_types)}")
    
    # Create content density instructions
    density_instructions = {
        "low": "Keep slides concise with minimal text. Use 2-3 bullet points per slide maximum. Focus on visual elements and key messages only.",
        "medium": "Balance text with visuals. Use 3-5 bullet points per slide. Include adequate detail without overwhelming the audience.",
        "high": "Provide comprehensive detail. Use 5-7 bullet points per slide. Include thorough explanations and supporting information."
    }
    
    # Create audience-specific instructions
    audience_instructions = {
        "executives": "Focus on high-level strategy, business impact, ROI, and key metrics. Use executive summary style content.",
        "technical": "Include technical details, implementation specifics, architecture diagrams, and technical considerations.",
        "general": "Use accessible language suitable for a broad audience. Balance technical concepts with business value.",
        "students": "Include educational context, step-by-step explanations, and learning objectives.",
        "sales": "Emphasize benefits, competitive advantages, customer success stories, and value propositions."
    }
    
    # Calculate speaker notes timing (approximate words per minute = 150)
    avg_words_per_minute = 150
    total_words_budget = presentation_duration * avg_words_per_minute
    words_per_slide = total_words_budget // target_slides if target_slides > 0 else 100
    
    # Build dynamic prompt additions
    customization_prompt = f"""
CUSTOMIZATION REQUIREMENTS:
- Target Audience: {target_audience.title()} - {audience_instructions.get(target_audience, audience_instructions['general'])}
- Content Density: {content_density.title()} - {density_instructions.get(content_density, density_instructions['medium'])}
- Presentation Duration: {presentation_duration} minutes total
- Speaker Notes: Write approximately {words_per_slide} words per slide in the "notes" field to match the {presentation_duration}-minute duration
"""
    
    if custom_prompt:
        customization_prompt += f"""
- Custom Instructions: {custom_prompt}
"""
    
    # Create the prompt for slide generation with updated format for the new Slide model
    prompt_template = await get_prompt("slides_prompt", DEFAULT_SLIDES_PROMPT)
    prompt = prompt_template.format(
        research_content=research_content, 
        target_slides=target_slides, 
        slide_types_info=slide_types_info, 
        author=author
    ) + customization_prompt
    
    print(f"DEBUG: Prompt length: {len(prompt)} characters")
    print(f"DEBUG: Target audience: {target_audience}, Content density: {content_density}, Duration: {presentation_duration}min")

    try:
        # Generate the slides using Gemini
        print(f"DEBUG: Initializing Gemini model: {SLIDES_MODEL}")
        model = genai.GenerativeModel(SLIDES_MODEL)
        print(f"DEBUG: Model initialized")
        
        print(f"DEBUG: Sending request to Gemini API...")

        function_declaration = {
            "name": "create_presentation",
            "description": "Structured slide presentation response",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "slides": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "fields": {"type": "object"}
                            },
                            "required": ["type", "fields"]
                        }
                    }
                },
                "required": ["title", "slides"]
            }
        }

        response = await model.generate_content_async(
            prompt,
            generation_config=SLIDES_CONFIG,
            tools=[{"function_declarations": [function_declaration]}],
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
            ]
        )
        print(f"DEBUG: Received response from Gemini")
        print(f"DEBUG: Response text length: {len(response.text)}")
        
        # Parse the response to extract the JSON
        json_str = None

        # Check for structured function call response
        try:
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if candidate.content.parts and hasattr(candidate.content.parts[0], "function_call"):
                    json_str = candidate.content.parts[0].function_call.args
                    if not isinstance(json_str, str):
                        json_str = None
        except Exception as e:
            print(f"DEBUG: Failed to parse structured response: {e}")

        if not json_str:
            response_text = response.text
            print(f"DEBUG: Looking for JSON content in response text...")
            if "```json" in response_text:
                print(f"DEBUG: Found markdown JSON code block")
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx == -1 or end_idx == 0:
                    print(f"DEBUG ERROR: No JSON object found in response")
                    raise ValueError("No JSON found in response")
                json_str = response_text[start_idx:end_idx]
        
        # Debug information about potentially problematic characters
        problem_chars = []
        for i, char in enumerate(json_str):
            if char in ['"', '\\'] and i > 0 and json_str[i-1] != '\\':
                if i > 13600 and i < 13800:  # Check around the problematic area
                    problem_chars.append((i, char, json_str[i-10:i+10]))
        
        if problem_chars:
            print(f"DEBUG: Potentially problematic characters in JSON around position 13705:")
            for pos, char, context in problem_chars:
                print(f"DEBUG: Position {pos}: Character '{char}', Context: '{context}'")
        
        # Try to parse JSON
        print(f"DEBUG: Attempting to parse JSON...")
        try:
            slides_data = json.loads(json_str)
            print(f"DEBUG: JSON parsed successfully")
            
            # Check slides_data structure
            print(f"DEBUG: Validating JSON structure...")
            if not isinstance(slides_data, dict):
                print(f"DEBUG ERROR: Parsed JSON is not a dictionary, got {type(slides_data)}")
                raise ValueError(f"Unexpected JSON structure: {type(slides_data)}")
                
            if "slides" not in slides_data:
                print(f"DEBUG ERROR: 'slides' key missing from JSON")
                print(f"DEBUG: Available keys: {list(slides_data.keys())}")
                raise ValueError("'slides' key missing from JSON")
                
            print(f"DEBUG: Found {len(slides_data['slides'])} slides in generated content")
            
            # Check slide types
            slide_types = [slide.get("type") for slide in slides_data["slides"]]
            print(f"DEBUG: Slide types in generated content: {slide_types}")
            
            # Check if all required slide types exist
            has_welcome = any(s_type == "Welcome" for s_type in slide_types)
            has_section = any(s_type == "Section" for s_type in slide_types)
            
            print(f"DEBUG: Has Welcome slide: {has_welcome}")
            print(f"DEBUG: Has Section slide: {has_section}")
            
            # Validate each slide has required fields for its type
            print(f"DEBUG: Validating slide fields...")
            for i, slide in enumerate(slides_data["slides"]):
                slide_type = slide.get("type")
                
                # Check that the slide has a fields property
                if "fields" not in slide:
                    print(f"DEBUG WARNING: Slide {i} missing 'fields' property. Converting old format to new.")
                    # Convert old format to new format
                    fields = {}
                    for key, value in slide.items():
                        if key != "type":
                            fields[key] = value
                    slide["fields"] = fields
                    # Remove all non-type keys from the slide
                    keys_to_remove = [k for k in slide.keys() if k not in ["type", "fields"]]
                    for key in keys_to_remove:
                        del slide[key]
                
                # Check that the fields conform to the slide type's components
                if slide_type in SLIDE_TYPES:
                    # Get allowed components for this slide type
                    required_components = SLIDE_TYPES[slide_type]["components"]
                    
                    # Check for and remove any fields that aren't in the components list
                    fields_to_remove = [field for field in slide["fields"] 
                                      if field not in required_components and field != "title"]
                    
                    if fields_to_remove:
                        print(f"DEBUG WARNING: Removing extra fields {fields_to_remove} from slide {i} (type: {slide_type})")
                        for field in fields_to_remove:
                            print(f"DEBUG: Removing field '{field}' with value: {slide['fields'][field]}")
                            
                            # Special handling for 3Images slide that might have 'images' array instead of individual image fields
                            if slide_type == '3Images' and field == 'images' and isinstance(slide['fields'][field], list):
                                images = slide['fields'][field]
                                print(f"DEBUG: Converting 'images' array to individual image fields for 3Images slide")
                                
                                # Map the first 3 images to the required image fields
                                for i, img_data in enumerate(images[:3]):
                                    img_num = i + 1
                                    if 'image' in img_data:
                                        slide['fields'][f'image{img_num}'] = img_data['image']
                                        print(f"DEBUG: Set image{img_num} to {img_data['image']}")
                                    if 'subtitle' in img_data:
                                        slide['fields'][f'image{img_num}subtitle'] = img_data['subtitle']
                                        print(f"DEBUG: Set image{img_num}subtitle to {img_data['subtitle']}")
                        
                            del slide['fields'][field]
                    
                    # Check for missing required fields
                    missing_fields = [field for field in required_components 
                                     if field not in slide["fields"] and field != "title"]
                    
                    if missing_fields:
                        print(f"DEBUG WARNING: Slide {i} (type: {slide_type}) missing required fields: {missing_fields}")
                        
                        # If critical fields are missing, convert to a simpler slide type
                        if slide_type == 'ContentImage' and 'image' in missing_fields:
                            print(f"DEBUG: Converting ContentImage slide to Content slide due to missing image field")
                            slide["type"] = 'Content'
                        elif slide_type == 'ImageFull' and 'image' in missing_fields:
                            print(f"DEBUG: Converting ImageFull slide to Content slide due to missing image field")
                            slide["type"] = 'Content'
                        elif slide_type == '3Images' and any(f'image{i}' in missing_fields for i in range(1, 4)):
                            if 'image1' not in missing_fields:  # At least one image exists
                                print(f"DEBUG: Converting 3Images slide to ContentImage slide due to missing image fields")
                                slide["type"] = 'ContentImage'
                                if 'image1' in slide["fields"]:
                                    slide["fields"]["image"] = slide["fields"]["image1"]
                                if 'image1subtitle' in slide["fields"]:
                                    slide["fields"]["subtitle"] = slide["fields"]["image1subtitle"]
                            else:
                                print(f"DEBUG: Converting 3Images slide to Content slide due to missing all image fields")
                                slide["type"] = 'Content'
                
                # Special handling for ContentWithLogos slide - fetch the actual logos
                if slide_type == 'ContentWithLogos':
                    print(f"DEBUG: Processing ContentWithLogos slide {i}")
                    
                    # Fetch logos from worldvectorlogo.com
                    for logo_field in ['logo1', 'logo2', 'logo3']:
                        if logo_field in slide["fields"] and slide["fields"][logo_field]:
                            logo_term = slide["fields"][logo_field]
                            print(f"DEBUG: Fetching logo for '{logo_term}'")
                            
                            try:
                                success, result = download_logo(logo_term)
                                if success:
                                    # Update the slide with the path to the downloaded logo
                                    slide["fields"][logo_field] = result
                                    print(f"DEBUG: Successfully fetched logo for '{logo_term}': {result}")
                                else:
                                    print(f"DEBUG WARNING: Failed to fetch logo for '{logo_term}': {result}")
                                    # If logo fetch fails, keep the text name
                            except Exception as e:
                                print(f"DEBUG ERROR: Exception while fetching logo '{logo_term}': {str(e)}")
            
            # Add TableOfContents slide if auto-generation is enabled
            if PRESENTATION_STRUCTURE.get("auto_generate_toc", True):
                print(f"DEBUG: Auto-generating TableOfContents slide")
                
                # Find all Section slides to build the TOC
                sections = []
                for slide in slides_data["slides"]:
                    if slide.get("type") == "Section":
                        sections.append(slide["fields"]["title"])
                
                # If we have sections, add the TOC slide
                # If we're adding sections later, just use the default section title
                if sections or not has_section:
                    # If we don't have sections yet but will add a default one
                    if not sections and not has_section:
                        sections = ["Main Content"]
                        
                    # Create a TableOfContents slide
                    toc_slide = {
                        "type": "TableOfContents",
                        "fields": {
                            "title": "Table of Contents",
                            "sections": sections
                        }
                    }
                    
                    # Insert after the Welcome slide
                    if has_welcome:
                        insert_index = 1  # After Welcome slide
                    else:
                        insert_index = 0  # At the beginning
                        
                    slides_data["slides"].insert(insert_index, toc_slide)
                    print(f"DEBUG: Added TableOfContents slide with {len(sections)} sections")
            
            # Add Welcome slide if missing
            if not has_welcome:
                print(f"DEBUG: Adding missing Welcome slide")
                welcome_slide = {
                    "type": "Welcome",
                    "fields": {
                        "title": slides_data.get("title", "Presentation"),
                        "subtitle": "Generated presentation",
                        "author": author
                    }
                }
                slides_data["slides"].insert(0, welcome_slide)
                
            # Check for sections and add at least one if missing
            if not has_section:
                print(f"DEBUG: No Section slides found, adding a default Section slide")
                section_slide = {
                    "type": "Section",
                    "fields": {
                        "title": "Main Content"
                    }
                }
                # Insert after Welcome slide and TOC (which will be auto-generated)
                slides_data["slides"].insert(2, section_slide)
            
        except json.JSONDecodeError as json_err:
            # Print the specific error and context
            error_pos = json_err.pos
            print(f"DEBUG ERROR: JSON parsing error at position {error_pos}")
            
            # Show context around error position
            start = max(0, error_pos - 50)
            end = min(len(json_str), error_pos + 50)
            context = json_str[start:end]
            
            marker = ' ' * (min(50, error_pos - start)) + '^'
            
            print(f"DEBUG: Context around error: \n{context}\n{marker}")
            
            # Try to fix common JSON issues
            print(f"DEBUG: Attempting to fix JSON...")
            fixed_json_str = json_str.replace('\\"', '"')
            fixed_json_str = re.sub(r'([^\\])"([^"]*?)([^\\])"', r'\1"\2\3"', fixed_json_str)
            
            try:
                slides_data = json.loads(fixed_json_str)
                print("DEBUG: Fixed JSON successfully")
            except json.JSONDecodeError as e:
                print(f"DEBUG ERROR: Failed to fix JSON: {str(e)}")
                raise
        
        # Create a SlidePresentation object
        print(f"DEBUG: Creating SlidePresentation object...")
        presentation = SlidePresentation(**slides_data)
        print(f"DEBUG: Successfully created SlidePresentation with {len(presentation.slides)} slides")
        return presentation
        
    except Exception as e:
        # Handle any error
        print(f"DEBUG ERROR: Error while generating slides: {str(e)}")
        print(f"DEBUG ERROR: Error type: {type(e).__name__}")
        print("DEBUG: Stack trace:")
        traceback.print_exc()
        
        # Create a minimal slide deck as fallback
        print(f"DEBUG: Generating fallback slides")
        fallback_slides = {
            "title": "Presentation on the Requested Topic",
            "author": author,
            "slides": [
                {
                    "type": "Content",
                    "fields": {
                        "title": "Overview",
                        "content": ["An error occurred while generating slides.", "Please try again or refine your research."]
                    }
                }
            ]
        }
        
        fallback_presentation = SlidePresentation(**fallback_slides)
        print(f"DEBUG: Returning fallback presentation with {len(fallback_presentation.slides)} slides")
        return fallback_presentation 