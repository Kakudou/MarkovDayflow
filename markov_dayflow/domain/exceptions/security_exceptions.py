"""Domain exceptions for business rule violations."""


class BlockAlreadyCompletedException(Exception):
    """Raised when trying to modify an already completed block."""

    def __init__(self, block_number: int) -> None:
        self.block_number = block_number
        self.message = (
            f"Block {block_number} is already completed and cannot be modified"
        )
        super().__init__(self.message)
