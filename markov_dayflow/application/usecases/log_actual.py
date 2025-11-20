"""Log actual work use case."""

from markov_dayflow.adapters.repositories import (
    PlanRepository,
    StateRepository,
    TaskRepository,
)
from markov_dayflow.infrastructure.utils import append_jsonl


class LogActualUseCase:
    """Use case for logging actual work done."""

    def __init__(
        self,
        plan_repo: PlanRepository | None = None,
        state_repo: StateRepository | None = None,
        task_repo: TaskRepository | None = None,
    ):
        self.plan_repo = plan_repo or PlanRepository()
        self.state_repo = state_repo or StateRepository()
        self.task_repo = task_repo or TaskRepository()

    def execute(
        self,
        plan_path: str,
        state_path: str,
        log_path: str,
        block_number: int | None = None,
        actual_bucket: str | None = None,
        actual_title: str | None = None,
        notes: str | None = None,
        task_id: int | None = None,
        tasks_path: str | None = None,
    ) -> dict[str, str]:
        """
        Log actual work for a block or completed task and update state.

        Args:
            plan_path: Path to plan JSON
            state_path: Path to state JSON
            log_path: Path to actual log JSONL
            block_number: Block number (1-indexed) - for planned work
            actual_bucket: Actual bucket worked on (optional for blocks)
            actual_title: Actual task title (optional for blocks)
            notes: Optional notes
            task_id: Task ID for unplanned completed work
            tasks_path: Path to tasks JSON (required if task_id provided)

        Returns:
            dict: Contains 'bucket' and 'title' actually used for logging

        Raises:
            ValueError: If neither block_number nor task_id provided
        """
        if task_id is not None and block_number is not None:
            if not tasks_path:
                raise ValueError("tasks_path required for task-based logging")

            return self._log_task_in_block(
                plan_path,
                state_path,
                log_path,
                block_number,
                task_id,
                tasks_path,
                notes,
            )
        elif task_id is not None:
            if not tasks_path:
                raise ValueError("tasks_path required for task-based logging")

            return self._log_task(state_path, log_path, task_id, tasks_path, notes)
        elif block_number is not None:
            return self._log_block(
                plan_path,
                state_path,
                log_path,
                block_number,
                actual_bucket,
                actual_title,
                notes,
            )
        else:
            raise ValueError("Either block_number or task_id must be provided")

    def _log_task(
        self,
        state_path: str,
        log_path: str,
        task_id: int,
        tasks_path: str,
        notes: str | None,
    ) -> dict[str, str]:
        """Log unplanned task completion."""
        tasks = self.task_repo.load_tasks(tasks_path)
        task = None
        for t in tasks:
            if t.id == task_id:
                task = t
                break

        if not task:
            raise ValueError(f"Task {task_id} not found")

        actual_bucket = task.bucket
        actual_title = task.title

        state = self.state_repo.load_state(state_path)
        planning_bucket = task.get_planning_bucket()

        state.weekly_blocks[planning_bucket] = (
            state.weekly_blocks.get(planning_bucket, 0) + 1
        )

        prev_bucket = state.current_bucket
        if prev_bucket not in state.transitions:
            state.transitions[prev_bucket] = {}
        state.transitions[prev_bucket][planning_bucket] = (
            state.transitions[prev_bucket].get(planning_bucket, 0.0) + 1.0
        )

        state.current_bucket = planning_bucket
        self.state_repo.save_state(state_path, state)

        log_entry = {
            "task_id": task_id,
            "actual_bucket": actual_bucket,
            "actual_title": actual_title,
            "notes": notes,
        }
        append_jsonl(log_path, log_entry)

        return {"bucket": actual_bucket, "title": actual_title}

    def _log_block(
        self,
        plan_path: str,
        state_path: str,
        log_path: str,
        block_number: int,
        actual_bucket: str | None,
        actual_title: str | None,
        notes: str | None,
    ) -> dict[str, str]:
        """Log planned block completion."""
        plan = self.plan_repo.load_plan(plan_path)
        state = self.state_repo.load_state(state_path)

        block = None
        for b in plan.blocks:
            if b.block == block_number:
                block = b
                break

        if not block:
            raise ValueError(f"Block {block_number} not found in plan")

        block.validate_can_be_modified()

        final_bucket = actual_bucket if actual_bucket else block.bucket
        final_title = actual_title if actual_title else block.title

        from markov_dayflow.domain.entities.task import map_to_planning_bucket

        planning_bucket = map_to_planning_bucket(final_bucket)

        state.weekly_blocks[planning_bucket] = (
            state.weekly_blocks.get(planning_bucket, 0) + 1
        )

        prev_bucket = state.current_bucket
        if prev_bucket not in state.transitions:
            state.transitions[prev_bucket] = {}
        state.transitions[prev_bucket][planning_bucket] = (
            state.transitions[prev_bucket].get(planning_bucket, 0.0) + 1.0
        )

        state.current_bucket = planning_bucket
        self.state_repo.save_state(state_path, state)

        block.mark_completed()
        self.plan_repo.save_plan(plan_path, plan)

        log_entry = {
            "block": block_number,
            "actual_bucket": final_bucket,
            "actual_title": final_title,
            "notes": notes,
        }
        append_jsonl(log_path, log_entry)

        return {"bucket": final_bucket, "title": final_title}

    def _log_task_in_block(
        self,
        plan_path: str,
        state_path: str,
        log_path: str,
        block_number: int,
        task_id: int,
        tasks_path: str,
        notes: str | None,
    ) -> dict[str, str]:
        """Log task completion in a specific block - updates both task and plan."""
        tasks = self.task_repo.load_tasks(tasks_path)
        task = None
        for t in tasks:
            if t.id == task_id:
                task = t
                break

        if not task:
            raise ValueError(f"Task {task_id} not found")

        plan = self.plan_repo.load_plan(plan_path)
        state = self.state_repo.load_state(state_path)

        block = None
        for b in plan.blocks:
            if b.block == block_number:
                block = b
                break

        if not block:
            raise ValueError(f"Block {block_number} not found in plan")

        block.validate_can_be_modified()

        actual_bucket = task.bucket
        actual_title = task.title

        from markov_dayflow.domain.entities.task import map_to_planning_bucket

        planning_bucket = map_to_planning_bucket(actual_bucket)

        state.weekly_blocks[planning_bucket] = (
            state.weekly_blocks.get(planning_bucket, 0) + 1
        )

        prev_bucket = state.current_bucket
        if prev_bucket not in state.transitions:
            state.transitions[prev_bucket] = {}
        state.transitions[prev_bucket][planning_bucket] = (
            state.transitions[prev_bucket].get(planning_bucket, 0.0) + 1.0
        )

        state.current_bucket = planning_bucket
        self.state_repo.save_state(state_path, state)

        block.update_content(actual_bucket, actual_title)
        block.mark_completed()
        self.plan_repo.save_plan(plan_path, plan)

        log_entry = {
            "block": block_number,
            "task_id": task_id,
            "actual_bucket": actual_bucket,
            "actual_title": actual_title,
            "notes": notes,
        }
        append_jsonl(log_path, log_entry)

        return {"bucket": actual_bucket, "title": actual_title}
