from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class PromptOptimizationRequest(BaseModel):
    """Request model for prompt optimization"""
    original_prompt: str = Field(..., description="The original prompt to optimize")
    purpose: str = Field(..., description="The purpose or goal of this prompt")
    examples: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Optional input/output examples"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for generation"
    )

class PromptOptimizationResponse(BaseModel):
    """Response model for prompt optimization"""
    optimized_prompt: str = Field(..., description="The optimized version of the prompt")
    improvements: List[str] = Field(..., description="List of improvements made")
    explanation: str = Field(..., description="Explanation of the optimization process")
    metrics: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optimization metrics if available"
    )
    original_prompt: str = Field(..., description="Original prompt for reference")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")