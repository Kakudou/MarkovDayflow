"""Main CLI entry point with grouped commands."""

import click

from markov_dayflow.adapters.cli.commands import (
    config_commands,
    logging_commands,
    plan_commands,
    reporting_commands,
    task_commands,
)
from markov_dayflow.application.usecases.plan_generation import PlanGenerationUseCase
from markov_dayflow.infrastructure.utils import PathResolver, parse_date


def show_default_status() -> None:
    """Show daily plan/status when no command is provided."""
    path_resolver = PathResolver()

    status_date = parse_date(None)
    plan_path = path_resolver.get_plan_path(status_date)

    if plan_path.exists():
        ctx = click.Context(plan_commands.show)
        ctx.invoke(plan_commands.show, date=None)
    else:
        click.echo(f"[Info] No plan found for {status_date}. Generating new plan...")

        try:
            path_resolver.ensure_directories()
            tasks_path = path_resolver.tasks_path
            state_path = path_resolver.state_path
            config_path = PathResolver.get_config_path()

            if not tasks_path.exists():
                click.echo(
                    "[ERROR] No tasks file found. Add tasks first with 'task add'"
                )
                return
            if not config_path.exists():
                click.echo("[ERROR] No config file found")
                return

            use_case = PlanGenerationUseCase()

            result_path = use_case.execute(
                tasks_path=str(tasks_path),
                state_path=str(state_path),
                config_path=str(config_path),
                output_path=str(plan_path),
                date=status_date,
                random_seed=None,
            )

            click.echo(f"[OK] Plan generated for {status_date}")

            ctx = click.Context(plan_commands.show)
            ctx.invoke(plan_commands.show, date=None)

        except Exception as e:
            click.echo(f"[ERROR] Failed to generate plan: {e}")


@click.group(invoke_without_command=True)
@click.version_option(version="2.0.0", prog_name="markov-dayflow")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Markov Dayflow - Focus Block Management System.

    A flexible scheduler that learns your work patterns using Markov chains.

    Run without arguments to show today's plan.
    """
    if ctx.invoked_subcommand is None:
        show_default_status()


@click.group()
def task():
    """Manage tasks (add, list, edit, update, delete)."""
    pass


task.add_command(task_commands.add_task, name="add")
task.add_command(task_commands.tasks, name="list")
task.add_command(task_commands.edit_task, name="edit")
task.add_command(task_commands.mark, name="update")
task.add_command(task_commands.remove, name="delete")


@click.group(invoke_without_command=True)
@click.pass_context
def plan(ctx: click.Context):
    """Manage daily plans (show, generate, log work)."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(plan_commands.show, date=None)


plan.add_command(plan_commands.show, name="show")
plan.add_command(plan_commands.plan, name="generate")
plan.add_command(logging_commands.log, name="log")


@click.group(invoke_without_command=True)
@click.pass_context
def report(ctx: click.Context):
    """View reports and manage state (weekly report, reset)."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(
            reporting_commands.report,
            state=None,
            config=None,
            plans_dir=None,
            with_chart=False,
        )


report.add_command(reporting_commands.report, name="weekly")
report.add_command(reporting_commands.weekly_reset, name="reset")


cli.add_command(task)
cli.add_command(plan)
cli.add_command(report)
cli.add_command(config_commands.config)


if __name__ == "__main__":
    cli()
