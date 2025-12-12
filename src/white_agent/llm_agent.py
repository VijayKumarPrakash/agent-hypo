"""LLM-powered White Agent for robust experimental data analysis.

This is a revamped version of the agent that uses LLM throughout the entire
pipeline for maximum flexibility with different data formats and structures.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .llm_data_loader import LLMDataLoader
from .llm_analyzer import LLMAnalyzer
from .report_generator import ReportGenerator
from .utils import get_next_result_version, ensure_directory_structure


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMWhiteAgent:
    """LLM-powered agent for analyzing experimental data of any format.

    This agent uses LLM throughout the pipeline:
    1. Intelligent data loading and format detection
    2. Context-aware variable identification
    3. Adaptive statistical analysis
    4. Comprehensive report generation

    The agent is designed to work with diverse data formats and structures
    without requiring manual configuration or preprocessing.
    """

    def __init__(
        self,
        inputs_dir: str = "inputs",
        results_dir: str = "results",
        gemini_api_key: Optional[str] = None,
        analyzer_model: str = "gemini-1.5-pro",
        loader_model: str = "gemini-1.5-flash",
        report_model: str = "gemini-1.5-pro"
    ):
        """Initialize the LLM-powered White Agent.

        Args:
            inputs_dir: Path to inputs directory
            results_dir: Path to results directory
            gemini_api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            analyzer_model: Model for analysis (pro for best quality)
            loader_model: Model for data loading (flash for speed)
            report_model: Model for report generation (pro for quality)
        """
        self.inputs_dir = Path(inputs_dir)
        self.results_dir = Path(results_dir)
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        if not self.gemini_api_key:
            raise ValueError(
                "LLM-powered agent requires Gemini API key. "
                "Please provide gemini_api_key or set GEMINI_API_KEY environment variable."
            )

        # Initialize LLM-powered components
        self.data_loader = LLMDataLoader(
            api_key=self.gemini_api_key,
            model_name=loader_model
        )
        self.analyzer = LLMAnalyzer(
            api_key=self.gemini_api_key,
            model_name=analyzer_model
        )
        self.report_generator = ReportGenerator(
            api_key=self.gemini_api_key,
            model_name=report_model
        )

        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"LLM-powered White Agent initialized. "
            f"Inputs: {self.inputs_dir}, Results: {self.results_dir}"
        )

    def process_test(self, test_index: int) -> Dict[str, Any]:
        """Process a single test from the inputs directory.

        This method performs end-to-end analysis using LLM guidance at each step.

        Args:
            test_index: The test number (e.g., 12 for inputs/test_12)

        Returns:
            Dictionary containing analysis results and output paths

        Raises:
            FileNotFoundError: If the test directory doesn't exist
            ValueError: If analysis fails
        """
        logger.info(f"Processing test_{test_index} with LLM-powered pipeline")

        # Step 1: Load input data (with intelligent format detection)
        test_dir = self.inputs_dir / f"test_{test_index}"
        if not test_dir.exists():
            raise FileNotFoundError(f"Test directory not found: {test_dir}")

        logger.info(f"Loading data from {test_dir}")
        context, data_df, data_file_path = self.data_loader.load_test_data(test_dir)

        logger.info(f"Loaded data: {data_df.shape[0]} rows, {data_df.shape[1]} columns")

        # Step 2: Create output directory with version
        result_version = get_next_result_version(self.results_dir, test_index)
        result_dir = self.results_dir / f"result_{test_index}_{result_version}"
        ensure_directory_structure(result_dir)

        logger.info(f"Created output directory: {result_dir}")

        # Step 3: Copy data source to output
        data_output_dir = result_dir / "data_source"
        self._copy_data_source(data_file_path, data_output_dir)

        # Step 4: Perform LLM-guided statistical analysis
        logger.info("Performing LLM-guided statistical analysis")
        analysis_results = self.analyzer.analyze_experiment(
            data=data_df,
            context=context
        )

        # Step 5: Generate analysis code
        logger.info("Generating reproducible analysis code")
        code_dir = result_dir / "code"
        self._generate_analysis_code(
            code_dir,
            data_file_path.name,
            analysis_results
        )

        # Step 6: Generate comprehensive report
        logger.info("Generating comprehensive report with LLM")
        report_dir = result_dir / "report"
        report_path = self.report_generator.generate_report(
            context=context,
            analysis_results=analysis_results,
            output_dir=report_dir
        )

        # Step 7: Save metadata
        metadata = self._create_metadata(
            test_index, result_version, test_dir, result_dir,
            data_file_path, data_df, analysis_results
        )

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

    def _generate_analysis_code(
        self,
        code_dir: Path,
        data_filename: str,
        analysis_results: Dict[str, Any]
    ):
        """Generate reproducible analysis code based on LLM analysis."""
        code_dir.mkdir(parents=True, exist_ok=True)

        # Extract variable info from LLM analysis
        variables = analysis_results.get("variables", {})
        treatment_col = variables.get("treatment", "treatment")
        outcome_col = variables.get("outcome", "outcome")
        treatment_value = variables.get("treatment_value", "1")
        control_value = variables.get("control_value", "0")

        # Get analysis plan info
        analysis_plan = analysis_results.get("analysis_plan", {})
        experiment_type = analysis_plan.get("experiment_type", "experiment")

        # Generate Python script
        code = f'''"""Reproducible analysis code for {experiment_type}.

This code was auto-generated by the LLM-powered White Agent.
It reproduces the analysis performed on the experimental data.
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from pathlib import Path

# Load data
data_path = Path(__file__).parent.parent / "data_source" / "{data_filename}"

# Try different loaders based on file extension
if data_path.suffix == '.csv':
    df = pd.read_csv(data_path)
elif data_path.suffix == '.parquet':
    df = pd.read_parquet(data_path)
elif data_path.suffix == '.json':
    df = pd.read_json(data_path)
elif data_path.suffix in ['.xlsx', '.xls']:
    df = pd.read_excel(data_path)
else:
    raise ValueError(f"Unsupported file format: {{data_path.suffix}}")

print(f"Loaded data with shape: {{df.shape}}")
print(f"Columns: {{df.columns.tolist()}}")

# Variable identification (from LLM analysis)
treatment_col = "{treatment_col}"
outcome_col = "{outcome_col}"
treatment_value = {repr(treatment_value)}
control_value = {repr(control_value)}

print(f"\\nTreatment variable: {{treatment_col}}")
print(f"Outcome variable: {{outcome_col}}")
print(f"Treatment value: {{treatment_value}}, Control value: {{control_value}}")

# Separate treatment and control groups
control_data = df[df[treatment_col] == control_value][outcome_col].dropna()
treatment_data = df[df[treatment_col] == treatment_value][outcome_col].dropna()

print(f"\\nControl group size: {{len(control_data)}}")
print(f"Treatment group size: {{len(treatment_data)}}")

# Calculate Average Treatment Effect (ATE)
control_mean = control_data.mean()
treatment_mean = treatment_data.mean()
ate = treatment_mean - control_mean

# Calculate standard errors
se_control = control_data.sem()
se_treatment = treatment_data.sem()
se_ate = np.sqrt(se_control**2 + se_treatment**2)

# Calculate 95% confidence intervals
ci_lower = ate - 1.96 * se_ate
ci_upper = ate + 1.96 * se_ate

# Perform t-test
t_stat, p_value = stats.ttest_ind(treatment_data, control_data)

# Calculate effect size (Cohen's d)
pooled_std = np.sqrt(
    ((len(control_data) - 1) * control_data.std()**2 +
     (len(treatment_data) - 1) * treatment_data.std()**2) /
    (len(control_data) + len(treatment_data) - 2)
)
cohens_d = ate / pooled_std if pooled_std > 0 else 0

# Print results
print("\\n" + "="*60)
print("ANALYSIS RESULTS")
print("="*60)
print(f"\\nControl mean: {{control_mean:.4f}}")
print(f"Treatment mean: {{treatment_mean:.4f}}")
print(f"\\nAverage Treatment Effect (ATE): {{ate:.4f}}")
print(f"Standard Error: {{se_ate:.4f}}")
print(f"95% Confidence Interval: [{{ci_lower:.4f}}, {{ci_upper:.4f}}]")
print(f"\\nt-statistic: {{t_stat:.4f}}")
print(f"p-value: {{p_value:.4f}}")
print(f"Statistically significant (α=0.05): {{p_value < 0.05}}")
print(f"\\nEffect size (Cohen's d): {{cohens_d:.4f}}")

# Simple regression
X = df[[treatment_col]].values
y = df[outcome_col].values
model = LinearRegression()
model.fit(X, y)

print(f"\\nRegression coefficient: {{model.coef_[0]:.4f}}")
print(f"R-squared: {{model.score(X, y):.4f}}")

print("\\nAnalysis complete!")
'''

        code_path = code_dir / "analysis.py"
        with open(code_path, 'w') as f:
            f.write(code)

        logger.info(f"Generated analysis code at {code_path}")

        # Save requirements
        requirements = """pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
pyarrow>=12.0.0
openpyxl>=3.1.0
"""
        req_path = code_dir / "requirements.txt"
        with open(req_path, 'w') as f:
            f.write(requirements)

    def _create_metadata(
        self,
        test_index: int,
        result_version: int,
        test_dir: Path,
        result_dir: Path,
        data_file_path: Path,
        data_df,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create metadata for the analysis run."""
        # Get key statistics
        ate = analysis_results.get("average_treatment_effect")
        p_value = analysis_results.get("p_value")
        significant = analysis_results.get("statistically_significant")

        # Get analysis plan info
        analysis_plan = analysis_results.get("analysis_plan", {})

        metadata = {
            "test_index": test_index,
            "result_version": result_version,
            "input_dir": str(test_dir),
            "output_dir": str(result_dir),
            "data_file": data_file_path.name,
            "analysis_type": "llm_powered",
            "experiment_type": analysis_plan.get("experiment_type"),
            "data_shape": {
                "rows": len(data_df),
                "columns": len(data_df.columns)
            },
            "variables": analysis_results.get("variables", {}),
            "analysis_summary": {
                "sample_size": len(data_df),
                "treatment_effect": ate,
                "p_value": p_value,
                "statistically_significant": significant
            },
            "analysis_successful": analysis_results.get("analysis_successful", False),
            "llm_models_used": {
                "data_loader": self.data_loader.model_name,
                "analyzer": self.analyzer.model_name,
                "report_generator": self.report_generator.model_name
            }
        }

        return metadata

    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming A2A messages from other agents.

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
                "agent_type": "llm_white_agent",
                "capabilities": [
                    "adaptive_data_loading",
                    "intelligent_variable_identification",
                    "context_aware_analysis",
                    "comprehensive_reporting",
                    "multi_format_support"
                ],
                "ready": True,
                "llm_enabled": True
            }

        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}"
            }

    def reset(self):
        """Reset agent state for new battle/session."""
        logger.info("LLM-powered White Agent reset called")
        # Clear any cached state if needed
        pass
