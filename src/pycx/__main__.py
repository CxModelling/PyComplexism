"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """PyCx."""


if __name__ == "__main__":
    main(prog_name="pycx")  # pragma: no cover
