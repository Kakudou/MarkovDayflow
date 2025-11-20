"""Reporting and status commands."""

from pathlib import Path

import click

from markov_dayflow.adapters.repositories import (
    ConfigRepository,
)
from markov_dayflow.adapters.visualization import GanttGenerator, PieChartGenerator
from markov_dayflow.application.usecases.reporting import ReportingUseCase
from markov_dayflow.application.usecases.weekly_reset import WeeklyResetUseCase
from markov_dayflow.infrastructure.utils import PathResolver, parse_date, read_jsonl


@click.command()
@click.option("--state", type=click.Path(), help="Path to state.json")
@click.option("--config", type=click.Path(exists=True), help="Path to config.yaml")
@click.option("--plans-dir", type=click.Path(), help="Directory with plan files")
@click.option("--with-chart", is_flag=True, help="Include Gantt chart and pie chart")
def report(
    state: str | None,
    config: str | None,
    plans_dir: str | None,
    with_chart: bool,
) -> None:
    """Generate weekly report."""
    path_resolver = PathResolver()

    state_path = path_resolver.resolve(state, path_resolver.state_path)
    config_path = path_resolver.resolve(config, PathResolver.get_config_path())
    plans_dir_path = Path(plans_dir) if plans_dir else path_resolver.plans_dir

    use_case = ReportingUseCase()
    report_data = use_case.execute(
        str(state_path),
        str(config_path),
        str(plans_dir_path),
        str(path_resolver.logs_dir),
    )

    click.echo("\n[Chart] Weekly Report")
    click.echo("=" * 60)
    click.echo(f"Week: {report_data['week_start']}")
    click.echo(f"Total blocks: {report_data['total_blocks']}")

    click.echo("\nPlanning Bucket Distribution (sorted by deviation):")
    click.echo("-" * 60)
    click.echo(f"{'Bucket':<12} {'Target':<10} {'Realized':<10} {'Error':<10}")
    click.echo("-" * 60)

    buckets_by_error = sorted(
        report_data["target_ratios"].keys(),
        key=lambda b: abs(report_data["ratio_errors"].get(b, 0.0)),
        reverse=True,
    )

    for i, bucket in enumerate(buckets_by_error):
        target = report_data["target_ratios"][bucket]
        realized = report_data["realized_ratios"].get(bucket, 0.0)
        error = report_data["ratio_errors"].get(bucket, 0.0)

        target_pct = f"{target:.1%}"
        realized_pct = f"{realized:.1%}"
        error_pct = f"{error:+.1%}"

        comment = ""
        if i == 0:
            comment = "  <- Biggest deviation"
        elif i == len(buckets_by_error) - 1:
            comment = "  <- Smallest deviation"

        click.echo(
            f"{bucket:<12} {target_pct:<10} {realized_pct:<10} {error_pct:<10}{comment}"
        )

    if "original_buckets" in report_data:
        orig = report_data["original_buckets"]
        click.echo(
            f"\nActual Work Logged ({orig['total_entries']} entries, sorted by time spent):"
        )
        click.echo("-" * 60)
        click.echo(f"{'Bucket':<15} {'Count':<8} {'Percentage':<10}")
        click.echo("-" * 60)

        buckets_by_count = sorted(
            orig["bucket_counts"].keys(),
            key=lambda b: orig["bucket_counts"][b],
            reverse=True,
        )

        for i, bucket in enumerate(buckets_by_count):
            count = orig["bucket_counts"][bucket]
            pct = orig["bucket_percentages"][bucket]

            comment = ""
            if i == 0:
                comment = "  <- Most time"
            elif i == len(buckets_by_count) - 1:
                comment = "  <- Least time"

            click.echo(f"{bucket:<15} {count:<8} {pct:.1%}{comment}")

        if "chaos_breakdown" in orig:
            chaos = orig["chaos_breakdown"]
            click.echo("\nChaos Bucket Breakdown (sorted by time):")
            click.echo("-" * 40)

            chaos_buckets_by_count = sorted(
                chaos["counts"].keys(), key=lambda b: chaos["counts"][b], reverse=True
            )

            for i, bucket in enumerate(chaos_buckets_by_count):
                count = chaos["counts"][bucket]
                pct = chaos["percentages"][bucket]

                comment = ""
                if i == 0:
                    comment = "  <- Most chaos"
                elif i == len(chaos_buckets_by_count) - 1:
                    comment = "  <- Least chaos"

                click.echo(f"  {bucket:<12} {count:<8} {pct:.1%}{comment}")

    if "adherence" in report_data:
        click.echo("\nPlan Adherence:")
        click.echo("-" * 60)
        adh = report_data["adherence"]
        click.echo(
            f"Completion: {adh['completion_rate']:.1%} "
            f"({adh['done_blocks']}/{adh['total_blocks']})"
        )
        click.echo(f"On-plan: {adh['on_plan_rate']:.1%}")

    if with_chart:
        config_repo = ConfigRepository()
        config_data = config_repo.load_config(config_path)

        global_gantt = GanttGenerator.generate_global_gantt(
            plans_dir_path, path_resolver.logs_dir, config_data
        )
        if global_gantt:
            click.echo("\n[Chart] Global Mermaid Gantt Chart:")
            click.echo("```mermaid")
            click.echo(global_gantt)
            click.echo("```")

        all_logs = []
        if path_resolver.logs_dir.exists():
            for file in path_resolver.logs_dir.iterdir():
                if file.name.startswith("actual_") and file.name.endswith(".jsonl"):
                    all_logs.extend(read_jsonl(file))

        if all_logs:
            global_pie = PieChartGenerator.generate_bucket_distribution(
                all_logs, "Weekly Work Distribution"
            )
            if global_pie:
                click.echo("\n[Chart] Weekly Work Distribution Pie Chart:")
                click.echo("```mermaid")
                click.echo(global_pie)
                click.echo("```")


@click.command(name="weekly-reset")
@click.option("--state", type=click.Path(), help="Path to state.json")
@click.option("--config", type=click.Path(exists=True), help="Path to config.yaml")
@click.option("--week-start", help="Week start date (ISO format, defaults to today)")
def weekly_reset(
    state: str | None,
    config: str | None,
    week_start: str | None,
) -> None:
    """Reset weekly state."""
    path_resolver = PathResolver()

    state_path = path_resolver.resolve(state, path_resolver.state_path)
    config_path = path_resolver.resolve(config, PathResolver.get_config_path())

    week_start_date = parse_date(week_start)

    use_case = WeeklyResetUseCase()
    use_case.execute(str(state_path), str(config_path), week_start_date)

    click.echo(f"[OK] Weekly reset complete (week: {week_start_date})")
