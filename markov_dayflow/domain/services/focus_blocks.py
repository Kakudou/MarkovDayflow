"""Focus block service for flexible daily planning system."""

from typing import Dict, List, Optional
from markov_dayflow.domain.entities import Task


def apply_focus_block_bias(
    probs: Dict[str, float], block_index: int, cfg: Dict, tasks: List[Task]
) -> Dict[str, float]:
    """
    Apply focus block preferences to bucket probabilities.

    This biases the selection based on the focus intensity and
    preferred work types for each block in the daily block system.

    Args:
        probs: Current bucket probabilities
        block_index: Block number (1-N where N is blocks_per_day)
        cfg: Configuration with block_config
        tasks: Available tasks for context

    Returns:
        Modified probabilities with focus block bias applied
    """
    result = probs.copy()

    if "block_config" not in cfg or block_index not in cfg["block_config"]:
        return result

    block_config = cfg["block_config"][block_index]
    preferred = block_config.get("preferred_buckets", [])
    avoided = block_config.get("avoid_buckets", [])

    for bucket in preferred:
        if bucket in result:
            result[bucket] *= 1.3

    for bucket in avoided:
        if bucket in result:
            result[bucket] *= 0.4

    return result


def get_focus_block_name(block_index: int, cfg: Dict) -> str:
    """
    Get the human-readable name for a focus block.

    Args:
        block_index: Block number (1-N where N is blocks_per_day)
        cfg: Configuration with block_config

    Returns:
        Block name (e.g., "High Focus Block")
    """
    if "block_config" not in cfg or block_index not in cfg["block_config"]:
        return f"Block {block_index}"

    return cfg["block_config"][block_index].get("name", f"Block {block_index}")


def validate_focus_block_quality_gates(
    weekly_blocks: Dict[str, int], targets: Dict[str, float]
) -> List[str]:
    """
    Simple quality check: warn if Feature work is below target.

    Args:
        weekly_blocks: Current weekly block counts by bucket
        targets: Target distribution

    Returns:
        List of quality warnings (empty if all good)
    """
    violations = []
    total_blocks = sum(weekly_blocks.values())

    if total_blocks == 0:
        return violations

    feature_blocks = weekly_blocks.get("Feature", 0)
    target_feature_blocks = int(total_blocks * targets.get("Feature", 0.4))

    if feature_blocks < target_feature_blocks:
        violations.append(
            f"Feature blocks below minimum: {feature_blocks}/{target_feature_blocks}"
        )

    return violations


def suggest_focus_optimization(
    weekly_blocks: Dict[str, int], targets: Dict[str, float]
) -> Optional[str]:
    """
    Simple optimization suggestion based on biggest deviation.

    Args:
        weekly_blocks: Current weekly block counts
        targets: Target distribution

    Returns:
        Optimization suggestion or None
    """
    total_blocks = sum(weekly_blocks.values())
    if total_blocks == 0:
        return None

    max_deviation = 0
    deviation_bucket = None

    for bucket, target_share in targets.items():
        actual_count = weekly_blocks.get(bucket, 0)
        actual_share = actual_count / total_blocks
        deviation = actual_share - target_share

        if abs(deviation) > abs(max_deviation):
            max_deviation = deviation
            deviation_bucket = bucket

    if abs(max_deviation) > 0.15:
        if max_deviation > 0:
            return f"Consider reducing {deviation_bucket} work ({max_deviation:+.1%} over target)"
        else:
            return f"Consider increasing {deviation_bucket} work ({abs(max_deviation):.1%} under target)"

    return None
