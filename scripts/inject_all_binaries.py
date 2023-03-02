import subprocess
from pathlib import Path

import click


@click.command()
@click.argument("mkpk_filepath")
@click.argument("parent_directory")
@click.option(
    "-o",
    "--output",
    "output_filepath",
    default="/tmp/",
    help="The filepath to output injected binaries to.",
    required=False,
)
@click.option(
    "-v",
    "--verbose",
    "verbose",
    is_flag=True,
    default=False,
    help="Logs a verbose output to stdout.",
)
def main(
    mkpk_filepath: str,
    parent_directory: str,
    output_filepath: str,
    verbose: bool,
) -> None:
    """
    Injects a .mkpk file into all elf64 files in a given directory.

    :param mkpk_filepath: The filepath to the .mkpk to inject.
    :param parent_directory: The parent directory of the ELF binaries to
    inject into.
    """
    if not mkpk_filepath or not parent_directory:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    if not Path(mkpk_filepath).exists():
        raise FileNotFoundError(f"{mkpk_filepath} file doesn't exist.")
    if not Path(mkpk_filepath).is_file():
        raise TypeError(f"{mkpk_filepath} is not a file.")
    if not Path(parent_directory).exists():
        raise FileNotFoundError(f"{parent_directory} path doesn't exist.")
    if not Path(parent_directory).is_dir():
        raise TypeError(f"{parent_directory} is not a directory.")

    if not Path(output_filepath).exists():
        if verbose:
            print(f"Creating directory: {output_filepath}")
        Path(output_filepath).mkdir(parents=True, exist_ok=True)

    # Iterate all the files in the parent directory.
    for target in [
        path for path in Path(parent_directory).glob("**/*") if path.is_file()
    ]:
        # Check that the file is an elf64.
        command: str = f"readelf -h {target}"
        proc = subprocess.run(command, shell=True, capture_output=True)

        if proc.returncode != 0:
            continue

        if "ELF64" not in str(proc.stdout):
            print(f"{target} is ELF, but not ELF64. Skipping.")
            continue

        command: str = (
            "mkpk "
            f"{mkpk_filepath} "
            f"{target} "
            f"-o {output_filepath}/{Path(target).name}_injected "
            f"-e"
        )

        if verbose:
            print(f"Running command: {command}")

        # Run the mkpk command.
        proc = subprocess.run(command, shell=True, capture_output=True)

        if proc.returncode != 0:
            print(f"Failed to inject into {target}.")
            if verbose:
                print(proc.stdout)
                print(proc.stderr)

        else:
            print(
                (
                    f"Successfully injected into {target}."
                    f"Stored in {Path(target).name}_injected."
                )
            )


if __name__ == "__main__":
    main()
