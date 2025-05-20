import google.generativeai as genai
import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from config import RESEARCH_MODEL, RESEARCH_CONFIG, OFFLINE_MODE
import logging
from models import ResearchData

# Fixed offline response for research
OFFLINE_RESEARCH_RESPONSE = {
    "title": "Artificial Intelligence in Modern Business",
    "summary": "This presentation explores how AI is transforming business operations, improving efficiency, and creating new opportunities for innovation across multiple industries.",
    "sections": [
        {
            "title": "Introduction to AI in Business",
            "content": ["AI is revolutionizing how businesses operate", "Companies are using AI to automate tasks, gain insights, and create new products", "85% of executives believe AI will significantly change their business model"]
        },
        {
            "title": "Key AI Technologies",
            "content": ["Machine Learning algorithms for prediction and pattern recognition", "Natural Language Processing for communication and text analysis", "Computer Vision for image and video understanding", "Robotics and automation for physical tasks"]
        },
        {
            "title": "Business Applications",
            "content": ["Customer service: Chatbots and virtual assistants", "Marketing: Personalization and targeting", "Operations: Predictive maintenance and supply chain optimization", "HR: Candidate screening and employee engagement", "Finance: Fraud detection and algorithmic trading"]
        },
        {
            "title": "Implementation Challenges",
            "content": ["Data quality and availability issues", "Integration with legacy systems", "Skills gap and training requirements", "Ethical considerations and bias", "Regulatory compliance"]
        },
        {
            "title": "Success Stories",
            "content": ["Amazon: Recommendation engines and logistics optimization", "JPMorgan Chase: Contract analysis with AI", "Unilever: AI-driven hiring reducing time-to-hire by 90%", "Walmart: Inventory management and demand forecasting"]
        },
        {
            "title": "Future Trends",
            "content": ["AI democratization through no-code tools", "Increased focus on explainable AI", "Edge AI for real-time processing", "Human-AI collaboration models", "Specialized AI for industry-specific applications"]
        },
        {
            "title": "Getting Started",
            "content": ["Identify high-value use cases", "Start with small, measurable pilot projects", "Build cross-functional teams with business and technical expertise", "Focus on data strategy and governance", "Measure ROI and scale successful initiatives"]
        }
    ],
    "keywords": ["Artificial Intelligence", "Machine Learning", "Business Transformation", "Automation", "Digital Innovation"],
    "companies": ["Google", "Microsoft", "Amazon", "IBM", "Tesla"]
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

    # For AI mode in offline mode, return the fixed response
    if OFFLINE_MODE:
        print(f"OFFLINE MODE: Returning fixed research response for query: {query}")
        # Convert the fixed response to markdown content
        sections_md = ""
        for section in OFFLINE_RESEARCH_RESPONSE["sections"]:
            sections_md += f"## {section['title']}\n\n"
            for content_item in section['content']:
                sections_md += f"- {content_item}\n"
            sections_md += "\n"
        
        # Create title and overall content
        title = OFFLINE_RESEARCH_RESPONSE["title"]
        content = f"# {title}\n\n{OFFLINE_RESEARCH_RESPONSE['summary']}\n\n{sections_md}"
        
        # Return as ResearchData
        return ResearchData(content=content, links=[])

    # Rest of the original function for online mode
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
    
    user_content = f"Research the following presentation topic comprehensively: {query}"
    
    # Get response from Gemini - With proper format for the API
    response = model.generate_content([
        {"role": "user", "parts": [{"text": system_content}]},
        {"role": "model", "parts": [{"text": "I understand. I'll research the topic and provide comprehensive markdown content with sources in JSON format without code blocks."}]},
        {"role": "user", "parts": [{"text": user_content}]}
    ])
    
    # Process response
    try:
        # Try to parse as JSON
        data = json.loads(response.text)
        
        # Extract content and links
        content = data.get("content", "")
        links = data.get("links", [])
        
        # Return as ResearchData
        return ResearchData(content=content, links=links)
    
    except Exception as e:
        logging.error(f"Error processing Gemini response: {e}")
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