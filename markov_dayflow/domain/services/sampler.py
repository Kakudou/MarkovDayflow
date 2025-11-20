"""Markov chain sampler for bucket selection."""

import random


def normalize(d: dict[str, float]) -> dict[str, float]:
    """Normalize dictionary values to sum to 1.0."""
    total = sum(d.values())
    if total == 0:
        n = len(d)
        return {k: 1.0 / n for k in d}
    return {k: v / total for k, v in d.items()}


def apply_ratio_bias(
    probs: dict[str, float],
    realized_share: dict[str, float],
    targets: dict[str, float],
    alpha: float = 1.0,
) -> dict[str, float]:
    """
    Bias probabilities based on realized vs target ratios.

    If a bucket is under-represented, increase its probability.
    If over-represented, decrease it.

    Args:
        probs: Current probabilities
        realized_share: Current weekly share per bucket
        targets: Target share per bucket
        alpha: Bias strength (default 1.0)

    Returns:
        Biased probabilities
    """
    result = probs.copy()

    for bucket in result:
        target = targets.get(bucket, 0.0)
        realized = realized_share.get(bucket, 0.0)

        diff = realized - target

        bias_factor = 2 ** (-alpha * diff)
        result[bucket] *= bias_factor

    return result


def sample_next_bucket(
    current: str,
    transitions: dict[str, dict[str, float]],
    realized_share: dict[str, float],
    targets: dict[str, float],
    cfg: dict,
    use_priors: bool = False,
) -> str:
    """
    Sample the next bucket using Markov chain with biases.

    Steps:
    1. Get transition row for current bucket
    2. Apply Laplace smoothing
    3. Apply ratio bias
    4. Normalize and sample

    Args:
        current: Current bucket
        transitions: Transition count matrix
        realized_share: Current weekly share
        targets: Target weekly share
        cfg: Configuration
        use_priors: Use target priors instead of transitions

    Returns:
        Next bucket name
    """
    laplace = cfg.get("laplace", 1.0)
    alpha = cfg.get("ratio_bias_alpha", 1.0)

    if use_priors:
        row = targets.copy()
    else:
        row = transitions.get(current, {}).copy()

        for bucket in row:
            row[bucket] += laplace

    probs = normalize(row)

    probs = apply_ratio_bias(probs, realized_share, targets, alpha)

    probs = normalize(probs)

    buckets = list(probs.keys())
    weights = [probs[b] for b in buckets]

    return random.choices(buckets, weights=weights, k=1)[0]
