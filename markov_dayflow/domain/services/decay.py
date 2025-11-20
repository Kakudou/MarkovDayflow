"""Decay logic for transition matrix."""


def decay_transitions(
    transitions: dict[str, dict[str, float]], decay: float = 0.9, laplace: float = 1.0
) -> None:
    """
    Apply exponential decay to transition counts and add Laplace smoothing.

    This gradually forgets old patterns while maintaining diagonal stability.

    Args:
        transitions: Transition count matrix (modified in-place)
        decay: Decay factor (0-1, default 0.9)
        laplace: Smoothing to add to diagonal (default 1.0)
    """
    for source_bucket, row in transitions.items():
        for target_bucket in row:
            transitions[source_bucket][target_bucket] *= decay

        transitions[source_bucket][source_bucket] += laplace
