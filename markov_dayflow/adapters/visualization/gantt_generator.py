"""Gantt chart generator for Mermaid."""

from datetime import datetime
from pathlib import Path

from markov_dayflow.domain.entities import Plan
from markov_dayflow.infrastructure.utils import read_jsonl


class GanttGenerator:
    """Generates Mermaid Gantt charts for work blocks."""

    @staticmethod
    def generate_daily_gantt(
        plan: Plan, actual_logs: list[dict], config: dict
    ) -> str | None:
        """
        Generate a Mermaid Gantt chart for a single day's blocks.

        Args:
            plan: Daily plan with blocks
            actual_logs: List of actual work logs
            config: Configuration with block_config and work_start_time

        Returns:
            Mermaid Gantt chart as string, or None if no data
        """
        if not plan or not plan.blocks:
            return None

        block_config = config.get("block_config", {})
        work_start_time = config.get("work_start_time", "09:00")

        start_parts = work_start_time.split(":")
        start_hour = int(start_parts[0])
        start_min = int(start_parts[1]) if len(start_parts) > 1 else 0

        actual_work = {}
        for log in actual_logs:
            if log.get("block") is not None:
                actual_work[log["block"]] = log

        lines = [
            "gantt",
            "    dateFormat HH:mm",
            "    axisFormat %H:%M",
            "    section Work Blocks",
        ]

        current_time_minutes = start_hour * 60 + start_min

        for block in plan.blocks:
            block_num = block.block
            duration_hours = block_config.get(block_num, {}).get("duration_hours", 1.0)
            duration_minutes = int(duration_hours * 60)

            start_hour_fmt = current_time_minutes // 60
            start_min_fmt = current_time_minutes % 60
            start_time_str = f"{start_hour_fmt:02d}:{start_min_fmt:02d}"

            actual = actual_work.get(block_num, {})

            if actual:
                actual_bucket = actual.get("actual_bucket", block.bucket)
                actual_title = actual.get("actual_title", block.title)
                actual_title = actual_title.replace(":", "").replace('"', "'")

                if actual.get("actual_bucket") == block.bucket:
                    status = "done"
                    title_display = f"[{actual_bucket}] {actual_title}"
                else:
                    status = "active"
                    title_display = (
                        f"[{actual_bucket}] {actual_title} (vs {block.bucket})"
                    )
            else:
                status = "crit"
                planned_title = block.title.replace(":", "").replace('"', "'")
                title_display = f"[{block.bucket}] {planned_title} (not done)"

            lines.append(
                f"    {title_display} :{status}, {start_time_str}, {duration_minutes}m"
            )

            current_time_minutes += duration_minutes

        return "\n".join(lines)

    @staticmethod
    def generate_global_gantt(
        plans_dir: Path, logs_dir: Path, config: dict
    ) -> str | None:
        """
        Generate a Mermaid Gantt chart for all available plans/logs.

        Args:
            plans_dir: Directory containing plan files
            logs_dir: Directory containing log files
            config: Configuration with block_config

        Returns:
            Mermaid Gantt chart as string, or None if no data
        """
        from markov_dayflow.adapters.repositories import PlanRepository

        if not plans_dir.exists():
            return None

        plan_files = []
        for file in plans_dir.iterdir():
            if file.name.startswith("plan_") and file.name.endswith(".json"):
                date_str = file.name[5:-5]
                plan_files.append((date_str, file))

        if not plan_files:
            return None

        plan_files.sort()

        lines = [
            "gantt",
            "    dateFormat HH:mm",
            "    axisFormat %H:%M",
        ]

        plan_repo = PlanRepository()

        for date_str, plan_path in plan_files:
            try:
                plan = plan_repo.load_plan(plan_path)

                log_path = logs_dir / f"actual_{date_str}.jsonl"
                actual_logs = []
                if log_path.exists():
                    actual_logs = read_jsonl(log_path)

                daily_gantt = GanttGenerator.generate_daily_gantt(
                    plan, actual_logs, config
                )
                if daily_gantt:
                    daily_lines = daily_gantt.split("\n")
                    task_lines = [
                        line
                        for line in daily_lines
                        if line.strip()
                        and not line.strip().startswith("gantt")
                        and not line.strip().startswith("dateFormat")
                        and not line.strip().startswith("axisFormat")
                        and not line.strip().startswith("section")
                    ]

                    day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
                    lines.append(f"    section {day_name} ({date_str})")
                    lines.extend(task_lines)

            except Exception:
                continue

        return "\n".join(lines) if len(lines) > 3 else None
