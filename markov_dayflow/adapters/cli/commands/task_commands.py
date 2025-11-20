"""Task management commands."""

import click

from markov_dayflow.adapters.cli.formatters import TaskFormatter
from markov_dayflow.adapters.repositories import TaskRepository
from markov_dayflow.domain.entities import Task
from markov_dayflow.domain.value_objects.task_size import TASK_SIZE_HOURS
from markov_dayflow.infrastructure.utils import PathResolver, parse_date


@click.command(name="add-task")
@click.argument("bucket")
@click.argument("title")
@click.option("--urgency", type=click.IntRange(0, 5), default=2, help="Urgency 0-5")
@click.option("--impact", type=click.IntRange(1, 5), default=3, help="Impact 1-5")
@click.option(
    "--size",
    type=click.Choice(["XS", "S", "M", "L", "XL"], case_sensitive=False),
    default="M",
    help="T-shirt size: XS(0.5h), S(1h), M(2h), L(4h), XL(8h)",
)
@click.option(
    "--difficulty", type=click.IntRange(0, 5), default=2, help="Difficulty 0-5"
)
@click.option(
    "--status",
    type=click.Choice(["todo", "planned", "wip"], case_sensitive=False),
    default="todo",
    help="Task status",
)
@click.option("--planned", help="Planned date (ISO format or 'today')")
@click.option("--deadline", type=int, help="Days until deadline")
@click.option("--sla-penalty", type=float, default=0.0, help="SLA penalty")
def add_task(
    bucket: str,
    title: str,
    urgency: int,
    impact: int,
    size: str,
    difficulty: int,
    status: str,
    planned: str | None,
    deadline: int | None,
    sla_penalty: float,
) -> None:
    """Add a new task."""
    path_resolver = PathResolver()
    path_resolver.ensure_directories()

    task_repo = TaskRepository()
    tasks_path = path_resolver.tasks_path

    if tasks_path.exists():
        tasks = task_repo.load_tasks(tasks_path)
    else:
        tasks = []

    planned_date = parse_date(planned) if planned else None

    size_hours = TASK_SIZE_HOURS.get(size.upper(), 2.0)

    new_task = Task(
        title=title,
        bucket=bucket,
        urgency=urgency,
        impact=impact,
        size=size_hours,
        difficulty=difficulty,
        status=status,
        planned_date=planned_date,
        sla_penalty=sla_penalty,
        deadline_days=deadline,
    )

    tasks.append(new_task)
    task_repo.save_tasks(tasks_path, tasks)

    click.echo(f"[OK] Added task #{new_task.id}: {title} ({bucket}, {status})")


@click.command()
@click.argument("identifier")
@click.argument(
    "status",
    type=click.Choice(["todo", "planned", "wip", "done"], case_sensitive=False),
)
@click.option("--date", help="Date for planned tasks (defaults to today)")
def mark(identifier: str, status: str, date: str | None) -> None:
    """Mark task with new status."""
    path_resolver = PathResolver()
    task_repo = TaskRepository()
    tasks_path = path_resolver.tasks_path

    if not tasks_path.exists():
        click.echo("[ERROR] No tasks file found. Add tasks first with 'add-task'")
        return

    tasks = task_repo.load_tasks(tasks_path)

    task = None
    if identifier.isdigit():
        task_id = int(identifier)
        for t in tasks:
            if t.id == task_id:
                task = t
                break
        if not task:
            click.echo(f"[ERROR] No task found with ID: {task_id}")
            return
    else:
        matching_tasks = [t for t in tasks if identifier.lower() in t.title.lower()]

        if not matching_tasks:
            click.echo(f"[ERROR] No tasks found matching: {identifier}")
            return
        elif len(matching_tasks) > 1:
            click.echo(f"[ERROR] Multiple tasks found matching '{identifier}':")
            for t in matching_tasks:
                click.echo(f"  #{t.id}: {t.title}")
            click.echo("Use task ID (e.g., 'mark 3 done') for exact match")
            return

        task = matching_tasks[0]

    old_status = task.status
    task.status = status

    if status == "planned":
        task.planned_date = parse_date(date)

    task_repo.save_tasks(tasks_path, tasks)
    click.echo(f"[OK] Marked #{task.id} '{task.title}': {old_status} -> {status}")


@click.command()
@click.argument("identifier")
def remove(identifier: str) -> None:
    """Remove a task."""
    path_resolver = PathResolver()
    task_repo = TaskRepository()
    tasks_path = path_resolver.tasks_path

    if not tasks_path.exists():
        click.echo("[ERROR] No tasks file found. Add tasks first with 'add-task'")
        return

    tasks = task_repo.load_tasks(tasks_path)

    task_to_remove = None
    if identifier.isdigit():
        task_id = int(identifier)
        task_to_remove = task_repo.find_by_id(tasks_path, task_id)
        if not task_to_remove:
            click.echo(f"[ERROR] No task found with ID: {task_id}")
            return
    else:
        matching_tasks = [t for t in tasks if identifier.lower() in t.title.lower()]

        if not matching_tasks:
            click.echo(f"[ERROR] No tasks found matching: {identifier}")
            return
        elif len(matching_tasks) > 1:
            click.echo(f"[ERROR] Multiple tasks found matching '{identifier}':")
            for t in matching_tasks:
                click.echo(f"  #{t.id}: {t.title}")
            click.echo("Use task ID (e.g., 'remove 3') for exact match")
            return

        task_to_remove = matching_tasks[0]

    tasks.remove(task_to_remove)
    task_repo.save_tasks(tasks_path, tasks)
    click.echo(f"[OK] Removed #{task_to_remove.id} '{task_to_remove.title}'")


@click.command(name="edit-task")
@click.argument("identifier")
@click.option("--bucket", help="New bucket name")
@click.option("--title", help="New task title")
@click.option("--urgency", type=click.IntRange(0, 5), help="New urgency 0-5")
@click.option("--impact", type=click.IntRange(1, 5), help="New impact 1-5")
@click.option(
    "--size",
    type=click.Choice(["XS", "S", "M", "L", "XL"], case_sensitive=False),
    help="New T-shirt size: XS(0.5h), S(1h), M(2h), L(4h), XL(8h)",
)
@click.option("--difficulty", type=click.IntRange(0, 5), help="New difficulty 0-5")
@click.option("--deadline", type=int, help="New days until deadline")
@click.option("--sla-penalty", type=float, help="New SLA penalty")
def edit_task(
    identifier: str,
    bucket: str | None,
    title: str | None,
    urgency: int | None,
    impact: int | None,
    size: str | None,
    difficulty: int | None,
    deadline: int | None,
    sla_penalty: float | None,
) -> None:
    """Edit task properties."""
    path_resolver = PathResolver()
    task_repo = TaskRepository()
    tasks_path = path_resolver.tasks_path

    if not tasks_path.exists():
        click.echo("[ERROR] No tasks file found. Add tasks first with 'add-task'")
        return

    tasks = task_repo.load_tasks(tasks_path)

    task = None
    if identifier.isdigit():
        task_id = int(identifier)
        for t in tasks:
            if t.id == task_id:
                task = t
                break
        if not task:
            click.echo(f"[ERROR] No task found with ID: {task_id}")
            return
    else:
        matching_tasks = [t for t in tasks if identifier.lower() in t.title.lower()]

        if not matching_tasks:
            click.echo(f"[ERROR] No tasks found matching: {identifier}")
            return
        elif len(matching_tasks) > 1:
            click.echo(f"[ERROR] Multiple tasks found matching '{identifier}':")
            for t in matching_tasks:
                click.echo(f"  #{t.id}: {t.title}")
            click.echo("Use task ID (e.g., 'edit-task 3 --urgency 4') for exact match")
            return

        task = matching_tasks[0]

    changes = []

    if bucket is not None and bucket != task.bucket:
        old_bucket = task.bucket
        task.bucket = bucket
        changes.append(f"bucket: {old_bucket} -> {bucket}")

    if title is not None and title != task.title:
        old_title = task.title
        task.title = title
        changes.append(f"title: {old_title} -> {title}")

    if urgency is not None and urgency != task.urgency:
        old_urgency = task.urgency
        task.urgency = urgency
        changes.append(f"urgency: {old_urgency} -> {urgency}")

    if impact is not None and impact != task.impact:
        old_impact = task.impact
        task.impact = impact
        changes.append(f"impact: {old_impact} -> {impact}")

    if size is not None:
        task_size = TaskSize.from_string(size)
        if task_size.hours != task.size:
            old_size = TaskSize.from_hours(task.size).name
            task.size = task_size.hours
            changes.append(f"size: {old_size} -> {size}")

    if difficulty is not None and difficulty != task.difficulty:
        old_difficulty = task.difficulty
        task.difficulty = difficulty
        changes.append(f"difficulty: {old_difficulty} -> {difficulty}")

    if deadline is not None and deadline != task.deadline_days:
        old_deadline = task.deadline_days
        task.deadline_days = deadline
        changes.append(f"deadline: {old_deadline} -> {deadline}")

    if sla_penalty is not None and sla_penalty != task.sla_penalty:
        old_sla = task.sla_penalty
        task.sla_penalty = sla_penalty
        changes.append(f"sla_penalty: {old_sla} -> {sla_penalty}")

    if not changes:
        click.echo(f"[INFO] No changes made to task #{task.id} '{task.title}'")
        return

    task_repo.save_tasks(tasks_path, tasks)

    click.echo(f"[OK] Updated task #{task.id} '{task.title}':")
    for change in changes:
        click.echo(f"  - {change}")


@click.command()
@click.option(
    "--status",
    type=click.Choice(["todo", "planned", "wip", "done"], case_sensitive=False),
    help="Filter by status",
)
@click.option(
    "--exclude-status",
    type=click.Choice(["todo", "planned", "wip", "done"], case_sensitive=False),
    help="Exclude tasks with this status",
)
def tasks(status: str | None, exclude_status: str | None) -> None:
    """List tasks."""
    path_resolver = PathResolver()
    task_repo = TaskRepository()
    tasks_path = path_resolver.tasks_path

    if not tasks_path.exists():
        click.echo("[ERROR] No tasks file found. Add tasks first with 'add-task'")
        return

    task_list = task_repo.load_tasks(tasks_path)

    if status:
        task_list = [t for t in task_list if t.status == status]
    elif exclude_status:
        task_list = [t for t in task_list if t.status != exclude_status]

    click.echo(TaskFormatter.format_task_list(task_list))

    if task_list:
        click.echo("\n[Tip] Tip: Use task IDs for quick commands (e.g., 'mark 3 done')")
