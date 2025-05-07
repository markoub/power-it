import google.generativeai as genai
from typing import Dict, Any

# Use absolute imports
from config import RESEARCH_MODEL, RESEARCH_CONFIG
from utils import process_gemini_response
from models import ResearchData

async def research_topic(topic: str) -> ResearchData:
    """
    Research a topic for a presentation and return detailed markdown content with sources.
    
    Args:
        topic: The presentation topic to research
        
    Returns:
        A ResearchData object containing markdown content and a list of source links
    """
    # Configure Gemini model
    model = genai.GenerativeModel(
        model_name=RESEARCH_MODEL,
        generation_config=RESEARCH_CONFIG
    )
    
    # Create system prompt and user prompt content
    system_content = """You are a professional researcher creating detailed content for presentations.
    Research the given topic thoroughly and create comprehensive markdown content.
    Make sure to include:
    1. Introduction to the topic
    2. Key facts, theories, or concepts
    3. Historical background if relevant
    4. Current state or applications
    5. Future directions or trends
    6. Organize with proper markdown headings, lists, and emphasis
    
    Format your response as a JSON object with these fields (NO CODE BLOCKS):
    - "content": Comprehensive markdown content for the presentation
    - "links": Array of objects with "href" and "title" fields for source references
    
    DO NOT wrap your response in ```json or any other markdown formatting.
    Just return a plain JSON object directly. Example:
    {"content": "# My Title\\n## Section 1\\n...", "links": [{"href": "https://example.com", "title": "Example"}]}
    
    For any source links, make sure to provide actual destination URLs, not redirect or tracking URLs.
    """
    
    user_content = f"Research the following presentation topic comprehensively: {topic}"
    
    # Get response from Gemini - With proper format for the API
    response = model.generate_content([
        {"role": "user", "parts": [{"text": system_content}]},
        {"role": "model", "parts": [{"text": "I understand. I'll research the topic and provide comprehensive markdown content with sources in JSON format without code blocks."}]},
        {"role": "user", "parts": [{"text": user_content}]}
    ])
    
    # Process response
    return process_gemini_response(response.text)

async def process_manual_research(content: str) -> ResearchData:
    """
    Process user-provided research content.
    
    Args:
        content: The user-provided research content
        
    Returns:
        A ResearchData object containing the content and empty links list
    """
    # Create a ResearchData object from the user-provided content
    return ResearchData(
        content=content,
        links=[]  # No links provided in manual research
    ) 