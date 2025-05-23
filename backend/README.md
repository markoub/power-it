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

The following environment variables are required:

- `GEMINI_API_KEY` - Google Gemini API key
- `OPENAI_API_KEY` - OpenAI API key (for image generation)
- `POWERIT_OFFLINE` - Set to `1` to run without internet using recorded fixtures

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