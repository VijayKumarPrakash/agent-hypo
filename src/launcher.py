"""AgentBeats launcher for White Agent.

This script provides the A2A protocol interface for the White Agent,
allowing it to be integrated into the AgentBeats platform and communicate
with other agents like the Green Agent orchestrator.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any
import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load from project root .env file
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv not installed, will use shell environment

# Add parent directory to path to import white_agent
sys.path.insert(0, str(Path(__file__).parent))

from white_agent.unified_agent import UnifiedWhiteAgent


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhiteAgentLauncher:
    """Launcher for White Agent with A2A protocol support.

    Automatically uses LLM-powered mode when GEMINI_API_KEY is available,
    or falls back to traditional mode otherwise.
    """

    def __init__(
        self,
        inputs_dir: str = "inputs",
        results_dir: str = "results",
        agent_host: str = "0.0.0.0",
        agent_port: int = 8001,
        launcher_host: str = "0.0.0.0",
        launcher_port: int = 8000,
        force_mode: str = None
    ):
        """Initialize the launcher.

        Args:
            inputs_dir: Directory containing test inputs
            results_dir: Directory for results output
            agent_host: Host for A2A agent communication
            agent_port: Port for A2A agent communication
            launcher_host: Host for launcher control
            launcher_port: Port for launcher control
            force_mode: Force specific analysis mode ('llm', 'traditional', or None for auto)
        """
        self.inputs_dir = inputs_dir
        self.results_dir = results_dir
        self.agent_host = agent_host
        self.agent_port = agent_port
        self.launcher_host = launcher_host
        self.launcher_port = launcher_port

        # Initialize the White Agent with UnifiedWhiteAgent (auto-detects mode)
        self.agent = UnifiedWhiteAgent(
            inputs_dir=inputs_dir,
            results_dir=results_dir,
            force_mode=force_mode
        )

        mode_type = "LLM-powered" if self.agent.is_llm_powered else "Traditional"
        logger.info(f"White Agent Launcher initialized in {mode_type} mode")
        logger.info(f"Agent endpoint: {agent_host}:{agent_port}")
        logger.info(f"Launcher endpoint: {launcher_host}:{launcher_port}")

    def handle_a2a_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming A2A protocol requests.

        Args:
            request: A2A request dictionary

        Returns:
            A2A response dictionary
        """
        logger.info(f"Received A2A request: {request}")
        return self.agent.handle_a2a_message(request)

    def handle_reset(self) -> Dict[str, Any]:
        """Handle reset signal from AgentBeats platform.

        Returns:
            Reset acknowledgment response
        """
        logger.info("Received reset signal")
        self.agent.reset()
        return {
            "status": "success",
            "message": "White Agent reset successfully"
        }

    def start_server(self):
        """Start the A2A protocol server.

        This would typically use FastAPI, Flask, or another web framework
        to expose the A2A endpoints. For now, we provide a simple interface.
        """
        try:
            from fastapi import FastAPI, Request
            from fastapi.responses import JSONResponse
            import uvicorn

            app = FastAPI(title="White Agent A2A Server")

            @app.post("/a2a/analyze")
            async def analyze_endpoint(request: Request):
                """A2A endpoint for analysis requests."""
                body = await request.json()
                response = self.handle_a2a_request(body)
                return JSONResponse(content=response)

            @app.get("/a2a/status")
            async def status_endpoint():
                """A2A endpoint for status checks."""
                response = self.agent.handle_a2a_message({"action": "get_status"})
                return JSONResponse(content=response)

            @app.post("/a2a/reset")
            async def reset_endpoint():
                """Launcher endpoint for reset signals."""
                response = self.handle_reset()
                return JSONResponse(content=response)

            @app.get("/health")
            async def health_endpoint():
                """Health check endpoint."""
                return JSONResponse(content={"status": "healthy"})

            logger.info(f"Starting White Agent A2A server on {self.agent_host}:{self.agent_port}")
            uvicorn.run(
                app,
                host=self.agent_host,
                port=self.agent_port,
                log_level="info"
            )

        except ImportError:
            logger.error("FastAPI and uvicorn are required for server mode")
            logger.error("Install with: pip install fastapi uvicorn")
            logger.info("Running in standalone mode instead")
            self.run_standalone()

    def run_standalone(self):
        """Run in standalone mode without server (for testing/development)."""
        logger.info("Running in standalone mode")
        logger.info("Use agent.process_test(test_index) to analyze tests")

        # Interactive mode
        print("\nWhite Agent - Standalone Mode")
        print("=" * 50)
        print("\nCommands:")
        print("  analyze <test_index>  - Analyze a test")
        print("  status                - Check agent status")
        print("  reset                 - Reset agent")
        print("  quit                  - Exit")
        print()

        while True:
            try:
                command = input("> ").strip().split()

                if not command:
                    continue

                if command[0] == "quit":
                    break

                elif command[0] == "analyze":
                    if len(command) < 2:
                        print("Error: Please provide test index")
                        continue

                    try:
                        test_index = int(command[1])
                        print(f"\nAnalyzing test_{test_index}...")
                        result = self.agent.process_test(test_index)
                        print("\nAnalysis complete!")
                        print(json.dumps(result, indent=2))
                    except Exception as e:
                        print(f"Error: {e}")

                elif command[0] == "status":
                    response = self.agent.handle_a2a_message({"action": "get_status"})
                    print(json.dumps(response, indent=2))

                elif command[0] == "reset":
                    response = self.handle_reset()
                    print(json.dumps(response, indent=2))

                else:
                    print(f"Unknown command: {command[0]}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point for the launcher."""
    parser = argparse.ArgumentParser(
        description="White Agent Launcher for AgentBeats"
    )

    parser.add_argument(
        "--inputs-dir",
        default="inputs",
        help="Directory containing test inputs (default: inputs)"
    )

    parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory for results output (default: results)"
    )

    parser.add_argument(
        "--agent-host",
        default="0.0.0.0",
        help="Host for A2A agent communication (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--agent-port",
        type=int,
        default=8001,
        help="Port for A2A agent communication (default: 8001)"
    )

    parser.add_argument(
        "--launcher-host",
        default="0.0.0.0",
        help="Host for launcher control (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--launcher-port",
        type=int,
        default=8000,
        help="Port for launcher control (default: 8000)"
    )

    parser.add_argument(
        "--mode",
        choices=["server", "standalone"],
        default="standalone",
        help="Run mode: server (A2A protocol) or standalone (interactive)"
    )

    parser.add_argument(
        "--analysis-mode",
        choices=["auto", "llm", "traditional"],
        default="auto",
        help="Analysis mode: 'auto' (default, auto-detect), 'llm' (force LLM), or 'traditional' (force traditional)"
    )

    args = parser.parse_args()

    # Determine force mode
    force_mode = None if args.analysis_mode == "auto" else args.analysis_mode

    launcher = WhiteAgentLauncher(
        inputs_dir=args.inputs_dir,
        results_dir=args.results_dir,
        agent_host=args.agent_host,
        agent_port=args.agent_port,
        launcher_host=args.launcher_host,
        launcher_port=args.launcher_port,
        force_mode=force_mode
    )

    if args.mode == "server":
        launcher.start_server()
    else:
        launcher.run_standalone()


if __name__ == "__main__":
    main()
