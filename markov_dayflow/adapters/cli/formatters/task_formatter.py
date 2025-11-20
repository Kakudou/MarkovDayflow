"""Task output formatting."""

from markov_dayflow.domain.entities import Task
from markov_dayflow.domain.services.scoring import compute_score


class TaskFormatter:
    """Formats tasks for CLI output."""

    @staticmethod
    def format_task_list(
        tasks: list[Task],
        beta: float = 0.3,
        gamma: float = 0.6,
    ) -> str:
        """
        Format task list grouped by status.

        Args:
            tasks: List of tasks to format
            beta: Difficulty penalty for scoring
            gamma: Deadline bonus for scoring

        Returns:
            Formatted task list as string
        """
        if not tasks:
            return "[Tasks] No tasks found"

        by_status: dict[str, list[tuple[Task, float]]] = {}

        for task in tasks:
            if task.status not in by_status:
                by_status[task.status] = []

            score = compute_score(task, beta=beta, gamma=gamma)
            by_status[task.status].append((task, score))

        lines = ["[Tasks] Task List:", "=" * 80]

        for status in ["planned", "wip", "todo", "done"]:
            if status in by_status:
                lines.append(f"\n{status.upper()}:")

                tasks_with_scores = by_status[status]
                tasks_with_scores.sort(key=lambda x: x[1], reverse=True)

                for task, score in tasks_with_scores:
                    planned_info = (
                        f" (planned: {task.planned_date})" if task.planned_date else ""
                    )
                    lines.append(
                        f"  #{task.id:2d} • [{task.bucket}]({score:.1f}) "
                        f"{task.title}{planned_info}"
                    )

        lines.append("=" * 80)
        return "\n".join(lines)

    @staticmethod
    def format_task_summary(tasks: list[Task]) -> str:
        """
        Format task count summary by status.

        Args:
            tasks: List of tasks

        Returns:
            Formatted summary string
        """
        by_status: dict[str, int] = {}
        for task in tasks:
            by_status[task.status] = by_status.get(task.status, 0) + 1

        lines = ["[Chart] Task Summary:"]
        for status in ["todo", "planned", "wip", "done"]:
            count = by_status.get(status, 0)
            lines.append(f"  {status}: {count}")

        return "\n".join(lines)
