import json
import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Union, List, Optional

from models import ResearchData, Link

def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from text that might contain code blocks or other formatting
    
    Args:
        text: Raw text that might contain JSON
        
    Returns:
        Extracted JSON string or None if not found
    """
    # Try to find JSON in a code block
    code_block_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1)
    
    # Try to find a JSON object pattern
    json_pattern = re.search(r'{.*}', text, re.DOTALL)
    if json_pattern:
        return json_pattern.group(0)
    
    # If no JSON is found, return the original text
    return text

def clean_vertex_urls(links: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Clean vertexsearch URLs from links if present
    
    Args:
        links: List of link dictionaries
        
    Returns:
        List of cleaned link dictionaries
    """
    for link in links:
        if "href" in link and isinstance(link["href"], str):
            if "vertexsearch.googleapis.com" in link["href"]:
                parsed_url = urlparse(link["href"])
                query_params = parse_qs(parsed_url.query)
                if "url" in query_params and query_params["url"]:
                    link["href"] = query_params["url"][0]
    return links

def process_gemini_response(response_text: str) -> ResearchData:
    """
    Process the raw text response from Gemini and convert to a Pydantic model
    
    Args:
        response_text: Raw text response from Gemini
        
    Returns:
        Processed ResearchData object
    """
    # Extract JSON from the response
    json_text = extract_json_from_text(response_text)
    
    try:
        # Try to parse the extracted text as JSON
        parsed_data = json.loads(json_text)
        
        # Check if we have a JSON structure wrapped in a content field
        if isinstance(parsed_data, dict) and "content" in parsed_data and isinstance(parsed_data["content"], str):
            try:
                # Try to parse the content field as JSON
                content_json = json.loads(parsed_data["content"])
                if isinstance(content_json, dict) and ("content" in content_json or "links" in content_json):
                    # We found JSON inside JSON - use the inner content
                    parsed_data = content_json
            except json.JSONDecodeError:
                # Content is not valid JSON, leave it as is
                pass
        
        # Clean up links if they exist
        if isinstance(parsed_data, dict) and "links" in parsed_data and isinstance(parsed_data["links"], list):
            parsed_data["links"] = clean_vertex_urls(parsed_data["links"])
        
        # Create a Pydantic model
        try:
            # Try to validate as a ResearchData object
            return ResearchData(**parsed_data)
        except Exception as e:
            # If validation fails, create a default object
            return ResearchData(
                content=json_text if isinstance(json_text, str) else response_text,
                links=[]
            )
    except json.JSONDecodeError:
        # If JSON parsing fails, create a default object
        return ResearchData(
            content=json_text if isinstance(json_text, str) else response_text,
            links=[]
        ) 