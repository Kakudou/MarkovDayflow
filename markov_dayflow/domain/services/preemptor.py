"""Preemption logic for urgent and support tasks."""

from typing import Optional
from markov_dayflow.domain.entities import Task
from markov_dayflow.domain.services.scoring import compute_score


def select_preempt(
    tasks: list[Task],
    allow_support: bool = True,
    urgent_thresh: float = 4.0,
    support_thresh: float = 6.0,
    support_budget: int = 2,
    used_support: int = 0,
    beta: float = 0.2,
    gamma: float = 0.5,
) -> Optional[Task]:
    """
    Select a task that should preempt normal planning.

    Rules:
    - Urgent tasks can always preempt if score >= urgent_thresh
    - Support tasks only if allow_support and score >= support_thresh
      and under budget

    Args:
        tasks: List of available tasks
        allow_support: Whether to allow support preemption
        urgent_thresh: Score threshold for urgent tasks
        support_thresh: Score threshold for support tasks
        support_budget: Max support preemptions per half-day
        used_support: Number of support preemptions already used
        beta: Difficulty penalty factor
        gamma: Difficulty bonus factor

    Returns:
        Highest-scoring preempting task or None
    """
    preempt_candidates = []

    for task in tasks:
        if task.status == "done":
            continue

        score = compute_score(task, beta=beta, gamma=gamma)

        if task.bucket == "Urgent" and score >= urgent_thresh:
            preempt_candidates.append((task, score))

        elif task.bucket == "Support":
            if (
                allow_support
                and score >= support_thresh
                and used_support < support_budget
            ):
                preempt_candidates.append((task, score))

    if not preempt_candidates:
        return None

    preempt_candidates.sort(key=lambda x: x[1], reverse=True)
    return preempt_candidates[0][0]
