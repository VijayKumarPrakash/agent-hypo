"""LLM-powered report generation using Gemini API."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive analysis reports using Gemini LLM."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro"):
        """Initialize the report generator.

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
                logger.info(f"Initialized Gemini model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        elif not GEMINI_AVAILABLE:
            logger.warning("google-generativeai package not available. Install with: pip install google-generativeai")

    def generate_report(
        self,
        context: str,
        analysis_results: Dict[str, Any],
        output_dir: Path
    ) -> Path:
        """Generate a comprehensive analysis report.

        Args:
            context: Experiment context/background
            analysis_results: Statistical analysis results
            output_dir: Directory to save the report

        Returns:
            Path to the generated report file
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate report content
        if self.model:
            report_content = self._generate_llm_report(context, analysis_results)
        else:
            report_content = self._generate_template_report(context, analysis_results)

        # Save as markdown
        report_path = output_dir / "analysis_report.md"
        with open(report_path, 'w') as f:
            f.write(report_content)

        # Also save results as JSON for programmatic access
        json_path = output_dir / "results.json"
        with open(json_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)

        logger.info(f"Report generated at {report_path}")
        return report_path

    def _generate_llm_report(self, context: str, results: Dict[str, Any]) -> str:
        """Generate report using Gemini LLM.

        Args:
            context: Experiment context
            results: Analysis results

        Returns:
            Report content as markdown
        """
        prompt = self._build_report_prompt(context, results)

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"LLM report generation failed: {e}")
            logger.info("Falling back to template report")
            return self._generate_template_report(context, results)

    def _build_report_prompt(self, context: str, results: Dict[str, Any]) -> str:
        """Build the prompt for LLM report generation.

        Args:
            context: Experiment context
            results: Analysis results

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert statistician and data scientist tasked with writing a comprehensive analysis report for a randomized controlled trial (RCT) or A/B test.

# EXPERIMENT CONTEXT
{context}

# STATISTICAL ANALYSIS RESULTS
{json.dumps(results, indent=2)}

# TASK
Write a thorough, professional analysis report in markdown format. The report should include:

1. **Executive Summary**: Key findings in 2-3 sentences for stakeholders

2. **Experiment Overview**:
   - Research question and objectives
   - Study design (RCT, A/B test, etc.)
   - Sample size and composition
   - Treatment and control group descriptions

3. **Data Quality Assessment**:
   - Sample size adequacy
   - Balance between treatment and control groups
   - Any potential data quality issues
   - Missing data or outliers

4. **Statistical Findings**:
   - Average Treatment Effect (ATE) with confidence intervals
   - Statistical significance (p-values, test statistics)
   - Effect size interpretation (Cohen's d)
   - Regression results if applicable
   - All relevant statistical tests performed

5. **Interpretation**:
   - What do the results mean in practical terms?
   - Is the treatment effective?
   - How confident can we be in these results?

6. **Threats to Validity**:
   - Possible confounders
   - Treatment design considerations
   - Selection bias concerns
   - External validity considerations
   - Any violations of RCT assumptions

7. **Recommendations**:
   - Based on the findings, what actions should be taken?
   - Suggestions for improving the study design
   - Ideas for future experiments
   - Caveats and limitations

8. **Technical Details**:
   - Statistical methods used
   - Assumptions made
   - Sensitivity analyses performed

Format the report in clean markdown with clear sections, subsections, tables where appropriate, and professional academic/industry style. Be thorough but concise. Include specific numbers and statistics throughout.
"""
        return prompt

    def _generate_template_report(self, context: str, results: Dict[str, Any]) -> str:
        """Generate a template-based report when LLM is not available.

        Args:
            context: Experiment context
            results: Analysis results

        Returns:
            Report content as markdown
        """
        variables = results.get("variables", {})
        treatment_var = variables.get("treatment", "unknown")
        outcome_var = variables.get("outcome", "unknown")

        ate = results.get("average_treatment_effect", 0)
        p_value = results.get("p_value", 1)
        significant = results.get("statistically_significant", False)
        control_mean = results.get("control_mean", 0)
        treatment_mean = results.get("treatment_mean", 0)

        sample_info = results.get("sample_info", {})
        total_n = sample_info.get("total_sample_size", 0)

        report = f"""# Randomized Controlled Trial Analysis Report

## Executive Summary

This analysis examines the treatment effect in a randomized controlled experiment. The average treatment effect (ATE) is **{ate:.4f}** with a p-value of **{p_value:.4f}**. The results are **{"statistically significant" if significant else "not statistically significant"}** at the α=0.05 level.

## Experiment Overview

### Context
{context}

### Study Design
- **Total Sample Size**: {total_n}
- **Treatment Variable**: {treatment_var}
- **Outcome Variable**: {outcome_var}
- **Design Type**: Randomized Controlled Trial

## Statistical Findings

### Primary Results

| Metric | Value |
|--------|-------|
| Control Group Mean | {control_mean:.4f} |
| Treatment Group Mean | {treatment_mean:.4f} |
| Average Treatment Effect (ATE) | {ate:.4f} |
| Standard Error | {results.get('ate_standard_error', 0):.4f} |
| 95% Confidence Interval | [{results.get('ate_ci_95', {}).get('lower', 0):.4f}, {results.get('ate_ci_95', {}).get('upper', 0):.4f}] |

### Hypothesis Testing

"""

        # Add t-test results
        if "t_test" in results:
            t_test = results["t_test"]
            report += f"""
**Two-Sample t-test**
- t-statistic: {t_test.get('t_statistic', 0):.4f}
- p-value: {t_test.get('p_value', 1):.4f}
- Degrees of Freedom: {t_test.get('degrees_of_freedom', 0)}

"""

        # Add effect size
        if "effect_size" in results:
            effect = results["effect_size"]
            report += f"""
**Effect Size**
- Cohen's d: {effect.get('cohens_d', 0):.4f}
- Interpretation: {effect.get('interpretation', 'unknown')}

"""

        # Add regression results
        if "simple_regression" in results:
            reg = results["simple_regression"]
            report += f"""
### Regression Analysis

**Simple Linear Regression: {outcome_var} ~ {treatment_var}**
- Treatment Coefficient: {reg.get('treatment_coefficient', 0):.4f}
- Intercept: {reg.get('intercept', 0):.4f}
- R²: {reg.get('r_squared', 0):.4f}

"""

        if "multiple_regression" in results:
            multi_reg = results["multiple_regression"]
            report += f"""
**Multiple Regression (with covariates)**
- R²: {multi_reg.get('r_squared', 0):.4f}
- Number of observations: {multi_reg.get('n_observations', 0)}
- Covariates included: {', '.join(multi_reg.get('covariates', []))}

Coefficients:
"""
            for var, coef in multi_reg.get('coefficients', {}).items():
                report += f"- {var}: {coef:.4f}\n"

        # Add balance check
        if "covariate_balance" in results and results["covariate_balance"]:
            report += f"""
## Covariate Balance

Balance between treatment and control groups on baseline covariates:

| Variable | Control Mean | Treatment Mean | Difference | p-value | Balanced |
|----------|--------------|----------------|------------|---------|----------|
"""
            for test in results["covariate_balance"]:
                report += f"| {test['variable']} | {test['control_mean']:.4f} | {test['treatment_mean']:.4f} | {test['difference']:.4f} | {test['p_value']:.4f} | {'✓' if test['balanced'] else '✗'} |\n"

            summary = results.get("summary", {})
            if summary:
                report += f"""
**Balance Summary**: {summary.get('n_balanced', 0)}/{summary.get('n_covariates_checked', 0)} covariates balanced ({summary.get('balance_rate', 0)*100:.1f}%)
"""

        # Interpretation section
        report += f"""
## Interpretation

The treatment {"increased" if ate > 0 else "decreased"} the outcome variable by an average of {abs(ate):.4f} units compared to the control group. """

        if significant:
            report += f"""This effect is statistically significant (p = {p_value:.4f} < 0.05), suggesting that the observed difference is unlikely to be due to random chance alone.

"""
        else:
            report += f"""However, this effect is not statistically significant at the α=0.05 level (p = {p_value:.4f}), meaning we cannot rule out that the observed difference could be due to random variation.

"""

        # Recommendations
        report += """
## Threats to Validity

**Potential Concerns:**
- Selection bias: Verify that randomization was properly implemented
- Attrition: Check if there was differential dropout between groups
- Spillover effects: Consider whether treatment effects could have spread to control group
- Compliance: Assess whether participants actually received the intended treatment
- Confounding: Although randomization should balance confounders, check covariate balance

## Recommendations

**Based on the analysis:**
"""

        if significant and ate > 0:
            report += "- The treatment shows a positive and statistically significant effect\n"
            report += "- Consider implementing the treatment more broadly\n"
            report += "- Monitor long-term effects in a follow-up study\n"
        elif significant and ate < 0:
            report += "- The treatment shows a negative and statistically significant effect\n"
            report += "- Investigate why the treatment had adverse effects\n"
            report += "- Do not implement the treatment as designed\n"
        else:
            report += "- The treatment effect is not statistically significant\n"
            report += "- Consider increasing sample size for a more powerful test\n"
            report += "- Investigate whether the treatment was implemented as intended\n"

        report += """
**Future Improvements:**
- Increase sample size to improve statistical power
- Collect additional covariates to improve precision
- Consider pre-registration to avoid p-hacking
- Conduct heterogeneity analysis to identify subgroups with stronger effects
- Perform sensitivity analyses to test robustness of findings

## Technical Details

**Statistical Methods:**
- Two-sample t-test for difference in means
- Linear regression for treatment effect estimation
- Covariate balance tests using t-tests
- 95% confidence intervals using normal approximation

**Assumptions:**
- Random assignment to treatment and control groups
- Independent observations
- Approximately normal distribution of outcomes (for t-test)
- No spillover effects between units

---

*Report generated automatically by White Agent RCT Analyzer*
"""

        return report
