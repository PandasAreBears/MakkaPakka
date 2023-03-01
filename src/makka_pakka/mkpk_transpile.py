import click

from makka_pakka.integrating.integrate import integrate_makka_pakka
from makka_pakka.linking.linker import parse_link_and_merge
from makka_pakka.processing.process import process_makka_pakka


@click.command()
@click.argument("mkpk_filepath")
@click.option(
    "-o",
    "--output",
    "output_filepath",
    default="",
    help="The filepath to output the transpiled makka pakka code to.",
    required=False,
)
def mkpk_transpile(mkpk_filepath, output_filepath):
    if not mkpk_filepath:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    linked = parse_link_and_merge(mkpk_filepath)
    processed = process_makka_pakka(linked)
    output_file = integrate_makka_pakka(processed, output_filepath)

    click.echo(f"Output: {output_file}")


if __name__ == "__main__":
    mkpk_transpile()
