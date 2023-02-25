from re import findall
from typing import List

from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKNameError
from makka_pakka.exceptions.exceptions import MKPKProcessingError
from makka_pakka.parsing.detect_headings import _assert_valid_mkpk_name
from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.parsing.parsing_structures import MKPKIR


def process_data_replacement(mkpkir: MKPKIR) -> MKPKIR:
    """
    Replaces any data references in code with the corresponding data value.
    For example:
        [[data]]
        num: 1

        [[code]]
        [my_func]
        mov rax, ${num}

    Will become:
        [[code]]
        [my_func]
        mov rax, 1

    :param mkpkir: The MKPKIR object to replace data references in.
    :return: The MKPKIR object with its data replaced.
    """
    if not isinstance(mkpkir, MKPKIR):
        raise MKPKInvalidParameter("mkpkir", "process_data_replacement", mkpkir)

    """
    Data references are wrapped in a ${<label>}. So iterate through each line
    in code:
     - find any part of the string with matches the pattern '\$\{\w*\}',
     - extract the label from the reference and look it up in the IR data
        archive
     - Replace the reference in the line the archive value.
    """
    # Loop through every archived function, then the code lines.
    for func_i, func in enumerate(mkpkir.functions):
        for code_line_i, code_line in enumerate(func.content):
            data_refs = _extract_data_references(code_line)

            """
            For every data reference:
             - Create temporary line (so that mulitple replacements can be
                made without overwritting old ones.)
             - Get the label
             - Get the label's value from the ir object
                - If this value doesn't exist then raise a MKPKProcessingError
             - Replace the ref with its value.
             - Store in the temporary line.
            """
            copy_code_line = code_line
            for ref in data_refs:
                label = _extract_label_from_reference(ref)
                value: MKPKData = MKPKData.get_data_with_label(mkpkir.data, label)

                if value is None:
                    # It could be the case that the label is a function
                    # in which case it is yet to be processed, so leave it for
                    # now and let the function replacer handle it.
                    continue

                copy_code_line = _replace_reference_with_value(
                    copy_code_line, ref, value
                )

            # Commit the temporary code line back to the IR.
            mkpkir.functions[func_i].content[code_line_i] = copy_code_line

    return mkpkir


def _extract_data_references(code_line: str) -> List[str]:
    """
    Extracts 0 to many data references in the format ${<label>} from a line of
      code.

    :param code_line: The line of code to extract data references from.
    :return: A list of string data references that were found in the code
     line.
    """
    if not isinstance(code_line, str):
        raise MKPKInvalidParameter("code_line", "_extract_data_references", code_line)

    return findall(r"\$\{\w*\}", code_line)


def _extract_label_from_reference(data_reference: str) -> str:
    """
    Extracts the label from a data references, e.g if data_reference is
    "${apple}" then the return value would be "apple".

    :param data_reference: The data reference to extract the label from.
    :return: The label extracted from the passed data reference.
    """
    if not isinstance(data_reference, str):
        raise MKPKInvalidParameter(
            "data_reference", "_extract_label_from_reference", data_reference
        )

    # Check that data_reference is in the format ${<label>}
    if len(data_reference) < 3:
        raise MKPKInvalidParameter(
            "data_reference", "_extract_label_from_reference", data_reference
        )

    if (
        not data_reference[0] == "$"
        or not data_reference[1] == "{"
        or not data_reference[-1] == "}"
    ):
        raise MKPKInvalidParameter(
            "data_reference", "_extract_label_from_reference", data_reference
        )

    # Not very clean, but assuming the parameter isn't malformed, this will do.
    label = data_reference[2:-1]

    # Check that the label has a valid name.
    try:
        _assert_valid_mkpk_name(label)
    except MKPKNameError:
        raise MKPKProcessingError(
            "Encountered invalid label while extracting data reference.",
            f"The label name ${label} is invalid. Found while replacing the data\
                reference: ${data_reference}",
            ErrorType.FATAL,
        )

    return label


def _replace_reference_with_value(
    code_line: str, data_reference: str, data: MKPKData
) -> str:
    """
    Replaces a data reference in a code line with its archived value.

    :param code_line: The code line to replace the data reference in.
    :param data_reference: The data reference in the line to replace.
    :param value: The value to replace the data reference with.
    :return: The new code line with the replaced value.
    """
    if not isinstance(code_line, str):
        raise MKPKInvalidParameter(
            "code_line", "_replace_reference_with_value", code_line
        )

    if not isinstance(data_reference, str):
        raise MKPKInvalidParameter(
            "data_reference", "_replace_reference_with_value", data_reference
        )

    if not isinstance(data, MKPKData):
        raise MKPKInvalidParameter("value", "_replace_reference_with_value", data)

    copy_code_line = code_line

    # If the data type is string, then a reference to the value must
    # be made. If it is an int, then it can be plugged into the code line
    # directly. If it is a register, then insert the register name.
    match data.type:
        case MKPKDataType.STR | MKPKDataType.REGISTER:
            code_line = code_line.replace(data_reference, data.name)

        case MKPKDataType.INT:
            code_line = code_line.replace(data_reference, str(data.value))

    # If the line hasn't changed, then the parameters are invalid, but its not
    # critical so just warn.
    if code_line == copy_code_line:
        print(
            f"Warning: Code line was unchanged by data reference replacement:\
            \n> {code_line}\nTried replacing {data_reference} with {data.value}"
        )

    return code_line
