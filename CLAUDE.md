# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DSPyUI is a web-based prompt optimizer using DSPy and OpenAI. It consists of two independent components:

- **Backend** (`/backend/`): FastAPI server that uses DSPy to optimize prompts via OpenAI API
- **Frontend** (`/docs/`): Vanilla JavaScript SPA served via GitHub Pages

The architecture is **serverless-friendly** with complete separation between frontend and backend. They communicate only via REST API with CORS enabled.

## Development Commands

### Backend Development

```bash
# Setup environment
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env to add OPENAI_API_KEY

# Run development server (with auto-reload)
uvicorn app:app --reload --port 8000

# Run production server
uvicorn app:app --host 0.0.0.0 --port $PORT
```

### Frontend Development

```bash
# Serve frontend locally
cd docs
python -m http.server 8080

# Update backend URL in app.js (line 6) for local testing:
# API_URL: 'http://localhost:8000'
```

## Architecture

### Backend Flow

1. **`app.py`**: FastAPI application entry point
   - Initializes `PromptOptimizer` on startup
   - Handles CORS for GitHub Pages origin
   - Endpoints: `/` (health), `/optimize` (main), `/analyze` (metrics only)

2. **`prompt_optimizer.py`**: Core DSPy integration
   - Initializes DSPy with OpenAI LM configuration
   - Uses `ChainOfThought` signature: `"purpose, original_prompt -> optimized_prompt, improvements"`
   - Falls back to template-based optimization if DSPy fails
   - Implements heuristic quality metrics (clarity, specificity, structure, completeness)

3. **`models.py`**: Pydantic models for request/response validation

### Frontend Flow

1. **`index.html`**: Single-page interface with form and results sections
2. **`app.js`**: Vanilla JS application logic
   - `CONFIG.API_URL`: Must be updated with actual Render backend URL before deployment
   - LocalStorage for session persistence (`STORAGE_KEYS.HISTORY`, `STORAGE_KEYS.LAST_REQUEST`)
   - Health check on page load to warn about backend sleep state
3. **`styles.css`**: CSS with CSS variables for theming

### Key Integration Points

- **CORS Configuration**: Backend must whitelist frontend URL via `FRONTEND_URL` env var
- **API Contract**: Backend expects `POST /optimize` with `PromptOptimizationRequest` schema
- **Error Handling**: Frontend displays user-friendly messages for network errors and 30s backend wake-up delay

## Environment Variables

Required for backend (set in Render dashboard or `.env` file):

- `OPENAI_API_KEY`: OpenAI API key (required)
- `FRONTEND_URL`: GitHub Pages URL for CORS (e.g., `https://albertocabasvidani.github.io/DSPyUI`)
- `OPENAI_MODEL`: Model to use (default: `gpt-4`)
- `DSPY_TEMPERATURE`: Generation temperature (default: `0.7`)

## Deployment

### Backend (Render)

Deploy configuration is in `backend/render.yaml`. Render will automatically:
- Detect Python runtime
- Run `pip install -r requirements.txt`
- Start with `uvicorn app:app --host 0.0.0.0 --port $PORT`

**Critical**: Set `OPENAI_API_KEY` in Render dashboard (not in code/repo).

### Frontend (GitHub Pages)

1. Enable Pages in repo settings: Settings → Pages
2. Source: Deploy from branch `main`, folder `/docs`
3. Update `docs/app.js` line 6 with actual Render backend URL
4. Commit and push - Pages auto-deploys on push

## DSPy Integration Details

The `PromptOptimizer` class uses DSPy's declarative prompt optimization:

- **Signature**: Defines input/output schema for LM calls
- **ChainOfThought**: Module that adds reasoning steps automatically
- **Fallback**: If DSPy optimization fails (API errors, invalid responses), falls back to template-based optimization with predefined structure

The optimizer analyzes prompts on multiple dimensions (clarity, specificity, structure, completeness) using simple heuristics, not ML models.

## Frontend-Backend Communication

```javascript
// Frontend makes POST request
fetch(`${API_URL}/optimize`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    original_prompt: "...",
    purpose: "...",
    examples: [...],  // optional
    temperature: 0.7
  })
})

// Backend responds with
{
  "optimized_prompt": "...",
  "improvements": ["...", "..."],
  "explanation": "...",
  "metrics": {
    "clarity_score": 0.85,
    "specificity_score": 0.72,
    ...
  },
  "original_prompt": "..."
}
```

## Render Free Tier Behavior

The backend **sleeps after 15 minutes** of inactivity. First request after sleep takes ~30 seconds. The frontend:
- Shows warning toast on page load if backend health check fails
- Displays user-friendly message during long waits
- Automatically retries on network errors

This is expected behavior for the free tier and should not be "fixed".