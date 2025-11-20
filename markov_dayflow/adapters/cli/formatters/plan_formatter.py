"""Plan output formatting."""

from markov_dayflow.domain.entities import Plan, Task


class PlanFormatter:
    """Formats plans for CLI output."""

    @staticmethod
    def format_daily_plan(plan: Plan, config: dict, tasks: list[Task] = None) -> str:
        """
        Format daily plan for display.

        Args:
            plan: Plan to format
            config: Configuration with block_config
            tasks: Optional list of tasks for enhanced display

        Returns:
            Formatted plan string
        """
        lines = [
            f"[Target] Today's Focus Blocks ({plan.date}):",
            "=" * 60,
        ]

        block_config = config.get("block_config", {})

        task_lookup = {}
        if tasks:
            for task in tasks:
                task_lookup[task.title] = task

        for block in plan.blocks:
            block_num = block.block
            block_status = "[DONE]" if block.status == "done" else "[PENDING]"

            if block_num in block_config:
                duration = block_config[block_num].get("duration_hours", 1.0)
                name = block_config[block_num].get("name", f"Block {block_num}")
                lines.append(
                    f"\nBlock {block_num} - {name} ({duration}h): {block_status}"
                )
            else:
                lines.append(f"\nBlock {block_num}: {block_status}")

            task = task_lookup.get(block.title)
            if task:
                task_status = f"({task.status})" if hasattr(task, "status") else ""
                lines.append(f"  Task #{task.id}: {block.title} {task_status}")
            else:
                enhanced_title = PlanFormatter._extract_task_from_title(
                    block.title, task_lookup
                )
                if enhanced_title:
                    lines.append(f"  {enhanced_title}")
                else:
                    lines.append(f"  {block.title}")

            lines.append(f"  Bucket: {block.bucket} | Score: {block.expected_score}")

        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def _extract_task_from_title(title: str, task_lookup: dict) -> str | None:
        """
        Extract task info from block titles like 'High Focus Block: Task Name'.

        Args:
            title: Block title to parse
            task_lookup: Dictionary mapping task titles to task objects

        Returns:
            Enhanced title with task ID and status, or None if no match
        """
        if not task_lookup:
            return None

        parts = title.split(": ", 1)
        if len(parts) == 2:
            block_type, task_title = parts
            task = task_lookup.get(task_title)
            if task:
                task_status = f"({task.status})" if hasattr(task, "status") else ""
                return f"Task #{task.id}: {task_title} {task_status}"

        task = task_lookup.get(title)
        if task:
            task_status = f"({task.status})" if hasattr(task, "status") else ""
            return f"Task #{task.id}: {title} {task_status}"

        return None
