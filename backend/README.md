# PowerIt Backend

## Overview

PowerIt is an AI-powered presentation generation system. The backend handles research, slide generation, image creation, and PowerPoint file assembly.

## Features

- Research presentation topics using AI
- Generate slide content
- Create images for slides
- Compile presentations with images
- Generate PowerPoint (PPTX) files
- Export to PDF
- Search for company logos

## API Documentation

The API includes comprehensive Swagger documentation available at:
```
http://localhost:8000/docs
```

Key improvements to the API documentation:
- Detailed schema definitions with descriptions for all fields
- Example requests and responses
- Clear organization using tags (presentations, images, logos)
- Documentation for all slide types and their available fields
- Enhanced endpoint descriptions

For detailed API documentation, see `API_README.md`.

The `routers` package now organizes presentation endpoints across multiple modules for readability. See `routers/presentation_steps.py`, `routers/presentation_modify.py`, and `routers/presentation_images.py`.

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

4. Set environment variables (see below)

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure your settings.

**Required API Keys:**
- `GEMINI_API_KEY` - Google Gemini API key for content generation
- `OPENAI_API_KEY` - OpenAI API key for image generation

**Common Configuration:**
- `POWERIT_OFFLINE` - Set to `1` to run without internet using recorded fixtures
- `POWERIT_ENV` - Environment setting (`production` or `test`)
- `DATABASE_FILE` - SQLite database filename (default: `presentations.db`)
- `STORAGE_DIR` - Custom storage directory for generated files

**AI Model Configuration:**
- `RESEARCH_MODEL` - Model for research tasks (default: `gemini-2.5-flash-preview-04-17`)
- `SLIDES_MODEL` - Model for slide generation (default: `gemini-2.5-flash-preview-04-17`)
- `MODIFY_MODEL` - Model for modifications (default: `gemini-2.5-flash-preview-04-17`)

**Generation Parameters:**
You can fine-tune AI generation by setting temperature, top_p, top_k, and max_output_tokens for each task type:
- Research: `RESEARCH_TEMPERATURE`, `RESEARCH_TOP_P`, `RESEARCH_TOP_K`, `RESEARCH_MAX_OUTPUT_TOKENS`
- Slides: `SLIDES_TEMPERATURE`, `SLIDES_TOP_P`, `SLIDES_TOP_K`, `SLIDES_MAX_OUTPUT_TOKENS`
- Modify: `MODIFY_TEMPERATURE`, `MODIFY_TOP_P`, `MODIFY_TOP_K`, `MODIFY_MAX_OUTPUT_TOKENS`

**Image Generation:**
- `OPENAI_IMAGE_MODEL` - OpenAI model for images (default: `gpt-image-1`)
- `OPENAI_IMAGE_QUALITY` - Image quality: `standard` or `hd`
- `OPENAI_IMAGE_SIZE` - Image dimensions (default: `1024x1024`)
- `OPENAI_IMAGE_FORMAT` - Output format (default: `png`)

See `.env.example` for a complete list with descriptions and defaults.

### Running the API

```bash
python run_api.py
```

The server will be available at http://localhost:8000.

To run completely offline, set `POWERIT_OFFLINE=1` before starting the server.

## Testing

Run the test suite with:

```bash
./run_tests.sh
```

## Project Structure

- `api.py` - Main FastAPI application
- `server.py` - MCP tools for AI integration
- `database.py` - Database models and connection
- `models.py` - Pydantic models for data
- `routers/` - API route modules
- `schemas/` - API request/response schemas
- `services/` - Business logic
- `tools/` - Utility functions

## Architecture

The application has been refactored into a modular structure:

```
backend/
├── api.py                    # Main FastAPI application entry point
├── database.py               # Database models and connection
├── models.py                 # Pydantic models for application data
├── config.py                 # Configuration settings
├── routers/                  # API route modules
│   ├── presentations.py      # Presentation-related endpoints
│   ├── images.py             # Image generation endpoints
│   ├── logos.py              # Logo fetching endpoints
│   ├── pptx.py               # PPTX and download endpoints
├── schemas/                  # API request/response schemas
│   ├── presentations.py      # Presentation schemas
│   ├── images.py             # Image schemas
├── services/                 # Business logic services
│   ├── presentation_service.py # Presentation processing logic
├── tools/                    # Utility modules
│   ├── logo_fetcher.py       # Logo fetching utilities
│   ├── ...                   # Other utility modules
```

## Running Tests

```bash
# Run all tests
python -m pytest

# Run specific tests
python -m pytest tests/test_api_structure.py
```

## Notes

The application uses:

- FastAPI for the web framework
- SQLAlchemy for database operations
- Google's Gemini and OpenAI for AI capabilities
- Python-PPTX for presentation generation 