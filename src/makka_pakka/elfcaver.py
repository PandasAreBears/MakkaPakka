import click

from makka_pakka.elf_caver.injector.binary_injector import (
    inject_nasm_into_binary,
)


@click.command()
@click.option(
    "-a",
    "--asm-file",
    "asm_file",
    help="The filepath of the .asm file to inject.",
    required=True,
)
@click.option(
    "-t",
    "--target-file",
    "target_file",
    help="The filepath of the binary to inject into.",
    required=True,
)
@click.option(
    "-o",
    "--output-file",
    "output_file",
    default="",
    help="The filepath to output the injected binary to.",
    required=True,
)
@click.option(
    "-n",
    "--patch-entrypoint",
    "patch_entrypoint",
    is_flag=True,
    default=False,
    help="(Optional) Patches the entrypoint to point to injected code.",
)
@click.option(
    "-e",
    "--patch-exit",
    "patch_exit",
    is_flag=True,
    default=False,
    help="(Optional) Patches the process exit to point to the injected code.",
)
def elfcaver(asm_file, target_file, output_file, patch_entrypoint, patch_exit):
    if not asm_file or not target_file:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    output_file: str = inject_nasm_into_binary(
        asm_file,
        target_file,
        output_filepath=output_file,
        patch_entrypoint=patch_entrypoint,
        patch_exit=patch_exit,
    )
    click.echo(f"Injected {asm_file} into {output_file}")


if __name__ == "__main__":
    elfcaver()
