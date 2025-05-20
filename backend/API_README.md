# PowerIt Presentation API Documentation

## Overview

The PowerIt Presentation API provides endpoints for creating, managing, and generating AI-powered presentations. This documentation provides a guide to help frontend developers integrate with the API effectively.

## API Documentation

The API includes comprehensive Swagger documentation that you can access at:
```
http://localhost:8000/docs
```

The Swagger UI provides interactive documentation where you can:
- View all available endpoints organized by tags
- See detailed request and response schemas with examples
- Try out API calls directly from the browser

## Key Features

The API supports the following main features:
- Creating presentations with AI-generated research
- Creating presentations with manual research
- Generating slide content from research
- Generating images for slides
- Compiling presentations with images
- Generating PowerPoint (PPTX) files
- Exporting presentations to PDF
- Searching for company logos

## Authentication

Currently, the API does not require authentication for development purposes.

## Presentation Workflow

A typical workflow for creating a presentation involves:

1. **Create a presentation** (`POST /presentations`)
   - Starts the research step automatically
   - Creates placeholder steps for all subsequent processes

2. **Wait for research to complete** or provide manual research
   - Monitor the research step status via `GET /presentations/{id}`
   - Or update with manual research via `PUT /presentations/{id}/steps/manual_research`

3. **Generate slides** (`POST /presentations/{id}/steps/slides/run`)
   - Creates slide content based on the research

4. **Generate images** (`POST /presentations/{id}/steps/images/run`)
   - Creates images for slides that require them

5. **Compile presentation** (`POST /presentations/{id}/steps/compiled/run`)
   - Merges slides and images into a single compiled format

6. **Generate PPTX** (`POST /presentations/{id}/steps/pptx/run`)
   - Creates a downloadable PowerPoint file

## Understanding Slide Types

The API provides a dedicated endpoint to retrieve information about all available slide types:
```
GET /presentations/slide-types
```

This endpoint returns detailed information about each slide type including:
- The type identifier
- Description of what the slide type is used for
- All available fields for that slide type with their descriptions

Use this information to understand how to structure slide content or interpret the slide data returned from the API.

## Examples

### Creating a Presentation

```json
POST /presentations

{
  "name": "Introduction to AI",
  "topic": "Artificial Intelligence",
  "research_type": "research",
  "author": "John Doe"
}
```

### Getting a Presentation

```
GET /presentations/1
```

Response includes all steps and their statuses:

```json
{
  "id": 1,
  "name": "Introduction to AI",
  "topic": "Artificial Intelligence",
  "author": "John Doe",
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:30:00",
  "steps": [
    {
      "id": 1,
      "step": "research",
      "status": "completed",
      "result": {
        "content": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines...",
        "links": [
          {"href": "https://example.com/ai-basics", "title": "AI Basics"}
        ]
      },
      "error_message": null,
      "created_at": "2023-01-01T12:00:00",
      "updated_at": "2023-01-01T12:30:00"
    },
    {
      "id": 2,
      "step": "slides",
      "status": "pending",
      "result": null,
      "error_message": null,
      "created_at": "2023-01-01T12:00:00",
      "updated_at": "2023-01-01T12:00:00"
    }
    // other steps...
  ]
}
```

## Data Models

### Presentations

Presentations contain metadata and multiple steps:
- `research` - Background information on the topic
- `slides` - Generated slide content
- `images` - Generated images for slides
- `compiled` - Slides with integrated images
- `pptx` - PowerPoint file generation

### Slides

Each slide has a `type` and `fields` object with content specific to that slide type.

Example slide types:
- `welcome` - Title slide
- `tableofcontents` - Table of contents
- `section` - Section divider
- `content` - Text content slide
- `contentimage` - Content with image
- `conclusion` - Summary slide

See the `/presentations/slide-types` endpoint for complete details on all slide types and their fields.

## Error Handling

The API uses standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (check your input data)
- `404` - Not Found
- `500` - Server Error

Error responses include a detail message explaining the issue:

```json
{
  "detail": "Presentation not found"
}
```

## Development Notes

For local development, the API server can be started using:

```bash
cd backend
python run_api.py
```

The server will be available at http://localhost:8000. 