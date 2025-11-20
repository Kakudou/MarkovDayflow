"""Plan entity."""

from dataclasses import dataclass, field

from markov_dayflow.domain.entities.block import Block


@dataclass
class Plan:
    """
    A day's plan consisting of multiple blocks.

    Attributes:
        date: ISO date string (YYYY-MM-DD)
        blocks: List of Block entities for the day
    """

    date: str
    blocks: list[Block] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate plan attributes."""
        assert len(self.date) == 10
        assert all(isinstance(b, Block) for b in self.blocks)
