"""Task status enum."""

from enum import Enum


class TaskStatus(str, Enum):
    """Task status lifecycle: todo -> planned -> wip -> done"""

    TODO = "todo"
    PLANNED = "planned"
    WIP = "wip"
    DONE = "done"
