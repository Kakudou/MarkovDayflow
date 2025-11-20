"""Weekly reset use case - resets Markov state for a new week."""

from pathlib import Path

from markov_dayflow.domain.entities import WeeklyState
from markov_dayflow.adapters.repositories import (
    ConfigRepository,
    StateRepository,
)


class WeeklyResetUseCase:
    """Reset weekly state for a new week."""

    def __init__(
        self,
        state_repo: StateRepository | None = None,
        config_repo: ConfigRepository | None = None,
    ):
        """Initialize use case with repositories."""
        self.state_repo = state_repo or StateRepository()
        self.config_repo = config_repo or ConfigRepository()

    def execute(self, state_path: str, config_path: str, week_start: str) -> None:
        """
        Reset weekly state.

        Creates a fresh WeeklyState for the new week, preserving configuration.

        Args:
            state_path: Path to state.json file
            config_path: Path to config.yaml file (not used, kept for compatibility)
            week_start: ISO format date for week start (YYYY-MM-DD)
        """
        fresh_state = WeeklyState(week_start=week_start)

        self.state_repo.save_state(Path(state_path), fresh_state)
