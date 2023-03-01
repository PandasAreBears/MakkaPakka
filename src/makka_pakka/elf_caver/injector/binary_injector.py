import subprocess
from pathlib import Path
from typing import List
from typing import Tuple
from uuid import uuid4

from lief import ELF
from lief import parse

from makka_pakka import settings
from makka_pakka.elf_caver.caver.code_caver import get_code_caves
from makka_pakka.elf_caver.exceptions.exceptions import ByteExtractionFailed
from makka_pakka.elf_caver.exceptions.exceptions import InsufficientCodeCaves
from makka_pakka.elf_caver.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.elf_caver.formatting.print_elf import pprint_header
from makka_pakka.elf_caver.injector.compile import compile
from makka_pakka.elf_caver.injector.redirect_execution import change_entrypoint
from makka_pakka.elf_caver.injector.redirect_execution import patch_pltsec_exit


def inject_nasm_into_binary(
    nasm_filepath: str,
    target_binary_filepath: str,
    output_filepath: str = "",
    **kwargs,
) -> str:
    """
    Injects a nasm source file into binary.

    :param nasm_filepath: The filepath of the nasm file to inject.
    :param target_binary_filepath: The filepath of the binary to inject into.
    :param output_filepath: Optional The filepath to output the injected binary to.
    :param kwargs:
        *patch_entrypoint* Whether the entrypoint of the output binary should be patched
        to point to the code cave.
        *patch_exit* Whether the process exit of the output binary should be patched to
        point to the code cave.
    :return: The filepath to the injected binary.
    :throws:
        InsufficientCodeCaves -> There was not a large enough code cave in the target
            binary to inject into.
        MKPKInvalidParameter -> A parameter was malformed.
    """
    patch_entrypoint = (
        kwargs["patch_entrypoint"] if "patch_entrypoint" in kwargs else False
    )
    patch_exit = kwargs["patch_exit"] if "patch_exit" in kwargs else False

    if not isinstance(nasm_filepath, str) or not Path(nasm_filepath).exists():
        raise MKPKInvalidParameter(
            "nasm_filepath", "inject_nasm_into_binary", nasm_filepath
        )

    if (
        not isinstance(target_binary_filepath, str)
        or not Path(target_binary_filepath).exists()
    ):
        raise MKPKInvalidParameter(
            "target_binary_filepath",
            "inject_nasm_into_binary",
            target_binary_filepath,
        )

    if not isinstance(output_filepath, str):
        raise MKPKInvalidParameter(
            "output_filepath", "inject_nasm_into_binary", output_filepath
        )

    if not isinstance(patch_entrypoint, bool):
        raise MKPKInvalidParameter(
            "patch_entrypoint", "inject_nasm_into_binary", patch_entrypoint
        )

    if not isinstance(patch_exit, bool):
        raise MKPKInvalidParameter(
            "patch_exit", "inject_nasm_into_binary", patch_entrypoint
        )

    shellcode = _get_shellcode_from_nasm(nasm_filepath)[0]
    shellcode_size: int = len(shellcode)

    target_binary: ELF.Binary = parse(target_binary_filepath)
    if settings.verbosity:
        pprint_header(target_binary)

    code_caves: List[Tuple[int, int]] = get_code_caves(target_binary)
    if settings.verbosity:
        if code_caves:
            print(
                f"Found code cave with size {code_caves[0][1]} at offset \
{hex(code_caves[0][0])}"
            )
        else:
            print("Couldn't find any code caves.")

    # Select the first code cave that's large enough to inject into.
    inject_offset = -1
    for offset, size in code_caves:
        if size > shellcode_size:
            inject_offset = offset
            break

    if -1 == inject_offset:
        raise InsufficientCodeCaves

    # Inject the shellcode into the binary
    output_file = _inject_shellcode_at_offset(
        shellcode,
        target_binary_filepath,
        inject_offset,
        output=output_filepath,
    )

    if patch_entrypoint:
        change_entrypoint(output_file, inject_offset, output_file)

    if patch_exit:
        patch_pltsec_exit(output_file, inject_offset, output_file)

    if not patch_entrypoint and not patch_exit:
        print(
            "Warning: Shellcode address has not been patch, therefore will not \
run without manual redirection. Use --help for patching options."
        )

    # Make the file executable.
    subprocess.run(f"chmod +x {output_file}", shell=True)

    return output_file


def _get_shellcode_from_nasm(nasm_filepath: str) -> List[int]:
    """
    Gets the shellcode bytes from a .nasm file

    :param nasm_filepath: The filepath of the nasm file to get the shellcode from.
    :return: A list of shellcode bytes.
    """
    if not isinstance(nasm_filepath, str):
        raise MKPKInvalidParameter(
            "nasm_filepath", "_get_shellcode_from_nasm", nasm_filepath
        )

    if not Path(nasm_filepath).exists():
        raise FileNotFoundError

    generated_files: List[str] = compile(nasm_filepath, "elf64")

    bytes_filename: str = f"{generated_files[1]}.bytes"
    with open(bytes_filename, "w") as outfile:
        cmd: str = f"objdump -d {generated_files[0]} | grep '^ ' | cut -f2"
        proc = subprocess.Popen(cmd, shell=True, stdout=outfile)
        proc.wait()

    if Path(bytes_filename).stat().st_size == 0:
        raise ByteExtractionFailed

    bytes_content: List[int] = []
    with open(bytes_filename, "r") as bytes_file:
        for line in bytes_file:
            for byte in line.strip().split(" "):
                bytes_content += [int(byte, 16)]

    return bytes_content, bytes_filename


def _inject_shellcode_at_offset(
    shellcode: List[int], target_binary: str, offset: int, output: str = ""
) -> str:
    """
    Injects shellcode into the binary at a given offset.

    :param shellcode: The shellcode bytes to inject into the binary.
    :param target_binary: The filepath to the binary to inject the shellcode into.
    :param offset: The offset into the binary where the shellcode should be injected.
    :param output: The filepath to where the patch binary should be created.
    :return: A filepath to the output binary.
    """
    if not isinstance(shellcode, list) or not all(
        [isinstance(byte, int) and byte < 256 for byte in shellcode]
    ):
        raise MKPKInvalidParameter(
            "shellcode", "_inject_shellcode_at_offset", shellcode
        )

    if not isinstance(target_binary, str) or not Path(target_binary).exists():
        raise MKPKInvalidParameter(
            "target_binary", "_inject_shellcode_at_offset", target_binary
        )

    if not isinstance(offset, int):
        raise MKPKInvalidParameter("offset", "_inject_shellcode_at_offset", offset)

    if not isinstance(output, str):
        raise MKPKInvalidParameter("output", "_inject_shellcode_at_offset", output)

    if output == "":
        output = f"/tmp/{uuid4()}"

    with open(target_binary, "rb") as input_file:
        raw_bytes = input_file.read()
        byte_array = bytearray(raw_bytes)
        byte_array[offset : offset + len(shellcode)] = shellcode

        with open(output, "wb") as output_file:
            output_file.write(byte_array)

    return output
