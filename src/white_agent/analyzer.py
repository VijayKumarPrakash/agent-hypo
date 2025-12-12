"""Statistical analysis module for RCT experiments."""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from scipy import stats
import logging


logger = logging.getLogger(__name__)


class RCTAnalyzer:
    """Performs statistical analysis on randomized controlled trial data."""

    def __init__(self, alpha: float = 0.05):
        """Initialize the analyzer.

        Args:
            alpha: Significance level for hypothesis testing (default: 0.05)
        """
        self.alpha = alpha

    def analyze(self, data: pd.DataFrame, context: str) -> Dict[str, Any]:
        """Perform comprehensive RCT analysis.

        Args:
            data: DataFrame containing experimental data
            context: Text description of the experiment

        Returns:
            Dictionary containing all analysis results
        """
        logger.info("Starting RCT analysis")

        # Identify treatment and outcome variables
        treatment_col, outcome_col = self._identify_variables(data, context)

        results = {
            "variables": {
                "treatment": treatment_col,
                "outcome": outcome_col,
                "all_columns": data.columns.tolist()
            },
            "sample_info": self._get_sample_info(data, treatment_col),
        }

        # Perform core analyses
        if treatment_col and outcome_col:
            results.update(self._analyze_treatment_effect(data, treatment_col, outcome_col))
            results.update(self._perform_hypothesis_tests(data, treatment_col, outcome_col))
            results.update(self._regression_analysis(data, treatment_col, outcome_col))
            results.update(self._check_balance(data, treatment_col))
        else:
            results["error"] = "Could not identify treatment and outcome variables"
            logger.warning("Could not identify treatment and outcome variables")

        return results

    def _identify_variables(
        self,
        data: pd.DataFrame,
        context: str
    ) -> tuple[Optional[str], Optional[str]]:
        """Identify treatment and outcome variables from data.

        Args:
            data: Experimental data
            context: Experiment description

        Returns:
            Tuple of (treatment_column, outcome_column)
        """
        treatment_col = None
        outcome_col = None

        # Look for binary treatment variable (0/1 or True/False)
        for col in data.columns:
            unique_vals = set(data[col].dropna().unique())

            # Check if binary
            if len(unique_vals) == 2:
                if unique_vals.issubset({0, 1, True, False, '0', '1'}):
                    # Common treatment variable names
                    if any(keyword in col.lower() for keyword in
                           ['treat', 'treatment', 'group', 'condition', 'arm']):
                        treatment_col = col
                        break
                    # If no explicit name match, use first binary column
                    elif treatment_col is None:
                        treatment_col = col

        # Look for continuous outcome variable
        for col in data.columns:
            if col == treatment_col:
                continue

            # Check if numeric
            if pd.api.types.is_numeric_dtype(data[col]):
                # Common outcome variable names
                if any(keyword in col.lower() for keyword in
                       ['outcome', 'result', 'y', 'response', 'score', 'value']):
                    outcome_col = col
                    break
                # Use first continuous numeric column
                elif outcome_col is None and data[col].nunique() > 2:
                    outcome_col = col

        logger.info(f"Identified variables - Treatment: {treatment_col}, Outcome: {outcome_col}")
        return treatment_col, outcome_col

    def _get_sample_info(self, data: pd.DataFrame, treatment_col: Optional[str]) -> Dict[str, Any]:
        """Get basic sample information.

        Args:
            data: Experimental data
            treatment_col: Name of treatment column

        Returns:
            Dictionary with sample information
        """
        info = {
            "total_sample_size": len(data),
            "n_variables": len(data.columns)
        }

        if treatment_col:
            treatment_counts = data[treatment_col].value_counts().to_dict()
            info["treatment_distribution"] = treatment_counts

        return info

    def _analyze_treatment_effect(
        self,
        data: pd.DataFrame,
        treatment_col: str,
        outcome_col: str
    ) -> Dict[str, Any]:
        """Calculate average treatment effect and related statistics.

        Args:
            data: Experimental data
            treatment_col: Treatment variable name
            outcome_col: Outcome variable name

        Returns:
            Dictionary with treatment effect estimates
        """
        # Separate treatment and control groups
        control = data[data[treatment_col] == 0][outcome_col].dropna()
        treatment = data[data[treatment_col] == 1][outcome_col].dropna()

        # Calculate means
        control_mean = control.mean()
        treatment_mean = treatment.mean()

        # Calculate ATE
        ate = treatment_mean - control_mean

        # Calculate standard errors
        se_control = control.sem()
        se_treatment = treatment.sem()
        se_ate = np.sqrt(se_control**2 + se_treatment**2)

        # 95% Confidence interval
        ci_lower = ate - 1.96 * se_ate
        ci_upper = ate + 1.96 * se_ate

        return {
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
        outcome_col: str
    ) -> Dict[str, Any]:
        """Perform statistical hypothesis tests.

        Args:
            data: Experimental data
            treatment_col: Treatment variable name
            outcome_col: Outcome variable name

        Returns:
            Dictionary with test results
        """
        control = data[data[treatment_col] == 0][outcome_col].dropna()
        treatment = data[data[treatment_col] == 1][outcome_col].dropna()

        # Two-sample t-test
        t_stat, p_value = stats.ttest_ind(treatment, control)

        # Mann-Whitney U test (non-parametric alternative)
        u_stat, p_value_mw = stats.mannwhitneyu(treatment, control, alternative='two-sided')

        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((len(control) - 1) * control.std()**2 +
                              (len(treatment) - 1) * treatment.std()**2) /
                             (len(control) + len(treatment) - 2))
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
            "statistically_significant": bool(p_value < self.alpha),
            "alpha": self.alpha,
            "p_value": float(p_value)
        }

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size.

        Args:
            d: Cohen's d value

        Returns:
            Interpretation string
        """
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
        outcome_col: str
    ) -> Dict[str, Any]:
        """Perform regression analysis with potential covariates.

        Args:
            data: Experimental data
            treatment_col: Treatment variable name
            outcome_col: Outcome variable name

        Returns:
            Dictionary with regression results
        """
        from sklearn.linear_model import LinearRegression

        # Simple regression: outcome ~ treatment
        X_simple = data[[treatment_col]].values
        y = data[outcome_col].values

        model_simple = LinearRegression()
        model_simple.fit(X_simple, y)

        treatment_coef = model_simple.coef_[0]
        intercept = model_simple.intercept_
        r_squared = model_simple.score(X_simple, y)

        results = {
            "simple_regression": {
                "treatment_coefficient": float(treatment_coef),
                "intercept": float(intercept),
                "r_squared": float(r_squared)
            }
        }

        # Multiple regression with covariates (if available)
        covariates = [col for col in data.columns
                     if col not in [treatment_col, outcome_col]
                     and pd.api.types.is_numeric_dtype(data[col])]

        if covariates:
            # Use only complete cases
            cols_to_use = [treatment_col] + covariates
            data_complete = data[cols_to_use + [outcome_col]].dropna()

            if len(data_complete) > len(cols_to_use):  # Ensure enough data
                X_multi = data_complete[cols_to_use].values
                y_multi = data_complete[outcome_col].values

                model_multi = LinearRegression()
                model_multi.fit(X_multi, y_multi)

                coef_dict = {cols_to_use[i]: float(model_multi.coef_[i])
                           for i in range(len(cols_to_use))}

                results["multiple_regression"] = {
                    "coefficients": coef_dict,
                    "intercept": float(model_multi.intercept_),
                    "r_squared": float(model_multi.score(X_multi, y_multi)),
                    "n_observations": int(len(data_complete)),
                    "covariates": covariates
                }

        return results

    def _check_balance(
        self,
        data: pd.DataFrame,
        treatment_col: str
    ) -> Dict[str, Any]:
        """Check balance between treatment and control groups on covariates.

        Args:
            data: Experimental data
            treatment_col: Treatment variable name

        Returns:
            Dictionary with balance check results
        """
        balance_results = {}

        # Get all numeric covariates
        covariates = [col for col in data.columns
                     if col != treatment_col
                     and pd.api.types.is_numeric_dtype(data[col])]

        balance_tests = []

        for covariate in covariates:
            control = data[data[treatment_col] == 0][covariate].dropna()
            treatment = data[data[treatment_col] == 1][covariate].dropna()

            if len(control) > 0 and len(treatment) > 0:
                # Perform t-test for balance
                t_stat, p_value = stats.ttest_ind(treatment, control)

                balance_tests.append({
                    "variable": covariate,
                    "control_mean": float(control.mean()),
                    "treatment_mean": float(treatment.mean()),
                    "difference": float(treatment.mean() - control.mean()),
                    "p_value": float(p_value),
                    "balanced": bool(p_value > 0.05)  # Not significantly different
                })

        balance_results["covariate_balance"] = balance_tests

        if balance_tests:
            n_balanced = sum(1 for test in balance_tests if test["balanced"])
            balance_results["summary"] = {
                "n_covariates_checked": len(balance_tests),
                "n_balanced": n_balanced,
                "balance_rate": n_balanced / len(balance_tests) if balance_tests else 0
            }

        return balance_results
