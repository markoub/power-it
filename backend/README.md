# Presentation Assistant Backend

A FastAPI application with integrated AI tools for creating presentations using Gemini and OpenAI models. The system uses Pydantic for robust data validation and type safety.

## Features

- **Research Tool**: Researches a topic and returns comprehensive markdown content with sources using Gemini 2.5 Flash
- **Slides Generator**: Creates well-structured presentation slides based on research data using Gemini 2.0 Flash
- **Image Generator**: Creates high-quality images for slides using OpenAI DALL-E
- **PPTX Export**: Generates PowerPoint presentations with proper layouts and styling
- **Orchestrator**: Chains research, slides generation, image creation, and compilation together

## Project Structure

```
backend/
├── api.py               # FastAPI application with API endpoints
├── config.py            # Configuration and environment setup
├── database.py          # SQLite database with SQLAlchemy
├── models.py            # Pydantic models for data validation
├── orchestrator.py      # Coordinates tool chaining
├── run_api.py           # Entry point for running the API server
├── run_server.py        # Entry point for running the FastMCP server
├── server.py            # FastMCP server with registered tools
├── utils.py             # Utility functions for processing data
├── tests/               # Test directory
│   ├── fixtures/        # Recorded API responses for testing
│   ├── test_data/       # Test data files and resources
│   ├── conftest.py      # Pytest configuration 
│   ├── test_api.py      # API endpoint tests
│   ├── test_images.py   # Image generation tests
│   ├── test_slides.py   # Slide generation tests
│   ├── test_gemini_vcr.py # Gemini API recording/replay
│   ├── test_openai_vcr.py # OpenAI API recording/replay
│   └── many other test files for specific functionality
└── tools/               # Tool implementations
    ├── __init__.py      # Package initialization
    ├── research.py      # Research tool implementation
    ├── slides.py        # Slides generation tool implementation
    ├── images.py        # Image generation 
    ├── pptx_generator.py # PowerPoint file generation
    ├── slide_config.py  # Slide type configurations
    └── logo_fetcher.py  # Company logo search & download tool
```

## Setup

1. Ensure you have Python 3.10+ installed
2. Set up a virtual environment (already available in `venv/`)
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## Running the Application

Start the FastAPI server:

```bash
# Start the API server
./venv/bin/python run_api.py
```

Or run the FastMCP server:

```bash
# Start the FastMCP server directly
./venv/bin/python run_server.py

# Or start in dev mode
./venv/bin/mcp dev server.py
```

## Testing

The project includes comprehensive test automation with a Virtual Cassette Recorder (VCR) pattern for mocking API calls to Gemini and OpenAI. This allows tests to run quickly without making actual API calls.

### Default Testing Mode

By default, tests run in **replay mode**, using pre-recorded API responses stored as fixtures. This is fast, reliable, and avoids incurring costs from repeated API calls:

```bash
# Run tests in replay mode (default)
./run_tests.sh

# Run specific tests
./run_tests.sh tests/test_api.py
```

### Running Tests with Real API Calls

When you need to verify that tests work with actual APIs, you can run tests in **record mode**. This makes real API calls to Gemini and OpenAI, which may incur costs:

```bash
# Run tests with real API calls, recording new fixtures
GEMINI_VCR_MODE=record OPENAI_VCR_MODE=record ./run_tests.sh

# For specific test files
GEMINI_VCR_MODE=record ./run_tests.sh tests/test_slides.py
OPENAI_VCR_MODE=record ./run_tests.sh tests/test_images.py
```

If you need to run all tests with all types of API calls (comprehensive verification):

```bash
# Run all tests with all real API calls
GEMINI_VCR_MODE=record OPENAI_VCR_MODE=record PRESENTATION_VCR_MODE=record \
TOC_FONT_VCR_MODE=record TEMPLATE_PPTX_VCR_MODE=record IMAGE_API_VCR_MODE=record \
./run_tests.sh
```

For convenience, you can also use the provided script:

```bash
# Record all API calls for a specific test
./record_tests.sh tests/test_slides.py
```

### Running Tests with Skipping

Some tests may fail because they depend on external APIs or specific environments. To skip these tests, you can use the `-k` option:

```bash
# Skip tests containing specific keywords
./venv/bin/python -m pytest -k "not image" 

# Skip multiple categories
./venv/bin/python -m pytest -k "not image and not openai"
```

The default test setup already excludes certain problematic tests:

```bash
# This is what the run_tests.sh script uses by default
./venv/bin/python -m pytest tests/ -v -k "not image and not openai and not pptx_core and not test_orchestrator"
```

You can also mark tests to be skipped based on specific conditions:

```bash
# Skip slow tests
./venv/bin/python -m pytest -m "not slow"
```

### Known Test Issues

Some tests are currently skipped because they require external API calls or have complex setup requirements:

1. **Image tests** - These tests require OpenAI API access for image generation
2. **OpenAI tests** - Tests that rely on OpenAI APIs are skipped by default
3. **Orchestrator tests** - Some orchestration tests have complex mock requirements
4. **PPTX core tests** - Some PowerPoint generation tests are skipped due to mocking issues  

### Test Framework

- Tests are written using pytest with pytest-asyncio for async support
- The VCR pattern is implemented in `tests/test_gemini_vcr.py` and `tests/test_openai_vcr.py`
- Tests will automatically skip if required fixtures are not available
- See `tests/README.md` for more detailed testing information

## API Endpoints

The backend exposes several endpoints:

- **GET /presentations** - List all presentations
- **POST /presentations** - Create a new presentation
- **GET /presentations/{id}** - Get presentation details
- **POST /presentations/{id}/steps/{step_name}/run** - Run a presentation step (research, slides, images, pptx)
- **PUT /presentations/{id}/steps/{step_name}** - Update step results
- **POST /images** - Generate a single image from a prompt
- **GET /presentations/{id}/download-pptx** - Download generated PowerPoint

## Testing Patterns

### Test Types

1. **Unit Tests**: Testing individual functions/components in isolation
2. **API Tests**: Testing FastAPI endpoints with TestClient
3. **Integration Tests**: Testing tool chains with mocked external dependencies
4. **VCR Tests**: Tests that record and replay external API calls

### VCR Pattern Implementation

The project uses a custom VCR implementation for API mocking:

- `test_gemini_vcr.py` - Mocks Gemini API calls
- `test_openai_vcr.py` - Mocks OpenAI API calls

Environment variables control recording behavior:
- `GEMINI_VCR_MODE=record` - Records Gemini API responses
- `OPENAI_VCR_MODE=record` - Records OpenAI API responses
- `PRESENTATION_VCR_MODE=record` - Records full presentation generation

## Models and Data Types

### Pydantic Models

- `ResearchData`: Contains research content and source links
- `SlidePresentation`: A complete presentation with multiple slides
- `Slide`: Individual slide with type and content
- `FullPresentation`: Combines research data, slides, and metadata

### Database Models

- `Presentation`: A presentation project with name and topic
- `PresentationStepModel`: Results and status for each processing step 