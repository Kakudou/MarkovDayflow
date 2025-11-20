"""Task size enum with t-shirt sizing."""

from enum import Enum


class TaskSize(str, Enum):
    """Task size using t-shirt sizing mapped to estimated hours."""

    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


TASK_SIZE_HOURS = {
    "XS": 0.5,
    "S": 1.0,
    "M": 2.0,
    "L": 4.0,
    "XL": 8.0,
}


def get_task_hours(size: str) -> float:
    """Get hours for a task size."""
    return TASK_SIZE_HOURS.get(size.upper(), 2.0)
