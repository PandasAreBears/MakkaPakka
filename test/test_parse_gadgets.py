from pathlib import Path
from typing import List

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKParsingError
from makka_pakka.parsing.parse import _split_into_headings
from makka_pakka.parsing.parse_headings import parse_gadgets
from makka_pakka.parsing.parsing_structures import MKPKGadget
from makka_pakka.parsing.parsing_structures import MKPKLines

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/parsing")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_GADGETS: str = str(RESOURCES_ROOT / "simple_gadget.mkpk")
INVALID_GADGET_CODE: str = str(RESOURCES_ROOT / "invalid_gadget_code.mkpk")
INVALID_GADGET_HEADING: str = str(RESOURCES_ROOT / "invalid_gadget_heading.mkpk")
MULTIPLE_GADGETS: str = str(RESOURCES_ROOT / "multiple_gadgets.mkpk")


@pytest.fixture
def empty_headings() -> MKPKLines:
    return _split_into_headings(EMPTY_HEADINGS)


@pytest.fixture
def simple_gadgets() -> MKPKLines:
    return _split_into_headings(SIMPLE_GADGETS)


@pytest.fixture
def invalid_gadget_code() -> MKPKLines:
    return _split_into_headings(INVALID_GADGET_CODE)


@pytest.fixture
def invalid_gadget_heading() -> MKPKLines:
    return _split_into_headings(INVALID_GADGET_HEADING)


@pytest.fixture
def multiple_gadgets() -> MKPKLines:
    return _split_into_headings(MULTIPLE_GADGETS)


def _assert_gadget_state_eq(
    gadget: MKPKGadget, memory_location: str, content: List[str]
):
    assert gadget.memory_location == memory_location
    assert gadget.content == content


class TestParseGadgets:
    def test_invalid_parameters(self):
        try:
            parse_gadgets(None)
            pytest.fail(
                "parse_gadgets should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_empty_headings(self, empty_headings: MKPKLines):
        gadgets: List[MKPKGadget] = parse_gadgets(empty_headings.gadgets)

        assert len(gadgets) == 0

    def test_simple_gadget(self, simple_gadgets: MKPKLines):
        gadgets: List[MKPKGadget] = parse_gadgets(simple_gadgets.gadgets)

        assert len(gadgets) == 1

        _assert_gadget_state_eq(gadgets[0], "0xcafefade", ["mov rsi, 0xfeed", "pop"])

    def test_invalid_gadget_code_errors(self, invalid_gadget_code: MKPKLines):
        try:
            parse_gadgets(invalid_gadget_code.gadgets)
            pytest.fail(
                "parse_gadgets should have failed with MKPKParsingError\
                due to invalid gadget code placement, but did not."
            )
        except MKPKParsingError:
            pass

    def test_invalid_gadget_headings_errors(self, invalid_gadget_heading: MKPKLines):
        try:
            parse_gadgets(invalid_gadget_heading.gadgets)
            pytest.fail(
                "parse_gadgets should have failed with MKPKParsingError\
                due to invalid gadget memory location, but did not."
            )
        except MKPKParsingError:
            pass

    def test_multiple_gadgets(self, multiple_gadgets: MKPKLines):
        gadgets: List[MKPKGadget] = parse_gadgets(multiple_gadgets.gadgets)

        assert len(gadgets) == 3

        _assert_gadget_state_eq(gadgets[0], "0xdeadb33f", ["mov rax, 1", "pop"])
        _assert_gadget_state_eq(gadgets[1], "0xcafebabe", ["lea rsi, 0x500"])
        _assert_gadget_state_eq(gadgets[2], "0xabcabcabc", ["xor eax, eax"])
