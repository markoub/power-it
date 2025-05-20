# Presentation Assistant

A full-stack application for creating AI-powered presentations using Gemini models. The system consists of a FastAPI backend wrapping MCP tools and a Next.js frontend.

## Project Structure

```
powerit/
├── backend/            # FastAPI backend & MCP tools
│   ├── tools/          # MCP presentation tools
│   ├── config.py       # Configuration and environment
│   ├── models.py       # Pydantic data models
│   ├── database.py     # SQLite database with SQLAlchemy
│   ├── api.py          # FastAPI application wrapper
│   ├── server.py       # FastMCP server
│   └── ...
└── frontend/           # Next.js frontend application
    ├── app/            # Next.js app router
    ├── components/     # React components
    ├── lib/            # Utilities and API client
    └── ...
```

## Features

- **Research**: Researches a topic and generates comprehensive markdown content with sources
- **Slides**: Creates structured presentation slides based on research results
- **Web Interface**: Modern UI for managing presentations and running tools
- **Background Processing**: Tasks run asynchronously with status tracking
- **Database Storage**: Persistent storage of presentations and results
- **Integrated API**: Frontend connects to backend via API for seamless operation
- **Static Export**: Frontend can be built as static HTML/JS/CSS for easy deployment

## Setup

### Initial environment preparation (online)

Run the following commands while your machine still has internet access to download all dependencies:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../frontend && npm install
cd ../testing && npm install && npx playwright install
cd ..
```

### Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. **Create the virtual environment and install dependencies** (run while the machine has internet access):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   deactivate
   ```

3. Create a `.env` file with your API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. For production builds, create a `.env.production` file with your backend URL:
   ```
   NEXT_PUBLIC_API_URL=http://your-backend-url:8000
   ```

## Running the Application

You can run both the backend and frontend together using:

```
./run.sh
```

Or run them separately:

### Backend

```
cd backend
./venv/bin/python run_api.py
```

The backend will be available at http://localhost:8000 with API documentation at http://localhost:8000/docs

### Frontend

```
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000

## Static Build and Deployment

The frontend can be built as a static site for deployment to any static hosting service:

```
cd frontend
npm run build
```

This will generate a static build in the `build` directory. You can then deploy this build to any static hosting service like:

- Netlify
- Vercel
- GitHub Pages
- Amazon S3
- Cloudflare Pages

Example deployment with a simple static server:
```
cd frontend/build
npx serve
```

This will serve the static build at http://localhost:3000.

## Integration

The frontend communicates with the backend through the API. The integration works as follows:

1. Frontend makes API calls to the backend using the API client in `frontend/lib/api.ts`
2. Backend processes requests and returns responses in JSON format
3. CORS is enabled on the backend to allow requests from the frontend

## Usage

1. Open http://localhost:3000 in your browser
2. Create a new presentation with a name and topic
3. Wait for the research step to complete
4. View and edit research results
5. Run the slides generation step
6. View the generated slides

## API Endpoints

- `GET /presentations` - List all presentations
- `POST /presentations` - Create a new presentation
- `GET /presentations/{id}` - Get presentation details
- `POST /presentations/{id}/steps/{step_name}/run` - Run a presentation step
- `PUT /presentations/{id}/steps/{step_name}` - Update step results

## Testing

The project uses pytest for testing with a VCR (Virtual Cassette Recorder) pattern to mock API calls to Gemini and OpenAI. This ensures tests are fast, reliable, and don't incur costs from repeated API calls.

### Testing Principles

1. **Use VCR for API calls**: All external API calls (Gemini, OpenAI) should use VCR fixtures
2. **Run tests in isolation**: Tests should not depend on each other
3. **Use virtual environment**: Always run tests in the provided virtual environment
4. **Clean up after tests**: Remove temporary files/resources created during tests
5. **Use valid slide types**: Tests should use valid slide types from the `SLIDE_TYPES` config

### Running Tests

#### Default Mode (Replay)

By default, tests run in **replay mode**, using pre-recorded fixtures instead of making real API calls:

```bash
cd backend
./run_tests.sh
```

To run specific test files or directories:

```bash
./run_tests.sh tests/test_images.py
./run_tests.sh tests/test_integration_research.py
```

With specific pytest options:

```bash
./run_tests.sh tests/test_images.py -v
./run_tests.sh -k "test_generate_image"
```

#### Running Tests with Real API Calls

When you need to verify tests with actual API calls or record new fixtures:

```bash
# Run all tests with real API calls
cd backend
GEMINI_VCR_MODE=record OPENAI_VCR_MODE=record ./run_tests.sh

# Or use the convenience script for a specific test
./record_tests.sh tests/test_images.py
```

For comprehensive verification with all types of API calls:

```bash
# Run all tests with all real API calls (complete verification)
cd backend
GEMINI_VCR_MODE=record OPENAI_VCR_MODE=record PRESENTATION_VCR_MODE=record \
TOC_FONT_VCR_MODE=record TEMPLATE_PPTX_VCR_MODE=record IMAGE_API_VCR_MODE=record \
./run_tests.sh
```

Requirements for using real API calls:
- Valid API keys in `.env` file:
  - `GEMINI_API_KEY` for Gemini API tests
  - `OPENAI_API_KEY` for OpenAI/image generation tests
- Internet connection
- Note that this will make actual API calls and may incur costs

### Adding New Tests

When adding new tests:

1. **Image Generation Tests**:
   - Always use the VCR fixtures (`mock_openai_responses`)
   - Use valid slide types from `SLIDE_TYPES` config
   - Check that result objects match the expected structure

2. **Gemini API Tests**:
   - Use the Gemini VCR fixtures (`mock_gemini_responses`)
   - Record fixtures for new test cases

3. **Slide Tests**:
   - Make sure test slides have valid types and fields
   - Use `SLIDE_TYPES` from `tools.slide_config` for reference

### Troubleshooting Tests

Common test issues:

1. **Missing fixtures**:
   - Run the test in record mode: `./record_tests.sh path/to/test.py`

2. **Model schema changes**:
   - Check if models in `models.py` have been updated
   - Update test objects to match the current schema

3. **VCR issues**:
   - Check the fixtures directory for corrupt/invalid fixtures
   - Delete problematic fixtures and re-record

4. **API errors in recording mode**:
   - Verify API keys are valid and have necessary permissions
   - Check API quotas and limits

### Test Configuration

- `GEMINI_VCR_MODE=record` - Records actual Gemini API calls
- `OPENAI_VCR_MODE=record` - Records actual OpenAI API calls
- Tests use the configuration from `backend/tests/test_config.py` instead of the real config
- Test fixtures are stored in `backend/tests/fixtures/`
- Dummy images for testing are in `backend/tests/test_data/` 