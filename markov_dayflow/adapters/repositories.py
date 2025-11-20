"""Simplified repository implementations without port abstraction layer."""

from pathlib import Path
from typing import Any

import yaml

from markov_dayflow.domain.entities import Block, Plan, Task, WeeklyState
from markov_dayflow.infrastructure.utils import atomic_write_json, read_json


class TaskRepository:
    """JSON-based task repository."""

    def load_tasks(self, path: str | Path) -> list[Task]:
        """Load tasks from JSON file."""
        data = read_json(path)
        tasks = []

        for item in data:
            task = Task(
                title=item["title"],
                bucket=item["bucket"],
                urgency=item["urgency"],
                impact=item["impact"],
                size=item["size"],
                difficulty=item["difficulty"],
                id=item.get("id", 0),
                status=item.get("status", "todo"),
                planned_date=item.get("planned_date"),
                sla_penalty=item.get("sla_penalty", 0.0),
                age_days=item.get("age_days", 0),
                deadline_days=item.get("deadline_days"),
            )
            tasks.append(task)

        return tasks

    def save_tasks(self, path: str | Path, tasks: list[Task]) -> None:
        """Save tasks to JSON file with auto-assigned IDs."""
        max_id = max((t.id for t in tasks if t.id > 0), default=0)
        for task in tasks:
            if task.id == 0:
                max_id += 1
                task.id = max_id

        data = []
        for task in tasks:
            item = {
                "id": task.id,
                "title": task.title,
                "bucket": task.bucket,
                "urgency": task.urgency,
                "impact": task.impact,
                "size": task.size,
                "difficulty": task.difficulty,
                "status": task.status,
                "sla_penalty": task.sla_penalty,
                "age_days": task.age_days,
            }
            if task.planned_date is not None:
                item["planned_date"] = task.planned_date
            if task.deadline_days is not None:
                item["deadline_days"] = task.deadline_days

            data.append(item)

        atomic_write_json(path, data)

    def find_by_id(self, path: str | Path, task_id: int) -> Task | None:
        """Find task by ID."""
        tasks = self.load_tasks(path)
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def find_by_status(self, path: str | Path, status: str) -> list[Task]:
        """Find tasks by status."""
        tasks = self.load_tasks(path)
        return [t for t in tasks if t.status == status]


class StateRepository:
    """JSON-based state repository."""

    def load_state(self, path: str | Path) -> WeeklyState:
        """Load weekly state from JSON file."""
        data = read_json(path)

        return WeeklyState(
            current_bucket=data.get("current_bucket", "Feature"),
            weekly_blocks=data.get("weekly_blocks", {}),
            transitions=data.get("transitions", {}),
            week_start=data.get("week_start", ""),
        )

    def save_state(self, path: str | Path, state: WeeklyState) -> None:
        """Save weekly state to JSON file."""
        data = {
            "current_bucket": state.current_bucket,
            "weekly_blocks": state.weekly_blocks,
            "transitions": state.transitions,
            "week_start": state.week_start,
        }

        atomic_write_json(path, data)


class PlanRepository:
    """JSON-based plan repository."""

    def load_plan(self, path: str | Path) -> Plan:
        """Load plan from JSON file."""
        data = read_json(path)

        blocks = []
        for item in data["blocks"]:
            block = Block(
                block=item["block"],
                bucket=item["bucket"],
                title=item["title"],
                expected_score=item["expected_score"],
                status=item.get("status", "planned"),
            )
            blocks.append(block)

        return Plan(date=data["date"], blocks=blocks)

    def save_plan(self, path: str | Path, plan: Plan) -> None:
        """Save plan to JSON file."""
        data = {"date": plan.date, "blocks": []}

        for block in plan.blocks:
            item = {
                "block": block.block,
                "bucket": block.bucket,
                "title": block.title,
                "expected_score": block.expected_score,
                "status": block.status,
            }
            data["blocks"].append(item)

        atomic_write_json(path, data)


class ConfigRepository:
    """YAML-based configuration repository."""

    def load_config(self, path: str | Path) -> dict[str, Any]:
        """Load configuration from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
