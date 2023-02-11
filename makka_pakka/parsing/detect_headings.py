from typing import Tuple

from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import InvalidParameter
from makka_pakka.exceptions.exceptions import ParsingError
from makka_pakka.parsing.headings import HeadingStyle


def _detect_heading_in_line(line: str) -> Tuple[int, str]:
    """Determines if a line contains a heading, i.e [{name}] or [[{name}]]
    :line: The line of makka pakka code to detect a heading in.
    :returns: A tuple of (HeadingStyle, {heading_name}), where heading_name is
        "" if the type is HeadingStyle.NO_HEADING.
    """
    if not isinstance(line, str):
        raise InvalidParameter("line", "_detect_heading_in_line", line)

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
    _assert_valid_heading_name(heading_name, line)
    print(heading_name)

    # Check if it is a double heading.
    if 0 <= backward_pass_index - 1 and forward_pass_index + 1 < len(line):
        if line[backward_pass_index - 1] == "[" and line[forward_pass_index + 1] == "]":
            return (
                HeadingStyle.DOUBLE_HEADING,
                heading_name,
            )

    # If nothing else, then it must be a single heading.
    return (
        HeadingStyle.SINGLE_HEADING,
        heading_name,
    )


def _assert_valid_heading_name(name: str, line: str) -> None:
    # Check if the name is valid, i.e in the one of the ranges [a-z][A-Z][0-9]
    # [_].
    # Define the valid chars using ascii value ranges
    valid_chars = (
        list(range(0x30, 0x40))
        + list(range(0x41, 0x5B))
        + list(range(0x61, 0x7B))
        + [0x5F]
    )
    if not all([ord(char) in valid_chars for char in [*name]]) or len(name) == 0:
        raise ParsingError(
            "Heading name is invalid.",
            f"The name assigned to the heading on the following line is\
                invalid:\n {line}\n\nValid heading names only use characters\
                in the range [a-z][A-Z][0-9][_]",
            ErrorType.FATAL,
        )