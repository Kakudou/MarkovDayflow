"""Pie chart generator for Mermaid."""

from markov_dayflow.domain.entities.task import map_to_planning_bucket


class PieChartGenerator:
    """Generates Mermaid pie charts for work distribution."""

    @staticmethod
    def generate_bucket_distribution(
        actual_logs: list[dict], title: str = "Work Distribution"
    ) -> str | None:
        """
        Generate a Mermaid pie chart for bucket distribution.

        Args:
            actual_logs: List of actual work logs
            title: Chart title

        Returns:
            Mermaid pie chart as string, or None if no data
        """
        if not actual_logs:
            return None

        bucket_counts: dict[str, int] = {}
        for log in actual_logs:
            bucket = log.get("actual_bucket", "Unknown")
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

        if not bucket_counts:
            return None

        lines = [
            "pie",
            f'    title "{title}"',
        ]

        for bucket, count in sorted(bucket_counts.items()):
            lines.append(f'    "{bucket}" : {count}')

        return "\n".join(lines)

    @staticmethod
    def generate_planning_bucket_distribution(
        actual_logs: list[dict], title: str = "Planning Bucket Distribution"
    ) -> str | None:
        """
        Generate a Mermaid pie chart for planning bucket distribution.
        This maps original buckets to their planning buckets (e.g., Meeting -> Chaos).

        Args:
            actual_logs: List of actual work logs
            title: Chart title

        Returns:
            Mermaid pie chart as string, or None if no data
        """
        if not actual_logs:
            return None

        planning_bucket_counts: dict[str, int] = {}
        for log in actual_logs:
            original_bucket = log.get("actual_bucket", "Unknown")
            planning_bucket = map_to_planning_bucket(original_bucket)
            planning_bucket_counts[planning_bucket] = (
                planning_bucket_counts.get(planning_bucket, 0) + 1
            )

        if not planning_bucket_counts:
            return None

        lines = [
            "pie",
            f'    title "{title}"',
        ]

        for bucket, count in sorted(planning_bucket_counts.items()):
            lines.append(f'    "{bucket}" : {count}')

        return "\n".join(lines)
