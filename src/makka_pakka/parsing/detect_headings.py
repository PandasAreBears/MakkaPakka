from typing import Tuple

from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKNameError
from makka_pakka.exceptions.exceptions import MKPKParsingError


class HeadingStyle:
    """Enum of heading style e.g [heading_name] is SINGLE_HEADING, [[name]] is
    a DOUBLE_HEADING."""

    NO_HEADING = 0
    SINGLE_HEADING = 1
    DOUBLE_HEADING = 2


class HeadingType:
    """Enum  of heading type, which defines the type of code expected below,
    and therefore how to parse this data, e.g [[data]] is DATA, [[code]] is
    CODE, [[gadget]] is gadget."""

    NONE = 0
    DATA = 1
    CODE = 2
    GADGETS = 3


def detect_heading_in_line(line: str) -> Tuple[HeadingStyle, str]:
    """
    Determines if a line contains a heading, i.e [{name}] or [[{name}]]

    :param line: The line of makka pakka code to detect a heading in.
    :return: A tuple of (HeadingStyle, {heading_name}), where heading_name is
        "" if the type is HeadingStyle.NO_HEADING.
    """
    if not isinstance(line, str):
        raise MKPKInvalidParameter("line", "_detect_heading_in_line", line)

    NO_HEADING_RETURN = (HeadingStyle.NO_HEADING, "")
    # Early breakout if the line can't be a heading.
    if "[" not in line or "]" not in line:
        return NO_HEADING_RETURN

    """
    A double pass algorithm is used to determine the length and location of the
    heading. Starting with a forward pass, the index of the first ']' character
    is located. Then, in the backwards pass the index of the first '[' is
    found. Using the length of the string its possible to get the index of the
    start of the heading.
        len. of heading = forward pass index - backward pass index
        start index = backward pass index

    To determine if it is a double heading, check the index before the backward
    pass index for a '[' character, and the index after the forward pass index
    for a ']' character.
    """

    # Forward pass
    NO_CHARACTER_FOUND = -1
    forward_pass_index: int = NO_CHARACTER_FOUND
    for i, char in enumerate(line):
        if char == "]":
            forward_pass_index = i
            break

    # Early return if no ']' character found.
    if forward_pass_index == NO_CHARACTER_FOUND:
        return NO_HEADING_RETURN

    # Backward pass
    backward_pass_index: int = NO_CHARACTER_FOUND
    for i, char in enumerate(line[::-1]):
        if char == "[":
            # The list has been reversed, so un-reverse the index.
            backward_pass_index = (len(line) - i) - 1
            break

    # Early return if no '[' character found.
    if backward_pass_index == NO_CHARACTER_FOUND:
        return NO_HEADING_RETURN

    # '[', ']' are valid characters in .asm, but only when inlined. Therefore
    # we can differenciate by enforcing that headings start at index 0|1.
    if backward_pass_index > 1:
        return NO_HEADING_RETURN

    # Check that the backward pass index is before the forward pass index.
    if backward_pass_index >= forward_pass_index:
        return NO_HEADING_RETURN

    heading_name = line[backward_pass_index + 1 : forward_pass_index]

    # Assert that the heading name is valid
    try:
        _assert_valid_mkpk_name(heading_name, line)
    except MKPKNameError:
        raise MKPKParsingError(
            "Invalid heading name",
            f"An invalid heading name '${heading_name}' was encountered in the\
                following line:\n >${line}",
            ErrorType.FATAL,
        )

    # Check if it is a double heading.
    if 0 <= backward_pass_index - 1 and forward_pass_index + 1 < len(line):
        if line[backward_pass_index - 1] == "[" and line[forward_pass_index + 1] == "]":
            # TODO: Check that the [[]] heading is in the valid set of heading
            # names.
            return (
                HeadingStyle.DOUBLE_HEADING,
                heading_name,
            )

    # If nothing else, then it must be a single heading.
    return (
        HeadingStyle.SINGLE_HEADING,
        heading_name,
    )


def _assert_valid_mkpk_name(name: str, line: str = "") -> None:
    """
    Asserts that a name used in makka pakka is valid.

    :param name: The name to be validated.
    :param line: The line that the heading is defined in, for debugging.
    :raises:
        MKPKNameError - When the heading name is invalid.
    """
    if not isinstance(name, str):
        raise MKPKInvalidParameter("name", "_assert_valid_mkpk_name", name)

    if not isinstance(line, str):
        raise MKPKInvalidParameter("line", "_assert_valid_mkpk_name", line)

    # Check if the name is valid, i.e in the one of the ranges [a-z][A-Z][0-9]
    # [_].
    # Define the valid chars using ascii value ranges
    valid_chars = (
        list(range(0x30, 0x3A))
        + list(range(0x41, 0x5B))
        + list(range(0x61, 0x7B))
        + [0x5F]
    )
    if not all([ord(char) in valid_chars for char in [*name]]) or len(name) == 0:
        raise MKPKNameError(
            "Encountered invalid name.",
            f"The name assigned on the following line is\
                invalid:\n> {line}\n\nValid names only use characters\
                in the range [a-z][A-Z][0-9][_]",
            ErrorType.FATAL,
        )
