from typing import List

from lief import ELF

from makka_pakka.elf_caver.caver.file_permissions import permission_to_str
from makka_pakka.elf_caver.formatting.table_formatter import print_table
from makka_pakka.elf_caver.formatting.table_formatter import (
    table_rows_to_columns,
)

RESET: str = "\u001b[0m"
BOLD: str = "\u001b[37;1m"
UNDERLINE: str = "\u001b[4m"


def pprint_elf(binary: ELF.Binary) -> None:
    pprint_header(binary)
    print("")
    pprint_segments(binary)
    print("")
    pprint_sections(binary)


def pprint_sections(binary: ELF.Binary) -> None:
    """Prints the ELF sections table"""
    print(f"{BOLD}{UNDERLINE} SECTIONS {RESET}")

    SECTIONS: List[ELF.Section] = binary.sections

    # Only grab the data needed from the section
    sections = [
        [s.name, str(hex(s.size)), str(hex(s.offset)), s.flags_list] for s in SECTIONS
    ]

    # Tranform the data into a string format
    FLAGS_LIST_INDEX: int = 3
    for s in sections:
        s[FLAGS_LIST_INDEX] = " ".join([str(f.name) for f in s[FLAGS_LIST_INDEX]])

    PRINT_PADDING: int = 2
    PRINT_OFFSET: int = 1
    HEADERS: List[str] = ["Section Name", "Size", "Offset", "Flags"]

    SECTION_COLUMNS: List[List[str]] = table_rows_to_columns(*sections)

    print_table(
        *SECTION_COLUMNS,
        headers=HEADERS,
        padding=PRINT_PADDING,
        offset=PRINT_OFFSET,
    )


def pprint_segments(binary: ELF.Binary) -> None:
    """Prints the ELF segments table"""
    print(f"{BOLD}{UNDERLINE} SEGMENTS {RESET}")

    SEGMENTS: List[ELF.Segment] = binary.segments

    # Only grab the data needed from the segment
    segments = [
        [
            s.type.name,
            str(hex(s.physical_size)),
            str(hex(s.file_offset)),
            str(hex(s.alignment)),
            str(hex(s.virtual_address)),
            s.flags,
        ]
        for s in SEGMENTS
    ]

    # Convert flags to string format
    FLAGS_INDEX: int = 5
    for s in segments:
        s[FLAGS_INDEX] = permission_to_str(s[FLAGS_INDEX].value)

    # Print the segments
    COLUMNS: List[List[str]] = table_rows_to_columns(*segments)
    HEADERS: List[str] = [
        "Type",
        "Phys size",
        "File offset",
        "Alignment",
        "Virt Addr",
        "Flags",
    ]
    PADDING: int = 2
    OFFSET: int = 1

    print_table(*COLUMNS, headers=HEADERS, padding=PADDING, offset=OFFSET)


def pprint_header(binary: ELF.Binary) -> None:
    """Prints the ELF header stdout in a readable format"""
    print(f"{BOLD}{UNDERLINE} HEADER {RESET}")

    header: ELF.Header = binary.header
    FIELDS = [
        "Type",
        "Architecture",
        "Entry point",
        "NO. Segments",
        "NO. Sections",
    ]
    VALUES = [
        header.file_type.name,
        header.machine_type.name,
        str(hex(header.entrypoint)),
        str(header.numberof_segments),
        str(header.numberof_sections),
    ]

    HEADERS = ["Fields", "Values"]
    PADDING = 2
    OFFSET = 1
    print_table(FIELDS, VALUES, headers=HEADERS, padding=PADDING, offset=OFFSET)
