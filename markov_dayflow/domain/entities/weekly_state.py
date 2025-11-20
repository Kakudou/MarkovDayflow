"""Weekly state entity."""

from dataclasses import dataclass, field

from markov_dayflow.domain.entities.task import get_all_planning_buckets


@dataclass
class WeeklyState:
    """
    Persistent state tracking weekly progress and transitions.

    Attributes:
        current_bucket: Last bucket worked on
        weekly_blocks: Count of blocks per bucket this week
        transitions: Markov transition matrix (bucket -> bucket -> count)
        week_start: ISO date string for week start
    """

    current_bucket: str = "Feature"
    weekly_blocks: dict[str, int] = field(default_factory=dict)
    transitions: dict[str, dict[str, float]] = field(default_factory=dict)
    week_start: str = ""

    def __post_init__(self) -> None:
        """Initialize empty structures if needed."""
        if not self.weekly_blocks:
            self.weekly_blocks = {b: 0 for b in get_all_planning_buckets()}

        if not self.transitions:
            buckets = list(get_all_planning_buckets())
            self.transitions = {b: {b2: 0.0 for b2 in buckets} for b in buckets}
