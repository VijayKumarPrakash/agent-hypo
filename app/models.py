"""Pydantic models for A2A API request/response schemas."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class AnalysisMode(str, Enum):
    """Analysis mode options."""
    AUTO = "auto"
    LLM = "llm"
    TRADITIONAL = "traditional"


class RunRequest(BaseModel):
    """Request model for /run endpoint.

    Accepts URLs to context and data files for RCT analysis.
    """
    context_url: HttpUrl = Field(
        ...,
        description="URL to context file (experiment description). Supports .txt, .md, etc."
    )
    data_url: HttpUrl = Field(
        ...,
        description="URL to data file. Supports .csv, .json, .parquet, .xlsx, etc."
    )
    mode: AnalysisMode = Field(
        default=AnalysisMode.AUTO,
        description="Analysis mode: 'auto' (default), 'llm', or 'traditional'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "context_url": "https://example.com/experiment_context.txt",
                "data_url": "https://example.com/experiment_data.csv",
                "mode": "auto"
            }
        }


class AnalysisSummary(BaseModel):
    """Summary statistics from the analysis."""
    sample_size: int = Field(..., description="Total number of samples in the dataset")
    treatment_effect: Optional[float] = Field(None, description="Average Treatment Effect (ATE)")
    p_value: Optional[float] = Field(None, description="Statistical p-value")
    statistically_significant: Optional[bool] = Field(
        None,
        description="Whether results are statistically significant (p < 0.05)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sample_size": 1000,
                "treatment_effect": 0.1234,
                "p_value": 0.0023,
                "statistically_significant": True
            }
        }


class OutputUrls(BaseModel):
    """URLs to generated output files in cloud storage."""
    report_url: str = Field(..., description="URL to markdown analysis report")
    results_url: str = Field(..., description="URL to JSON results file")
    analysis_code_url: str = Field(..., description="URL to generated Python analysis code")
    data_copy_url: str = Field(..., description="URL to copy of input data file")
    context_copy_url: Optional[str] = Field(None, description="URL to copy of context file")

    class Config:
        json_schema_extra = {
            "example": {
                "report_url": "https://bucket.s3.amazonaws.com/runs/abc-123/report.md",
                "results_url": "https://bucket.s3.amazonaws.com/runs/abc-123/results.json",
                "analysis_code_url": "https://bucket.s3.amazonaws.com/runs/abc-123/analysis.py",
                "data_copy_url": "https://bucket.s3.amazonaws.com/runs/abc-123/data.csv",
                "context_copy_url": "https://bucket.s3.amazonaws.com/runs/abc-123/context.txt"
            }
        }


class RunResponse(BaseModel):
    """Response model for successful /run endpoint execution."""
    status: str = Field(default="success", description="Execution status")
    run_id: str = Field(..., description="Unique identifier for this analysis run")
    analysis_type: Optional[str] = Field(None, description="Type of analysis performed")
    experiment_type: Optional[str] = Field(None, description="Type of experiment detected")
    mode_used: str = Field(..., description="Analysis mode used: 'llm' or 'traditional'")
    analysis_summary: AnalysisSummary = Field(..., description="Summary statistics")
    outputs: OutputUrls = Field(..., description="URLs to generated output files")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "run_id": "abc-123-def-456",
                "analysis_type": "RCT",
                "experiment_type": "parallel",
                "mode_used": "llm",
                "analysis_summary": {
                    "sample_size": 1000,
                    "treatment_effect": 0.1234,
                    "p_value": 0.0023,
                    "statistically_significant": True
                },
                "outputs": {
                    "report_url": "https://bucket.s3.amazonaws.com/runs/abc-123/report.md",
                    "results_url": "https://bucket.s3.amazonaws.com/runs/abc-123/results.json",
                    "analysis_code_url": "https://bucket.s3.amazonaws.com/runs/abc-123/analysis.py",
                    "data_copy_url": "https://bucket.s3.amazonaws.com/runs/abc-123/data.csv"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error conditions."""
    status: str = Field(default="error", description="Error status")
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "error": "FileDownloadError",
                "message": "Failed to download data file from provided URL",
                "details": {
                    "url": "https://example.com/data.csv",
                    "reason": "404 Not Found"
                }
            }
        }


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(..., description="API version")
    llm_available: bool = Field(..., description="Whether LLM mode is available (API key configured)")
    storage_configured: bool = Field(..., description="Whether cloud storage is configured")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "llm_available": True,
                "storage_configured": True
            }
        }
