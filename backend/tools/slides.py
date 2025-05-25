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

# Check for offline mode
OFFLINE_MODE = os.environ.get("POWERIT_OFFLINE", "0").lower() in {"1", "true", "yes"}

def generate_offline_slides(research: ResearchData, target_slides: int = 10, author: str = None) -> dict:
    """
    Generate realistic offline slides response based on the research content.
    This creates a dynamic response that better matches what the real API would return.
    """
    # Use default author if none provided
    if author is None:
        author = PRESENTATION_STRUCTURE.get("default_author", "AI Presenter")
    
    # Extract key information from research content
    research_content = research.content if research and research.content else "Artificial Intelligence in Modern Business"
    
    # Try to extract a title from the research content
    lines = research_content.split('\n')
    title_candidates = []
    
    # Look for title-like content in the first few lines
    for line in lines[:10]:
        line = line.strip()
        if len(line) > 10 and len(line) < 100 and not line.startswith('-') and not line.startswith('•'):
            title_candidates.append(line)
    
    # Use the first good candidate or generate a generic title
    if title_candidates:
        presentation_title = title_candidates[0].rstrip('.').rstrip(':')
    else:
        presentation_title = "Business Presentation"
    
    # Extract key topics for sections
    content_sections = []
    current_section = []
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 5:
            # Check if this looks like a section header
            if (line.isupper() or 
                line.endswith(':') or 
                line.startswith('#') or 
                (len(line) < 50 and not line.startswith('-') and not line.startswith('•'))):
                if current_section:
                    content_sections.append(current_section)
                    current_section = []
                current_section.append(line.rstrip(':').rstrip('#').strip())
            else:
                current_section.append(line)
    
    if current_section:
        content_sections.append(current_section)
    
    # If no sections found, create generic ones
    if not content_sections:
        content_sections = [
            ["Introduction", "Overview of the topic", "Key concepts and definitions"],
            ["Main Content", "Core information and insights", "Important details and analysis"],
            ["Applications", "Practical applications", "Real-world examples and use cases"],
            ["Conclusion", "Summary of key points", "Next steps and recommendations"]
        ]
    
    # Generate slides dynamically
    slides = []
    
    # 1. Welcome slide
    slides.append({
        "type": "Welcome",
        "fields": {
            "title": presentation_title,
            "subtitle": "Professional Business Presentation",
            "author": author
        }
    })
    
    # 2. Process sections and create content
    section_count = 0
    slide_count = 1  # Already have welcome slide
    
    for section_data in content_sections[:4]:  # Limit to 4 sections to keep reasonable length
        section_title = section_data[0] if section_data else f"Section {section_count + 1}"
        section_content = section_data[1:] if len(section_data) > 1 else ["Content for this section"]
        
        # Add section divider
        slides.append({
            "type": "Section", 
            "fields": {
                "title": section_title
            }
        })
        slide_count += 1
        section_count += 1
        
        # Add 2-3 content slides per section with variety
        slides_in_section = 0
        max_slides_per_section = min(3, max(1, (target_slides - len(content_sections) - 1) // len(content_sections)))
        
        for i, content_item in enumerate(section_content[:max_slides_per_section]):
            if slide_count >= target_slides:
                break
                
            # Vary slide types for visual interest
            if slides_in_section == 0 and len(content_item) > 20:
                # First slide in section - use ContentImage for visual appeal
                slides.append({
                    "type": "ContentImage",
                    "fields": {
                        "title": f"{section_title} Overview",
                        "subtitle": "Key Points and Insights",
                        "content": [
                            content_item,
                            f"Important aspects of {section_title.lower()}",
                            "Supporting details and context"
                        ],
                        "image": f"Professional illustration representing {section_title.lower()} concepts and applications in business environment"
                    }
                })
            elif slides_in_section == 1 and section_count <= 2:
                # Second slide - use ImageFull for emphasis
                slides.append({
                    "type": "ImageFull",
                    "fields": {
                        "title": f"{section_title} in Detail",
                        "image": f"Detailed visual representation of {content_item[:50]}... showing modern business applications and innovative solutions",
                        "explanation": f"This image illustrates the key concepts and practical applications related to {section_title.lower()}, demonstrating real-world implementation and benefits"
                    }
                })
            elif slides_in_section == 2 and section_count == 2:
                # Third slide in second section - use 3Images for comparison
                slides.append({
                    "type": "3Images",
                    "fields": {
                        "title": f"Three Aspects of {section_title}",
                        "image1": f"Modern technology solutions for {section_title.lower()} showing digital transformation",
                        "image2": f"Business processes and workflows related to {section_title.lower()} in corporate environment", 
                        "image3": f"Future trends and innovations in {section_title.lower()} with growth projections",
                        "image1subtitle": "Technology Solutions",
                        "image2subtitle": "Business Processes", 
                        "image3subtitle": "Future Innovations"
                    }
                })
            elif "company" in content_item.lower() or "business" in content_item.lower() or any(word in content_item.lower() for word in ["google", "microsoft", "amazon", "apple", "meta"]):
                # Use ContentWithLogos when content mentions companies
                slides.append({
                    "type": "ContentWithLogos",
                    "fields": {
                        "title": f"Leading Companies in {section_title}",
                        "content": [
                            content_item,
                            "Industry leaders and innovators",
                            "Key players driving innovation",
                            "Market leaders setting industry standards"
                        ],
                        "logo1": "Google",
                        "logo2": "Microsoft", 
                        "logo3": "Amazon"
                    }
                })
            else:
                # Default to regular Content slide
                slides.append({
                    "type": "Content",
                    "fields": {
                        "title": content_item if len(content_item) < 60 else f"{section_title} Details",
                        "content": [
                            content_item,
                            f"Key insights about {section_title.lower()}",
                            "Supporting information and context",
                            "Practical implications and applications"
                        ]
                    }
                })
            
            slides_in_section += 1
            slide_count += 1
    
    # Add a conclusion slide if we have room
    if slide_count < target_slides:
        slides.append({
            "type": "Content",
            "fields": {
                "title": "Thank You & Questions",
                "content": [
                    "Thank you for your attention",
                    "Questions and discussion",
                    "Contact information available",
                    "Additional resources provided"
                ]
            }
        })
    
    # Process logos just like in online mode
    print(f"OFFLINE MODE: Processing logos for ContentWithLogos slides")
    for i, slide in enumerate(slides):
        slide_type = slide.get('type')
        if slide_type == 'ContentWithLogos':
            print(f"OFFLINE MODE: Processing ContentWithLogos slide {i}")
            
            # Fetch logos from worldvectorlogo.com (same as online mode)
            for logo_field in ['logo1', 'logo2', 'logo3']:
                if logo_field in slide["fields"] and slide["fields"][logo_field]:
                    logo_term = slide["fields"][logo_field]
                    print(f"OFFLINE MODE: Fetching logo for '{logo_term}'")
                    
                    try:
                        success, result = download_logo(logo_term)
                        if success:
                            # Update the slide with the path to the downloaded logo
                            slide["fields"][logo_field] = result
                            print(f"OFFLINE MODE: Successfully fetched logo for '{logo_term}': {result}")
                        else:
                            print(f"OFFLINE MODE WARNING: Failed to fetch logo for '{logo_term}': {result}")
                            # If logo fetch fails, keep the text name
                    except Exception as e:
                        print(f"OFFLINE MODE ERROR: Exception while fetching logo '{logo_term}': {str(e)}")

    # Add simple speaker notes for each slide
    for slide in slides:
        title = slide.get('fields', {}).get('title', 'this slide')
        slide.setdefault('fields', {})['notes'] = f"Speaker notes for {title}."

    return {
        "title": presentation_title,
        "author": author,
        "slides": slides
    }

async def generate_slides(research: ResearchData, target_slides: int = 10, author: str = None) -> SlidePresentation:
    """
    Generate presentation slides based on research data.
    
    Args:
        research: Research data about the topic
        target_slides: Approximate number of slides to generate
        author: Author name for the presentation (defaults to PRESENTATION_STRUCTURE's default_author)
        
    Returns:
        A SlidePresentation object with slide content
    """
    if OFFLINE_MODE:
        print(f"OFFLINE MODE: Generating dynamic slides response based on research content")
        offline_response = generate_offline_slides(research, target_slides, author)
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
    
    # Create the prompt for slide generation with updated format for the new Slide model
    prompt = f"""You are tasked with creating a professional presentation based on the following research:

{research_content}

Review the research content carefully and follow these guidelines:

1. If the research content contains specific instructions about:
   - Exact slide content
   - Specific number of slides
   - Particular speaker notes
   - Specific visual elements
   - Slide organization or structure
   - Any other precise details about the presentation

   Follow these instructions closely as specified. Do not deviate too much from explicit instructions, only if you want to introduce more visual elements.

2. If the research does not contain specific instructions:
   Create approximately {target_slides} slides for a professional presentation organized by sections.
   
IMPORTANT: You MUST use MULTIPLE DIFFERENT slide types. DO NOT default to using mostly 'Content' slides.
PRIORITIZE using 'ContentImage', 'ImageFull', and '3Images' slides wherever possible to make the presentation visually engaging.
AIM for no more than 30-40% of the main content slides (excluding Welcome/TOC/Section) to be of the plain 'Content' type.

REQUIRED SLIDE TYPES (these MUST be included):\
- 'Welcome' as the FIRST slide with title, subtitle, and author
- At least 2-3 'Section' slides to divide your content into logical sections
- A mix of 'Content' and 'ContentImage' slides (prefer 'ContentImage')
- At least one '3Images' or 'ImageFull' slide if the content suits visual presentation

Available slide types:
{slide_types_info}

SPECIAL INSTRUCTIONS FOR 'ContentWithLogos' SLIDES:
- Use the 'ContentWithLogos' slide type when discussing specific companies, products, technologies, tools, or services
- You can include 1 to 3 logos per slide
- For each logo, simply include the company or product name (e.g., "Amazon AWS", "Microsoft", "Google Cloud")
- Do not include any URLs or placeholders; the actual logos will be fetched automatically

The presentation MUST follow this structure:
- First slide MUST be a 'Welcome' slide that includes the presentation title, subtitle, and "{author}" as the author
- Content MUST be organized into sections, each STARTING with a 'Section' slide
- Use 'ContentImage' slides for important points that would benefit from visual illustration
- Use regular 'Content' slides for general material when you have too much text, and no suitable image (do not have too many slides with only text)
- Use 'ImageFull' for topics that need visual emphasis
- Use '3Images' for comparing multiple items visually
- Use 'ContentWithLogos' whenever discussing specific companies, products, or technologies that have recognizable logos

The slides should be organized in clear sections (like "Market Research", "Our Services", "Reference Cases", etc.)

REMEMBER: Use a VARIETY of slide types, prioritizing visual elements over plain text slides.

For each slide, ONLY provide the required fields based on its type, as follows, and always include a "notes" field with 1-2 sentences of speaker notes:
- Welcome slides: title, subtitle, author
- Section slides: title
- Content slides: title, content (MUST be a JSON array of strings, each string a bullet point)
- ContentImage slides: title, subtitle, image, content (MUST be a JSON array of strings, each string a bullet point)
- ImageFull slides: title, image, explanation
- 3Images slides: title, image1, image2, image3, image1subtitle, image2subtitle, image3subtitle
- ContentWithLogos slides: title, content (MUST be a JSON array of strings), logo1, logo2 (optional), logo3 (optional)

When there are images, do not put placeholders, put the explanation what should be on the image.
For logos, simply put the company or product name (e.g., "AWS", "Microsoft", "Google") - the actual logo will be fetched.

DO NOT include any fields not specifically listed for each slide type. For example, Welcome slides should NOT have a content field.

Note: Include the "notes" field for each slide. Do not include any "visual_suggestions" field.

Format your response as a valid JSON object where:
1. The root object has "title", "author", and "slides" properties
2. Each slide has "type" and "fields" properties
3. The "fields" property contains only the fields allowed for that slide type, AND the "content" field, when present, MUST be a JSON array of strings.

Make sure your JSON is valid with proper escaping of quotes and special characters. 
Each slide should only have the 'type' and 'fields' properties.
The 'fields' property should only contain the fields specified for that slide type.
"""
    print(f"DEBUG: Prompt length: {len(prompt)} characters")

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