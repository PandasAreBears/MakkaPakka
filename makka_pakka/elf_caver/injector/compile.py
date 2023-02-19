import subprocess
from os.path import splitext
from typing import List


def compile(filepath: str, target_arch: str) -> List[str]:
    """
    Compiles a .asm file

    :param filepath: A filepath to the .asm file to be compiled
    :param target_arch: The architecture target of the compilation
    :return: A list of files created by this function
    """
    # Strip the extension from the filepath
    filepath_no_ext = splitext(filepath)[0]

    result = subprocess.run(
        [
            "nasm",
            "-f",
            target_arch,
            "-o",
            filepath_no_ext + ".o",
            filepath,
        ],
        capture_output=True,
    )

    if result.stderr:
        raise Exception(result.stderr)

    result = subprocess.run(["ld", filepath_no_ext + ".o", "-o", filepath_no_ext])

    if result.stderr:
        raise Exception(result.stderr)

    return [filepath_no_ext + ".o", filepath_no_ext]
