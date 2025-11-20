"""Consolidated utility functions for file operations, paths, and dates."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional


# ============================================================================
# File Operations
# ============================================================================


def ensure_directory(path: str | Path) -> None:
    """
    Ensure directory exists, create if necessary.

    Args:
        path: Directory path or file path (directory will be extracted)
    """
    path_obj = Path(path)
    directory = path_obj.parent if path_obj.suffix else path_obj
    directory.mkdir(parents=True, exist_ok=True)


def atomic_write_json(path: str | Path, data: Any, indent: int = 2) -> None:
    """
    Atomically write JSON data to file using temporary file and rename.

    Args:
        path: Target file path
        data: Data to serialize as JSON
        indent: JSON indentation level
    """
    path_obj = Path(path)
    ensure_directory(path_obj.parent)

    temp_path = path_obj.with_suffix(path_obj.suffix + ".tmp")

    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

    if path_obj.exists():
        path_obj.unlink()

    temp_path.rename(path_obj)


def append_jsonl(path: str | Path, data: dict[str, Any]) -> None:
    """
    Append JSON line to file.

    Args:
        path: Target JSONL file path
        data: Dictionary to append as JSON line
    """
    path_obj = Path(path)
    ensure_directory(path_obj.parent)

    with open(path_obj, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def read_json(path: str | Path) -> Any:
    """
    Read JSON from file.

    Args:
        path: JSON file path

    Returns:
        Deserialized JSON data
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """
    Read all lines from JSONL file.

    Args:
        path: JSONL file path

    Returns:
        List of dictionaries
    """
    path_obj = Path(path)

    if not path_obj.exists():
        return []

    lines = []
    with open(path_obj, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(json.loads(line))

    return lines


# ============================================================================
# Path Resolution
# ============================================================================


class PathResolver:
    """Centralizes path resolution for data files."""

    def __init__(self, base_dir: Optional[str | Path] = None):
        """
        Initialize path resolver.

        Args:
            base_dir: Base directory for data files (defaults to ./data)
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "data"

    @property
    def tasks_path(self) -> Path:
        """Get path to tasks.json."""
        return self.base_dir / "tasks.json"

    @property
    def state_path(self) -> Path:
        """Get path to state.json."""
        return self.base_dir / "state.json"

    @property
    def plans_dir(self) -> Path:
        """Get path to plans directory."""
        return self.base_dir / "plans"

    @property
    def logs_dir(self) -> Path:
        """Get path to logs directory."""
        return self.base_dir / "logs"

    def get_plan_path(self, date_str: str) -> Path:
        """
        Get path for plan file for specific date.

        Args:
            date_str: ISO date string (YYYY-MM-DD)

        Returns:
            Path to plan file
        """
        return self.plans_dir / f"plan_{date_str}.json"

    def get_log_path(self, date_str: str) -> Path:
        """
        Get path for log file for specific date.

        Args:
            date_str: ISO date string (YYYY-MM-DD)

        Returns:
            Path to log file
        """
        return self.logs_dir / f"actual_{date_str}.jsonl"

    @staticmethod
    def get_config_path() -> Path:
        """
        Get path to configuration file.

        Returns:
            Path to blocks_config.yaml
        """
        infrastructure_dir = Path(__file__).parent.parent
        return infrastructure_dir / "config" / "blocks_config.yaml"

    def ensure_directories(self) -> None:
        """Create all necessary directories."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def resolve(self, custom_path: Optional[str | Path], default_path: Path) -> Path:
        """
        Resolve path with custom override support.

        Args:
            custom_path: Custom path override (optional)
            default_path: Default path if no override

        Returns:
            Resolved path
        """
        return Path(custom_path) if custom_path else default_path


# ============================================================================
# Date Utilities
# ============================================================================


def get_current_date() -> str:
    """
    Get current date in ISO format.

    Returns:
        ISO date string (YYYY-MM-DD)
    """
    return date.today().isoformat()


def parse_date(date_str: str | None) -> str:
    """
    Parse date string or return current date.

    Args:
        date_str: Date string in ISO format or None

    Returns:
        ISO date string

    Raises:
        ValueError: If date string is invalid
    """
    if date_str is None or date_str.lower() == "today":
        return get_current_date()

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD") from e


def format_date(date_obj: date) -> str:
    """
    Format date object to ISO string.

    Args:
        date_obj: Date object

    Returns:
        ISO date string (YYYY-MM-DD)
    """
    return date_obj.isoformat()
