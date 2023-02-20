from pathlib import Path
from typing import List
from uuid import uuid4

from makka_pakka import settings
from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import MKPKIntegratingError
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.processing.processing_structures import MKPKCode


def integrate_makka_pakka(code: MKPKCode, output_filepath: str = "") -> str:
    """
    Runs the integrating phase of makka pakka compilation.

    :param code: The MKPKCode object which as the result of the processing phase.
    :param output_filepath: The filepath to write the integrated code to. This will
        be a random /tmp/{uuid} path if not specified.
    :return: The filepath that the code was written to.
    """
    if not isinstance(code, MKPKCode):
        raise MKPKInvalidParameter("code", "integrate_makka_pakka", code)
    if not isinstance(output_filepath, str):
        raise MKPKInvalidParameter(
            "output_filepath", "integrate_makka_pakka", output_filepath
        )

    if settings.verbosity:
        print("Integrating...")

    # TODO: Integrate the gadgets here.

    # Format the code into a _start function
    code = _format_code_into_asm_function(code)

    # Format the data, then append it to the bottom of the code.
    asm_data: List[str] = _translate_mkpkdata_to_asm(code.data)
    code.code = code.code + [""] + asm_data

    # Finally, write the code to a file.
    return _write_code_to_file(code, output_filepath)


def _write_code_to_file(code: MKPKCode, output_filepath: str = "") -> str:
    """
    Writes makka pakka code into an output filepath.

    :param code: The MKPKCode obj to write to file.
    :param output_filepath: (Optional) The filepath to write the code to. This will
        be a random /tmp/{uuid} path if not specified.
    :return: The filepath that the code was written to.
    """
    if not isinstance(code, MKPKCode):
        raise MKPKInvalidParameter("code", "_write_code_to_file", code)
    if not isinstance(output_filepath, str):
        raise MKPKInvalidParameter(
            "output_filepath", "_write_code_to_file", output_filepath
        )

    # If the filepath is not specified, then generate a random filepath.
    if output_filepath == "":
        output_filepath = f"/tmp/{uuid4()}.asm"

    # Check that the path is valid, and create the file.
    try:
        Path(output_filepath).touch()
    except FileNotFoundError:
        # Pathlib raises a FileNotFound when there's insufficient permissions
        # to create a file at this path.
        raise MKPKIntegratingError(
            "Couldn't create file.",
            f"Creating a file at the path {output_filepath} is invalid.",
            ErrorType.FATAL,
        )

    with open(output_filepath, "w") as output_file:
        for line in code.code:
            output_file.write(line + "\n")

    return output_filepath


def _translate_mkpkdata_to_asm(data: List[MKPKData]) -> List[str]:
    """
    Translates a MKPKData object into assembly data definitions.

    :param data: The MKPKData object to translate into assembly.
    :return: A List of assembly strings, translated from the passed MKPKData.
    """
    if not isinstance(data, list) or not all([isinstance(d, MKPKData) for d in data]):
        raise MKPKInvalidParameter("data", "_translate_mkpkdata_to_asm", data)

    data_asm: List[str] = []

    for mkpk_data in data:
        # Only STR types need to be added as data definitions, as ints will be
        # directly into inserted into data references.
        if mkpk_data.type == MKPKDataType.STR:
            data_asm += [f'{mkpk_data.name} db "{mkpk_data.value}", 0']

    return data_asm


def _format_code_into_asm_function(code: MKPKCode) -> MKPKCode:
    """
    Formats the assembly code into an _start function so that it can be
    compiled as a standalone binary.

    :param code: The MKPKCode to be formatted into an assembly function.
    :return: The formatted MKPKCode obj.
    """
    if not isinstance(code, MKPKCode):
        raise MKPKInvalidParameter("code", "_format_code_into_asm_function", code)

    formatted_code: List[str] = [
        "Section .text",
        "    global _start",
        "_start:",
    ]

    for line in code.code:
        formatted_code += ["    " + line]

    code.code = formatted_code

    return code
