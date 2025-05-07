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
    ├── src/            # Frontend source code
    │   ├── app/        # Next.js app router
    │   ├── components/ # React components
    │   └── lib/        # Utilities and API client
    └── ...
```

## Features

- **Research**: Researches a topic and generates comprehensive markdown content with sources
- **Slides**: Creates structured presentation slides based on research results
- **Web Interface**: Modern UI for managing presentations and running tools
- **Background Processing**: Tasks run asynchronously with status tracking
- **Database Storage**: Persistent storage of presentations and results

## Setup

### Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies in the virtual environment:
   ```
   ./venv/bin/pip install -r requirements.txt
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

### Frontend

```
cd frontend
npm run dev
```

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