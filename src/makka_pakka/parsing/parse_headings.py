from typing import Any
from typing import List
from typing import Tuple
from typing import Union

from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKNameError
from makka_pakka.exceptions.exceptions import MKPKParsingError
from makka_pakka.parsing.detect_headings import _assert_valid_mkpk_name
from makka_pakka.parsing.detect_headings import detect_heading_in_line
from makka_pakka.parsing.detect_headings import HeadingStyle
from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.parsing.parsing_structures import MKPKFunction
from makka_pakka.parsing.parsing_structures import MKPKGadget
from makka_pakka.parsing.parsing_structures import MKPKMetaData
from makka_pakka.parsing.registers import REGISTER_NAMES


def parse_metadata(lines: List[str]) -> List[MKPKMetaData]:
    """
    Packs metadata from the .mkpk file into MKPKMetaData structures.

    :param lines: A list of code lines from the .mkpk source file.
    :return: A list of parsed MKPKMetaData objects.
    """

    if not isinstance(lines, list) or not all(
        [isinstance(line, str) for line in lines]
    ):
        raise MKPKInvalidParameter("lines", "parse_functions", lines)

    # Early breakout when no lines are supplied
    if len(lines) == 0:
        return []

    metadata: List[MKPKMetaData] = []

    for line in lines:
        if line == "":
            continue

        # Metadata lines begin with the '!' directive.
        if line[0] != "!":
            raise MKPKParsingError(
                "Couldn't interpret metadata code.",
                f"The code in the following line is not under a heading, and\
                  does not contain the metadata directive (!):\n> {line}\n\n\
            Either prefix the line with a ! if it is metadata, or put the code\
            under the correct heading.",
                ErrorType.FATAL,
            )

        # Get the label of the metadata, and assert that it's correctly
        # formatted.
        line = line[1:]
        label: str = line.split(" ")[0]

        try:
            _assert_valid_mkpk_name(label, line)
        except MKPKNameError:
            raise MKPKParsingError(
                "Metadata label is invalid.",
                f"The label {label} is invalid in line:\n> {line}\n\nValid\
                    label names only use characters in the range\
                         [a-z][A-Z][0-9][_].",
                ErrorType.FATAL,
            )

        # Get the value by taking everything after the label + space
        value: str = line[len(label) + 1 :]

        # Check if the a metadata object already exists for this label, if it
        # does then add the value to the existing object.
        metadata_with_label: List[MKPKMetaData] = list(
            filter(lambda md: md.label == label, metadata)
        )
        if len(metadata_with_label) > 0:
            metadata_with_label[0].append_value(value)

        # Otherwise, create a new object with this label, value pair.
        else:
            metadata.append(MKPKMetaData(label, value))

    return metadata


def parse_functions(lines: List[str]) -> List[MKPKFunction]:
    """
    Packs code lines from the .mkpk file into MKPKFunction strcutures.

    :param lines: A list of code lines from the .mkpk source file.
    :return: A list of parsed MKPKFunction objects.
    """

    if not isinstance(lines, list) or not all(
        [isinstance(line, str) for line in lines]
    ):
        raise MKPKInvalidParameter("lines", "parse_functions", lines)

    # Early breakout when there are no code lines.
    if len(lines) == 0:
        return []

    functions: List[MKPKFunction] = []

    # Loop through each line, excluding the first line, as this will always be
    # the [[code]] heading.
    current_function: MKPKFunction = None
    for line in lines[1:]:
        # Single headings indicate a new function
        heading_style, name = detect_heading_in_line(line)
        if heading_style == HeadingStyle.SINGLE_HEADING:
            # Assert that the heading only uses valid characters
            _assert_valid_mkpk_name(name, line)

            # We're now in a new function, so save the old one, if applicable
            if current_function is not None:
                functions.append(current_function)

            # Extract the arguments from the function then create a new
            # MKPKFunction.
            func_args = _extract_args_from_function(line)

            current_function = MKPKFunction(name=name, arguments=func_args, content=[])

        # If the line is not a function declaration, then it is a line of code
        # that should be added to the current function.
        else:
            if current_function is None:
                raise MKPKParsingError(
                    "Code line not in function",
                    f"A code line has no associated function:\n> {line}\n\n\
                        Code must be assigned to a function - functions are\
                        declared using a [function_heading]",
                    ErrorType.FATAL,
                )

            current_function.add_line_to_content(line)

    # Add the last function to the functions list
    if current_function is not None:
        functions.append(current_function)

    return functions


def parse_data(lines: List[str]) -> List[MKPKData]:
    """
    Packs data lines from the .mkpk file into MKPKData structures.

    :param lines: A list of code lines from the .mkpk source file.
    :return: A list of parsed MKPKData objects.
    """
    if not isinstance(lines, list) or not all(
        [isinstance(line, str) for line in lines]
    ):
        raise MKPKInvalidParameter("lines", "parse_data", lines)

    # Early breakout when no lines are supplied
    if len(lines) == 0:
        return []

    data: List[MKPKData] = []

    # Loop through each line, excluding the first line, as this will always be
    # the [[data]] heading.
    for line in lines[1:]:
        # Data declarations should always be in the format name: value, so
        # split by ':' and expect [name, value]
        if len(line.split(":")) != 2:
            raise MKPKParsingError(
                "Data declaration is invalid",
                f"The data declaration on the following line is invalid:\n> {line}\
                \n\nData declarations should be in the format `name: value`.",
                ErrorType.FATAL,
            )

        (name, value) = line.split(":")
        value = value.strip()

        # Data identifiers have the same requirements are heading names, so use
        # that assertion and re-write the error message.
        try:
            _assert_valid_mkpk_name(name, line)
        except MKPKNameError:
            raise MKPKParsingError(
                "Data identifier name is invalid.",
                f"The argument\
                    {name} is invalid in line:\n> {line}\n\nValid heading names \
                    only use characters in the range [a-z][A-Z][0-9][_].",
                ErrorType.FATAL,
            )

        parsed_value, value_type = _interpret_data_type(value, line)

        data.append(MKPKData(name, parsed_value, value_type))

    return data


def _interpret_data_type(value: str, line: str) -> Tuple[Union[str, int], MKPKDataType]:
    """
    Interprets data in a .mkpk file.

    :param value: The value to interpret.
    :param line: The line that the data was found in.
    :return: A tuple containing the data as a string or int, and the
        MKPKDataType of the data.
    :raises:
        MKPKParsingError - When the data couldn't be interpretted.
    """
    if not isinstance(value, str):
        raise MKPKInvalidParameter("value", "_interpret_data_type", value)
    if not isinstance(line, str):
        raise MKPKInvalidParameter("line", "_interpret_data_type", line)

    # If the value is wrapped in "" then it is a string, otherwise it is an
    # int in either decimal or hexadecimal format. Alternatively, it may be
    # a register name.
    value_type: MKPKDataType = MKPKDataType.NONE
    parsed_value: Any = 0
    if value in REGISTER_NAMES:
        value_type = MKPKDataType.REGISTER
        parsed_value = value

    elif len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value_type = MKPKDataType.STR
        # Strip the surrounding ""
        parsed_value = value[1:-1]

    else:
        value_type = MKPKDataType.INT

        if "0x" in value:
            try:
                parsed_value = int(value, 16)
            except ValueError:
                raise MKPKParsingError(
                    "Unable to interpret hex value.",
                    f"Unable to parse as integer in the following line:\n> \
                    {line}\n\nHex data is defined using the 0x prefix.",
                    ErrorType.FATAL,
                )

        else:
            try:
                parsed_value = int(value)
            except ValueError:
                raise MKPKParsingError(
                    "Unable to interpret integer value.",
                    f'Unable to parse as integer in the following line:\n> \
                    {line}\n\nData must either be a string, defined using\
                    "your_string_here", or an integer, either in decimal\
                        or hexadecimal notation.',
                    ErrorType.FATAL,
                )

    return (parsed_value, value_type)


def parse_gadgets(lines: List[str]) -> List[MKPKGadget]:
    """
    Packs gadget lines from the .mkpk file into MKPKGadget structures.

    :param lines: A list of code lines from the .mkpk source file.
    :return: A list of parsed MKPKGadget objects.
    """
    if not isinstance(lines, list) or not all(
        [isinstance(line, str) for line in lines]
    ):
        raise MKPKInvalidParameter("lines", "parse_gadgets", lines)

    # Early breakout when no lines are supplied
    if len(lines) == 0:
        return []

    gadgets: List[MKPKGadget] = []

    # Loop through each line, excluding the first line, as this will always be
    # the [[gadgets]] heading.
    current_gadget: MKPKGadget = None
    for line in lines[1:]:
        # Single headings indicate a new gadget
        heading_style, gadget_address = detect_heading_in_line(line)
        if heading_style == HeadingStyle.SINGLE_HEADING:
            # Assert that the gadget address is a valid memory address.
            try:
                int(gadget_address, 16)
            except ValueError:
                raise MKPKParsingError(
                    "Gadget address in heading is invalid.",
                    f"The gadget address specified in the heading in the following\
                    line is invalid:\n> {line}\n\nGadget address headings\
                    should be the virtual memory address of the gadget in the\
                    target binary.",
                    ErrorType.FATAL,
                )

            # We're now in a new function, so save the old one, if applicable
            if current_gadget is not None:
                gadgets.append(current_gadget)

            current_gadget = MKPKGadget(memory_location=gadget_address, content=[])

        # If the line is not a function declaration, then it is a line of code
        # that should be added to the current function.
        else:
            if current_gadget is None:
                raise MKPKParsingError(
                    "Code line not in gadget",
                    f"A code line has no associated gadget:\n> {line}\n\n\
                        Code must be assigned to a gadget - gadgets are\
                        declared using a [memory_address] heading.",
                    ErrorType.FATAL,
                )

            current_gadget.add_line_to_content(line)

    # Add the last gadget to the gadgets list
    if current_gadget is not None:
        gadgets.append(current_gadget)

    return gadgets


def _extract_args_from_function(line: str) -> List[str]:
    """
    Extracts the args definined in a function definition line. e.g the function
    definition "[func_name] name age" will return ["name", "age"].

    :param line: The function definition line to extract the args from.
    :return: A list of strings indicating the names of the function arguments.
    """
    if not isinstance(line, str):
        raise MKPKInvalidParameter("line", "_extract_args_from_function", line)

    # Check that the line is actually a function.
    headingStyle, _ = detect_heading_in_line(line)
    if headingStyle != HeadingStyle.SINGLE_HEADING:
        raise MKPKInvalidParameter("line", "_extract_args_from_function", line)

    # Strip the function name definition from the line by taking everything
    # after the ]
    args_str: str = line.split("]")[1]

    args: List[str] = []
    for arg in args_str.split(" "):
        if arg != "":
            # The same naming rules apply to args and function names.
            try:
                _assert_valid_mkpk_name(arg, line)
            except MKPKNameError:
                raise MKPKParsingError(
                    "Argument name is invalid.",
                    f"The argument\
                     {arg} is invalid in line:\n> {line}\n\nValid heading names \
                        only use characters in the range [a-z][A-Z][0-9][_].",
                    ErrorType.FATAL,
                )
            args.append(arg)

    return args
