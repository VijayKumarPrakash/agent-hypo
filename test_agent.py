#!/usr/bin/env python3
"""Quick test script to verify White Agent installation and functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from white_agent import WhiteAgent


def test_agent():
    """Test basic agent functionality."""
    print("=" * 60)
    print("White Agent - Installation Test")
    print("=" * 60)
    print()

    # Initialize agent
    print("1. Initializing White Agent...")
    try:
        agent = WhiteAgent(
            inputs_dir="inputs",
            results_dir="results"
        )
        print("   ✓ Agent initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize agent: {e}")
        return False

    # Test A2A status message
    print("\n2. Testing A2A protocol (status message)...")
    try:
        response = agent.handle_a2a_message({"action": "get_status"})
        assert response["status"] == "success"
        assert response["agent_type"] == "white_agent"
        print("   ✓ A2A protocol working")
        print(f"   Capabilities: {', '.join(response['capabilities'])}")
    except Exception as e:
        print(f"   ✗ A2A protocol failed: {e}")
        return False

    # Check if example test exists
    print("\n3. Checking for example test data...")
    test_dir = Path("inputs/test_1")
    if not test_dir.exists():
        print(f"   ✗ Test directory not found: {test_dir}")
        return False

    context_file = test_dir / "context.txt"
    data_file = test_dir / "data.csv"

    if not context_file.exists():
        print(f"   ✗ Context file not found: {context_file}")
        return False

    if not data_file.exists():
        print(f"   ✗ Data file not found: {data_file}")
        return False

    print("   ✓ Example test data found")
    print(f"   Context: {context_file}")
    print(f"   Data: {data_file}")

    # Test analysis (optional - can be slow)
    run_analysis = input("\n4. Run full analysis on test_1? (y/n): ").lower().strip()

    if run_analysis == 'y':
        print("\n   Running analysis...")
        try:
            result = agent.process_test(1)
            print("   ✓ Analysis completed successfully!")
            print(f"\n   Results saved to: {result['output_dir']}")
            print(f"   Sample size: {result['analysis_summary']['sample_size']}")
            print(f"   Treatment effect: {result['analysis_summary']['treatment_effect']:.4f}")
            print(f"   p-value: {result['analysis_summary']['p_value']:.4f}")
            print(f"   Significant: {result['analysis_summary']['statistically_significant']}")

            print(f"\n   View the report:")
            print(f"   cat {result['output_dir']}/report/analysis_report.md")

        except Exception as e:
            print(f"   ✗ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("   Skipping full analysis")

    print("\n" + "=" * 60)
    print("Installation Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run: python src/launcher.py --mode standalone")
    print("  2. Type: analyze 1")
    print("  3. Read: QUICKSTART.md for more examples")
    print()

    return True


if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
