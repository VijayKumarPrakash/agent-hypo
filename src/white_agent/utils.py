"""Utility functions for White Agent."""

from pathlib import Path
from typing import List
import re


def get_next_result_version(results_dir: Path, test_index: int) -> int:
    """Get the next available version number for a test result.

    Args:
        results_dir: Base results directory
        test_index: Test index number

    Returns:
        Next available version number (1-indexed)
    """
    if not results_dir.exists():
        return 1

    # Find all existing result directories for this test
    pattern = re.compile(rf"result_{test_index}_(\d+)")
    versions = []

    for item in results_dir.iterdir():
        if item.is_dir():
            match = pattern.match(item.name)
            if match:
                versions.append(int(match.group(1)))

    # Return next version number
    return max(versions, default=0) + 1


def ensure_directory_structure(result_dir: Path) -> None:
    """Create the standard result directory structure.

    Creates:
        - data_source/
        - code/
        - report/

    Args:
        result_dir: Base result directory path
    """
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / "data_source").mkdir(exist_ok=True)
    (result_dir / "code").mkdir(exist_ok=True)
    (result_dir / "report").mkdir(exist_ok=True)


def find_files_by_extension(directory: Path, extensions: List[str]) -> List[Path]:
    """Find all files with specified extensions in a directory.

    Args:
        directory: Directory to search
        extensions: List of file extensions (e.g., ['.csv', '.json'])

    Returns:
        List of matching file paths
    """
    files = []
    for ext in extensions:
        files.extend(directory.glob(f"*{ext}"))
    return files


def identify_data_file(directory: Path) -> Path:
    """Identify the data file in a test directory.

    Looks for common data formats: .csv, .json, .parquet, .xlsx

    Args:
        directory: Test directory to search

    Returns:
        Path to the data file

    Raises:
        FileNotFoundError: If no data file is found
        ValueError: If multiple data files are found
    """
    data_extensions = ['.csv', '.json', '.parquet', '.xlsx']
    data_files = find_files_by_extension(directory, data_extensions)

    if not data_files:
        raise FileNotFoundError(
            f"No data file found in {directory}. "
            f"Expected one of: {', '.join(data_extensions)}"
        )

    if len(data_files) > 1:
        raise ValueError(
            f"Multiple data files found in {directory}: {[f.name for f in data_files]}. "
            "Please ensure only one data file is present."
        )

    return data_files[0]


def identify_context_file(directory: Path) -> Path:
    """Identify the context/background text file in a test directory.

    Looks for .txt or .md files containing experiment context.

    Args:
        directory: Test directory to search

    Returns:
        Path to the context file

    Raises:
        FileNotFoundError: If no context file is found
        ValueError: If multiple context files are found
    """
    context_extensions = ['.txt', '.md']
    context_files = find_files_by_extension(directory, context_extensions)

    if not context_files:
        raise FileNotFoundError(
            f"No context file found in {directory}. "
            f"Expected one of: {', '.join(context_extensions)}"
        )

    if len(context_files) > 1:
        raise ValueError(
            f"Multiple context files found in {directory}: {[f.name for f in context_files]}. "
            "Please ensure only one context file is present."
        )

    return context_files[0]
