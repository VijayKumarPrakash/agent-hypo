"""Core White Agent implementation with A2A compatibility."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .data_loader import DataLoader
from .analyzer import RCTAnalyzer
from .report_generator import ReportGenerator
from .utils import get_next_result_version, ensure_directory_structure, identify_context_file


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhiteAgent:
    """White Agent for analyzing randomized controlled experiments.

    This agent is designed to be A2A (Agent-to-Agent) compatible for use
    within the AgentBeats platform. It can be triggered by a green agent
    and performs autonomous analysis of experimental data.

    Attributes:
        inputs_dir: Base directory for input test folders
        results_dir: Base directory for result outputs
        gemini_api_key: API key for Gemini LLM
    """

    def __init__(
        self,
        inputs_dir: str = "inputs",
        results_dir: str = "results",
        gemini_api_key: Optional[str] = None
    ):
        """Initialize the White Agent.

        Args:
            inputs_dir: Path to inputs directory
            results_dir: Path to results directory
            gemini_api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.inputs_dir = Path(inputs_dir)
        self.results_dir = Path(results_dir)
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        # Initialize components
        self.data_loader = DataLoader()
        self.analyzer = RCTAnalyzer()
        self.report_generator = ReportGenerator(self.gemini_api_key)

        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"White Agent initialized. Inputs: {self.inputs_dir}, Results: {self.results_dir}")

    def process_test(self, test_index: int) -> Dict[str, Any]:
        """Process a single test from the inputs directory.

        This is the main entry point for A2A communication. A green agent
        can trigger this method to analyze a specific test.

        Args:
            test_index: The test number (e.g., 12 for inputs/test_12)

        Returns:
            Dictionary containing analysis results and output paths

        Raises:
            FileNotFoundError: If the test directory doesn't exist
            ValueError: If required files are missing or invalid
        """
        logger.info(f"Processing test_{test_index}")

        # Step 1: Load input data
        test_dir = self.inputs_dir / f"test_{test_index}"
        if not test_dir.exists():
            raise FileNotFoundError(f"Test directory not found: {test_dir}")

        logger.info(f"Loading data from {test_dir}")
        context, data_df, data_file_path = self.data_loader.load_test_data(test_dir)

        # Step 2: Create output directory with version
        result_version = get_next_result_version(self.results_dir, test_index)
        result_dir = self.results_dir / f"result_{test_index}_{result_version}"
        ensure_directory_structure(result_dir)

        logger.info(f"Created output directory: {result_dir}")

        # Step 3: Copy data source to output
        data_output_dir = result_dir / "data_source"
        self._copy_data_source(data_file_path, data_output_dir)

        # Copy context file to output
        context_file_path = self._copy_context_file(test_dir, data_output_dir)

        # Step 4: Perform statistical analysis
        logger.info("Performing statistical analysis")
        analysis_results = self.analyzer.analyze(data_df, context)

        # Step 5: Generate analysis code
        logger.info("Generating analysis code")
        code_dir = result_dir / "code"
        self._generate_analysis_code(
            code_dir,
            data_file_path.name,
            analysis_results
        )

        # Step 6: Generate comprehensive report
        logger.info("Generating report with LLM")
        report_dir = result_dir / "report"
        report_path = self.report_generator.generate_report(
            context=context,
            analysis_results=analysis_results,
            output_dir=report_dir
        )

        # Step 7: Save metadata
        metadata = {
            "test_index": test_index,
            "result_version": result_version,
            "input_dir": str(test_dir),
            "output_dir": str(result_dir),
            "data_file": data_file_path.name,
            "context_file": context_file_path.name,
            "analysis_summary": {
                "sample_size": len(data_df),
                "treatment_effect": analysis_results.get("average_treatment_effect"),
                "p_value": analysis_results.get("p_value"),
                "statistically_significant": analysis_results.get("statistically_significant")
            }
        }

        metadata_path = result_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Analysis complete. Results saved to {result_dir}")

        return metadata

    def _copy_data_source(self, source_path: Path, dest_dir: Path):
        """Copy data source file to output directory."""
        import shutil
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / source_path.name
        shutil.copy2(source_path, dest_path)
        logger.info(f"Copied data source to {dest_path}")

    def _copy_context_file(self, test_dir: Path, dest_dir: Path) -> Path:
        """Copy context file to output directory.

        Args:
            test_dir: Source test directory containing context file
            dest_dir: Destination data_source directory

        Returns:
            Path to the copied context file
        """
        import shutil

        # Identify and copy context file
        context_path = identify_context_file(test_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / context_path.name
        shutil.copy2(context_path, dest_path)

        logger.info(f"Copied context file to {dest_path}")
        return dest_path

    def _generate_analysis_code(
        self,
        code_dir: Path,
        data_filename: str,
        analysis_results: Dict[str, Any]
    ):
        """Generate reproducible analysis code."""
        code_dir.mkdir(parents=True, exist_ok=True)

        # Generate Python script that reproduces the analysis
        code = f'''"""Reproducible analysis code for RCT experiment."""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# Load data
data_path = Path(__file__).parent.parent / "data_source" / "{data_filename}"
df = pd.read_csv(data_path) if data_path.suffix == '.csv' else pd.read_parquet(data_path)

# Identify treatment and outcome variables
# This assumes binary treatment (0/1) and continuous outcome
treatment_col = None
outcome_col = None

for col in df.columns:
    if df[col].nunique() == 2 and set(df[col].unique()).issubset({{0, 1, True, False}}):
        treatment_col = col
    elif df[col].dtype in ['float64', 'int64'] and col != treatment_col:
        outcome_col = col

if treatment_col is None or outcome_col is None:
    print("Could not automatically identify treatment and outcome variables")
    print("Available columns:", df.columns.tolist())
else:
    print(f"Treatment variable: {{treatment_col}}")
    print(f"Outcome variable: {{outcome_col}}")

    # Calculate Average Treatment Effect (ATE)
    control_outcomes = df[df[treatment_col] == 0][outcome_col]
    treatment_outcomes = df[df[treatment_col] == 1][outcome_col]

    ate = treatment_outcomes.mean() - control_outcomes.mean()

    # Perform t-test
    t_stat, p_value = stats.ttest_ind(treatment_outcomes, control_outcomes)

    # Calculate standard errors
    se_control = control_outcomes.sem()
    se_treatment = treatment_outcomes.sem()
    se_ate = np.sqrt(se_control**2 + se_treatment**2)

    # Calculate confidence intervals
    ci_lower = ate - 1.96 * se_ate
    ci_upper = ate + 1.96 * se_ate

    # Print results
    print("\\n=== Analysis Results ===")
    print(f"Sample size: {{len(df)}}")
    print(f"Control group size: {{len(control_outcomes)}}")
    print(f"Treatment group size: {{len(treatment_outcomes)}}")
    print(f"\\nControl mean: {{control_outcomes.mean():.4f}}")
    print(f"Treatment mean: {{treatment_outcomes.mean():.4f}}")
    print(f"\\nAverage Treatment Effect (ATE): {{ate:.4f}}")
    print(f"Standard Error: {{se_ate:.4f}}")
    print(f"95% CI: [{{ci_lower:.4f}}, {{ci_upper:.4f}}]")
    print(f"\\nt-statistic: {{t_stat:.4f}}")
    print(f"p-value: {{p_value:.4f}}")
    print(f"Statistically significant (α=0.05): {{p_value < 0.05}}")
'''

        code_path = code_dir / "analysis.py"
        with open(code_path, 'w') as f:
            f.write(code)

        logger.info(f"Generated analysis code at {code_path}")

        # Also save a requirements file for the analysis code
        requirements = """pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
pyarrow>=12.0.0
"""
        req_path = code_dir / "requirements.txt"
        with open(req_path, 'w') as f:
            f.write(requirements)

    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming A2A messages from other agents.

        This method provides the A2A protocol interface for AgentBeats.

        Args:
            message: A2A message dictionary containing action and parameters

        Returns:
            Response dictionary with status and results
        """
        action = message.get("action")
        params = message.get("params", {})

        logger.info(f"Received A2A message: action={action}")

        if action == "analyze_test":
            test_index = params.get("test_index")
            if test_index is None:
                return {
                    "status": "error",
                    "error": "Missing required parameter: test_index"
                }

            try:
                results = self.process_test(test_index)
                return {
                    "status": "success",
                    "results": results
                }
            except Exception as e:
                logger.error(f"Error processing test: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e)
                }

        elif action == "get_status":
            return {
                "status": "success",
                "agent_type": "white_agent",
                "capabilities": ["rct_analysis", "statistical_testing", "report_generation"],
                "ready": True
            }

        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}"
            }

    def reset(self):
        """Reset agent state for new battle/session.

        Called by AgentBeats launcher when agent needs to be reset.
        """
        logger.info("White Agent reset called")
        # Clear any cached state if needed
        pass
