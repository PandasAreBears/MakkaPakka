import subprocess
from pathlib import Path
from typing import List
from typing import Tuple
from uuid import uuid4

from makka_pakka import settings
from makka_pakka.elf_caver.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.elf_caver.injector.byte_extraction import (
    to_little_endian_32bit,
)


def change_entrypoint(target_binary: str, entrypoint: int, output: str = ""):
    """
    Change the entrypoint of an elf64 file.

    :param target_binary: The target binary to change the entrypoint of.
    :param entrypoint: The new entrypoint to change to.
    :param output: The output binary with the new entrypoint.
    :return: The output filepath.
    """
    if not isinstance(target_binary, str) or not Path(target_binary).exists():
        raise MKPKInvalidParameter("target_binary", "change_entrypoint", target_binary)
    if not isinstance(entrypoint, int) or not 0 <= entrypoint <= 2**32:
        raise MKPKInvalidParameter("entrypoint", "change_entrypoint", entrypoint)
    if not isinstance(output, str):
        raise MKPKInvalidParameter("output", "change_entrypoint", output)

    if settings.verbosity:
        print(f"Patching entrypoint with new address: {hex(entrypoint)}")

    if output == "":
        output = f"/tmp/{uuid4()}"

    # The entrypoint is a little-endian 64-bit value starting from 0x18
    entrypoint_offset = 0x18

    # Realistically the entrypoint will only require a 32-bit value.
    entrypoint_size = 0x4

    with open(target_binary, "rb") as input_file:
        byte_array = bytearray(input_file.read())

        le_bytes = to_little_endian_32bit(entrypoint)
        byte_array[entrypoint_offset : entrypoint_offset + entrypoint_size] = le_bytes

    with open(output, "wb") as output_file:
        output_file.write(byte_array)

    return output


def patch_pltsec_exit(target_binary: str, inject_offset: int, output: str = "") -> str:
    """
    Patches the address of the exit functions in .plt.sec. Code at the patched address
    will be executed on process exit (under certain conditions). This function
    calculates the address using the offset of the code in the binary (this is to comply
    with PIE restrictions).

    :param target_binary: The binary the patch the .plt.sec exit entries in.
    :param inject_offset: The offset into the binary that will be executed on
        process exit.
    :param output: Optional The file to save the patched binary to.
    :return: The filepath of the patched binary.
    """
    if not isinstance(target_binary, str) or not Path(target_binary).exists():
        raise MKPKInvalidParameter("target_binary", "patch_pltsec_exit")

    if not isinstance(inject_offset, int):
        raise MKPKInvalidParameter("inject_offset", "patch_pltsec_exit")

    if not isinstance(output, str):
        raise MKPKInvalidParameter("output", "patch_pltsec_exit")

    if output == "":
        output = f"/tmp/{uuid4()}"

    # Uses grep to get the exit@plt offset. This is a little hacky, but I can't think
    # of a cleaner way to do this, so maybe change in future.
    cmd: str = f"objdump -d {target_binary} | egrep '<_?exit@plt>:'"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    proc.wait()

    # Store each exit entry in a list of strings
    # e.g entry: '00000000000023b0 <_exit@plt>:'
    entries = proc.communicate()[0].decode("utf-8").split("\n")[:-1]

    # .plt.sec entries start with a 4-byte 'endbr64' instruction that we do not want to
    # overwrite
    SKIP_BYTES: int = 4
    patches: List[Tuple[List[int], int, int]] = []
    for entry in entries:
        entry_offset = int(entry.split(" ")[0], 16)

        # The formula for the relative address is: '({shellcode offset} - {.plt.sec
        # entry offset}) - 9
        relative_address = (inject_offset - entry_offset) - 9
        patch_address = to_little_endian_32bit(relative_address)

        # The full shellcode to rewrite into the .plt.sec entry, in asm:
        #   jmp {injection offset}
        #   nop
        #   nop
        patch_shellcode = [233] + list(patch_address) + [90, 90]
        patch_size = len(patch_shellcode)
        patch_offset = entry_offset + SKIP_BYTES

        patches += [(patch_shellcode, patch_size, patch_offset)]

    with open(target_binary, "rb") as input_file:
        byte_array = bytearray(input_file.read())

    # Patch the new addresses into the bytearray
    for p_shellcode, p_size, p_offset in patches:
        if settings.verbosity:
            print(
                (
                    "Patching process exit address:\n"
                    f"\tShellcode: {p_shellcode}\n"
                    f"\tSize: {p_size}\n"
                    f"\tOffset: {hex(p_offset)}"
                )
            )
        byte_array[p_offset : p_offset + p_size] = p_shellcode

    with open(output, "wb") as output_file:
        output_file.write(byte_array)

    return output
