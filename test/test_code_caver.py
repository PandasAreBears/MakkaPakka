from pathlib import Path
from typing import List
from typing import Tuple

import pytest
from lief import ELF
from lief import parse

from makka_pakka.elf_caver.caver.code_caver import _get_end_of_section
from makka_pakka.elf_caver.caver.code_caver import _get_end_of_segment
from makka_pakka.elf_caver.caver.code_caver import _get_executable_segments
from makka_pakka.elf_caver.caver.code_caver import (
    _get_last_section_in_segment,
)
from makka_pakka.elf_caver.caver.code_caver import get_code_caves
from makka_pakka.elf_caver.caver.file_permissions import is_executable
from makka_pakka.elf_caver.exceptions.exceptions import (
    MKPKInvalidParameter,
)

RES_PATH: str = Path("test/resources/elf_caver")


@pytest.fixture
def crontab_binary() -> ELF.Binary:
    PATH: str = get_bin_path_if_exists("crontab")
    return parse(PATH)


@pytest.fixture
def cat_binary() -> ELF.Binary:
    PATH: str = get_bin_path_if_exists("cat")
    return parse(PATH)


@pytest.fixture
def cpp_binary() -> ELF.Binary:
    PATH: str = get_bin_path_if_exists("cpp")
    return parse(PATH)


def get_bin_path_if_exists(bin_name: str) -> str:
    BIN_PATH: Path = RES_PATH / bin_name
    if not BIN_PATH.exists():
        raise FileNotFoundError

    return str(BIN_PATH)


class TestGetExecSegments:
    def test_invalid_parameter_none(self):
        try:
            _get_executable_segments(None)
            pytest.fail(
                "_get_executable_segments should have failed with invalid parameter but\
                     did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_invalid_parameter_int(self):
        try:
            _get_executable_segments(5)
            pytest.fail(
                "_get_executable_segments should have failed with invalid parameter but\
                     did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_get_seg_count_for_crontab(self, crontab_binary):
        EXEC_SEGMENTS: List[ELF.Segment] = _get_executable_segments(
            crontab_binary.segments
        )

        assert len(EXEC_SEGMENTS) == 1
        assert all([is_executable(seg.flags.value) for seg in EXEC_SEGMENTS])


class TestGetLastSectionInSegment:
    def test_invalid_parameter_none(self):
        try:
            _get_last_section_in_segment(None)
            pytest.fail(
                "_get_last_section_in_segment should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_invalid_parameter_int(self):
        try:
            _get_last_section_in_segment(107)
            pytest.fail(
                "_get_last_section_in_segment should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_get_last_section_of_code(self, cat_binary):
        # Get the CODE segment of the binary
        CODE_SEGMENT: ELF.Segment = _get_executable_segments(cat_binary.segments)[0]

        assert is_executable(CODE_SEGMENT.flags.value)
        assert ".text" in [sec.name for sec in CODE_SEGMENT.sections]

        LAST_SECTION: ELF.Section = _get_last_section_in_segment(CODE_SEGMENT)
        assert LAST_SECTION.name == ".fini"


class TestGetEndOfSegment:
    def test_invalid_parameter_none(self):
        try:
            _get_end_of_segment(None)
            pytest.fail(
                "_get_end_of_segment should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_invalid_parameter_int(self):
        try:
            _get_end_of_segment(7000)
            pytest.fail(
                "_get_end_of_segment should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_get_last_address_of_code(self, cat_binary):
        # Get the CODE segment of the binary
        CODE_SEGMENT: ELF.Segment = _get_executable_segments(cat_binary.segments)[0]

        CODE_SEG_INDEX: int = list(cat_binary.segments).index(CODE_SEGMENT)
        NEXT_SEG: ELF.Segment = cat_binary.segments[CODE_SEG_INDEX + 1]
        assert isinstance(NEXT_SEG, ELF.Segment)

        assert _get_end_of_segment(CODE_SEGMENT) == NEXT_SEG.file_offset


class TestGetEndOfSection:
    def test_invalid_parameter_none(self):
        try:
            _get_end_of_section(None)
            pytest.fail(
                "_get_end_of_section should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_invalid_parameter_int(self):
        try:
            _get_end_of_section(333)
            pytest.fail(
                "_get_end_of_section should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_get_end_of_fini(self, crontab_binary):
        # Get the CODE segment of the binary
        CODE_SEGMENT: ELF.Segment = _get_executable_segments(crontab_binary.segments)[0]

        # Get the .fini section
        LAST_CODE_SECTION: ELF.Section = _get_last_section_in_segment(CODE_SEGMENT)
        assert isinstance(LAST_CODE_SECTION, ELF.Section)

        # There is a code cave in the crontab binary at the end of the code section,
        # therefore last address of the section should be before the end of the segment
        assert _get_end_of_section(LAST_CODE_SECTION) < _get_end_of_segment(
            CODE_SEGMENT
        )


class TestGetCodeCaves:
    def test_invalid_parameter_none(self):
        try:
            get_code_caves(None)
            pytest.fail(
                "get_code_caves should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_invalid_parameter_int(self):
        try:
            get_code_caves(80)
            pytest.fail(
                "get_code_caves should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_invalid_parameter_section(self, cat_binary):
        try:
            get_code_caves(cat_binary.sections[0])
            pytest.fail(
                "get_code_caves should have failed with invalid parameter\
                     but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_get_code_caves_from_cat(self, cat_binary):
        CAVES: List[Tuple[int, int]] = get_code_caves(cat_binary)

        # Ensure that a cave was found
        assert len(CAVES) > 0

        # Ensure that the address and offset of the cave is non-zero
        assert CAVES[0][0] > 0 and CAVES[0][1] > 0

    def test_get_code_caves_from_cpp(self, cpp_binary):
        CAVES: List[Tuple[int, int]] = get_code_caves(cpp_binary)

        # Ensure that a cave was found
        assert len(CAVES) > 0

        # Ensure that the address and offset of the cave is non-zero
        assert CAVES[0][0] > 0 and CAVES[0][1] > 0
