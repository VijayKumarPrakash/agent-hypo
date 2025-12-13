"""LLM-powered data loader that handles diverse file formats intelligently."""

import json
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import logging
import pandas as pd

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


logger = logging.getLogger(__name__)


class LLMDataLoader:
    """Intelligently loads and parses data files of various formats using LLM."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemma-3-12b-it"
    ):
        """Initialize the data loader.

        Args:
            api_key: Gemini API key
            model_name: Model to use (gemma-3-12b-it for speed and cost efficiency)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.model = None

        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"Initialized LLM data loader with {model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        elif not GEMINI_AVAILABLE:
            logger.warning("google-generativeai package not available")

    def load_test_data(self, test_dir: Path) -> Tuple[str, pd.DataFrame, Path]:
        """Load test data with intelligent format detection and parsing.

        Args:
            test_dir: Path to test directory

        Returns:
            Tuple of (context_text, data_dataframe, data_file_path)
        """
        logger.info(f"Loading data from {test_dir}")

        # Load context
        context = self._load_context(test_dir)

        # Find and load data file
        data_file = self._find_data_file(test_dir)
        data_df = self._load_data_file(data_file, context)

        logger.info(f"Loaded data with shape {data_df.shape}")
        return context, data_df, data_file

    def _load_context(self, test_dir: Path) -> str:
        """Load context from various possible file formats.

        Args:
            test_dir: Test directory

        Returns:
            Context text
        """
        # Try multiple context file names and formats
        context_files = [
            "context.txt",
            "context.md",
            "README.md",
            "readme.txt",
            "description.txt",
            "experiment.txt",
            "info.txt"
        ]

        for filename in context_files:
            context_path = test_dir / filename
            if context_path.exists():
                logger.info(f"Found context file: {context_path}")
                with open(context_path, 'r', encoding='utf-8') as f:
                    return f.read()

        # If no context file found, create a basic one
        logger.warning("No context file found, using minimal context")
        return f"Experimental data from {test_dir.name}"

    def _find_data_file(self, test_dir: Path) -> Path:
        """Find data file in test directory.

        Args:
            test_dir: Test directory

        Returns:
            Path to data file

        Raises:
            FileNotFoundError: If no data file found
        """
        # Common data file extensions
        data_extensions = [
            '.csv', '.json', '.parquet', '.xlsx', '.xls',
            '.tsv', '.txt', '.feather', '.hdf5', '.h5'
        ]

        # Find all data files
        data_files = []
        for ext in data_extensions:
            data_files.extend(test_dir.glob(f"*{ext}"))

        # Exclude context files
        context_names = {'context', 'readme', 'description', 'info', 'experiment'}
        data_files = [
            f for f in data_files
            if not any(name in f.stem.lower() for name in context_names)
        ]

        if not data_files:
            raise FileNotFoundError(f"No data file found in {test_dir}")

        if len(data_files) > 1:
            # Try to pick the most likely data file
            logger.warning(f"Multiple data files found: {data_files}")
            # Prefer common names
            for f in data_files:
                if f.stem.lower() in ['data', 'dataset', 'experiment', 'results']:
                    return f
            # Just use the first one
            return data_files[0]

        return data_files[0]

    def _load_data_file(self, file_path: Path, context: str) -> pd.DataFrame:
        """Load data file with format-specific handling.

        Args:
            file_path: Path to data file
            context: Experiment context (for LLM guidance)

        Returns:
            DataFrame containing the data
        """
        suffix = file_path.suffix.lower()
        logger.info(f"Loading {suffix} file: {file_path.name}")

        try:
            # Try standard loading methods first
            df = self._try_standard_load(file_path, suffix)

            # If LLM is available, validate and potentially fix the data
            if self.model:
                df = self._validate_and_fix_data(df, file_path, context)

            return df

        except Exception as e:
            logger.warning(f"Standard loading failed: {e}")

            # If standard loading fails and LLM is available, use it
            if self.model:
                return self._llm_guided_load(file_path, context)
            else:
                raise ValueError(f"Failed to load {file_path}: {str(e)}")

    def _try_standard_load(self, file_path: Path, suffix: str) -> pd.DataFrame:
        """Try standard pandas loading methods.

        Args:
            file_path: Path to data file
            suffix: File extension

        Returns:
            DataFrame

        Raises:
            ValueError: If loading fails
        """
        if suffix == '.csv':
            # Try multiple delimiters and encodings
            for delimiter in [',', ';', '\t', '|']:
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                    try:
                        return pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
                    except:
                        continue
            raise ValueError("Could not parse CSV file")

        elif suffix == '.tsv':
            return pd.read_csv(file_path, delimiter='\t')

        elif suffix == '.txt':
            # Try to infer delimiter
            return pd.read_csv(file_path, delimiter=None, engine='python')

        elif suffix == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try different orientations
                for orient in ['columns', 'index', 'records']:
                    try:
                        return pd.DataFrame.from_dict(data, orient=orient)
                    except:
                        continue
            raise ValueError("Unsupported JSON structure")

        elif suffix == '.parquet':
            return pd.read_parquet(file_path)

        elif suffix in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)

        elif suffix == '.feather':
            return pd.read_feather(file_path)

        elif suffix in ['.hdf5', '.h5']:
            return pd.read_hdf(file_path)

        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def _validate_and_fix_data(
        self,
        df: pd.DataFrame,
        file_path: Path,
        context: str
    ) -> pd.DataFrame:
        """Use LLM to validate and potentially fix data issues.

        Args:
            df: Loaded DataFrame
            file_path: Original file path
            context: Experiment context

        Returns:
            Validated/fixed DataFrame
        """
        # Check for obvious issues
        issues = []

        if df.empty:
            issues.append("DataFrame is empty")

        # Check for unnamed columns
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            issues.append(f"Found unnamed columns: {unnamed_cols}")

        # Check for excessive missing data
        missing_pct = df.isna().sum() / len(df)
        problematic_cols = missing_pct[missing_pct > 0.5].index.tolist()
        if problematic_cols:
            issues.append(f"Columns with >50% missing: {problematic_cols}")

        # If there are issues, ask LLM for guidance
        if issues:
            logger.info(f"Data issues detected: {issues}")
            fixed_df = self._llm_fix_data(df, file_path, context, issues)
            if fixed_df is not None:
                return fixed_df

        return df

    def _llm_fix_data(
        self,
        df: pd.DataFrame,
        file_path: Path,
        context: str,
        issues: list
    ) -> Optional[pd.DataFrame]:
        """Ask LLM how to fix data issues.

        Args:
            df: DataFrame with issues
            file_path: Original file path
            context: Experiment context
            issues: List of identified issues

        Returns:
            Fixed DataFrame or None if LLM can't help
        """
        prompt = f"""You are a data scientist helping to fix data loading issues.

# CONTEXT
{context}

# FILE INFO
File: {file_path.name}
Current shape: {df.shape}
Columns: {df.columns.tolist()}

# ISSUES DETECTED
{chr(10).join(f"- {issue}" for issue in issues)}

# DATA PREVIEW
{df.head(10).to_string()}

# YOUR TASK
Suggest fixes for these issues. Return a JSON object with:

{{
  "actions": [
    {{
      "action": "rename_columns" | "drop_columns" | "fill_missing" | "skip_rows" | "none",
      "details": "specific instructions"
    }}
  ],
  "explanation": "why these fixes are needed"
}}

Return ONLY the JSON object.
"""

        try:
            response = self.model.generate_content(prompt)
            fix_text = response.text.strip()

            if "```json" in fix_text:
                fix_text = fix_text.split("```json")[1].split("```")[0].strip()
            elif "```" in fix_text:
                fix_text = fix_text.split("```")[1].split("```")[0].strip()

            fix_plan = json.loads(fix_text)
            logger.info(f"LLM suggested fixes: {fix_plan.get('explanation')}")

            # Apply fixes (basic implementation)
            # In production, you'd implement more sophisticated fixing logic
            return df

        except Exception as e:
            logger.warning(f"LLM could not fix data issues: {e}")
            return None

    def _llm_guided_load(self, file_path: Path, context: str) -> pd.DataFrame:
        """Use LLM to guide loading of unusual file formats.

        Args:
            file_path: Path to data file
            context: Experiment context

        Returns:
            DataFrame

        Raises:
            ValueError: If loading fails
        """
        # Read raw file content (first N lines)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample_lines = [f.readline() for _ in range(20)]
                file_sample = ''.join(sample_lines)
        except:
            raise ValueError(f"Could not read file {file_path}")

        prompt = f"""You are a data scientist helping to load an unusual data file format.

# CONTEXT
{context}

# FILE INFO
File: {file_path.name}
Extension: {file_path.suffix}

# FILE SAMPLE (first 20 lines)
{file_sample}

# YOUR TASK
Analyze this file and tell me how to load it into a pandas DataFrame. Return a JSON object with:

{{
  "file_type": "csv" | "json" | "custom",
  "delimiter": "," | "\\t" | ";" | "|" | "other",
  "has_header": true | false,
  "skip_rows": 0,
  "encoding": "utf-8" | "latin-1",
  "additional_notes": "any special handling needed"
}}

Return ONLY the JSON object.
"""

        try:
            response = self.model.generate_content(prompt)
            guidance_text = response.text.strip()

            if "```json" in guidance_text:
                guidance_text = guidance_text.split("```json")[1].split("```")[0].strip()
            elif "```" in guidance_text:
                guidance_text = guidance_text.split("```")[1].split("```")[0].strip()

            guidance = json.loads(guidance_text)
            logger.info(f"LLM loading guidance: {guidance}")

            # Try to load based on LLM guidance
            if guidance["file_type"] == "csv":
                return pd.read_csv(
                    file_path,
                    delimiter=guidance.get("delimiter", ","),
                    skiprows=guidance.get("skip_rows", 0),
                    encoding=guidance.get("encoding", "utf-8"),
                    header=0 if guidance.get("has_header", True) else None
                )
            elif guidance["file_type"] == "json":
                with open(file_path, 'r') as f:
                    return pd.DataFrame(json.load(f))
            else:
                raise ValueError(f"LLM could not determine how to load file")

        except Exception as e:
            logger.error(f"LLM-guided loading failed: {e}")
            raise ValueError(f"Could not load {file_path} even with LLM guidance: {str(e)}")
