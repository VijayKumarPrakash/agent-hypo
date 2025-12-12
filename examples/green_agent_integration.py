#!/usr/bin/env python3
"""
Example: How a Green Agent would interact with the White Agent via A2A protocol.

This demonstrates the A2A (Agent-to-Agent) communication pattern that would be
used in an AgentBeats multi-agent system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from white_agent import WhiteAgent


class MockGreenAgent:
    """
    A mock Green Agent (orchestrator) that triggers the White Agent.

    In a real AgentBeats deployment, this would be a separate process
    communicating over HTTP using the A2A protocol.
    """

    def __init__(self):
        """Initialize the Green Agent."""
        self.name = "Green Agent (Orchestrator)"
        print(f"{self.name} initialized")

    def trigger_white_agent_analysis(self, white_agent: WhiteAgent, test_index: int):
        """
        Trigger the White Agent to analyze a specific test.

        This simulates the A2A message flow:
        Green Agent -> White Agent: "Please analyze test X"
        White Agent -> Green Agent: "Here are the results"

        Args:
            white_agent: WhiteAgent instance to communicate with
            test_index: Test number to analyze
        """
        print(f"\n{self.name}: Requesting analysis of test_{test_index}")

        # Construct A2A message
        a2a_request = {
            "action": "analyze_test",
            "params": {
                "test_index": test_index
            }
        }

        print(f"{self.name}: Sending A2A message: {a2a_request}")

        # Send to White Agent
        response = white_agent.handle_a2a_message(a2a_request)

        # Process response
        if response["status"] == "success":
            print(f"{self.name}: ✓ Analysis successful!")
            results = response["results"]

            print(f"\n{self.name}: Received results:")
            print(f"  - Test index: {results['test_index']}")
            print(f"  - Result version: {results['result_version']}")
            print(f"  - Output directory: {results['output_dir']}")

            summary = results['analysis_summary']
            print(f"\n{self.name}: Analysis summary:")
            print(f"  - Sample size: {summary['sample_size']}")
            print(f"  - Treatment effect: {summary['treatment_effect']:.4f}")
            print(f"  - p-value: {summary['p_value']:.4f}")
            print(f"  - Statistically significant: {summary['statistically_significant']}")

            # Green Agent can now make decisions based on results
            self.evaluate_results(summary)

            return results
        else:
            print(f"{self.name}: ✗ Analysis failed: {response.get('error')}")
            return None

    def evaluate_results(self, summary: dict):
        """
        Green Agent evaluates the results and makes decisions.

        This is where the Green Agent (orchestrator) would decide:
        - Should we deploy this intervention?
        - Do we need more data?
        - Should we trigger other agents?
        - What should we report to stakeholders?

        Args:
            summary: Analysis summary from White Agent
        """
        print(f"\n{self.name}: Evaluating results...")

        ate = summary['treatment_effect']
        p_value = summary['p_value']
        significant = summary['statistically_significant']

        if significant and ate > 0:
            print(f"{self.name}: ✓ RECOMMENDATION: Deploy intervention")
            print(f"  Positive effect (ATE={ate:.4f}) is statistically significant")
        elif significant and ate < 0:
            print(f"{self.name}: ✗ RECOMMENDATION: Do NOT deploy")
            print(f"  Negative effect (ATE={ate:.4f}) is statistically significant")
        else:
            print(f"{self.name}: ⚠ RECOMMENDATION: Collect more data")
            print(f"  Effect not statistically significant (p={p_value:.4f})")

    def check_white_agent_status(self, white_agent: WhiteAgent):
        """Check if White Agent is ready."""
        print(f"\n{self.name}: Checking White Agent status...")

        a2a_request = {
            "action": "get_status"
        }

        response = white_agent.handle_a2a_message(a2a_request)

        if response["status"] == "success":
            print(f"{self.name}: White Agent is ready")
            print(f"  Type: {response['agent_type']}")
            print(f"  Capabilities: {', '.join(response['capabilities'])}")
            return True
        else:
            print(f"{self.name}: White Agent not ready")
            return False


def main():
    """Demonstrate Green Agent -> White Agent A2A communication."""
    print("=" * 70)
    print("A2A Communication Example: Green Agent -> White Agent")
    print("=" * 70)

    # Initialize White Agent
    print("\nInitializing White Agent...")
    white_agent = WhiteAgent(
        inputs_dir="inputs",
        results_dir="results"
    )
    print("White Agent ready")

    # Initialize Green Agent (orchestrator)
    print("\nInitializing Green Agent...")
    green_agent = MockGreenAgent()

    # Green Agent checks White Agent status
    if not green_agent.check_white_agent_status(white_agent):
        print("Cannot proceed - White Agent not available")
        return

    # Green Agent triggers analysis
    results = green_agent.trigger_white_agent_analysis(white_agent, test_index=1)

    if results:
        print(f"\n{green_agent.name}: Workflow complete!")
        print(f"Full results available at: {results['output_dir']}")

    print("\n" + "=" * 70)
    print("A2A Communication Example Complete")
    print("=" * 70)

    print("\nIn a real AgentBeats deployment:")
    print("  1. White Agent runs as HTTP server (port 8001)")
    print("  2. Green Agent sends HTTP POST to /a2a/analyze")
    print("  3. White Agent processes and responds with JSON")
    print("  4. Green Agent makes decisions based on response")
    print("\nRun White Agent in server mode:")
    print("  python src/launcher.py --mode server --agent-port 8001")


if __name__ == "__main__":
    main()
