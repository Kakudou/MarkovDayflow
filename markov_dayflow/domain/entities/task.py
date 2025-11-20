"""Task entity."""

from dataclasses import dataclass

from markov_dayflow.domain.value_objects import TaskStatus


STANDARD_BUCKETS = {"Feature", "Bug", "R&D", "Docs", "Review", "Support", "Urgent"}


def map_to_planning_bucket(bucket: str) -> str:
    """
    Map any bucket name to a planning bucket.

    Standard buckets pass through unchanged.
    Non-standard buckets (like 'meeting', 'email', 'admin') map to 'Chaos'.

    Args:
        bucket: Original bucket name from user

    Returns:
        Planning bucket name (standard bucket or 'Chaos')
    """
    if bucket in STANDARD_BUCKETS:
        return bucket
    return "Chaos"


def get_all_planning_buckets() -> set[str]:
    """Get all possible planning bucket names including Chaos."""
    return STANDARD_BUCKETS | {"Chaos"}


@dataclass
class Task:
    """
    Represents a work task with scoring attributes.

    Attributes:
        title: Task description
        bucket: Work category (Feature, Bug, R&D, etc. or custom)
        urgency: Urgency level (0-5)
        impact: Business impact (1-5)
        size: Estimated hours (use TaskSize.hours)
        difficulty: Technical difficulty (0-5)
        id: Unique identifier (auto-assigned)
        status: Current status (todo, planned, wip, done)
        planned_date: ISO date string for planned work
        sla_penalty: Service level agreement penalty
        age_days: Days since task creation
        deadline_days: Days until deadline
    """

    title: str
    bucket: str
    urgency: int
    impact: int
    size: float
    difficulty: int
    id: int = 0
    status: str = TaskStatus.TODO.value
    planned_date: str | None = None
    sla_penalty: float = 0.0
    age_days: int = 0
    deadline_days: int | None = None

    def __post_init__(self) -> None:
        """Validate task attributes."""
        assert isinstance(self.bucket, str) and len(self.bucket.strip()) > 0
        assert 0 <= self.urgency <= 5
        assert 1 <= self.impact <= 5
        assert self.size > 0
        assert 0 <= self.difficulty <= 5
        assert self.status in [s.value for s in TaskStatus]

    def get_planning_bucket(self) -> str:
        """Get the bucket name used for planning (maps non-standard buckets to Chaos)."""
        return map_to_planning_bucket(self.bucket)

    def get_display_bucket(self) -> str:
        """Get the bucket name for display (always the original bucket name)."""
        return self.bucket

    def is_completed(self) -> bool:
        """Check if this task is already completed."""
        return self.status == TaskStatus.DONE.value
