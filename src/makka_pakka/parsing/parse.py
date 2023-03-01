from pathlib import Path

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.parsing.detect_headings import detect_heading_in_line
from makka_pakka.parsing.detect_headings import HeadingStyle
from makka_pakka.parsing.detect_headings import HeadingType
from makka_pakka.parsing.parse_headings import parse_data
from makka_pakka.parsing.parse_headings import parse_functions
from makka_pakka.parsing.parse_headings import parse_gadgets
from makka_pakka.parsing.parse_headings import parse_metadata
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.parsing.parsing_structures import MKPKLines
from makka_pakka.parsing.parsing_structures import MKPKMetaData


def parse_makka_pakka(mkpk_filepath: str) -> MKPKIR:
    """
    Parses a makka pakka code file to generate an intermediate representation
    object used by the processing phase.

    :param mkpk_filepath: The filepath to the .mkpk file to be split into headings.
    :return: A MKPKIR object to be used during the processing phase.
    """
    if not isinstance(mkpk_filepath, str) or not Path(mkpk_filepath).exists():
        raise MKPKInvalidParameter("mkpk_filepath", "parse_makka_pakka", mkpk_filepath)

    mkpk_im_repr: MKPKIR = MKPKIR()

    headings: MKPKLines = _split_into_headings(mkpk_filepath)

    mkpk_im_repr.functions = parse_functions(headings.code)
    mkpk_im_repr.data = parse_data(headings.data)
    mkpk_im_repr.gadgets = parse_gadgets(headings.gadgets)
    mkpk_im_repr.metadata = parse_metadata(headings.metadata)

    # Add the filename to the metadata of every IR.
    mkpk_im_repr.metadata.append(MKPKMetaData("filename", Path(mkpk_filepath).name))

    return mkpk_im_repr


def _split_into_headings(
    mkpk_filepath: str,
) -> MKPKLines:
    """
    Splits a makka pakka code file into its headings - code, data, gadgets.

    :param mkpk_filepath: The filepath to the .mkpk file to be split into headings.
    :return: A MKPKLines object contain the raw lines from the .mkpk files.
    """
    if not isinstance(mkpk_filepath, str) or not Path(mkpk_filepath).exists():
        raise MKPKInvalidParameter(
            "mkpk_filepath", "_split_into_headings", mkpk_filepath
        )

    code_lines: MKPKLines = MKPKLines(code=[], data=[], gadgets=[], metadata=[])

    def _add_to_section(line: str, type: HeadingType):
        """
        Adds a line to the specified section's code store
        """
        match type:
            case HeadingType.DATA:
                code_lines.add_data(line)
            case HeadingType.CODE:
                code_lines.add_code(line)
            case HeadingType.GADGETS:
                code_lines.add_gadget(line)
            case HeadingType.NONE:
                code_lines.add_metadata(line)

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
                # Every line before headings is interpretted as metadata.
                _add_to_section(line, curr_heading_type)

            # The line is not a heading so add to the previous heading.
            else:
                _add_to_section(line, curr_heading_type)

    return code_lines


def _convert_heading_name_to_type(name: str) -> HeadingType:
    """
    Converts a string heading name into its associated HeadingType value.

    :param name: The name to convert into a HeadingType.
    :return: The HeadingType of the passed name, None if invalid.
    """

    if not isinstance(name, str):
        raise MKPKInvalidParameter("name", "_convert_heading_name_to_type", name)

    match name:
        case "data":
            return HeadingType.DATA
        case "code":
            return HeadingType.CODE
        case "gadgets":
            return HeadingType.GADGETS
        case _:
            return HeadingType.NONE
