"""Reporting use case - cleaned and refactored."""

from pathlib import Path

from markov_dayflow.domain.entities.task import map_to_planning_bucket
from markov_dayflow.adapters.repositories import (
    ConfigRepository,
    PlanRepository,
    StateRepository,
)
from markov_dayflow.infrastructure.utils import read_jsonl


class ReportingUseCase:
    """Use case for generating weekly reports."""

    def __init__(
        self,
        state_repo: StateRepository | None = None,
        config_repo: ConfigRepository | None = None,
        plan_repo: PlanRepository | None = None,
    ):
        self.state_repo = state_repo or StateRepository()
        self.config_repo = config_repo or ConfigRepository()
        self.plan_repo = plan_repo or PlanRepository()

    def execute(
        self,
        state_path: str | Path,
        config_path: str | Path,
        plans_dir: str | Path | None = None,
        logs_dir: str | Path | None = None,
    ) -> dict:
        """
        Generate weekly report with metrics.

        Args:
            state_path: Path to state JSON
            config_path: Path to config YAML
            plans_dir: Optional directory with plan files for adherence
            logs_dir: Optional directory with log files for original bucket analysis

        Returns:
            Dictionary with report metrics
        """
        state = self.state_repo.load_state(state_path)
        config = self.config_repo.load_config(config_path)

        targets = config.get("targets", {})
        total_blocks = sum(state.weekly_blocks.values())

        if total_blocks > 0:
            realized_ratios = {
                bucket: count / total_blocks
                for bucket, count in state.weekly_blocks.items()
            }
        else:
            realized_ratios = {bucket: 0.0 for bucket in targets.keys()}

        ratio_errors = {}
        for bucket, target in targets.items():
            realized = realized_ratios.get(bucket, 0.0)
            error = realized - target
            ratio_errors[bucket] = round(error, 3)

        report = {
            "week_start": state.week_start,
            "total_blocks": total_blocks,
            "realized_ratios": {k: round(v, 3) for k, v in realized_ratios.items()},
            "target_ratios": {k: round(v, 3) for k, v in targets.items()},
            "ratio_errors": ratio_errors,
        }

        if logs_dir:
            original_buckets = self._analyze_original_buckets(Path(logs_dir))
            if original_buckets:
                report["original_buckets"] = original_buckets

        if plans_dir:
            adherence_metrics = self._calculate_adherence(Path(plans_dir))
            if adherence_metrics:
                report["adherence"] = adherence_metrics

        return report

    def _analyze_original_buckets(self, logs_dir: Path) -> dict | None:
        """Analyze original bucket names from log files."""
        if not logs_dir.exists():
            return None

        log_files = [f for f in logs_dir.iterdir() if f.name.startswith("actual_")]
        if not log_files:
            return None

        original_bucket_counts = {}
        chaos_breakdown = {}
        total_entries = 0

        for log_file in log_files:
            try:
                logs = read_jsonl(log_file)
                for entry in logs:
                    original_bucket = entry.get("actual_bucket", "Unknown")
                    original_bucket_counts[original_bucket] = (
                        original_bucket_counts.get(original_bucket, 0) + 1
                    )
                    total_entries += 1

                    planning_bucket = map_to_planning_bucket(original_bucket)
                    if planning_bucket == "Chaos" and original_bucket != "Chaos":
                        chaos_breakdown[original_bucket] = (
                            chaos_breakdown.get(original_bucket, 0) + 1
                        )
            except Exception:
                continue

        if total_entries == 0:
            return None

        original_percentages = {
            bucket: round(count / total_entries, 3)
            for bucket, count in original_bucket_counts.items()
        }

        result = {
            "total_entries": total_entries,
            "bucket_counts": original_bucket_counts,
            "bucket_percentages": original_percentages,
        }

        if chaos_breakdown:
            result["chaos_breakdown"] = {
                "counts": chaos_breakdown,
                "percentages": {
                    bucket: round(count / total_entries, 3)
                    for bucket, count in chaos_breakdown.items()
                },
            }

        return result

    def _calculate_adherence(self, plans_dir: Path) -> dict | None:
        """Calculate plan adherence metrics from plan files."""
        if not plans_dir.exists():
            return None

        plan_files = [f for f in plans_dir.iterdir() if f.name.startswith("plan_")]

        if not plan_files:
            return None

        total_blocks = 0
        done_blocks = 0
        on_plan_blocks = 0

        for plan_file in plan_files:
            try:
                plan = self.plan_repo.load_plan(plan_file)

                for block in plan.blocks:
                    total_blocks += 1

                    if block.status == "done":
                        done_blocks += 1
                        on_plan_blocks += 1
            except Exception:
                continue

        if total_blocks == 0:
            return None

        return {
            "total_blocks": total_blocks,
            "done_blocks": done_blocks,
            "completion_rate": round(done_blocks / total_blocks, 3),
            "on_plan_rate": round(on_plan_blocks / total_blocks, 3),
        }
