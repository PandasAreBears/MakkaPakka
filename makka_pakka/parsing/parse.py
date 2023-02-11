from pathlib import Path

from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import InvalidParameter
from makka_pakka.exceptions.exceptions import ParsingError
from makka_pakka.parsing.detect_headings import detect_heading_in_line
from makka_pakka.parsing.detect_headings import HeadingStyle
from makka_pakka.parsing.detect_headings import HeadingType
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.parsing.parsing_structures import MKPKLines


def parse_makka_pakka(mkpk_filepath: str) -> MKPKIR:
    """
    Parses a makka pakka code file to generate an intermediate representation
    object used by the processing phase.
    :mkpk_filepath: The filepath to the .mkpk file to be split into headings.
    :returns: A MKPKIR object to be used during the processing phase.
    """
    if not isinstance(mkpk_filepath) or not Path(mkpk_filepath).exists():
        raise InvalidParameter("mkpk_filepath", "parse_makka_pakka", mkpk_filepath)


def _split_into_headings(
    mkpk_filepath: str,
) -> MKPKLines:
    """
    Splits a makka pakka code file into its headings - code, data, gadgets.
    :mkpk_filepath: The filepath to the .mkpk file to be split into headings.
    :returns: A MKPKLines object contain the raw lines from the .mkpk files.
    """
    if not isinstance(mkpk_filepath, str) or not Path(mkpk_filepath).exists():
        raise InvalidParameter("mkpk_filepath", "_split_into_headings", mkpk_filepath)

    code_lines: MKPKLines = MKPKLines(code=[], data=[], gadgets=[])

    def _add_to_section(line: str, type: HeadingType):
        """Adds a line to the specified section's code store"""
        match type:
            case HeadingType.DATA:
                code_lines.add_data(line)
            case HeadingType.CODE:
                code_lines.add_code(line)
            case HeadingType.GADGETS:
                code_lines.add_gadget(line)

    curr_heading_type: HeadingType = HeadingType.NONE
    with open(mkpk_filepath, "r") as mkpk_file:
        for line in mkpk_file:
            # Remove any formatting characters
            line = line.replace("\n", "").replace("\r", "").replace("\t", "")

            # Ignore empty lines and comments.
            if line == "" or line.startswith("#"):
                continue

            # Detect if the line is a heading
            heading_style, name = detect_heading_in_line(line)

            # When the line is new heading, work out which heading it is, then
            # set flag to indicate this for the following lines.
            if heading_style == HeadingStyle.DOUBLE_HEADING:
                new_heading_type = _convert_heading_name_to_type(name)
                if new_heading_type != HeadingType.NONE:
                    # The heading type has changed, so set the flag and add to
                    # new list.
                    curr_heading_type = new_heading_type
                    _add_to_section(line, curr_heading_type)

            # If the heading type is NONE and the line is not a heading
            # definition, then code will be ignored.
            elif curr_heading_type == HeadingType.NONE:
                # TODO: Warn that code here may be ignored.
                continue

            # The line is not a heading so add to the previous heading.
            else:
                _add_to_section(line, curr_heading_type)

    # Assert that there is a code section defined in the .mkpk file.
    if len(code_lines.code) == 0:
        raise ParsingError(
            "No code heading defined.",
            "The .mkpk file doesn't have a [[code]] section defined.",
            ErrorType.FATAL,
        )

    return code_lines


def _convert_heading_name_to_type(name: str) -> HeadingType:
    """
    Converts a string heading name into its associated HeadingType value.
    :name: The name to convert into a HeadingType.
    :returns: The HeadingType of the passed name, None if invalid.
    """

    if not isinstance(name, str):
        raise InvalidParameter("name", "_convert_heading_name_to_type", name)

    match name:
        case "data":
            return HeadingType.DATA
        case "code":
            return HeadingType.CODE
        case "gadgets":
            return HeadingType.GADGETS
        case _:
            return HeadingType.NONE