"""Block entity."""

from dataclasses import dataclass


@dataclass
class Block:
    """
    Represents a single time block in a plan.

    Attributes:
        block: Block number (1-indexed)
        bucket: Work category assigned to this block
        title: Task title or description
        expected_score: Expected priority score
        status: Block status (planned, done)
    """

    block: int
    bucket: str
    title: str
    expected_score: float
    status: str = "planned"

    def __post_init__(self) -> None:
        """Validate block attributes."""
        assert self.block > 0
        assert len(self.bucket.strip()) > 0
        assert len(self.title.strip()) > 0
        assert self.status in ["planned", "done"]

    def is_completed(self) -> bool:
        """Check if this block is already completed."""
        return self.status == "done"

    def validate_can_be_modified(self) -> None:
        """
        Validate that this block can be modified.

        Raises:
            BlockAlreadyCompletedException: If block is already completed
        """
        if self.is_completed():
            from markov_dayflow.domain.exceptions import BlockAlreadyCompletedException

            raise BlockAlreadyCompletedException(self.block)

    def mark_completed(self) -> None:
        """
        Mark this block as completed.

        Raises:
            BlockAlreadyCompletedException: If block is already completed
        """
        self.validate_can_be_modified()
        self.status = "done"

    def update_content(self, bucket: str, title: str) -> None:
        """
        Update block content (bucket and title).

        Args:
            bucket: New bucket name
            title: New title

        Raises:
            BlockAlreadyCompletedException: If block is already completed
        """
        self.validate_can_be_modified()
        self.bucket = bucket
        self.title = title
