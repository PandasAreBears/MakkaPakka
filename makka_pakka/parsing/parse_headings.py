from typing import List

from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import InvalidParameter
from makka_pakka.exceptions.exceptions import ParsingError
from makka_pakka.parsing.detect_headings import _assert_valid_heading_name
from makka_pakka.parsing.detect_headings import detect_heading_in_line
from makka_pakka.parsing.detect_headings import HeadingStyle
from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKFunction
from makka_pakka.parsing.parsing_structures import MKPKGadget


def parse_functions(lines: List[str]) -> List[MKPKFunction]:
    """
    Packs code lines from the .mkpk file into MKPKFunction strcutures.
    :lines: A list of code lines from the .mkpk source file.
    :returns: A list of parsed MKPKFunction objects.
    """

    if not isinstance(lines, list) or not all(
        [isinstance(line, str) for line in lines]
    ):
        raise InvalidParameter("lines", "parse_functions", lines)

    functions: List[MKPKFunction] = []

    # Loop through each line, excluding the first line, as this will always be
    # the [[code]] heading.
    current_function: MKPKFunction = None
    for line in lines[1:]:
        # Single headings indicate a new function
        heading_style, name = detect_heading_in_line(line)
        if heading_style == HeadingStyle.SINGLE_HEADING:
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
                raise ParsingError(
                    "Code line not in function",
                    f"A code line has no associated function:\n> {line}\n\n\
                        Code must be assigned to a function - functions are\
                        declared using a [function_heading]",
                    ErrorType.FATAL,
                )

            current_function.add_line_to_content(line)

    # Assert that there is atleast one function defined in the file
    if current_function is None:
        raise ParsingError(
            "No functions defined.",
            "No function are defined\
             in the .mkpk file. Function are defined using a [function_name]\
                declaration.",
            ErrorType.FATAL,
        )

    # Add the last function to the functions list
    functions.append(current_function)

    # Check that there is one, and only one main function.
    func_names: List[str] = [func.name for func in functions]
    num_main_funcs: int = func_names.count("main")
    if num_main_funcs > 1:
        raise ParsingError(
            "More than 1 main functions declared.",
            f"Only 1 main function should be defined in a .mkpk file, however\
            {num_main_funcs} were found.",
            ErrorType.FATAL,
        )
    elif num_main_funcs == 0:
        raise ParsingError(
            "No main function found.",
            "No main function was found in the .mkpk file. A main function is\
            delared using [main].",
            ErrorType.FATAL,
        )

    return functions


def parse_data(lines: List[str]) -> List[MKPKData]:
    """
    Packs data lines from the .mkpk file into MKPKData structures.
    :lines: A list of code lines from the .mkpk source file.
    :returns: A list of parsed MKPKData objects.
    """
    pass


def parse_gadgets(lines: List[str]) -> List[MKPKGadget]:
    """
    Packs gadget lines from the .mkpk file into MKPKGadget structures.
    :lines: A list of code lines from the .mkpk source file.
    :returns: A list of parsed MKPKGadget objects.
    """
    pass


def _extract_args_from_function(line: str) -> List[str]:
    """
    Extracts the args definined in a function definition line. e.g the function
    definition "[func_name] name age" will return ["name", "age"].
    :line: The function definition line to extract the args from.
    :returns: A list of strings indicating the names of the function arguments.
    """
    if not isinstance(line, str):
        raise InvalidParameter("line", "_extract_args_from_function", line)

    # Check that the line is actually a function.
    headingStyle, _ = detect_heading_in_line(line)
    if headingStyle != HeadingStyle.SINGLE_HEADING:
        raise InvalidParameter("line", "_extract_args_from_function", line)

    # Strip the function name definition from the line by taking everything
    # after the ]
    args_str: str = line.split("]")[1]

    args: List[str] = []
    for arg in args_str.split(" "):
        if arg != "":
            # The same naming rules apply to args and function names.
            try:
                _assert_valid_heading_name(arg, line)
            except ParsingError:
                raise ParsingError(
                    "Argument name is invalid.",
                    f"The argument\
                     {arg} is invalid in line:\n> {line}\n\nValid heading names \
                        only use characters in the range [a-z][A-Z][0-9][_].",
                    ErrorType.FATAL,
                )
            args.append(arg)

    return args
