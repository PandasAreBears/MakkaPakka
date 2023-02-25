import subprocess
from typing import Tuple

from makka_pakka.elf_caver.exceptions.exceptions import MKPKInvalidParameter


def extract_bytes(binary_filepath: str) -> str:
    """
    Extracts the bytes from a hex file and returns them as a concatenated string.

    :param binary_filepath: The filepath string to the binary to extract bytes from.
    :return: The bytes as a continuous string i.e "12 34 56..."
    """

    cmd: str = f"xxd {binary_filepath} | cut -d ' ' -f2-10"
    proc = subprocess.Popen(cmd)
    bytes_content = proc.communicate()[0]

    return bytes_content.replace("\n", "").replace(" ", "")


def to_little_endian_32bit(value: int) -> Tuple[int, int, int, int]:
    """
    Converts a 32-bit value to little endian byte array
    """
    if not isinstance(value, int):
        raise MKPKInvalidParameter("value", "to_little_endian_32bit", value)
    byte1 = value & 0x000000FF
    byte2 = (value & 0x0000FF00) >> 8
    byte3 = (value & 0x00FF0000) >> 16
    byte4 = (value & 0xFF000000) >> 24

    return byte1, byte2, byte3, byte4
