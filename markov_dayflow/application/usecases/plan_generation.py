"""Plan generation use case - cleaned and refactored."""

import random
from pathlib import Path

from markov_dayflow.adapters.repositories import (
    ConfigRepository,
    PlanRepository,
    StateRepository,
    TaskRepository,
)
from markov_dayflow.domain.entities import Block, Plan, Task, WeeklyState
from markov_dayflow.domain.services.focus_blocks import (
    apply_focus_block_bias,
    get_focus_block_name,
    suggest_focus_optimization,
    validate_focus_block_quality_gates,
)
from markov_dayflow.domain.services.preemptor import select_preempt
from markov_dayflow.domain.services.sampler import (
    apply_ratio_bias,
    normalize,
)
from markov_dayflow.domain.services.scoring import compute_score
from markov_dayflow.infrastructure.utils import ensure_directory


class PlanGenerationUseCase:
    """Use case for generating daily focus block plans."""

    def __init__(
        self,
        task_repo: TaskRepository | None = None,
        state_repo: StateRepository | None = None,
        plan_repo: PlanRepository | None = None,
        config_repo: ConfigRepository | None = None,
    ):
        self.task_repo = task_repo or TaskRepository()
        self.state_repo = state_repo or StateRepository()
        self.plan_repo = plan_repo or PlanRepository()
        self.config_repo = config_repo or ConfigRepository()

    def execute(
        self,
        tasks_path: str | Path,
        state_path: str | Path,
        config_path: str | Path,
        output_path: str | Path,
        date: str,
    ) -> str:
        """
        Generate a daily focus block plan.

        Args:
            tasks_path: Path to tasks JSON
            state_path: Path to state JSON
            config_path: Path to config YAML
            output_path: Path for output plan
            date: ISO date string

        Returns:
            Path to generated plan file
        """

        ensure_directory(tasks_path)
        ensure_directory(state_path)
        ensure_directory(output_path)

        tasks = self._load_or_create_tasks(tasks_path)
        state = self._load_or_create_state(state_path, date)
        config = self.config_repo.load_config(config_path)

        self._validate_config(config)

        params = self._extract_config_params(config)

        realized_share = self._calculate_realized_share(
            state.weekly_blocks, params["targets"]
        )

        self._display_quality_feedback(state.weekly_blocks, params["targets"])

        existing_plan = self._load_existing_plan(output_path)

        blocks = self._generate_blocks(
            tasks=tasks,
            state=state,
            params=params,
            realized_share=realized_share,
            date=date,
            config=config,
            existing_blocks=existing_plan.blocks if existing_plan else [],
        )

        plan = Plan(date=date, blocks=blocks)
        self.plan_repo.save_plan(output_path, plan)

        return str(output_path)

    def _validate_config(self, config: dict) -> None:
        """Validate configuration consistency."""
        blocks_per_day = config.get("blocks_per_day", 5)
        block_config = config.get("block_config", {})
        configured_blocks = len(block_config)

        if configured_blocks != blocks_per_day:
            raise ValueError(
                f"Configuration mismatch: blocks_per_day={blocks_per_day} but "
                f"only {configured_blocks} blocks configured in block_config."
            )

    def _extract_config_params(self, config: dict) -> dict:
        """Extract configuration parameters into a dictionary."""
        return {
            "blocks_per_day": config.get("blocks_per_day", 5),
            "beta": config.get("beta", 0.3),
            "gamma": config.get("gamma", 0.6),
            "targets": config.get("targets", {}),
            "urgent_threshold": config.get("urgent_threshold", 3.5),
            "support_threshold": config.get("support_threshold", 4.5),
            "support_budget": config.get("support_budget", 1),
            "allow_support_preempt": config.get("allow_support_preempt", True),
            "laplace": config.get("laplace", 1.5),
            "ratio_bias_alpha": config.get("ratio_bias_alpha", 1.2),
        }

    def _calculate_realized_share(
        self, weekly_blocks: dict[str, int], targets: dict[str, float]
    ) -> dict[str, float]:
        """Calculate realized bucket share from weekly blocks."""
        total_blocks = sum(weekly_blocks.values())
        if total_blocks > 0:
            return {
                bucket: count / total_blocks for bucket, count in weekly_blocks.items()
            }
        else:
            return {bucket: 0.0 for bucket in targets.keys()}

    def _display_quality_feedback(
        self, weekly_blocks: dict[str, int], targets: dict[str, float]
    ) -> None:
        """Display quality gates and optimization suggestions."""
        violations = validate_focus_block_quality_gates(weekly_blocks, targets)
        if violations:
            print("[!] Quality gate violations detected:")
            for violation in violations:
                print(f"   - {violation}")

        optimization = suggest_focus_optimization(weekly_blocks, targets)
        if optimization:
            print(f"[Tip] Focus optimization: {optimization}")

    def _generate_blocks(
        self,
        tasks: list[Task],
        state: WeeklyState,
        params: dict,
        realized_share: dict[str, float],
        date: str,
        config: dict,
        existing_blocks: list[Block] = None,
    ) -> list[Block]:
        """Generate blocks for the day."""
        blocks = []
        current_bucket = state.current_bucket
        used_support = 0
        used_tasks: set[int] = set()

        existing_blocks_map = {}
        if existing_blocks:
            for block in existing_blocks:
                existing_blocks_map[block.block] = block

        for block_num in range(1, params["blocks_per_day"] + 1):
            if (
                block_num in existing_blocks_map
                and existing_blocks_map[block_num].status == "done"
            ):
                block = existing_blocks_map[block_num]
                blocks.append(block)
                if block.bucket == "Support":
                    used_support += 1
                continue
            block = self._generate_single_block(
                block_num=block_num,
                tasks=tasks,
                state=state,
                params=params,
                realized_share=realized_share,
                current_bucket=current_bucket,
                used_support=used_support,
                used_tasks=used_tasks,
                date=date,
                config=config,
            )

            blocks.append(block)

            if "planning_bucket" in locals():
                current_bucket = block.bucket
            used_support += 1 if block.bucket == "Support" else 0

        return blocks

    def _generate_single_block(
        self,
        block_num: int,
        tasks: list[Task],
        state: WeeklyState,
        params: dict,
        realized_share: dict[str, float],
        current_bucket: str,
        used_support: int,
        used_tasks: set[int],
        date: str,
        config: dict,
    ) -> Block:
        """Generate a single block."""
        focus_block_name = get_focus_block_name(block_num, config)

        available_for_preempt = [t for t in tasks if t.id not in used_tasks]
        preempt_task = select_preempt(
            available_for_preempt,
            allow_support=params["allow_support_preempt"],
            urgent_thresh=params["urgent_threshold"],
            support_thresh=params["support_threshold"],
            support_budget=params["support_budget"],
            used_support=used_support,
            beta=params["beta"],
            gamma=params["gamma"],
        )

        if preempt_task:
            bucket = preempt_task.get_display_bucket()
            title = f"{focus_block_name}: {preempt_task.title}"
            score = compute_score(
                preempt_task, beta=params["beta"], gamma=params["gamma"]
            )
            used_tasks.add(preempt_task.id)
        else:
            available_tasks = self._get_available_tasks(tasks, date, used_tasks)

            if not available_tasks:
                bucket = "Feature"
                title = f"{focus_block_name}: No tasks available"
                score = 0.0
            else:
                row = state.transitions.get(current_bucket, {}).copy()
                for b in row:
                    row[b] += params["laplace"]

                probs = normalize(row)
                probs = apply_ratio_bias(
                    probs, realized_share, params["targets"], params["ratio_bias_alpha"]
                )
                probs = apply_focus_block_bias(
                    probs, block_num, config, available_tasks
                )
                probs = normalize(probs)

                buckets = list(probs.keys())
                weights = [probs[b] for b in buckets]
                planning_bucket = random.choices(buckets, weights=weights, k=1)[0]

                task, score = self._select_task_from_bucket(
                    planning_bucket, available_tasks, params, used_tasks
                )

                if task:
                    bucket = task.get_display_bucket()
                    title = f"{focus_block_name}: {task.title}"
                else:
                    task, score = self._select_task_with_fallback(
                        probs, available_tasks, params, used_tasks, planning_bucket
                    )
                    if task:
                        bucket = task.get_display_bucket()
                        title = f"{focus_block_name}: {task.title}"
                    else:
                        bucket = planning_bucket
                        title = f"{focus_block_name}: No tasks available"
                        score = 0.0

        return Block(
            block=block_num,
            bucket=bucket,
            title=title,
            expected_score=round(score, 2),
            status="planned",
        )

    def _select_task_from_bucket(
        self,
        planning_bucket: str,
        available_tasks: list[Task],
        params: dict,
        used_tasks: set[int],
    ) -> tuple[Task | None, float]:
        """Select highest-scoring task from bucket."""
        bucket_tasks = [
            t for t in available_tasks if t.get_planning_bucket() == planning_bucket
        ]

        if bucket_tasks:
            scored_tasks = [
                (t, compute_score(t, beta=params["beta"], gamma=params["gamma"]))
                for t in bucket_tasks
            ]
            scored_tasks.sort(key=lambda x: x[1], reverse=True)
            task, score = scored_tasks[0]
            used_tasks.add(task.id)
            return task, score

        return None, 0.0

    def _select_task_with_fallback(
        self,
        bucket_probs: dict[str, float],
        available_tasks: list[Task],
        params: dict,
        used_tasks: set[int],
        exclude_bucket: str,
    ) -> tuple[Task | None, float]:
        """
        Select task from fallback buckets in order of probability.

        Tries buckets in descending probability order (excluding the one that failed),
        selecting the highest-scoring task from each bucket.
        """
        if not available_tasks:
            return None, 0.0

        sorted_buckets = sorted(
            [(b, p) for b, p in bucket_probs.items() if b != exclude_bucket],
            key=lambda x: x[1],
            reverse=True,
        )

        for bucket, _ in sorted_buckets:
            task, score = self._select_task_from_bucket(
                bucket, available_tasks, params, used_tasks
            )
            if task:
                return task, score

        return None, 0.0

    def _get_available_tasks(
        self, tasks: list[Task], date: str, used_tasks: set[int]
    ) -> list[Task]:
        """Get tasks available for planning on given date."""
        return [
            task
            for task in tasks
            if task.status != "done"
            and task.id not in used_tasks
            and task.status in ["todo", "wip", "planned"]
        ]

    def _load_or_create_tasks(self, tasks_path: str | Path) -> list[Task]:
        """Load tasks or create empty task file."""
        path = Path(tasks_path)
        if path.exists():
            return self.task_repo.load_tasks(tasks_path)
        else:
            print(f"Creating empty tasks file at {tasks_path}")
            print(
                "[Tip] Add your first task with: markov-dayflow task add Feature 'Your task'"
            )
            self.task_repo.save_tasks(tasks_path, [])
            return []

    def _load_existing_plan(self, plan_path: str | Path) -> Plan | None:
        """Load existing plan if it exists."""
        path = Path(plan_path)
        if path.exists():
            try:
                return self.plan_repo.load_plan(plan_path)
            except Exception:
                return None
        return None

    def _load_or_create_state(self, state_path: str | Path, date: str) -> WeeklyState:
        """Load state or create new weekly state."""
        path = Path(state_path)
        if path.exists():
            return self.state_repo.load_state(state_path)
        else:
            print(f"Creating new state at {state_path}")
            state = WeeklyState(week_start=date)
            self.state_repo.save_state(state_path, state)
            return state
