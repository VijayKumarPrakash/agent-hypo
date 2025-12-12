"""Data loading utilities for White Agent."""

import json
from pathlib import Path
from typing import Tuple
import pandas as pd
import logging

from .utils import identify_data_file, identify_context_file


logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading of test data and context files."""

    def load_test_data(self, test_dir: Path) -> Tuple[str, pd.DataFrame, Path]:
        """Load test context and data from a test directory.

        Args:
            test_dir: Path to test directory (e.g., inputs/test_1)

        Returns:
            Tuple of (context_text, data_dataframe, data_file_path)

        Raises:
            FileNotFoundError: If required files are missing
            ValueError: If files cannot be parsed
        """
        # Load context file
        context_path = identify_context_file(test_dir)
        logger.info(f"Loading context from {context_path}")

        with open(context_path, 'r', encoding='utf-8') as f:
            context = f.read()

        # Load data file
        data_path = identify_data_file(test_dir)
        logger.info(f"Loading data from {data_path}")

        data_df = self._load_data_file(data_path)

        logger.info(f"Loaded data with shape {data_df.shape}")

        return context, data_df, data_path

    def _load_data_file(self, file_path: Path) -> pd.DataFrame:
        """Load data file based on extension.

        Args:
            file_path: Path to data file

        Returns:
            DataFrame containing the data

        Raises:
            ValueError: If file format is unsupported or cannot be parsed
        """
        suffix = file_path.suffix.lower()

        try:
            if suffix == '.csv':
                return pd.read_csv(file_path)

            elif suffix == '.json':
                # Try to read as records-oriented JSON
                with open(file_path, 'r') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    # Try to convert dict to DataFrame
                    return pd.DataFrame(data)
                else:
                    raise ValueError(f"Unsupported JSON structure in {file_path}")

            elif suffix == '.parquet':
                return pd.read_parquet(file_path)

            elif suffix == '.xlsx':
                return pd.read_excel(file_path)

            else:
                raise ValueError(f"Unsupported file format: {suffix}")

        except Exception as e:
            raise ValueError(f"Failed to load data from {file_path}: {str(e)}")
