# Presentation Assistant Backend

A FastMCP server providing tools for creating presentations using Gemini AI models. The system uses Pydantic for robust data validation and type safety.

## Features

- **Research Tool**: Researches a topic and returns comprehensive markdown content with sources using Gemini 2.5 Flash
- **Slides Generator**: Creates well-structured presentation slides based on research data using Gemini 2.0 Flash
- **Orchestrator**: Chains research and slides generation together for full presentation creation

## Project Structure

```
backend/
├── config.py            # Configuration and environment setup
├── models.py            # Pydantic models for data validation
├── orchestrator.py      # Coordinates tool chaining
├── run_server.py        # Entry point for running the server
├── server.py            # Main FastMCP server with registered tools
├── test_presentation.py # Basic unit tests for tools
├── test_tools.py        # Integration tests for tools
├── utils.py             # Utility functions for processing data
└── tools/               # Tool implementations
    ├── __init__.py      # Package initialization
    ├── research.py      # Research tool implementation
    └── slides.py        # Slides generation tool implementation
```

## Setup

1. Ensure you have Python 3.10+ installed
2. Set up a virtual environment (already available in `venv/`)
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with your `GEMINI_API_KEY`

## Running the Server

```bash
# Start the server directly
./venv/bin/python run_server.py

# Or start the server with MCP dev mode
./venv/bin/mcp dev server.py
```

## Testing

Test the tools directly without needing to run the server:

```bash
# Run the test tool script
./venv/bin/python test_tools.py
```

Run basic unit tests with:

```bash
./venv/bin/python -m unittest test_presentation.py
```

## Models and Tools

### Pydantic Models

The system uses Pydantic models for data validation and serialization:

- `ResearchData`: Contains research content and source links
- `SlideContent`: Represents a single slide with title, content, and styling
- `SlidePresentation`: A complete presentation with multiple slides
- `FullPresentation`: Combines research data, slides, and metadata

### Available Tools

#### ping()
Simple health check to verify the server is running.

#### research_topic_tool(topic: str)
Researches a presentation topic and returns detailed markdown content with sources.

- **Parameters:**
  - `topic`: The presentation topic to research
  
- **Returns:**
  - Dictionary with:
    - `content`: Markdown content for the presentation
    - `links`: Array of source links with href and title

#### generate_slides_tool(research_data: Dict, target_slides: int = 10)
Generates presentation slides based on research data.

- **Parameters:**
  - `research_data`: JSON data returned from research_topic tool
  - `target_slides`: Approximate number of slides to generate (default: 10)
  
- **Returns:**
  - Dictionary with:
    - `title`: Overall presentation title
    - `slides`: Array of slide objects

#### create_full_presentation(topic: str, target_slides: int = 10)
Creates a complete presentation by chaining research and slide generation.

- **Parameters:**
  - `topic`: The presentation topic to research
  - `target_slides`: Approximate number of slides to generate (default: 10)
  
- **Returns:**
  - Dictionary with:
    - `research`: Research data
    - `slides`: Slide proposals
    - `meta`: Presentation metadata

## AI Models Used

- **Research**: `gemini-2.5-flash-preview-04-17` - Optimized for high-quality content generation and deep research
- **Slides Generation**: `gemini-2.0-flash` - Efficient for structured content creation

## Dependencies

- `fastmcp`: For creating the MCP server tools
- `python-dotenv`: For loading environment variables
- `google-generativeai`: For interfacing with Gemini API
- `pydantic`: For data validation and serialization 