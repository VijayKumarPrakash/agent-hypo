"""Unified agent that automatically selects between traditional and LLM-powered modes."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .agent import WhiteAgent
from .llm_agent import LLMWhiteAgent


logger = logging.getLogger(__name__)


class UnifiedWhiteAgent:
    """Unified agent that automatically uses LLM mode when API key is available.

    This wrapper provides a single interface that:
    - Uses LLM-powered mode when Gemini API key is available
    - Falls back to traditional mode when API key is not available
    - Allows explicit mode selection via parameter
    """

    def __init__(
        self,
        inputs_dir: str = "inputs",
        results_dir: str = "results",
        gemini_api_key: Optional[str] = None,
        force_mode: Optional[str] = None
    ):
        """Initialize the unified agent.

        Args:
            inputs_dir: Path to inputs directory
            results_dir: Path to results directory
            gemini_api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            force_mode: Force specific mode ("llm" or "traditional"), or None for auto
        """
        self.inputs_dir = inputs_dir
        self.results_dir = results_dir
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        # Determine which mode to use
        if force_mode == "traditional":
            self.mode = "traditional"
            self.agent = WhiteAgent(
                inputs_dir=inputs_dir,
                results_dir=results_dir,
                gemini_api_key=self.gemini_api_key
            )
            logger.info("Using traditional analysis mode (forced)")

        elif force_mode == "llm":
            if not self.gemini_api_key:
                raise ValueError(
                    "LLM mode requires Gemini API key. "
                    "Set GEMINI_API_KEY environment variable or provide gemini_api_key parameter."
                )
            self.mode = "llm"
            self.agent = LLMWhiteAgent(
                inputs_dir=inputs_dir,
                results_dir=results_dir,
                gemini_api_key=self.gemini_api_key
            )
            logger.info("Using LLM-powered analysis mode (forced)")

        else:
            # Auto-detect mode based on API key availability
            if self.gemini_api_key:
                self.mode = "llm"
                self.agent = LLMWhiteAgent(
                    inputs_dir=inputs_dir,
                    results_dir=results_dir,
                    gemini_api_key=self.gemini_api_key
                )
                logger.info("Using LLM-powered analysis mode (auto-detected)")
            else:
                self.mode = "traditional"
                self.agent = WhiteAgent(
                    inputs_dir=inputs_dir,
                    results_dir=results_dir,
                    gemini_api_key=None
                )
                logger.warning(
                    "No Gemini API key found. Using traditional analysis mode. "
                    "For enhanced LLM-powered analysis, set GEMINI_API_KEY environment variable."
                )

    def process_test(self, test_index: int) -> Dict[str, Any]:
        """Process a test using the selected analysis mode.

        Args:
            test_index: The test number

        Returns:
            Dictionary containing analysis results and output paths
        """
        logger.info(f"Processing test_{test_index} using {self.mode} mode")
        return self.agent.process_test(test_index)

    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A messages.

        Args:
            message: A2A message dictionary

        Returns:
            Response dictionary
        """
        return self.agent.handle_a2a_message(message)

    def reset(self):
        """Reset agent state."""
        self.agent.reset()

    @property
    def is_llm_powered(self) -> bool:
        """Check if using LLM-powered mode.

        Returns:
            True if using LLM mode, False if using traditional mode
        """
        return self.mode == "llm"
