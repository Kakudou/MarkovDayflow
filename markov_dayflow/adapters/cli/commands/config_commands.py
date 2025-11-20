"""Configuration display commands."""

from pathlib import Path

import click

from markov_dayflow.adapters.repositories import ConfigRepository


@click.command()
@click.option("--config", type=click.Path(exists=True), help="Path to config.yaml")
def config(config_path: str | None) -> None:
    """Show current block configuration."""
    if config_path:
        resolved_path = config_path
    else:
        package_dir = Path(__file__).parent.parent.parent.parent
        resolved_path = str(
            package_dir / "infrastructure" / "config" / "blocks_config.yaml"
        )

    config_repo = ConfigRepository()
    config_data = config_repo.load_config(resolved_path)

    blocks_per_day = config_data.get("blocks_per_day", 5)
    block_config = config_data.get("block_config", {})

    click.echo(f"[Tasks] Current Block Configuration ({resolved_path}):")
    click.echo("=" * 60)
    click.echo(f"Blocks per day: {blocks_per_day}")
    click.echo()

    for block_num in range(1, blocks_per_day + 1):
        if block_num in block_config:
            block = block_config[block_num]
            name = block.get("name", f"Block {block_num}")
            duration = block.get("duration_hours", 1.0)
            preferred = ", ".join(block.get("preferred_buckets", []))
            avoided = ", ".join(block.get("avoid_buckets", []))

            click.echo(f"Block {block_num}: {name} ({duration}h)")
            click.echo(f"  Preferred: {preferred}")
            if avoided:
                click.echo(f"  Avoided: {avoided}")
            click.echo()
        else:
            click.echo(f"Block {block_num}: No configuration found")
            click.echo()

    click.echo("[Tip] To customize: Edit the configuration file above")
