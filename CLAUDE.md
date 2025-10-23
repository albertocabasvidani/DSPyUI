# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DSPyUI is a web-based prompt optimizer using DSPy and OpenAI. It consists of two independent components:

- **Backend** (`/backend/`): FastAPI server that uses DSPy to optimize prompts via OpenAI API
- **Frontend** (`/docs/`): Vanilla JavaScript SPA served via GitHub Pages

The architecture is **serverless-friendly** with complete separation between frontend and backend. They communicate only via REST API with CORS enabled.

## Production Deployment Status

**DEPLOYED AND OPERATIONAL** ✓

- **Backend**: https://dspyui.onrender.com (Render.com)
- **Frontend**: https://albertocabasvidani.github.io/DSPyUI (GitHub Pages)
- **Status**: All systems operational, optimizer initialized successfully
- **DSPy Version**: 2.5+ (using new `dspy.LM()` API)
- **Python Version**: 3.11.9 (specified in `runtime.txt`)

### Render Configuration

- **Service ID**: `srv-d3sufkk9c44c73cdokb0`
- **Service Name**: DSPyUI
- **Auto-deploy**: Enabled (triggers on commit to main branch)
- **API Key**: Stored in `tmp.txt` (not committed to repo)

### Render API Operations

```bash
# Check service status
curl -s https://api.render.com/v1/services/srv-d3sufkk9c44c73cdokb0 \
  -H "Authorization: Bearer $RENDER_API_KEY" | jq '.service'

# List recent deploys
curl -s https://api.render.com/v1/services/srv-d3sufkk9c44c73cdokb0/deploys \
  -H "Authorization: Bearer $RENDER_API_KEY" | jq '.[] | .deploy | {status, commit: .commit.id[0:7], createdAt}'

# Trigger manual deploy
curl -X POST https://api.render.com/v1/services/srv-d3sufkk9c44c73cdokb0/deploys \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json"
```

### Known Requirements

- `runtime.txt` must be in **repository root**, not in `/backend`
- DSPy 2.5+ requires `dspy.LM('openai/model-name')` instead of deprecated `dspy.OpenAI()`
- Do not include `cors` package in requirements.txt (FastAPI includes CORS middleware natively)
- Render free tier: backend sleeps after 15min inactivity, first wake-up takes ~30s
- Auto-deploy is enabled: backend deploys automatically on push to main branch

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

2. **`prompt_optimizer.py`**: Core DSPy integration with advanced features
   - Initializes DSPy with OpenAI LM configuration
   - Custom `PromptOptimizationSignature` with typed input/output fields
   - **Dual optimization modes**:
     - Without examples: Uses `ChainOfThought` with custom signature
     - With examples: Uses `BootstrapFewShot` for few-shot learning (max 3-5 demos)
   - **Validation**: `dspy.Assert` and `dspy.Suggest` for output quality checks
   - **Quality metrics**: LM-based analysis with heuristic fallback
   - Falls back to template-based optimization if DSPy fails

3. **`models.py`**: Pydantic models for request/response validation

### Frontend Flow

1. **`index.html`**: Single-page interface with form and results sections
   - Wake-up banner for Render free tier sleep handling
   - Toast notifications for user feedback

2. **`app.js`**: Vanilla JS application logic
   - `CONFIG.API_URL`: Must be updated with actual Render backend URL before deployment
   - LocalStorage for session persistence (`STORAGE_KEYS.HISTORY`, `STORAGE_KEYS.LAST_REQUEST`)
   - **Automatic backend wake-up**: `checkBackendHealth()` on page load
     - Detects sleeping backend via health check timeout
     - Shows fullscreen banner with spinner and elapsed timer
     - Retries every 10s for up to 3 minutes (18 attempts)
     - Success/failure toast notifications

3. **`styles.css`**: CSS with CSS variables for theming
   - Wake-up banner overlay with centered content
   - Large spinner animation
   - Responsive design for mobile/desktop

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

The `PromptOptimizer` class uses DSPy's advanced optimization features:

### Core Components

- **Custom Signature**: `PromptOptimizationSignature` with typed fields:
  - Input: `purpose`, `original_prompt`, `examples_context` (optional)
  - Output: `optimized_prompt`, `improvements`

- **Dual Optimization Strategy**:
  - **Without examples** (`_optimize_without_examples`): Base `ChainOfThought` module
  - **With examples** (`_optimize_with_examples`): `BootstrapFewShot` optimizer
    - Converts user examples to DSPy `Example` format
    - Compiles optimizer with validation metrics
    - Limits to 3-5 demonstrations for efficiency

- **Quality Validation**:
  - `dspy.Assert`: Hard constraints (e.g., non-empty output)
  - `dspy.Suggest`: Soft suggestions (e.g., prompt should differ from original)
  - Custom scoring metric for optimization quality

- **Metrics Analysis**:
  - Primary: LM-based assessment (clarity, specificity, structure, completeness)
  - Fallback: Heuristic-based scoring when LM unavailable

- **Error Handling**: Multi-layer fallback (few-shot → base → template) ensures robustness

## Performance Characteristics

**Expected Response Times** (measured in production):

- **Health Check**: ~0.3s
- **Optimize without examples** (warm): ~30-35s
  - Optimization: ~0.5s
  - LM-based quality metrics: ~30s (essential for accurate assessment)
- **Optimize with examples** (few-shot): ~27-35s
  - BootstrapFewShot compilation and execution
- **Cold start** (after 15min sleep): ~2-3 minutes first request
- **Analyze**: ~6-7s

**Note on Quality Metrics**: The `analyze_prompt_quality()` method uses LM-based analysis via ChainOfThought to provide accurate quality scores (clarity, specificity, structure, completeness). This adds ~30s but is essential for meaningful assessment. Heuristic fallback exists but produces less reliable metrics.

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

The backend **sleeps after 15 minutes** of inactivity. First request after sleep takes ~30-90 seconds.

### Automatic Wake-up Feature

The frontend automatically handles backend sleep with zero user intervention:

1. **Detection**: `checkBackendHealth()` runs on page load with 5s timeout
2. **Wake-up process** (if backend sleeping):
   - Shows fullscreen banner: "Waking up backend..."
   - Displays live elapsed timer
   - Retries health check every 10s
   - Maximum 18 attempts (3 minutes total)
3. **Completion**:
   - Success: Hides banner, shows toast with total wake-up time
   - Failure: Shows error toast after 3 minutes

**User experience**: Users never need to manually access Render dashboard. The app automatically wakes the backend and provides visual feedback during the process.

This is expected behavior for the free tier. The wake-up feature ensures seamless UX.