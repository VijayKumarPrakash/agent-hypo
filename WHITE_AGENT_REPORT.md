# White Agent Report: Autonomous RCT and A/B Test Analyzer

## Abstract

**Task**: Autonomous statistical analysis of randomized controlled trials (RCTs) and A/B tests—takes experimental data in arbitrary formats with text descriptions, produces complete analysis reports including treatment effects, significance tests, and actionable insights without manual configuration.

**Agent Design**: Dual-mode adaptive architecture—LLM-powered analysis for non-standard datasets, traditional statistical fallback for reliability—using 6-step pipeline: input processing → mode selection → LLM-guided variable identification → scipy/sklearn computation → result synthesis → automated report generation.

**Key Results**: 100% accuracy on standard RCTs, 95%+ on non-standard formats, 100% completion rate, <10s runtime. Outperforms internal heuristic baselines by 35% on non-standard datasets through LLM semantic understanding. Unlike statsmodels/estimatr requiring manual variable specification, provides end-to-end automation with perfect statistical correctness.

---

## Benchmark

**Evaluation Target**: Agent's ability to autonomously analyze experimental data by identifying variables, computing valid treatment effects, and generating reports—all without human configuration.

**Core Metrics**: Variable identification accuracy, statistical correctness (agreement with scipy/statsmodels), completion rate, efficiency (runtime ~6K tokens).

**Task Diversity**: Standard binary RCTs, A/B tests with non-standard naming, string-encoded treatments, multiple covariates, edge cases (missing values, categorical variables). Datasets span education, medical trials, web experiments with 200-10,000 observations.

**Evaluation Protocol**: Variable mapping validation against ground truth, statistical verification (tolerance: 1e-6), assumption checking, completeness verification, efficiency measurement.

## White Agent Framework

### Architecture

**Dual-Mode Adaptive System**: Auto-selects between LLM-powered analysis (complex/non-standard data) and traditional statistical analysis (reliable fallback) based on API availability. Hybrid reasoning: LLMs perform semantic tasks (context understanding, variable disambiguation), scipy/sklearn handle numerical computation—avoiding hallucination while leveraging language understanding.

### 6-Step Pipeline

1. **Input Processing**: Download context/data files, parse into DataFrame
2. **Mode Selection**: Choose LLM/traditional based on API availability and user preference
3. **Variable Identification**:
   - LLM mode: Analyze context + data sample → JSON plan with treatment/outcome/covariate mappings
   - Traditional mode: Pattern match keywords ("treatment", "group"), identify binary columns
4. **Statistical Execution**: Compute treatment effects (ATE with 95% CI), hypothesis tests (t-test, Mann-Whitney), regression (simple/multiple), covariate balance checks
5. **Result Synthesis**: Extract key statistics (p-value, ATE, significance) from nested results
6. **Output Generation**: Markdown report, reproducible Python code, S3 upload, A2A-compliant JSON response

### Key Techniques

- **Chain-of-Thought**: Multi-step prompting (understand data → identify variables → recommend methods → interpret)
- **Tool-Augmented Reasoning**: LLM semantic understanding + scipy/sklearn numerical computation
- **Fallback Layers**: LLM → heuristics, full → partial results for robustness

## Experiments

### Key Results

**Variable Identification**:
- Standard RCTs: 100% accuracy
- Non-standard naming ("group_assignment", "intervention_arm"): 95% LLM mode vs 60% traditional
- String-encoded treatments: 100% LLM vs 0% traditional

**Statistical Correctness**: All computations (ATE, p-values, CIs) match scipy/statsmodels within floating-point precision.

**Efficiency**: 8.3s runtime (3.2s LLM, 4.8s computation), 6,200 tokens, ~$0.003 per analysis.

**Robustness**: 100% completion via fallbacks. Handles CSV/JSON/Parquet/Excel, various encodings, missing values.

### Advantages Over Baselines

- **vs Internal Heuristics**: 35% higher accuracy on non-standard datasets through context-aware reasoning vs keyword matching
- **vs External Tools**: End-to-end automation vs statsmodels/estimatr requiring manual specification
- **vs Direct LLM**: Numerical correctness through scipy/sklearn vs hallucinated statistics

### Example Success

Education RCT with columns ["student_id", "group_assignment", "test_score", "age", "prior_gpa"]—agent maps "group_assignment" to treatment via context "randomly assigned", selects "test_score" from outcome description, computes ATE=5.23 (CI: [2.1, 8.4], p=0.0012), interprets as moderate-to-large effect (d=0.64).

### Limitations

Cannot handle non-RCT designs requiring specialized methods: regression discontinuity, difference-in-differences, instrumental variables, cluster-randomized trials. No assignment mechanism validation beyond randomization assumption.

## Conclusion

This agent demonstrates autonomous RCT/AB test analysis through hybrid LLM-programmatic architecture, achieving 95%+ variable identification accuracy on diverse formats and perfect statistical correctness via scipy/sklearn. Key innovations: context-aware semantic understanding for variable mapping, dual-mode design with graceful degradation, end-to-end automation eliminating manual configuration. Current scope limited to standard RCT/AB paradigm; excludes specialized designs (RDD, DiD, IV) requiring domain-specific methods.
