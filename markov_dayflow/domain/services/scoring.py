"""Task scoring logic."""

from markov_dayflow.domain.entities import Task


def compute_score(task: Task, beta: float = 0.3, gamma: float = 0.6) -> float:
    """
    Compute priority score for a task.

    Formula:
    score = (urgency + impact + 0.1*age + SLA + γ*difficulty_if_deadline) /
            max(size * (1 + β*difficulty), 0.5)

    Args:
        task: Task to score
        beta: Difficulty penalty factor (default 0.3)
        gamma: Deadline urgency bonus (default 0.6)

    Returns:
        Priority score (higher is more urgent)
    """
    numerator = task.urgency + task.impact + 0.1 * task.age_days + task.sla_penalty

    if task.deadline_days is not None and task.deadline_days >= 0:
        numerator += gamma * task.difficulty

    if task.size <= 1:
        denominator = max(task.size, 0.5)
    else:
        denominator = max(task.size * (1 + beta * task.difficulty), 0.5)

    return numerator / denominator
