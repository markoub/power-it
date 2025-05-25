import google.generativeai as genai
import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from config import RESEARCH_MODEL, RESEARCH_CONFIG, OFFLINE_MODE
import logging
from models import ResearchData
from utils import process_gemini_response
from offline_responses.research import get_offline_research
from default_prompts import DEFAULT_RESEARCH_PROMPT
from prompts import get_prompt

# Define the structured output schema for research results
RESEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "content": {
            "type": "string",
            "description": "Comprehensive markdown content for the presentation including headings, lists, and detailed information"
        },
        "links": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "href": {
                        "type": "string",
                        "description": "URL of the source"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the source"
                    }
                },
                "required": ["href", "title"]
            },
            "description": "List of reference links with href and title"
        }
    },
    "required": ["content", "links"]
}

async def research_topic(query: str, mode: str = "ai") -> ResearchData:
    """
    Research a topic for a presentation.
    
    Args:
        query: Research topic or presentation title
        mode: Research mode ('ai' or 'manual')
        
    Returns:
        ResearchData object containing research results
    """
    # For manual research mode, just return a template, even in offline mode
    if mode == "manual":
        content = f"# {query}\n\n## Introduction\n\nThis is a template for a presentation about {query}.\n\n## Key Points\n\nAdd your key points here.\n\n## Details\n\nAdd details here.\n\n## Examples\n\nAdd examples here.\n\n## Conclusion\n\nAdd your conclusion here."
        return ResearchData(content=content, links=[])

    # For AI mode in offline mode, use the dedicated offline response
    if OFFLINE_MODE:
        return await get_offline_research(query)

    # Rest of the original function for online mode with structured output
    # Create a copy of the research config and add structured output schema
    structured_config = RESEARCH_CONFIG.copy()
    structured_config["response_schema"] = RESEARCH_SCHEMA
    
    # Configure Gemini model with structured output
    model = genai.GenerativeModel(
        model_name=RESEARCH_MODEL,
        generation_config=structured_config
    )
    
    # Load the prompt template from the database
    prompt_template = await get_prompt("research_prompt", DEFAULT_RESEARCH_PROMPT)
    prompt = prompt_template.format(query=query)
    
    # Get response from Gemini with structured output
    try:
        response = model.generate_content(prompt)
        
        # Debug logging to see the raw response
        print("Gemini API structured response:")
        print(response.text)
        print("=====================")

        # Parse the JSON response directly since it's guaranteed to be valid JSON
        parsed_data = json.loads(response.text)
        
        # Create and return ResearchData object
        return ResearchData(
            content=parsed_data.get("content", ""),
            links=parsed_data.get("links", [])
        )
    
    except Exception as e:
        logging.error(f"Error processing Gemini structured response: {e}")
        # Return fallback response if there's an error
        content = f"# Research Results\n\nThere was an error processing the research results for {query}.\n\n## Error\n\nUnable to process research results. Please try again later."
        return ResearchData(content=content, links=[])

async def process_manual_research(content: str) -> ResearchData:
    """
    Process user-provided research content.
    
    Args:
        content: The user-provided research content
        
    Returns:
        A ResearchData object containing the content and empty links list
    """
    # Process manually provided content into a ResearchData object
    return ResearchData(content=content, links=[]) 