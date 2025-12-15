"""Core agent logic for A2A-compliant RCT analysis.

This module provides a pure function interface for the agent, accepting inputs
and returning outputs without any file I/O operations. It downloads inputs from
URLs, processes them in-memory, and uploads results to cloud storage.
"""

import io
import sys
import os
import json
import tempfile
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import requests
import pandas as pd

# Add src to path for importing white_agent modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from white_agent.unified_agent import UnifiedWhiteAgent
from white_agent.data_loader import DataLoader
from white_agent.llm_data_loader import LLMDataLoader
from white_agent.analyzer import RCTAnalyzer
from white_agent.llm_analyzer import LLMAnalyzer
from white_agent.report_generator import ReportGenerator

from .storage import StorageUploader, get_content_type

logger = logging.getLogger(__name__)


class FileDownloadError(Exception):
    """Raised when file download from URL fails."""
    pass


class AnalysisError(Exception):
    """Raised when analysis execution fails."""
    pass


def download_file(url: str, timeout: int = 30) -> Tuple[bytes, str]:
    """Download a file from a URL.

    Args:
        url: URL to download from
        timeout: Request timeout in seconds

    Returns:
        Tuple of (file_content as bytes, filename)

    Raises:
        FileDownloadError: If download fails
    """
    try:
        logger.info(f"Downloading file from: {url}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        # Try to get filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"\'')
        else:
            # Extract from URL
            filename = url.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                # Generate a default filename based on content type
                ext = _get_extension_from_content_type(response.headers.get('Content-Type', ''))
                filename = f"downloaded_file{ext}"

        logger.info(f"Downloaded {len(response.content)} bytes as '{filename}'")
        return response.content, filename

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download file from {url}: {e}")
        raise FileDownloadError(f"Failed to download file from {url}: {str(e)}")


def _get_extension_from_content_type(content_type: str) -> str:
    """Get file extension from MIME type."""
    type_map = {
        'text/plain': '.txt',
        'text/markdown': '.md',
        'text/csv': '.csv',
        'application/json': '.json',
        'application/vnd.ms-excel': '.xlsx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/octet-stream': '.parquet',
    }
    return type_map.get(content_type.split(';')[0].strip(), '.txt')


def load_context_from_bytes(content: bytes, filename: str) -> str:
    """Load context text from bytes.

    Args:
        content: File content as bytes
        filename: Original filename (for encoding detection)

    Returns:
        Context text as string
    """
    try:
        # Try UTF-8 first
        return content.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback to latin-1
        return content.decode('latin-1')


def load_data_from_bytes(content: bytes, filename: str) -> pd.DataFrame:
    """Load data file into pandas DataFrame.

    Supports CSV, JSON, Parquet, and Excel formats.

    Args:
        content: File content as bytes
        filename: Original filename (for format detection)

    Returns:
        pandas DataFrame

    Raises:
        ValueError: If file format is not supported
    """
    ext = Path(filename).suffix.lower()

    try:
        if ext == '.csv':
            return pd.read_csv(io.BytesIO(content))
        elif ext == '.json':
            return pd.read_json(io.BytesIO(content))
        elif ext == '.parquet':
            return pd.read_parquet(io.BytesIO(content))
        elif ext in ['.xlsx', '.xls']:
            return pd.read_excel(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported data file format: {ext}")
    except Exception as e:
        logger.error(f"Failed to load data file: {e}")
        raise ValueError(f"Failed to parse data file '{filename}': {str(e)}")


def run_agent(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Core agent function for A2A-compliant RCT analysis.

    This is the main entry point for the agent. It downloads inputs from URLs,
    runs the analysis pipeline in-memory, uploads outputs to cloud storage,
    and returns URLs to the results.

    Args:
        input_payload: Dictionary containing:
            - context_url: URL to context/description file
            - data_url: URL to data file (CSV, JSON, Parquet, Excel)
            - mode: Analysis mode ("auto", "llm", or "traditional")

    Returns:
        Dictionary containing:
            - status: "success" or "error"
            - run_id: Unique identifier for this run
            - analysis_type: Type of analysis performed
            - experiment_type: Type of experiment detected
            - mode_used: Analysis mode used
            - analysis_summary: Summary statistics
            - outputs: Dictionary of URLs to generated files

    Raises:
        FileDownloadError: If downloading input files fails
        AnalysisError: If analysis execution fails
    """
    # Use fixed run_id to overwrite results each time
    run_id = "latest"
    logger.info(f"Starting analysis run: {run_id}")

    # Extract inputs
    context_url = str(input_payload["context_url"])
    data_url = str(input_payload["data_url"])
    mode = input_payload.get("mode", "auto")

    logger.info(f"Mode: {mode}")
    logger.info(f"Context URL: {context_url}")
    logger.info(f"Data URL: {data_url}")

    # Step 1: Download input files
    try:
        context_content, context_filename = download_file(context_url)
        data_content, data_filename = download_file(data_url)
    except FileDownloadError as e:
        raise AnalysisError(f"Failed to download inputs: {str(e)}")

    # Step 2: Load context and data
    try:
        context_text = load_context_from_bytes(context_content, context_filename)
        data_df = load_data_from_bytes(data_content, data_filename)
        logger.info(f"Loaded data: {data_df.shape[0]} rows, {data_df.shape[1]} columns")
    except Exception as e:
        raise AnalysisError(f"Failed to parse input files: {str(e)}")

    # Step 3: Initialize agent components based on mode
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    # Determine actual mode to use
    if mode == "llm" and not gemini_api_key:
        raise AnalysisError("LLM mode requires GEMINI_API_KEY environment variable")

    use_llm = (mode == "llm") or (mode == "auto" and gemini_api_key is not None)
    actual_mode = "llm" if use_llm else "traditional"

    logger.info(f"Using {actual_mode} mode for analysis")

    # Step 4: Run analysis
    try:
        if use_llm:
            # LLM-powered analysis
            analyzer = LLMAnalyzer(
                api_key=gemini_api_key,
                model_name="gemini-2.5-flash"
            )
            analysis_results = analyzer.analyze_experiment(
                data=data_df,
                context=context_text
            )
            report_generator = ReportGenerator(
                api_key=gemini_api_key,
                model_name="gemini-2.5-flash"
            )
        else:
            # Traditional analysis
            analyzer = RCTAnalyzer()
            analysis_results = analyzer.analyze(data_df, context_text)
            report_generator = ReportGenerator(gemini_api_key=None)

        logger.info("Analysis completed successfully")

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise AnalysisError(f"Analysis execution failed: {str(e)}")

    # Step 5: Generate outputs
    try:
        # Generate report (in-memory)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_report_dir = Path(temp_dir)
            report_path = report_generator.generate_report(
                context=context_text,
                analysis_results=analysis_results,
                output_dir=temp_report_dir
            )

            # Read generated report
            with open(report_path, 'r') as f:
                report_markdown = f.read()

            # Read results JSON
            results_json_path = temp_report_dir / "results.json"
            if results_json_path.exists():
                with open(results_json_path, 'r') as f:
                    results_json = f.read()
            else:
                # Generate results JSON from analysis_results
                results_json = json.dumps(analysis_results, indent=2)

        # Generate analysis code
        analysis_code = _generate_analysis_code(
            data_filename=data_filename,
            analysis_results=analysis_results,
            use_llm=use_llm
        )

        logger.info("Generated all output files")

    except Exception as e:
        logger.error(f"Failed to generate outputs: {e}", exc_info=True)
        raise AnalysisError(f"Failed to generate output files: {str(e)}")

    # Step 6: Upload outputs to S3
    try:
        uploader = StorageUploader()

        # Upload to report/ folder
        report_url = uploader.upload_text_file(
            text_content=report_markdown,
            s3_key=f"runs/{run_id}/report/analysis_report.md",
            content_type="text/markdown"
        )

        # Upload results JSON to report/ folder
        results_url = uploader.upload_json_file(
            json_content=results_json,
            s3_key=f"runs/{run_id}/report/results.json"
        )

        # Upload analysis code to code/ folder
        analysis_code_url = uploader.upload_text_file(
            text_content=analysis_code,
            s3_key=f"runs/{run_id}/code/analysis.py",
            content_type="text/x-python"
        )

        # Upload data copy to data_source/ folder
        data_copy_url = uploader.upload_file(
            file_content=data_content,
            s3_key=f"runs/{run_id}/data_source/{data_filename}",
            content_type=get_content_type(data_filename)
        )

        # Upload context copy to data_source/ folder
        context_copy_url = uploader.upload_file(
            file_content=context_content,
            s3_key=f"runs/{run_id}/data_source/{context_filename}",
            content_type=get_content_type(context_filename)
        )

        logger.info("Uploaded all outputs to cloud storage")

    except Exception as e:
        logger.error(f"Failed to upload outputs: {e}", exc_info=True)
        raise AnalysisError(f"Failed to upload outputs to cloud storage: {str(e)}")

    # Step 7: Construct response
    response = {
        "status": "success",
        "run_id": run_id,
        "analysis_type": analysis_results.get("analysis_plan", {}).get("analysis_type", "RCT"),
        "experiment_type": analysis_results.get("analysis_plan", {}).get("experiment_type"),
        "mode_used": actual_mode,
        "analysis_summary": {
            "sample_size": len(data_df),
            "treatment_effect": analysis_results.get("average_treatment_effect"),
            "p_value": analysis_results.get("p_value"),
            "statistically_significant": analysis_results.get("statistically_significant")
        },
        "outputs": {
            "report_url": report_url,
            "results_url": results_url,
            "analysis_code_url": analysis_code_url,
            "data_copy_url": data_copy_url,
            "context_copy_url": context_copy_url
        }
    }

    logger.info(f"Analysis run {run_id} completed successfully")
    return response


def _generate_analysis_code(
    data_filename: str,
    analysis_results: Dict[str, Any],
    use_llm: bool
) -> str:
    """Generate reproducible Python analysis code.

    Args:
        data_filename: Name of the data file
        analysis_results: Results from the analysis
        use_llm: Whether LLM mode was used

    Returns:
        Python code as string
    """
    if use_llm:
        # LLM-powered code generation
        variables = analysis_results.get("variables", {})
        treatment_col = variables.get("treatment", "treatment")
        outcome_col = variables.get("outcome", "outcome")
        treatment_value = variables.get("treatment_value", "1")
        control_value = variables.get("control_value", "0")
        experiment_type = analysis_results.get("analysis_plan", {}).get("experiment_type", "experiment")

        code = f'''"""Reproducible analysis code for {experiment_type}.

This code was auto-generated by the LLM-powered White Agent.
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

# Note: Update this path to point to your data file
DATA_FILE = "{data_filename}"

# Load data
df = pd.read_csv(DATA_FILE) if DATA_FILE.endswith('.csv') else pd.read_parquet(DATA_FILE)

print(f"Loaded data with shape: {{df.shape}}")

# Variable identification (from LLM analysis)
treatment_col = "{treatment_col}"
outcome_col = "{outcome_col}"
treatment_value = {repr(treatment_value)}
control_value = {repr(control_value)}

# Separate groups
control_data = df[df[treatment_col] == control_value][outcome_col].dropna()
treatment_data = df[df[treatment_col] == treatment_value][outcome_col].dropna()

# Calculate ATE
ate = treatment_data.mean() - control_data.mean()
se_ate = np.sqrt(control_data.sem()**2 + treatment_data.sem()**2)
t_stat, p_value = stats.ttest_ind(treatment_data, control_data)

print("\\n=== Results ===")
print(f"Average Treatment Effect: {{ate:.4f}}")
print(f"Standard Error: {{se_ate:.4f}}")
print(f"p-value: {{p_value:.4f}}")
print(f"Significant: {{p_value < 0.05}}")
'''
    else:
        # Traditional code generation
        code = f'''"""Reproducible analysis code for RCT experiment."""

import pandas as pd
import numpy as np
from scipy import stats

DATA_FILE = "{data_filename}"

df = pd.read_csv(DATA_FILE) if DATA_FILE.endswith('.csv') else pd.read_parquet(DATA_FILE)

# Auto-detect treatment and outcome variables
treatment_col = None
outcome_col = None

for col in df.columns:
    if df[col].nunique() == 2 and set(df[col].unique()).issubset({{0, 1, True, False}}):
        treatment_col = col
    elif df[col].dtype in ['float64', 'int64'] and col != treatment_col:
        outcome_col = col

if treatment_col and outcome_col:
    control = df[df[treatment_col] == 0][outcome_col]
    treatment = df[df[treatment_col] == 1][outcome_col]

    ate = treatment.mean() - control.mean()
    t_stat, p_value = stats.ttest_ind(treatment, control)

    print(f"ATE: {{ate:.4f}}")
    print(f"p-value: {{p_value:.4f}}")
'''

    return code
