"""Example: Using the LLM-powered White Agent.

This script demonstrates how to use the new LLM-powered analysis mode
which can robustly handle diverse data formats and structures.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.white_agent import LLMWhiteAgent
from src.white_agent.unified_agent import UnifiedWhiteAgent


def example_1_basic_usage():
    """Example 1: Basic usage of LLM-powered agent."""
    print("="*60)
    print("Example 1: Basic LLM-Powered Analysis")
    print("="*60)

    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("Set it with: export GEMINI_API_KEY='your-key'")
        return

    # Initialize LLM-powered agent
    agent = LLMWhiteAgent(
        inputs_dir="inputs",
        results_dir="results",
        gemini_api_key=api_key
    )

    # Process a test
    print("\nProcessing test_1 with LLM-powered analysis...")
    results = agent.process_test(test_index=1)

    # Display results
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"Output directory: {results['output_dir']}")
    print(f"Experiment type: {results.get('experiment_type', 'N/A')}")
    print(f"Sample size: {results['analysis_summary']['sample_size']}")
    print(f"Treatment effect: {results['analysis_summary']['treatment_effect']:.4f}")
    print(f"P-value: {results['analysis_summary']['p_value']:.4f}")
    print(f"Significant: {results['analysis_summary']['statistically_significant']}")

    print(f"\nView full report: {results['output_dir']}/report/analysis_report.md")


def example_2_unified_agent():
    """Example 2: Using UnifiedWhiteAgent (auto-detects mode)."""
    print("\n" + "="*60)
    print("Example 2: Unified Agent (Auto-Mode Selection)")
    print("="*60)

    # UnifiedWhiteAgent automatically detects which mode to use
    agent = UnifiedWhiteAgent(
        inputs_dir="inputs",
        results_dir="results"
    )

    print(f"Agent mode: {'LLM-powered' if agent.is_llm_powered else 'Traditional'}")

    if not agent.is_llm_powered:
        print("\nNote: Using traditional mode because no API key found.")
        print("Set GEMINI_API_KEY to use LLM-powered mode.")
        return

    # Process test
    print("\nProcessing test_1...")
    results = agent.process_test(test_index=1)

    print(f"\nAnalysis saved to: {results['output_dir']}")


def example_3_model_configuration():
    """Example 3: Customizing LLM models for cost/performance."""
    print("\n" + "="*60)
    print("Example 3: Custom Model Configuration")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        return

    # Use cost-optimized hybrid approach: Gemma for data loading, Gemini 2.5 Flash for analysis
    agent = LLMWhiteAgent(
        inputs_dir="inputs",
        results_dir="results",
        gemini_api_key=api_key,
        analyzer_model="gemini-2.5-flash",    # Fast, high-quality analysis
        loader_model="gemma-3-12b-it",        # Cost-efficient for data loading
        report_model="gemini-2.5-flash"       # Fast, high-quality reports
    )

    print("Configured with hybrid model approach:")
    print(f"  Data loading: gemma-3-12b-it (cost-efficient)")
    print(f"  Analysis: gemini-2.5-flash (fast, high quality)")
    print(f"  Reports: gemini-2.5-flash (fast, high quality)")

    print("\nProcessing test_1...")
    results = agent.process_test(test_index=1)

    print(f"\nAnalysis complete: {results['output_dir']}")


def example_4_comparing_modes():
    """Example 4: Comparing traditional vs LLM-powered modes."""
    print("\n" + "="*60)
    print("Example 4: Comparing Traditional vs LLM Modes")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        return

    # Run both modes
    print("\nRunning traditional mode...")
    traditional_agent = UnifiedWhiteAgent(
        inputs_dir="inputs",
        results_dir="results",
        force_mode="traditional"
    )
    traditional_results = traditional_agent.process_test(test_index=1)

    print("\nRunning LLM-powered mode...")
    llm_agent = UnifiedWhiteAgent(
        inputs_dir="inputs",
        results_dir="results",
        force_mode="llm"
    )
    llm_results = llm_agent.process_test(test_index=1)

    # Compare results
    print("\n" + "="*60)
    print("COMPARISON")
    print("="*60)

    print("\nTraditional Mode:")
    print(f"  ATE: {traditional_results['analysis_summary']['treatment_effect']:.4f}")
    print(f"  P-value: {traditional_results['analysis_summary']['p_value']:.4f}")

    print("\nLLM-Powered Mode:")
    print(f"  ATE: {llm_results['analysis_summary']['treatment_effect']:.4f}")
    print(f"  P-value: {llm_results['analysis_summary']['p_value']:.4f}")
    print(f"  Experiment type: {llm_results.get('experiment_type', 'N/A')}")

    print("\nNote: Results should be very similar. The LLM mode provides")
    print("additional context and can handle more diverse data formats.")


def example_5_error_handling():
    """Example 5: Error handling and fallbacks."""
    print("\n" + "="*60)
    print("Example 5: Error Handling")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")

    # Example: Missing API key
    print("\nTrying to create LLM agent without API key...")
    try:
        agent = LLMWhiteAgent(
            inputs_dir="inputs",
            results_dir="results",
            gemini_api_key=None  # No API key
        )
    except ValueError as e:
        print(f"Expected error: {e}")

    # Example: UnifiedAgent handles this gracefully
    print("\nUsing UnifiedAgent without API key (auto-fallback)...")
    agent = UnifiedWhiteAgent(
        inputs_dir="inputs",
        results_dir="results",
        gemini_api_key=None
    )
    print(f"Agent mode: {'LLM-powered' if agent.is_llm_powered else 'Traditional'}")
    print("Successfully fell back to traditional mode!")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("LLM-POWERED WHITE AGENT EXAMPLES")
    print("="*60)

    # Check if test data exists
    test_dir = Path("inputs/test_1")
    if not test_dir.exists():
        print("\nERROR: No test data found at inputs/test_1")
        print("Please create test data first.")
        return

    print("\nThese examples demonstrate the LLM-powered analysis mode.")
    print("Make sure you have set GEMINI_API_KEY environment variable.")

    # Run examples
    try:
        example_1_basic_usage()
        example_2_unified_agent()
        example_3_model_configuration()
        example_4_comparing_modes()
        example_5_error_handling()

        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETE")
        print("="*60)
        print("\nCheck the results/ directory for output files.")
        print("See docs/LLM_POWERED_ANALYSIS.md for full documentation.")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
