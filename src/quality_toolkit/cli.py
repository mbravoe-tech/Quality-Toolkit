from __future__ import annotations

import click
from pandas.errors import EmptyDataError

from .analysis import evaluate_data_quality
from .data_loader import load_dataset
from .report import build_markdown_report


@click.command()
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option(
    "--sample-size",
    default=5,
    show_default=True,
    help="Number of sample values to include per column.",
)
@click.option(
    "--delimiter",
    default=None,
    help="Override the automatically detected delimiter.",
)
def main(source: str, sample_size: int, delimiter: str | None) -> None:
    """Generate a quick data-quality report for ``source``."""

    try:
        dataset = load_dataset(source, delimiter=delimiter)
    except FileNotFoundError as error:
        raise click.ClickException(str(error)) from error
    except ValueError as error:
        raise click.ClickException(str(error)) from error
    except EmptyDataError as error:
        raise click.ClickException("The input file contains no rows.") from error

    try:
        quality = evaluate_data_quality(dataset, sample_size=sample_size)
    except ValueError as error:
        raise click.ClickException(str(error)) from error

    click.echo(build_markdown_report(quality))


if __name__ == "__main__":
    main()
