import click

from makka_pakka import settings
from makka_pakka.elf_caver.injector.binary_injector import (
    inject_nasm_into_binary,
)
from makka_pakka.integrating.integrate import integrate_makka_pakka
from makka_pakka.linking.linker import parse_link_and_merge
from makka_pakka.processing.process import process_makka_pakka


@click.command()
@click.argument("mkpk_filepath")
@click.argument("target_binary")
@click.option(
    "-o",
    "--output-file",
    "output_file",
    default="",
    help="The filepath to output the injected binary to.",
)
@click.option(
    "-n",
    "--patch-entrypoint",
    "patch_entrypoint",
    is_flag=True,
    default=False,
    help="Patches the entrypoint to point to injected code.",
)
@click.option(
    "-e",
    "--patch-exit",
    "patch_exit",
    is_flag=True,
    default=False,
    help="Patches the process exit to point to the injected code.",
)
@click.option(
    "-v",
    "--verbose",
    "verbose",
    is_flag=True,
    default=False,
    help="Logs a verbose output to stdout.",
)
def mkpk(
    mkpk_filepath,
    target_binary,
    output_file,
    patch_entrypoint,
    patch_exit,
    verbose,
):
    if not mkpk_filepath or not target_binary:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    settings.set_verbosity(True if verbose else False)

    output_asm_file = ""
    if output_file != "":
        output_asm_file = f"{output_file}.asm"

    linked = parse_link_and_merge(mkpk_filepath)
    processed = process_makka_pakka(linked)
    asm_file = integrate_makka_pakka(processed, output_asm_file)

    click.echo(f"Generated .asm file - {asm_file}")
    output_file: str = inject_nasm_into_binary(
        asm_file,
        target_binary,
        output_filepath=output_file,
        patch_entrypoint=patch_entrypoint,
        patch_exit=patch_exit,
    )
    click.echo(f"Injected {asm_file} into {output_file}")


if __name__ == "__main__":
    mkpk()
