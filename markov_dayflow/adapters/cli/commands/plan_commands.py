"""Plan generation and display commands."""

import click

from markov_dayflow.adapters.cli.formatters import PlanFormatter, TaskFormatter
from markov_dayflow.adapters.repositories import (
    ConfigRepository,
    PlanRepository,
    TaskRepository,
)
from markov_dayflow.application.usecases.plan_generation import PlanGenerationUseCase
from markov_dayflow.infrastructure.utils import PathResolver, parse_date, read_jsonl


@click.command()
@click.option(
    "--tasks",
    type=click.Path(exists=True),
    help="Path to tasks.json (default: data/tasks.json)",
)
@click.option(
    "--state",
    type=click.Path(),
    help="Path to state.json (default: data/state.json)",
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to blocks_config.yaml",
)
@click.option(
    "--out",
    type=click.Path(),
    help="Output path for plan",
)
@click.option(
    "--date",
    help="Date in ISO format (YYYY-MM-DD, default: today)",
)
def plan(
    tasks: str | None,
    state: str | None,
    config: str | None,
    out: str | None,
    date: str | None,
) -> None:
    """Generate today's focus block plan."""
    path_resolver = PathResolver()
    path_resolver.ensure_directories()

    tasks_path = path_resolver.resolve(tasks, path_resolver.tasks_path)
    state_path = path_resolver.resolve(state, path_resolver.state_path)
    config_path = path_resolver.resolve(config, PathResolver.get_config_path())

    plan_date = parse_date(date)

    if out:
        output_path = path_resolver.resolve(out, path_resolver.get_plan_path(plan_date))
    else:
        output_path = path_resolver.get_plan_path(plan_date)

    use_case = PlanGenerationUseCase()

    result_path = use_case.execute(
        tasks_path=str(tasks_path),
        state_path=str(state_path),
        config_path=str(config_path),
        output_path=str(output_path),
        date=plan_date,
    )

    plan_repo = PlanRepository()
    config_repo = ConfigRepository()
    task_repo = TaskRepository()

    plan_obj = plan_repo.load_plan(result_path)
    config_data = config_repo.load_config(config_path)
    tasks_data = task_repo.load_tasks(tasks_path)

    click.echo(f"[OK] Focus Block Plan generated: {result_path}\n")
    click.echo(PlanFormatter.format_daily_plan(plan_obj, config_data, tasks_data))

    blocks_per_day = config_data.get("blocks_per_day", 5)
    click.echo(
        f"\n[Tip] Using {blocks_per_day}-block system. Want different? Edit {config_path}"
    )


@click.command()
@click.option("--date", help="Date to show (YYYY-MM-DD, defaults to today)")
def show(date: str | None) -> None:
    """Show today's plan and status."""
    path_resolver = PathResolver()

    status_date = parse_date(date)
    plan_path = path_resolver.get_plan_path(status_date)
    log_path = path_resolver.get_log_path(status_date)
    tasks_path = path_resolver.tasks_path

    if plan_path.exists():
        plan_repo = PlanRepository()
        plan = plan_repo.load_plan(plan_path)

        task_repo = TaskRepository()
        tasks = task_repo.load_tasks(tasks_path) if tasks_path.exists() else []
        task_lookup = {task.title: task for task in tasks}

        actual_logs = []
        if log_path.exists():
            actual_logs = read_jsonl(log_path)

        block_to_log = {}
        for log in actual_logs:
            if "block" in log:
                block_to_log[log["block"]] = log

        click.echo(f"[Calendar] Today's Plan ({status_date}):")
        click.echo("=" * 50)
        for block in plan.blocks:
            actual_log = block_to_log.get(block.block)

            task_title = block.title
            if ":" in block.title:
                parts = block.title.split(": ", 1)
                if len(parts) > 1:
                    task_title = parts[1]

            task = task_lookup.get(task_title)
            task_prefix = f"Task #{task.id}: " if task else ""

            if block.status == "done":
                if actual_log:
                    actual_bucket = actual_log.get("actual_bucket", "")
                    actual_title = actual_log.get("actual_title", "")
                    planned_bucket = block.bucket
                    planned_title = block.title

                    bucket_changed = actual_bucket != planned_bucket
                    title_changed = actual_title != planned_title

                    if bucket_changed or title_changed:
                        status = "[PREEMPTED]"
                        click.echo(
                            f"{status} Block {block.block}: {task_prefix}{planned_title}"
                        )
                        click.echo(
                            f"  -> Actually did: {actual_bucket} - {actual_title}"
                        )
                    else:
                        status = "[DONE]"
                        click.echo(
                            f"{status} Block {block.block}: {task_prefix}{block.title}"
                        )
                else:
                    status = "[DONE]"
                    click.echo(
                        f"{status} Block {block.block}: {task_prefix}{block.title}"
                    )
            else:
                status = "[PENDING]"
                click.echo(f"{status} Block {block.block}: {task_prefix}{block.title}")
        click.echo("=" * 50)

        if actual_logs:
            click.echo(f"\n[Logged] Actual Work Done ({len(actual_logs)} entries):")
            click.echo("-" * 50)
            for i, log in enumerate(actual_logs, 1):
                bucket = log.get("actual_bucket", "Unknown")
                title = log.get("actual_title", "No title")
                if "block" in log:
                    click.echo(f"{i}. Block {log['block']}: {bucket} - {title}")
                else:
                    task_id = log.get("task_id", "?")
                    click.echo(f"{i}. Task {task_id}: {bucket} - {title}")

    else:
        click.echo(f"[Calendar] No plan for {status_date}")
        click.echo("[Tip] Generate one with: markov-dayflow plan generate")

    tasks_path = path_resolver.tasks_path
    if tasks_path.exists():
        task_repo = TaskRepository()
        tasks = task_repo.load_tasks(tasks_path)

        click.echo("\n" + TaskFormatter.format_task_summary(tasks))
