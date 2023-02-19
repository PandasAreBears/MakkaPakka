from math import ceil
from typing import Iterator
from typing import List
from typing import Tuple

from lief import ELF

from makka_pakka.elf_caver.caver.file_permissions import is_executable
from makka_pakka.elf_caver.exceptions.exceptions import MKPKInvalidParameter


def _get_executable_segments(
    segments: Iterator[ELF.Segment],
) -> List[ELF.Segment]:
    """
    Filters a list of segments to just those with the executable flag.

    :param segments: An Iterator of ELF.Segment objects to be filtered
    :return: A list of ELF.Segment objects with the executable flag
    """
    if not isinstance(segments, Iterator) or not all(
        [isinstance(seg, ELF.Segment) for seg in segments]
    ):
        raise MKPKInvalidParameter("segments", "_get_executable_segments", segments)

    return list(filter(lambda s: is_executable(s.flags.value), segments))


def _get_last_section_in_segment(segment: ELF.Segment) -> ELF.Section:
    """
    Gets the last section in a segment

    :param segment: The ELF.Segment object to get the last section from
    :return: The ELF.Section object which was last in the segment.
    """
    if not isinstance(segment, ELF.Segment):
        raise MKPKInvalidParameter("segments", "_get_executable_segments", segment)

    # The last section is the one with the biggest offset value
    return sorted(segment.sections, key=lambda sect: sect.offset)[-1]


def _get_end_of_segment(segment: ELF.Segment) -> int:
    """
    Returns the offset at the end of a segment.

    :param segment: The ELF.Segment object to get final offset of.
    :return: The offset at the end of the segment.
    """
    if not isinstance(segment, ELF.Segment):
        raise MKPKInvalidParameter("segments", "_get_executable_segments", segment)

    # The end of the segment is the start + offset rounded up to the alignment
    SEGMENT_END = segment.file_offset + segment.physical_size
    SEGMENT_ALIGN = segment.alignment

    # A bit hacky, but rounding up to the nearest x is not something python does well.
    return int(ceil(SEGMENT_END / SEGMENT_ALIGN)) * SEGMENT_ALIGN


def _get_end_of_section(section: ELF.Section) -> int:
    """
    Gets the offset at the end of the passed section

    :param sections: The ELF.Section object to get the final offset of.
    :return: The offset at the end of the section.
    """
    if not isinstance(section, ELF.Section):
        raise MKPKInvalidParameter("section", "_get_end_of_section", section)

    return section.offset + section.size


def get_code_caves(binary: ELF.Binary) -> List[Tuple[int, int]]:
    """
    Gets the code caves from the passed binary. Returns a list of tuples in the
    format: (code cave offset, code cave size).

    :param binary: The binary to find the code caves in
    :return: A list of code caves in the format (code cave offset, code cave size)
    """
    if not isinstance(binary, ELF.Binary):
        raise MKPKInvalidParameter("binary", "get_code_caves", binary)

    # Find the executable segments.
    EXEC_SEGMENTS: List[ELF.Segment] = _get_executable_segments(binary.segments)

    # Get the last section in each exectuable segment.
    LAST_SECTIONS: List[ELF.Section] = [
        _get_last_section_in_segment(seg) for seg in EXEC_SEGMENTS
    ]

    LAST_SECTION_ENDS: List[int] = [_get_end_of_section(sec) for sec in LAST_SECTIONS]

    # Get a list of offsets for where the executable segments end.
    SEGMENT_ENDS: List[int] = [_get_end_of_segment(seg) for seg in EXEC_SEGMENTS]

    # The code cave is the difference between the end of the last section and the end
    # of the segment that it's in.
    NO_EXEC_SEGMENTS: int = len(EXEC_SEGMENTS)
    return [
        (
            _get_end_of_section(LAST_SECTIONS[i]),
            SEGMENT_ENDS[i] - LAST_SECTION_ENDS[i],
        )
        for i in range(NO_EXEC_SEGMENTS)
    ]
