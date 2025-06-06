import google.generativeai as genai
import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from config import RESEARCH_MODEL, RESEARCH_CONFIG, OFFLINE_MODE
import logging
from models import ResearchData
from utils.gemini import process_gemini_response
from offline_responses.research import get_offline_research
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

# Schema for clarification detection
CLARIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "needs_clarification": {
            "type": "boolean",
            "description": "Whether the topic needs clarification"
        },
        "initial_message": {
            "type": "string",
            "description": "The initial conversational message to ask the user for clarification"
        }
    },
    "required": ["needs_clarification", "initial_message"]
}

async def check_clarifications(query: str) -> Optional[Dict[str, Any]]:
    """
    Check if a research topic needs clarification.
    
    Args:
        query: Research topic to check
        
    Returns:
        Dictionary with clarification questions if needed, None otherwise
    """
    if OFFLINE_MODE:
        # In offline mode, simulate clarification for ambiguous topics to match online behavior
        ambiguous_terms = {
            "ADK": "I noticed you mentioned 'ADK' in your topic. Could you help me understand which ADK you're referring to? For example, are you interested in Android Development Kit, Agent Development Kit, or something else?",
            "SDK": "You mentioned SDK in your topic. Which SDK are you interested in learning about? For instance, are you looking for mobile SDKs (iOS/Android), cloud service SDKs (AWS/Azure), or a specific programming language SDK?",
            "API": "I see you're interested in APIs. To help me research better, could you tell me more about what specific aspect of APIs you'd like to explore? Are you looking for REST APIs, GraphQL, a specific service's API, or API design in general?",
            "ML": "I notice 'ML' in your topic. Are you referring to Machine Learning, or perhaps something else? And if it's Machine Learning, what specific aspect interests you?",
            "AI": "Great topic! When you say 'AI', are you interested in a specific area like generative AI, computer vision, natural language processing, or AI in a particular industry?",
            "A2A": "I see 'A2A' in your topic. Could you clarify what this refers to? It could mean Application-to-Application integration, Account-to-Account transfers, or something else entirely."
        }
        
        # Check if query contains ambiguous terms
        for term, message in ambiguous_terms.items():
            if term in query.upper():
                return {
                    "needs_clarification": True,
                    "initial_message": message
                }
        return None
    
    # Configure model for clarification detection
    clarification_config = RESEARCH_CONFIG.copy()
    clarification_config["response_schema"] = CLARIFICATION_SCHEMA
    
    model = genai.GenerativeModel(
        model_name=RESEARCH_MODEL,
        generation_config=clarification_config
    )
    
    # Load clarification prompt
    prompt_template = await get_prompt("research_clarification")
    prompt = prompt_template.format(query=query)
    
    try:
        response = model.generate_content(prompt)
        parsed_data = json.loads(response.text)
        
        if parsed_data.get("needs_clarification", False) and parsed_data.get("initial_message"):
            return parsed_data
        return None
    except Exception as e:
        logging.error(f"Error checking clarifications: {e}")
        return None

async def research_topic(query: str, mode: str = "ai", clarified_query: Optional[str] = None) -> ResearchData:
    """
    Research a topic for a presentation.
    
    Args:
        query: Research topic or presentation title
        mode: Research mode ('ai' or 'manual')
        clarified_query: Optional clarified version of the query after disambiguation
        
    Returns:
        ResearchData object containing research results
        
    Raises:
        ValueError: If query is empty, None, or not a string
    """
    # Input validation
    if not query or not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")
    
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
    prompt_template = await get_prompt("research")
    # Use clarified query if provided, otherwise use original query
    research_query = clarified_query if clarified_query else query
    prompt = prompt_template.format(query=research_query)
    
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
        
    Raises:
        ValueError: If content is empty, None, or not a string
    """
    # Input validation
    if not content or not isinstance(content, str) or not content.strip():
        raise ValueError("Content must be a non-empty string")
    
    # Process manually provided content into a ResearchData object
    return ResearchData(content=content, links=[]) 