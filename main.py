#!/usr/bin/env python3
"""
Main entry point for White Agent RCT Analysis.

This script provides a simple interface to run the White Agent on input tests.
By default, it processes the latest test available. You can also specify a
specific test index using the --test-index argument.
"""

import argparse
import sys
from pathlib import Path
import logging
import os

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Environment variables will be loaded from shell environment only.\n")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from white_agent import WhiteAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_latest_test(inputs_dir: Path) -> int:
    """Find the latest test index in the inputs directory.

    Args:
        inputs_dir: Path to inputs directory

    Returns:
        Latest test index number

    Raises:
        FileNotFoundError: If no test directories are found
    """
    if not inputs_dir.exists():
        raise FileNotFoundError(f"Inputs directory not found: {inputs_dir}")

    test_indices = []
    for item in inputs_dir.iterdir():
        if item.is_dir() and item.name.startswith("test_"):
            try:
                index = int(item.name.split("_")[1])
                test_indices.append(index)
            except (IndexError, ValueError):
                continue

    if not test_indices:
        raise FileNotFoundError(f"No test directories found in {inputs_dir}")

    return max(test_indices)


def list_available_tests(inputs_dir: Path) -> list:
    """List all available test indices.

    Args:
        inputs_dir: Path to inputs directory

    Returns:
        Sorted list of test indices
    """
    if not inputs_dir.exists():
        return []

    test_indices = []
    for item in inputs_dir.iterdir():
        if item.is_dir() and item.name.startswith("test_"):
            try:
                index = int(item.name.split("_")[1])
                test_indices.append(index)
            except (IndexError, ValueError):
                continue

    return sorted(test_indices)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="White Agent - RCT Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze the latest test
  python main.py

  # Analyze a specific test
  python main.py --test-index 1

  # Use custom directories
  python main.py --inputs-dir my_inputs --results-dir my_results

  # List available tests
  python main.py --list

Environment Variables:
  GEMINI_API_KEY          API key for Gemini LLM (optional)
  WHITE_AGENT_INPUTS_DIR  Default inputs directory (default: inputs)
  WHITE_AGENT_RESULTS_DIR Default results directory (default: results)
        """
    )

    parser.add_argument(
        "--test-index",
        type=int,
        help="Test index to analyze (e.g., 1 for test_1). If not specified, analyzes the latest test."
    )

    parser.add_argument(
        "--inputs-dir",
        default=os.getenv("WHITE_AGENT_INPUTS_DIR", "inputs"),
        help="Directory containing test inputs (default: inputs or WHITE_AGENT_INPUTS_DIR env var)"
    )

    parser.add_argument(
        "--results-dir",
        default=os.getenv("WHITE_AGENT_RESULTS_DIR", "results"),
        help="Directory for results output (default: results or WHITE_AGENT_RESULTS_DIR env var)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available tests and exit"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Convert paths
    inputs_dir = Path(args.inputs_dir)
    results_dir = Path(args.results_dir)

    # List tests if requested
    if args.list:
        print(f"\nSearching for tests in: {inputs_dir}")
        tests = list_available_tests(inputs_dir)
        if tests:
            print(f"\nAvailable tests ({len(tests)}):")
            for test_idx in tests:
                test_path = inputs_dir / f"test_{test_idx}"
                print(f"  - test_{test_idx} ({test_path})")
        else:
            print("\nNo tests found.")
            print(f"\nCreate a test directory: mkdir -p {inputs_dir}/test_1")
            print("Then add context.txt and data.csv files to the directory.")
        return 0

    # Determine test index
    if args.test_index is not None:
        test_index = args.test_index
        logger.info(f"Using specified test index: {test_index}")
    else:
        try:
            test_index = find_latest_test(inputs_dir)
            logger.info(f"Auto-detected latest test index: {test_index}")
        except FileNotFoundError as e:
            print(f"\nError: {e}")
            print(f"\nNo tests found in {inputs_dir}")
            print("\nTo create a test:")
            print(f"  mkdir -p {inputs_dir}/test_1")
            print(f"  # Add context.txt and data.csv to {inputs_dir}/test_1/")
            print("\nThen run:")
            print("  python main.py")
            return 1

    # Check if Gemini API key is available
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        logger.info("Gemini API key found - will use LLM for report generation")
    else:
        logger.warning("No Gemini API key found - will use template-based reports")
        logger.warning("To use LLM-powered reports, set GEMINI_API_KEY in .env file")

    # Print banner
    print("\n" + "=" * 70)
    print("White Agent - RCT Analysis")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Inputs directory:  {inputs_dir}")
    print(f"  Results directory: {results_dir}")
    print(f"  Test index:        {test_index}")
    print(f"  LLM mode:          {'Gemini API' if gemini_api_key else 'Template-based'}")
    print()

    # Initialize agent
    try:
        logger.info("Initializing White Agent...")
        agent = WhiteAgent(
            inputs_dir=str(inputs_dir),
            results_dir=str(results_dir),
            gemini_api_key=gemini_api_key
        )
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}", exc_info=True)
        return 1

    # Process test
    try:
        logger.info(f"Processing test_{test_index}...")
        print(f"Analyzing test_{test_index}...\n")

        results = agent.process_test(test_index)

        # Print results
        print("\n" + "=" * 70)
        print("Analysis Complete!")
        print("=" * 70)

        print(f"\nResults saved to: {results['output_dir']}")
        print(f"Test index: {results['test_index']}")
        print(f"Result version: {results['result_version']}")

        summary = results['analysis_summary']
        print(f"\nQuick Summary:")
        print(f"  Sample size:               {summary['sample_size']}")
        print(f"  Average Treatment Effect:  {summary['treatment_effect']:.4f}")
        print(f"  p-value:                   {summary['p_value']:.4f}")
        print(f"  Statistically significant: {summary['statistically_significant']}")

        print(f"\nOutput Files:")
        output_dir = Path(results['output_dir'])
        print(f"  Report (Markdown): {output_dir}/report/analysis_report.md")
        print(f"  Results (JSON):    {output_dir}/report/results.json")
        print(f"  Analysis Code:     {output_dir}/code/analysis.py")
        print(f"  Data Copy:         {output_dir}/data_source/{results['data_file']}")
        print(f"  Metadata:          {output_dir}/metadata.json")

        print("\nNext Steps:")
        print(f"  View report:  cat {output_dir}/report/analysis_report.md")
        print(f"  Run analysis: python {output_dir}/code/analysis.py")
        print()

        return 0

    except FileNotFoundError as e:
        logger.error(f"Test not found: {e}")
        print(f"\nError: Test directory not found")
        print(f"Expected location: {inputs_dir}/test_{test_index}/")
        print(f"\nCreate the test directory and add:")
        print(f"  - context.txt (or .md) with experiment description")
        print(f"  - data.csv (or .json/.parquet/.xlsx) with experimental data")
        return 1

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\nError: Analysis failed - {e}")
        print("\nFor detailed error information, run with --verbose flag:")
        print(f"  python main.py --test-index {test_index} --verbose")
        return 1


if __name__ == "__main__":
    sys.exit(main())
