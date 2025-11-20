"""Work logging commands."""

import click

from markov_dayflow.application.usecases.log_actual import LogActualUseCase
from markov_dayflow.domain.entities.task import map_to_planning_bucket
from markov_dayflow.domain.exceptions import BlockAlreadyCompletedException
from markov_dayflow.infrastructure.utils import PathResolver, parse_date


@click.command()
@click.option("--block", type=int, help="Block number for planned work")
@click.option("--task", "task_id", type=int, help="Task ID for unplanned work")
@click.option("--bucket", help="Actual bucket (overrides planned)")
@click.option("--title", help="Actual work done (overrides planned)")
@click.option("--plan", type=click.Path(), help="Path to plan file")
@click.option("--state", type=click.Path(), help="Path to state file")
@click.option("--tasks", type=click.Path(), help="Path to tasks file")
@click.option("--notes", help="Optional notes")
@click.option(
    "--date",
    help="Date for plan file (YYYY-MM-DD, defaults to today, block logging only)",
)
def log(
    block: int | None,
    task_id: int | None,
    bucket: str | None,
    title: str | None,
    plan: str | None,
    state: str | None,
    tasks: str | None,
    notes: str | None,
    date: str | None,
) -> None:
    """Log actual work done."""
    if block is None and task_id is None:
        click.echo("[ERROR] Either --block or --task must be specified")
        raise click.Abort()

    path_resolver = PathResolver()
    path_resolver.ensure_directories()

    log_date = parse_date(date)

    plan_path = path_resolver.resolve(plan, path_resolver.get_plan_path(log_date))
    state_path = path_resolver.resolve(state, path_resolver.state_path)
    tasks_path = path_resolver.resolve(tasks, path_resolver.tasks_path)
    log_path = path_resolver.get_log_path(log_date)

    use_case = LogActualUseCase()

    try:
        if task_id is not None and block is not None:
            result = use_case.execute(
                plan_path=str(plan_path),
                state_path=str(state_path),
                log_path=str(log_path),
                block_number=block,
                task_id=task_id,
                tasks_path=str(tasks_path),
                notes=notes,
            )
            actual_bucket = result["bucket"]
            actual_title = result["title"]
            click.echo(
                f"[OK] Logged block {block}: {actual_bucket} - {actual_title} (task #{task_id} completed in block)"
            )
        elif task_id is not None:
            result = use_case.execute(
                plan_path=str(plan_path),
                state_path=str(state_path),
                log_path=str(log_path),
                task_id=task_id,
                tasks_path=str(tasks_path),
                notes=notes,
            )
            click.echo(f"[OK] Logged completed task {task_id}")
        else:
            result = use_case.execute(
                plan_path=str(plan_path),
                state_path=str(state_path),
                log_path=str(log_path),
                block_number=block,
                actual_bucket=bucket,
                actual_title=title,
                notes=notes,
            )

            actual_bucket = result["bucket"]
            planning_bucket = map_to_planning_bucket(actual_bucket)

            if planning_bucket != actual_bucket:
                click.echo(
                    f"[OK] Logged block {block}: {actual_bucket} - {result['title']} (maps to {planning_bucket} for planning)"
                )
            else:
                click.echo(
                    f"[OK] Logged block {block}: {actual_bucket} - {result['title']}"
                )
    except BlockAlreadyCompletedException as e:
        click.echo(f"[ERROR] {e.message}")
        raise click.Abort()
