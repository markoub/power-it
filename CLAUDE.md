# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PowerIt is a full-stack AI-powered presentation creation system that generates professional presentations through research, slide generation, and PowerPoint export.

**Architecture:**
- **Backend**: FastAPI + FastMCP server providing AI tools and API endpoints
- **Frontend**: Next.js 15 with React 19, TypeScript, and Tailwind CSS
- **Database**: SQLite with SQLAlchemy ORM
- **AI Integration**: Google Gemini for content, OpenAI for images
- **Testing**: pytest (backend) + Playwright (E2E) with VCR fixtures for API mocking

## Development Commands

### Running the Application
```bash
# Full application (recommended)
./run.sh                    # or: make run

# Backend only
cd backend && ./venv/bin/python run_api.py

# Frontend only  
cd frontend && npm run dev

# Offline mode (no external API calls)
export POWERIT_OFFLINE=1 && ./run.sh
```

### Testing Commands

**Backend Tests:**
```bash
make test-backend              # Run all (offline by default)
make test-backend-online       # With real API calls
make test-backend-offline      # Using VCR fixtures only
make test-backend-unit         # Unit tests only
make test-backend-integration  # Integration tests only

# Run specific test
cd backend && ./run_tests.sh tests/test_images.py -v

# Record new VCR fixtures
cd backend && ./record_tests.sh tests/test_images.py
```

**E2E Tests:**
```bash
make test-e2e                     # Run all E2E tests
make test-e2e-headed              # With visible browser
make test-e2e-debug               # Debug mode
make test-e2e-specific test=name  # Specific test
make test-e2e-list                # List available tests
```

**All Tests:**
```bash
make test-all           # Backend + E2E
make test-all-online    # With network access
make test-all-offline   # Without network
```

### Linting and Type Checking
```bash
# Backend (Python)
cd backend
./venv/bin/python -m ruff check .
./venv/bin/python -m mypy .

# Frontend (TypeScript/Next.js)
cd frontend
npm run lint
npm run type-check
```

## Architecture Details

### Backend Structure
- **`/routers`**: API endpoints organized by feature (presentations, images, logos, pptx)
- **`/tools`**: Core MCP tools for AI operations (research, slides, images)
- **`/tools/wizard`**: Context-aware AI assistants for different presentation steps
- **`/services`**: Business logic layer
- **`/offline_responses`**: Cached responses for offline mode
- **Key APIs**:
  - `POST /presentations` - Create new presentation
  - `GET /presentations/{id}/steps/{step}/run` - Execute presentation step
  - `PUT /presentations/{id}/steps/{step}` - Update step results

### Frontend Structure
- **`/app`**: Next.js App Router pages
- **`/components/steps`**: Step-specific components (research, slides, etc.)
- **`/components/slides`**: Slide type renderers
- **`/components/wizard`**: AI assistant interface
- **`/lib/api.ts`**: Backend API client

### Presentation Workflow
1. **Research**: Generate comprehensive content about the topic
2. **Slides**: Structure content into presentation slides
3. **Illustrations**: Generate images for slides
4. **PPTX Export**: Create downloadable PowerPoint file

### Slide Types
Valid slide types defined in `backend/tools/slide_config.py`:
- `welcome`, `table_of_contents`, `section`
- `content`, `content_with_logos`, `content_image`
- `image_full`, `three_images`

## Key Configuration

### Environment Variables

**Required API Keys:**
```bash
# Backend (.env)
GEMINI_API_KEY=your_key_here      # Google Gemini API for content generation
OPENAI_API_KEY=your_key_here      # OpenAI API for image generation
```

**Operational Modes:**
```bash
POWERIT_OFFLINE=1                 # Enable offline mode (uses cached responses)
POWERIT_ENV=production            # Environment setting (production/test)
```

**Model Configuration:**
```bash
# AI models for different tasks (defaults to gemini-2.5-flash-preview-04-17)
RESEARCH_MODEL=gemini-2.5-flash-preview-04-17
SLIDES_MODEL=gemini-2.5-flash-preview-04-17
MODIFY_MODEL=gemini-2.5-flash-preview-04-17
```

**Generation Parameters:**
```bash
# Research generation
RESEARCH_TEMPERATURE=0.2          # Controls randomness (0.0-1.0)
RESEARCH_TOP_P=0.95              # Nucleus sampling threshold
RESEARCH_TOP_K=40                # Top-k sampling
RESEARCH_MAX_OUTPUT_TOKENS=108192

# Slides generation  
SLIDES_TEMPERATURE=0.3
SLIDES_TOP_P=0.95
SLIDES_TOP_K=40
SLIDES_MAX_OUTPUT_TOKENS=104096

# Modify generation
MODIFY_TEMPERATURE=0.25
MODIFY_TOP_P=0.92
MODIFY_TOP_K=50
MODIFY_MAX_OUTPUT_TOKENS=108192
```

**OpenAI Image Generation:**
```bash
OPENAI_IMAGE_MODEL=gpt-image-1    # Model to use
OPENAI_IMAGE_QUALITY=standard     # Quality: standard or hd
OPENAI_IMAGE_SIZE=1024x1024       # Image dimensions
OPENAI_IMAGE_FORMAT=png           # Output format
```

**Storage & Database:**
```bash
STORAGE_DIR=/custom/storage/path  # Custom storage directory
DATABASE_FILE=presentations.db    # SQLite database file
TEST_DATABASE_FILE=presentations_test.db
```

**Frontend Configuration:**
```bash
# Frontend (.env.production)
NEXT_PUBLIC_API_URL=http://backend-url:8000
```

See `backend/.env.example` for a complete list of available environment variables.

### VCR Test Modes
- `GEMINI_VCR_MODE=record` - Record Gemini API calls
- `OPENAI_VCR_MODE=record` - Record OpenAI API calls
- Default: `replay` mode using existing fixtures

## Important Notes

1. **Offline Mode**: Set `POWERIT_OFFLINE=1` to use cached responses instead of real API calls
2. **Test Fixtures**: Located in `backend/tests/fixtures/` - delete and re-record if APIs change
3. **CORS**: Backend allows frontend requests - ensure proper origins in production
4. **Database**: SQLite file `presentations.db` auto-created on first run
5. **API Docs**: Available at `http://localhost:8000/docs` when backend is running
6. **Image Storage**: Generated images stored in `storage/presentations/{id}/images/`

## Development Guidelines

- **Server Management**: never run new server, backend or frontend, without checking if there is one already available. If needed, first kill all active ones, before running new

## Recent Fixes and Known Issues

### Wizard Research Apply Fix (May 31, 2025)
**Issue**: The wizard's research modifications weren't being applied when users clicked the "Apply" button.

**Root Cause**: In `frontend/app/edit/[id]/page.tsx`, the `applyWizardChanges` function was checking for `changes.research` inside the `changes.presentation` block, but the wizard was sending `changes.research` at the top level.

**Fix**: Moved the `changes.research` check to be a separate condition that handles research updates independently:
```typescript
// Before (incorrect):
} else if (changes.presentation) {
  // ... presentation changes ...
  if (changes.research) {
    // This was never reached!
  }
}

// After (correct):
} else if (changes.research) {
  // Apply research changes directly
  const updatedSteps = presentation.steps?.map(s =>
    s.step === "research" || s.step === "manual_research"
      ? { ...s, result: changes.research, status: "completed" as const }
      : s
  ) || [];
  setPresentation({ ...presentation, steps: updatedSteps });
  await api.saveModifiedResearch(String(presentation.id), changes.research);
}
```

**Testing**: Verify with `make test-e2e-specific test=test-research-apply-fix`

## Custom Commands

### /gitcommit - Review Changes and Create Git Commit

When you want to review changes and create a git commit, use the `/gitcommit` command. This command will:

1. Run `git status` to see all changed files
2. Run `git diff` to see detailed changes in each file  
3. Analyze the changes to understand what was modified
4. Suggest an appropriate commit message following conventional commit format
5. Create the commit with proper formatting

**Usage**: Simply type `/gitcommit` and I will:
- Show you all modified, added, and deleted files
- Review the actual changes in detail
- Generate a commit message that accurately describes the changes
- Include Co-Authored-By attribution

**Example commit format**:
```
feat(wizard): fix research apply functionality in frontend

- Fixed applyWizardChanges to handle research updates at top level
- Added separate condition for research changes with proper toast
- Updated documentation across multiple files
- Added E2E test to verify apply functionality

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

This command helps maintain consistent commit messages and ensures all changes are properly documented in version control.

### /update-docs - Update Documentation from Environment Configuration

When you want to update documentation to reflect current environment variable usage, use the `/update-docs` command. This command will:

1. Analyze the current `.env` file to identify all environment variables
2. Search the codebase to determine which variables are actually used
3. Check `config.py` to see how environment variables are loaded
4. Update relevant documentation files to reflect the current configuration
5. Create or update `.env.example` with all available variables

**Usage**: Simply type `/update-docs` and I will:
- Scan for environment variable usage across the backend
- Identify unused variables in `.env`
- Update `CLAUDE.md`, `backend/README.md`, and main `README.md`
- Generate a comprehensive `.env.example` file
- Report which documentation files were updated

**What gets updated**:
- Environment variable sections in all documentation
- Configuration examples and defaults
- Descriptions of each variable's purpose
- Organization by logical categories (API Keys, Models, Parameters, etc.)

This command ensures your documentation stays in sync with your actual configuration usage.