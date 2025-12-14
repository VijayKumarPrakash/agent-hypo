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
        model_name: str = "gemini-2.5-flash"
    ):
        """Initialize the LLM analyzer.

        Args:
            api_key: Gemini API key
            model_name: Gemini model to use (gemini-2.5-flash for fast statistical reasoning)
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

        # Step 3: Use LLM to extract key summary statistics from results
        results = self._extract_summary_statistics(results)

        # Step 4: Interpret results using LLM
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

            # Always perform core statistical analyses
            # (LLM will later parse these results to extract what's needed)
            # Use individual try-except blocks so one failure doesn't stop others

            # 1. Treatment effect analysis
            try:
                results.update(
                    self._analyze_treatment_effect(
                        data, treatment_var, outcome_var,
                        treatment_value, control_value
                    )
                )
            except Exception as e:
                logger.warning(f"Treatment effect analysis failed: {e}")

            # 2. Hypothesis tests (t-test, Mann-Whitney U)
            try:
                results.update(
                    self._perform_hypothesis_tests(
                        data, treatment_var, outcome_var,
                        treatment_value, control_value
                    )
                )
            except Exception as e:
                logger.warning(f"Hypothesis tests failed: {e}")

            # 3. Regression analysis (if covariates present)
            if plan.get("covariates"):
                try:
                    results.update(
                        self._regression_analysis(
                            data, treatment_var, outcome_var, plan.get("covariates", [])
                        )
                    )
                except Exception as e:
                    logger.warning(f"Regression analysis failed: {e}")

            # 4. Balance check (if covariates present)
            if plan.get("covariates"):
                try:
                    results.update(
                        self._check_balance(
                            data, treatment_var, treatment_value, control_value,
                            plan.get("covariates", [])
                        )
                    )
                except Exception as e:
                    logger.warning(f"Balance check failed: {e}")

            # Mark as successful if we got the core results
            results["analysis_successful"] = "average_treatment_effect" in results and "p_value" in results

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

        # Prepare treatment variable (encode categorical to numeric if needed)
        treatment_data = data[treatment_col].copy()
        if treatment_data.dtype == 'object' or treatment_data.dtype.name == 'category':
            # Encode categorical treatment as 0/1
            unique_vals = treatment_data.unique()
            if len(unique_vals) == 2:
                # Binary encoding: map to 0 and 1
                treatment_encoded = (treatment_data == unique_vals[1]).astype(int)
            else:
                logger.warning(f"Treatment variable has {len(unique_vals)} unique values, expected 2")
                return results
        else:
            treatment_encoded = treatment_data

        # Simple regression
        X_simple = treatment_encoded.values.reshape(-1, 1)
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
                # Prepare data with encoded treatment and covariates
                data_for_regression = data[covariate_cols + [outcome_col]].copy()
                data_for_regression[treatment_col] = treatment_encoded

                # Encode categorical covariates
                for col in covariate_cols:
                    if data_for_regression[col].dtype == 'object' or data_for_regression[col].dtype.name == 'category':
                        # Binary encode categorical variables
                        unique_vals = data_for_regression[col].unique()
                        if len(unique_vals) == 2:
                            data_for_regression[col] = (data_for_regression[col] == unique_vals[1]).astype(int)
                        else:
                            # For multiple categories, use one-hot encoding (drop first to avoid multicollinearity)
                            logger.info(f"One-hot encoding categorical covariate '{col}' with {len(unique_vals)} categories")
                            dummies = pd.get_dummies(data_for_regression[col], prefix=col, drop_first=True)
                            data_for_regression = pd.concat([data_for_regression.drop(columns=[col]), dummies], axis=1)
                            # Update covariate_cols to include dummy columns
                            covariate_cols = [c for c in covariate_cols if c != col] + list(dummies.columns)

                cols_to_use = [treatment_col] + covariate_cols
                data_complete = data_for_regression[cols_to_use + [outcome_col]].dropna()

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
                    # Check if covariate is categorical
                    if control.dtype == 'object' or control.dtype.name == 'category':
                        # For categorical variables, use chi-square test
                        from scipy.stats import chi2_contingency

                        # Create contingency table
                        contingency = pd.crosstab(
                            data[treatment_col],
                            data[col]
                        )
                        chi2, p_value, dof, expected = chi2_contingency(contingency)

                        # For categorical, report proportions instead of means
                        control_mode = control.mode()[0] if len(control.mode()) > 0 else control.iloc[0]
                        treatment_mode = treatment.mode()[0] if len(treatment.mode()) > 0 else treatment.iloc[0]
                        control_prop = (control == control_mode).mean()
                        treatment_prop = (treatment == treatment_mode).mean()

                        balance_tests.append({
                            "variable": col,
                            "type": "categorical",
                            "control_mode": str(control_mode),
                            "treatment_mode": str(treatment_mode),
                            "control_proportion": float(control_prop),
                            "treatment_proportion": float(treatment_prop),
                            "p_value": float(p_value),
                            "test": "chi-square",
                            "balanced": bool(p_value > 0.05)
                        })
                    else:
                        # For continuous variables, use t-test
                        t_stat, p_value = stats.ttest_ind(treatment, control)

                        balance_tests.append({
                            "variable": col,
                            "type": "continuous",
                            "control_mean": float(control.mean()),
                            "treatment_mean": float(treatment.mean()),
                            "difference": float(treatment.mean() - control.mean()),
                            "p_value": float(p_value),
                            "test": "t-test",
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

    def _extract_summary_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to extract key summary statistics from analysis results.

        This method robustly extracts p_value, statistically_significant, and other
        key fields from the analysis results, avoiding fragile heuristics.

        Args:
            results: Full analysis results dictionary

        Returns:
            Updated results dictionary with guaranteed summary fields
        """
        if not self.model:
            # Fallback: try to extract from known fields
            logger.warning("No LLM available for result parsing, using fallback logic")
            return self._fallback_extract_summary(results)

        # Prepare results summary for LLM
        results_json = json.dumps({
            k: v for k, v in results.items()
            if k not in ["interpretation"]  # Exclude interpretation to save tokens
        }, indent=2, default=str)

        prompt = f"""You are a statistical analyst. Extract the key summary statistics from the following analysis results.

# ANALYSIS RESULTS
{results_json}

# YOUR TASK
Extract and return a JSON object with these exact fields:

{{
  "p_value": <the primary p-value for the treatment effect (float, or null if not available)>,
  "statistically_significant": <true if p-value < 0.05, false otherwise, or null if p-value unavailable>,
  "average_treatment_effect": <the ATE/treatment effect (float)>,
  "treatment_effect": <same as average_treatment_effect for compatibility>,
  "sample_size": <total sample size (int)>
}}

IMPORTANT RULES:
1. Look for p-values in order of preference:
   - "p_value" field at the root level
   - "t_test" -> "p_value"
   - "mann_whitney_u_test" -> "p_value"
   - Any other test's p-value
2. For average_treatment_effect, look for:
   - "average_treatment_effect" field
   - Difference between treatment_mean and control_mean
3. Return ONLY the JSON object, no other text.
4. If a value is not available, use null (not 0 or empty string).

Return the JSON now:"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            summary = json.loads(response_text)

            # Update results with extracted summary
            results["p_value"] = summary.get("p_value")
            results["statistically_significant"] = summary.get("statistically_significant")

            # Ensure we have average_treatment_effect
            if "average_treatment_effect" not in results and summary.get("average_treatment_effect") is not None:
                results["average_treatment_effect"] = summary["average_treatment_effect"]

            logger.info(f"Extracted summary: p_value={summary.get('p_value')}, "
                       f"significant={summary.get('statistically_significant')}, "
                       f"ate={summary.get('average_treatment_effect')}")

            return results

        except Exception as e:
            logger.error(f"LLM-based summary extraction failed: {e}, using fallback")
            return self._fallback_extract_summary(results)

    def _fallback_extract_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback method to extract summary statistics without LLM.

        Args:
            results: Analysis results dictionary

        Returns:
            Updated results with summary fields
        """
        # Try to extract p_value from various sources
        p_value = None

        # Check direct p_value field
        if "p_value" in results:
            p_value = results["p_value"]
        # Check t_test
        elif "t_test" in results and isinstance(results["t_test"], dict):
            p_value = results["t_test"].get("p_value")
        # Check mann_whitney_u_test
        elif "mann_whitney_u_test" in results and isinstance(results["mann_whitney_u_test"], dict):
            p_value = results["mann_whitney_u_test"].get("p_value")

        # Set p_value and significance
        results["p_value"] = p_value
        results["statistically_significant"] = bool(p_value < 0.05) if p_value is not None else None

        logger.info(f"Fallback extraction: p_value={p_value}, "
                   f"significant={results['statistically_significant']}")

        return results

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

        # Find treatment variable with improved heuristics
        treatment_col = None
        treatment_value = None
        control_value = None

        # Strategy 1: Look for columns with suggestive names
        treatment_name_patterns = ['treatment', 'group', 'arm', 'condition', 'assign', 'intervention']
        for col in data.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in treatment_name_patterns):
                unique_vals = data[col].dropna().unique()
                if len(unique_vals) == 2:
                    treatment_col = col
                    # Identify which value is treatment vs control
                    vals_list = list(unique_vals)
                    # Look for control indicators in values
                    control_indicators = ['control', 'ctrl', '0', 0, False]
                    treatment_indicators = ['treatment', 'treat', 'treated', '1', 1, True]

                    for val in vals_list:
                        val_str = str(val).lower()
                        # Check for string matches in val_str and direct equality for non-string indicators
                        for ind in control_indicators:
                            if (isinstance(ind, str) and ind in val_str) or val == ind:
                                control_value = val
                                break
                        for ind in treatment_indicators:
                            if (isinstance(ind, str) and ind in val_str) or val == ind:
                                treatment_value = val
                                break

                    # If we identified both, we're done
                    if treatment_value is not None and control_value is not None:
                        break
                    # Otherwise assign arbitrarily
                    if treatment_value is None:
                        treatment_value = vals_list[1] if control_value == vals_list[0] else vals_list[0]
                    if control_value is None:
                        control_value = vals_list[1] if treatment_value == vals_list[0] else vals_list[0]
                    break

        # Strategy 2: If no name match, look for binary 0/1 or True/False columns
        if treatment_col is None:
            for col in data.columns:
                unique_vals = set(data[col].dropna().unique())
                if len(unique_vals) == 2 and unique_vals.issubset({0, 1, True, False}):
                    treatment_col = col
                    control_value = min(unique_vals)
                    treatment_value = max(unique_vals)
                    break

        # Strategy 3: Any binary column as last resort
        if treatment_col is None:
            for col in data.columns:
                unique_vals = data[col].dropna().unique()
                if len(unique_vals) == 2:
                    treatment_col = col
                    vals_list = list(unique_vals)
                    control_value = vals_list[0]
                    treatment_value = vals_list[1]
                    break

        # Find outcome variable
        outcome_col = None
        context_lower = context.lower()

        # Strategy 1: Look for explicit "primary outcome" or "outcome measure" mentions in context
        # Parse patterns like "primary outcome is X" or "outcome measure is X"
        import re
        primary_patterns = [
            r'primary outcome[^:]*:\s*([a-z_]+)',
            r'primary outcome[^i]*is\s+([a-z_]+)',
            r'outcome measure[^:]*:\s*([a-z_]+)',
            r'outcome measure[^i]*is\s+([a-z_]+)',
            r'primary metric[^:]*:\s*([a-z_]+)',
            r'outcome variable[^:]*:\s*([a-z_]+)',
        ]

        for pattern in primary_patterns:
            match = re.search(pattern, context_lower)
            if match:
                candidate = match.group(1).strip()
                # Check if this matches a column name
                for col in data.columns:
                    if col.lower() == candidate and pd.api.types.is_numeric_dtype(data[col]):
                        outcome_col = col
                        break
                if outcome_col:
                    break

        # Strategy 2: Look for columns with outcome-related names mentioned in context
        if outcome_col is None:
            # Score candidate columns by how prominently they appear in context
            candidates = []
            for col in data.columns:
                if col != treatment_col and pd.api.types.is_numeric_dtype(data[col]):
                    col_lower = col.lower()
                    # Count occurrences in context
                    count = context_lower.count(col_lower)
                    if count > 0 and data[col].nunique() > 2:
                        candidates.append((col, count))

            # Pick the most mentioned column
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                outcome_col = candidates[0][0]

        # Strategy 3: Look for columns with suggestive names
        if outcome_col is None:
            outcome_name_patterns = ['outcome', 'result', 'response', 'score', 'time', 'rate', 'count']
            for col in data.columns:
                if col != treatment_col and pd.api.types.is_numeric_dtype(data[col]):
                    col_lower = col.lower()
                    if any(pattern in col_lower for pattern in outcome_name_patterns) and data[col].nunique() > 2:
                        outcome_col = col
                        break

        # Strategy 4: First numeric column that's not treatment and has reasonable variance
        if outcome_col is None:
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
                "treatment_value": treatment_value,
                "control_value": control_value
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
