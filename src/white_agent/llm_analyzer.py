"""LLM-powered data analysis engine for robust RCT/experiment analysis.

This module uses an LLM to understand data structure, identify variables,
and perform comprehensive statistical analysis regardless of input format.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Uses LLM to robustly analyze experimental data of any format."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-pro"
    ):
        """Initialize the LLM analyzer.

        Args:
            api_key: Gemini API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.model = None

        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"Initialized LLM analyzer with {model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        elif not GEMINI_AVAILABLE:
            logger.warning("google-generativeai package not available")

    def analyze_experiment(
        self,
        data: pd.DataFrame,
        context: str,
        data_sample_size: int = 100
    ) -> Dict[str, Any]:
        """Perform complete experimental analysis using LLM guidance.

        Args:
            data: DataFrame containing experimental data
            context: Text description of the experiment
            data_sample_size: Number of rows to send to LLM for inspection

        Returns:
            Dictionary containing comprehensive analysis results
        """
        if not self.model:
            raise ValueError(
                "LLM analyzer requires Gemini API key. "
                "Please provide api_key or set GEMINI_API_KEY environment variable."
            )

        logger.info("Starting LLM-powered analysis")

        # Step 1: Understand data structure and identify variables
        analysis_plan = self._create_analysis_plan(data, context, data_sample_size)

        # Step 2: Execute statistical analysis based on LLM plan
        results = self._execute_analysis(data, analysis_plan)

        # Step 3: Interpret results using LLM
        results["interpretation"] = self._interpret_results(
            context, analysis_plan, results
        )

        logger.info("LLM-powered analysis complete")
        return results

    def _create_analysis_plan(
        self,
        data: pd.DataFrame,
        context: str,
        sample_size: int
    ) -> Dict[str, Any]:
        """Use LLM to understand data and create analysis plan.

        Args:
            data: Experimental data
            context: Experiment context
            sample_size: Number of rows to sample for LLM

        Returns:
            Analysis plan with variable mappings and analysis type
        """
        # Prepare data summary for LLM
        data_summary = self._prepare_data_summary(data, sample_size)

        prompt = f"""You are an expert statistician analyzing experimental data. Your task is to understand the data structure and create a detailed analysis plan.

# EXPERIMENT CONTEXT
{context}

# DATA STRUCTURE
Columns: {data.columns.tolist()}
Total rows: {len(data)}
Data types: {data.dtypes.to_dict()}

# DATA SAMPLE (first {min(sample_size, len(data))} rows)
{data.head(sample_size).to_string()}

# STATISTICAL SUMMARY
{data.describe().to_string()}

# YOUR TASK
Based on the experiment context and data structure, create a comprehensive analysis plan. Return a JSON object with the following structure:

{{
  "experiment_type": "RCT" | "A/B test" | "observational study" | "other",
  "treatment_variable": {{
    "column_name": "exact column name in data",
    "description": "what this variable represents",
    "type": "binary" | "categorical" | "continuous",
    "treatment_value": "value representing treatment (e.g., 1, 'treatment', etc.)",
    "control_value": "value representing control (e.g., 0, 'control', etc.)"
  }},
  "outcome_variable": {{
    "column_name": "exact column name in data",
    "description": "what this variable measures",
    "type": "continuous" | "binary" | "categorical" | "count"
  }},
  "covariates": [
    {{
      "column_name": "exact column name",
      "description": "what this represents",
      "type": "continuous" | "categorical" | "binary",
      "role": "confounder" | "mediator" | "precision variable" | "other"
    }}
  ],
  "analysis_methods": [
    "t-test",
    "regression",
    "mann-whitney",
    "balance-check",
    "other methods as appropriate"
  ],
  "potential_issues": [
    "list any data quality issues, missing values, outliers, etc."
  ],
  "recommended_approach": "detailed description of how to analyze this data"
}}

IMPORTANT:
- Be precise with column names - they must exactly match the data
- Consider the context when identifying variables
- If the data structure is unclear, make your best interpretation
- Consider edge cases like missing values, outliers, or unusual distributions
- The treatment variable might not be binary (could be dose levels, multiple arms, etc.)

Return ONLY the JSON object, no additional text.
"""

        try:
            response = self.model.generate_content(prompt)
            plan_text = response.text.strip()

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0].strip()

            plan = json.loads(plan_text)
            logger.info(f"Created analysis plan: {plan.get('experiment_type')}")
            return plan

        except Exception as e:
            logger.error(f"Failed to create analysis plan: {e}")
            # Fallback to heuristic-based plan
            return self._fallback_analysis_plan(data, context)

    def _prepare_data_summary(
        self,
        data: pd.DataFrame,
        sample_size: int
    ) -> str:
        """Prepare a concise data summary for LLM."""
        summary_parts = []

        # Basic info
        summary_parts.append(f"Shape: {data.shape}")
        summary_parts.append(f"Columns: {list(data.columns)}")

        # Data types and unique values
        for col in data.columns:
            dtype = data[col].dtype
            n_unique = data[col].nunique()
            n_missing = data[col].isna().sum()

            info = f"  {col}: {dtype}, {n_unique} unique values"
            if n_missing > 0:
                info += f", {n_missing} missing"
            summary_parts.append(info)

        return "\n".join(summary_parts)

    def _execute_analysis(
        self,
        data: pd.DataFrame,
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute statistical analysis based on LLM plan.

        Args:
            data: Experimental data
            plan: Analysis plan from LLM

        Returns:
            Statistical analysis results
        """
        results = {
            "analysis_plan": plan,
            "sample_info": {
                "total_sample_size": len(data),
                "n_variables": len(data.columns)
            }
        }

        try:
            # Extract variable information
            treatment_var = plan["treatment_variable"]["column_name"]
            outcome_var = plan["outcome_variable"]["column_name"]

            # Validate variables exist
            if treatment_var not in data.columns:
                raise ValueError(f"Treatment variable '{treatment_var}' not found in data")
            if outcome_var not in data.columns:
                raise ValueError(f"Outcome variable '{outcome_var}' not found in data")

            # Get treatment and control values
            treatment_value = plan["treatment_variable"].get("treatment_value")
            control_value = plan["treatment_variable"].get("control_value")

            # Perform analysis based on experiment type and variable types
            results.update(
                self._analyze_treatment_effect(
                    data, treatment_var, outcome_var,
                    treatment_value, control_value
                )
            )

            # Additional analyses
            if "t-test" in plan.get("analysis_methods", []):
                results.update(
                    self._perform_hypothesis_tests(
                        data, treatment_var, outcome_var,
                        treatment_value, control_value
                    )
                )

            if "regression" in plan.get("analysis_methods", []):
                results.update(
                    self._regression_analysis(
                        data, treatment_var, outcome_var, plan.get("covariates", [])
                    )
                )

            if "balance-check" in plan.get("analysis_methods", []):
                results.update(
                    self._check_balance(
                        data, treatment_var, treatment_value, control_value,
                        plan.get("covariates", [])
                    )
                )

            results["analysis_successful"] = True

        except Exception as e:
            logger.error(f"Analysis execution failed: {e}")
            results["analysis_successful"] = False
            results["error"] = str(e)

        return results

    def _analyze_treatment_effect(
        self,
        data: pd.DataFrame,
        treatment_col: str,
        outcome_col: str,
        treatment_value: Any,
        control_value: Any
    ) -> Dict[str, Any]:
        """Calculate treatment effect based on data types."""
        # Separate groups
        if treatment_value is not None and control_value is not None:
            control = data[data[treatment_col] == control_value][outcome_col].dropna()
            treatment = data[data[treatment_col] == treatment_value][outcome_col].dropna()
        else:
            # Fallback: assume binary 0/1
            unique_vals = data[treatment_col].unique()
            if len(unique_vals) == 2:
                control_value = min(unique_vals)
                treatment_value = max(unique_vals)
                control = data[data[treatment_col] == control_value][outcome_col].dropna()
                treatment = data[data[treatment_col] == treatment_value][outcome_col].dropna()
            else:
                raise ValueError(f"Cannot determine treatment/control groups from {unique_vals}")

        # Calculate statistics
        control_mean = control.mean()
        treatment_mean = treatment.mean()
        ate = treatment_mean - control_mean

        se_control = control.sem()
        se_treatment = treatment.sem()
        se_ate = np.sqrt(se_control**2 + se_treatment**2)

        ci_lower = ate - 1.96 * se_ate
        ci_upper = ate + 1.96 * se_ate

        return {
            "variables": {
                "treatment": treatment_col,
                "outcome": outcome_col,
                "treatment_value": str(treatment_value),
                "control_value": str(control_value)
            },
            "control_mean": float(control_mean),
            "treatment_mean": float(treatment_mean),
            "average_treatment_effect": float(ate),
            "ate_standard_error": float(se_ate),
            "ate_ci_95": {
                "lower": float(ci_lower),
                "upper": float(ci_upper)
            },
            "control_std": float(control.std()),
            "treatment_std": float(treatment.std()),
            "control_n": int(len(control)),
            "treatment_n": int(len(treatment))
        }

    def _perform_hypothesis_tests(
        self,
        data: pd.DataFrame,
        treatment_col: str,
        outcome_col: str,
        treatment_value: Any,
        control_value: Any
    ) -> Dict[str, Any]:
        """Perform statistical hypothesis tests."""
        # Get groups
        control = data[data[treatment_col] == control_value][outcome_col].dropna()
        treatment = data[data[treatment_col] == treatment_value][outcome_col].dropna()

        # t-test
        t_stat, p_value = stats.ttest_ind(treatment, control)

        # Mann-Whitney U test
        u_stat, p_value_mw = stats.mannwhitneyu(
            treatment, control, alternative='two-sided'
        )

        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(control) - 1) * control.std()**2 +
             (len(treatment) - 1) * treatment.std()**2) /
            (len(control) + len(treatment) - 2)
        )
        cohens_d = (treatment.mean() - control.mean()) / pooled_std if pooled_std > 0 else 0

        return {
            "t_test": {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "degrees_of_freedom": int(len(control) + len(treatment) - 2)
            },
            "mann_whitney_u_test": {
                "u_statistic": float(u_stat),
                "p_value": float(p_value_mw)
            },
            "effect_size": {
                "cohens_d": float(cohens_d),
                "interpretation": self._interpret_cohens_d(cohens_d)
            },
            "statistically_significant": bool(p_value < 0.05),
            "p_value": float(p_value)
        }

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"

    def _regression_analysis(
        self,
        data: pd.DataFrame,
        treatment_col: str,
        outcome_col: str,
        covariates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform regression analysis."""
        results = {}

        # Simple regression
        X_simple = data[[treatment_col]].values
        y = data[outcome_col].values

        model_simple = LinearRegression()
        model_simple.fit(X_simple, y)

        results["simple_regression"] = {
            "treatment_coefficient": float(model_simple.coef_[0]),
            "intercept": float(model_simple.intercept_),
            "r_squared": float(model_simple.score(X_simple, y))
        }

        # Multiple regression with covariates
        if covariates:
            covariate_cols = [c["column_name"] for c in covariates
                            if c["column_name"] in data.columns]

            if covariate_cols:
                cols_to_use = [treatment_col] + covariate_cols
                data_complete = data[cols_to_use + [outcome_col]].dropna()

                if len(data_complete) > len(cols_to_use):
                    X_multi = data_complete[cols_to_use].values
                    y_multi = data_complete[outcome_col].values

                    model_multi = LinearRegression()
                    model_multi.fit(X_multi, y_multi)

                    coef_dict = {
                        cols_to_use[i]: float(model_multi.coef_[i])
                        for i in range(len(cols_to_use))
                    }

                    results["multiple_regression"] = {
                        "coefficients": coef_dict,
                        "intercept": float(model_multi.intercept_),
                        "r_squared": float(model_multi.score(X_multi, y_multi)),
                        "n_observations": int(len(data_complete)),
                        "covariates": covariate_cols
                    }

        return results

    def _check_balance(
        self,
        data: pd.DataFrame,
        treatment_col: str,
        treatment_value: Any,
        control_value: Any,
        covariates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check covariate balance between treatment groups."""
        if not covariates:
            return {"covariate_balance": []}

        balance_tests = []

        for covariate in covariates:
            col = covariate["column_name"]
            if col not in data.columns:
                continue

            control = data[data[treatment_col] == control_value][col].dropna()
            treatment = data[data[treatment_col] == treatment_value][col].dropna()

            if len(control) > 0 and len(treatment) > 0:
                try:
                    t_stat, p_value = stats.ttest_ind(treatment, control)

                    balance_tests.append({
                        "variable": col,
                        "control_mean": float(control.mean()),
                        "treatment_mean": float(treatment.mean()),
                        "difference": float(treatment.mean() - control.mean()),
                        "p_value": float(p_value),
                        "balanced": bool(p_value > 0.05)
                    })
                except Exception as e:
                    logger.warning(f"Could not check balance for {col}: {e}")

        result = {"covariate_balance": balance_tests}

        if balance_tests:
            n_balanced = sum(1 for test in balance_tests if test["balanced"])
            result["summary"] = {
                "n_covariates_checked": len(balance_tests),
                "n_balanced": n_balanced,
                "balance_rate": n_balanced / len(balance_tests)
            }

        return result

    def _interpret_results(
        self,
        context: str,
        plan: Dict[str, Any],
        results: Dict[str, Any]
    ) -> str:
        """Use LLM to interpret statistical results in context.

        Args:
            context: Experiment context
            plan: Analysis plan
            results: Statistical results

        Returns:
            Natural language interpretation
        """
        prompt = f"""You are an expert statistician providing interpretation of experimental results.

# EXPERIMENT CONTEXT
{context}

# ANALYSIS PLAN
{json.dumps(plan, indent=2)}

# STATISTICAL RESULTS
{json.dumps(results, indent=2)}

# YOUR TASK
Provide a clear, concise interpretation of these results. Address:

1. What does the treatment effect mean in practical terms?
2. Is the effect statistically significant and practically meaningful?
3. How confident can we be in these results?
4. What are the key limitations or caveats?
5. What actions should be taken based on these findings?

Write in clear, accessible language suitable for both technical and non-technical stakeholders.
Keep it concise (3-5 paragraphs).
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to generate interpretation: {e}")
            return "Interpretation unavailable."

    def _fallback_analysis_plan(
        self,
        data: pd.DataFrame,
        context: str
    ) -> Dict[str, Any]:
        """Create a basic analysis plan using heuristics when LLM fails."""
        logger.info("Using fallback heuristic-based analysis plan")

        # Find treatment variable
        treatment_col = None
        for col in data.columns:
            unique_vals = set(data[col].dropna().unique())
            if len(unique_vals) == 2 and unique_vals.issubset({0, 1, True, False}):
                treatment_col = col
                break

        # Find outcome variable
        outcome_col = None
        for col in data.columns:
            if col != treatment_col and pd.api.types.is_numeric_dtype(data[col]):
                if data[col].nunique() > 2:
                    outcome_col = col
                    break

        # Find covariates
        covariates = []
        for col in data.columns:
            if col not in [treatment_col, outcome_col] and pd.api.types.is_numeric_dtype(data[col]):
                covariates.append({
                    "column_name": col,
                    "description": f"Covariate: {col}",
                    "type": "continuous" if data[col].nunique() > 10 else "categorical",
                    "role": "precision variable"
                })

        return {
            "experiment_type": "RCT",
            "treatment_variable": {
                "column_name": treatment_col,
                "description": "Treatment indicator",
                "type": "binary",
                "treatment_value": 1,
                "control_value": 0
            },
            "outcome_variable": {
                "column_name": outcome_col,
                "description": "Primary outcome",
                "type": "continuous"
            },
            "covariates": covariates,
            "analysis_methods": ["t-test", "regression", "balance-check"],
            "potential_issues": ["Using heuristic-based plan - LLM unavailable"],
            "recommended_approach": "Standard RCT analysis with t-test and regression"
        }
