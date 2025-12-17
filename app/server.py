"""FastAPI server for A2A-compliant White Agent RCT Analysis service.

This server provides HTTP endpoints for running RCT analysis remotely.
It accepts JSON requests with URLs to input files, processes them,
and returns URLs to generated output files in cloud storage.
"""

import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    RunRequest,
    RunResponse,
    ErrorResponse,
    HealthResponse,
    AnalysisSummary,
    OutputUrls
)
from .agent import run_agent, FileDownloadError, AnalysisError
from .storage import StorageUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting White Agent A2A service...")

    # Check configuration
    gemini_key = os.getenv("GEMINI_API_KEY")
    storage_configured = StorageUploader.is_configured()

    logger.info(f"LLM mode available: {gemini_key is not None}")
    logger.info(f"Cloud storage configured: {storage_configured}")

    if not storage_configured:
        logger.warning(
            "Cloud storage not configured! Set S3_BUCKET, S3_ACCESS_KEY_ID, "
            "and S3_SECRET_ACCESS_KEY environment variables."
        )

    yield

    # Shutdown
    logger.info("Shutting down White Agent A2A service...")


# Create FastAPI app
app = FastAPI(
    title="White Agent - A2A RCT Analysis Service",
    description="""
    A2A-compliant HTTP service for Randomized Controlled Trial (RCT) analysis.

    ## Features
    - Accepts URLs to context and data files
    - Supports multiple data formats (CSV, JSON, Parquet, Excel)
    - LLM-powered intelligent analysis (when API key configured)
    - Returns URLs to generated reports and analysis outputs
    - Fully stateless and cloud-ready

    ## Usage
    1. POST your analysis request to `/run` with URLs to your files
    2. Receive URLs to generated analysis reports and results
    3. Access the reports from cloud storage

    ## Required Configuration
    - `GEMINI_API_KEY`: For LLM-powered analysis (optional, falls back to traditional mode)
    - `S3_BUCKET`: S3 bucket name for storing outputs
    - `S3_ACCESS_KEY_ID`: S3 access key
    - `S3_SECRET_ACCESS_KEY`: S3 secret key
    - `S3_ENDPOINT_URL`: Custom S3 endpoint (optional, for R2/MinIO)
    - `S3_PUBLIC_URL_BASE`: Base URL for public access (optional, auto-detected)
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Status"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": "White Agent - A2A RCT Analysis",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "run_analysis": "/run",
            "agent_card": "/.well-known/agent-card.json",
            "documentation": "/docs"
        }
    }


@app.get("/.well-known/agent-card.json", tags=["Status"])
async def agent_card():
    """A2A agent card endpoint for agent discovery.

    Returns metadata about this agent's capabilities, endpoints, and schema
    according to the A2A protocol specification.
    """
    import json
    from pathlib import Path
    import os

    # Try multiple possible locations for the agent card file
    possible_paths = [
        Path(__file__).parent.parent / ".well-known" / "agent-card.json",  # Development
        Path("/app/.well-known/agent-card.json"),  # Docker production
        Path.cwd() / ".well-known" / "agent-card.json",  # Current working directory
    ]

    # Try to load from file first
    for card_path in possible_paths:
        if card_path.exists():
            try:
                with open(card_path) as f:
                    return json.load(f)
            except Exception as e:
                # Log error but continue to fallback
                import logging
                logging.error(f"Failed to load agent card from {card_path}: {e}")
                continue

    # Fallback: return inline if file not found (shouldn't happen in production)
    import logging
    logging.warning("Agent card file not found, using inline fallback")

    return {
        "agent": {
            "name": "White Agent - RCT Analyzer",
            "version": "1.0.0",
            "description": "An autonomous agent that performs comprehensive statistical analysis on randomized controlled trial data and generates detailed reports",
            "capabilities": {
                "primary_function": "rct_analysis",
                "supported_formats": [
                    "csv",
                    "json",
                    "parquet",
                    "xlsx"
                ],
                "analysis_types": [
                    "average_treatment_effect",
                    "hypothesis_testing",
                    "regression_analysis",
                    "covariate_balance",
                    "effect_size_calculation"
                ],
                "output_types": [
                    "statistical_report",
                    "analysis_code",
                    "data_copy",
                    "metadata"
                ]
            },
            "role": {
                "type": "analyzer",
                "color": "white",
                "a2a_compatible": True,
                "autonomous": True
            }
        },
        "endpoints": {
            "health": "/health",
            "run_analysis": "/run"
        },
        "schema": {
            "request": {
                "type": "object",
                "properties": {
                    "context_url": {
                        "type": "string",
                        "description": "URL to experiment description/context file"
                    },
                    "data_url": {
                        "type": "string",
                        "description": "URL to experimental data file"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["auto", "llm", "traditional"],
                        "default": "auto",
                        "description": "Analysis mode"
                    }
                },
                "required": ["context_url", "data_url"]
            },
            "response": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string"
                    },
                    "run_id": {
                        "type": "string"
                    },
                    "analysis_summary": {
                        "type": "object"
                    },
                    "outputs": {
                        "type": "object",
                        "properties": {
                            "report_url": {"type": "string"},
                            "data_url": {"type": "string"},
                            "code_url": {"type": "string"},
                            "metadata_url": {"type": "string"}
                        }
                    }
                }
            }
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Health check endpoint.

    Returns service health status and configuration information.
    """
    gemini_available = os.getenv("GEMINI_API_KEY") is not None
    storage_configured = StorageUploader.is_configured()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        llm_available=gemini_available,
        storage_configured=storage_configured
    )


@app.get("/status", response_model=HealthResponse, tags=["Status"])
async def status_check():
    """Status check endpoint (alias for /health).

    This endpoint is used by Render.com and Docker health checks.
    Returns the same information as /health.
    """
    return await health_check()


@app.post("/run", response_model=RunResponse, tags=["Analysis"])
async def run_analysis(request: RunRequest):
    """Run RCT analysis on provided data.

    This is the main A2A endpoint. It:
    1. Downloads context and data files from provided URLs
    2. Runs RCT analysis (LLM-powered or traditional mode)
    3. Uploads generated reports and results to cloud storage
    4. Returns URLs to the uploaded files

    **Request Body:**
    - `context_url`: URL to experiment description/context file
    - `data_url`: URL to experimental data file
    - `mode`: Analysis mode ("auto", "llm", or "traditional")

    **Response:**
    - `run_id`: Unique identifier for this analysis run
    - `analysis_summary`: Statistical summary of results
    - `outputs`: URLs to generated files in cloud storage

    **Errors:**
    - 400: Invalid request or configuration error
    - 500: Internal server error during analysis
    """
    try:
        # Convert request to dict
        input_payload = {
            "context_url": request.context_url,
            "data_url": request.data_url,
            "mode": request.mode.value
        }

        logger.info(f"Received analysis request: mode={request.mode.value}")

        # Run agent
        result = run_agent(input_payload)

        # Convert to response model
        response = RunResponse(
            status=result["status"],
            run_id=result["run_id"],
            analysis_type=result.get("analysis_type"),
            experiment_type=result.get("experiment_type"),
            mode_used=result["mode_used"],
            analysis_summary=AnalysisSummary(**result["analysis_summary"]),
            outputs=OutputUrls(**result["outputs"])
        )

        logger.info(f"Analysis completed successfully: run_id={result['run_id']}")
        return response

    except FileDownloadError as e:
        logger.error(f"File download error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error": "FileDownloadError",
                "message": str(e)
            }
        )

    except AnalysisError as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": "AnalysisError",
                "message": str(e)
            }
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error": "ValidationError",
                "message": str(e)
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": "InternalServerError",
                "message": "An unexpected error occurred during analysis"
            }
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "InternalServerError",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Get host and port from environment variables
    # AgentBeats controller sets HOST and AGENT_PORT
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", os.getenv("PORT", "8000")))

    uvicorn.run(
        "app.server:app",
        host=host,
        port=port,
        log_level="info"
    )
