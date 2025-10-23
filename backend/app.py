from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from models import PromptOptimizationRequest, PromptOptimizationResponse, ErrorResponse
from prompt_optimizer import PromptOptimizer
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DSPy Prompt Optimizer",
    description="Optimize your prompts using DSPy and OpenAI",
    version="1.0.0"
)

# Configure CORS for GitHub Pages
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
    os.getenv("FRONTEND_URL", "https://yourusername.github.io"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize prompt optimizer
try:
    optimizer = PromptOptimizer()
    logger.info("Prompt optimizer initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize prompt optimizer: {e}")
    optimizer = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DSPy Prompt Optimizer",
        "optimizer_ready": optimizer is not None
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy" if optimizer else "degraded",
        "optimizer_initialized": optimizer is not None,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.post("/optimize", response_model=PromptOptimizationResponse)
async def optimize_prompt(request: PromptOptimizationRequest):
    """
    Optimize a prompt using DSPy

    Args:
        request: PromptOptimizationRequest containing the original prompt and purpose

    Returns:
        PromptOptimizationResponse with optimized prompt and explanations
    """

    if not optimizer:
        raise HTTPException(
            status_code=503,
            detail="Optimizer not initialized. Please check API key configuration."
        )

    try:
        # Log the request
        logger.info(f"Optimizing prompt for purpose: {request.purpose[:50]}...")

        # Perform optimization
        optimized_prompt, improvements, explanation = optimizer.optimize_prompt(
            original_prompt=request.original_prompt,
            purpose=request.purpose,
            examples=request.examples
        )

        # Analyze quality metrics
        metrics = optimizer.analyze_prompt_quality(optimized_prompt)

        # Create response
        response = PromptOptimizationResponse(
            optimized_prompt=optimized_prompt,
            improvements=improvements,
            explanation=explanation,
            metrics=metrics,
            original_prompt=request.original_prompt
        )

        logger.info("Prompt optimization completed successfully")
        return response

    except Exception as e:
        logger.error(f"Error optimizing prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing prompt: {str(e)}"
        )

@app.post("/analyze")
async def analyze_prompt(request: dict):
    """
    Analyze a prompt without optimizing it

    Args:
        request: Dictionary with 'prompt' field

    Returns:
        Quality metrics for the prompt
    """

    if not optimizer:
        raise HTTPException(
            status_code=503,
            detail="Optimizer not initialized"
        )

    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise ValueError("No prompt provided")

        metrics = optimizer.analyze_prompt_quality(prompt)

        return {
            "prompt": prompt,
            "metrics": metrics,
            "overall_score": round(sum(metrics.values()) / len(metrics), 2)
        }

    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing prompt: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)