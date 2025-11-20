"""Simplified configuration management using YAML only."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    """Application configuration loaded from YAML."""

    weekly_decay: float = 0.85
    laplace: float = 1.5
    ratio_bias_alpha: float = 1.2

    beta: float = 0.3
    gamma: float = 0.6

    urgent_threshold: float = 3.5
    support_threshold: float = 4.5
    support_budget: int = 1
    allow_support_preempt: bool = True

    blocks_per_day: int = 5
    work_start_time: str = "09:00"

    _raw_config: dict[str, Any] | None = None

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "Config":
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to blocks_config.yaml

        Returns:
            Config instance
        """
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(
            weekly_decay=data.get("weekly_decay", 0.85),
            laplace=data.get("laplace", 1.5),
            ratio_bias_alpha=data.get("ratio_bias_alpha", 1.2),
            beta=data.get("beta", 0.3),
            gamma=data.get("gamma", 0.6),
            urgent_threshold=data.get("urgent_threshold", 3.5),
            support_threshold=data.get("support_threshold", 4.5),
            support_budget=data.get("support_budget", 1),
            allow_support_preempt=data.get("allow_support_preempt", True),
            blocks_per_day=data.get("blocks_per_day", 5),
            work_start_time=data.get("work_start_time", "09:00"),
            _raw_config=data,
        )

    @property
    def raw(self) -> dict[str, Any]:
        """Get raw configuration dictionary for complex nested structures."""
        return self._raw_config or {}

    @property
    def targets(self) -> dict[str, float]:
        """Get target weekly distribution."""
        return self.raw.get("targets", {})

    @property
    def block_config(self) -> dict[int, dict[str, Any]]:
        """Get block-specific configuration."""
        return self.raw.get("block_config", {})


@lru_cache
def get_config(config_path: str | Path | None = None) -> Config:
    """
    Get cached configuration instance.

    Args:
        config_path: Optional custom config path. If None, uses default package config.

    Returns:
        Config singleton
    """
    if config_path is None:
        package_dir = Path(__file__).parent.parent
        config_path = package_dir / "infrastructure" / "config" / "blocks_config.yaml"

    return Config.from_yaml(config_path)
