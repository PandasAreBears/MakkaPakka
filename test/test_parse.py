from pathlib import Path

import pytest

from makka_pakka.exceptions.exceptions import InvalidParameter
from makka_pakka.parsing.detect_headings import HeadingType
from makka_pakka.parsing.parse import _convert_heading_name_to_type
from makka_pakka.parsing.parse import _split_into_headings
from makka_pakka.parsing.parsing_structures import MKPKLines

RESOURCES_ROOT: str = Path("test/resources/mkpk_files")
EMPTY_FILE: str = str(RESOURCES_ROOT / "empty_file.mkpk")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_CODE: str = str(RESOURCES_ROOT / "simple_code.mkpk")
SIMPLE_DATA: str = str(RESOURCES_ROOT / "simple_data.mkpk")
SIMPLE_GADGET: str = str(RESOURCES_ROOT / "simple_gadget.mkpk")
MISPLACED_CODE: str = str(RESOURCES_ROOT / "misplaced_code.mkpk")
COMMENTS: str = str(RESOURCES_ROOT / "comments.mkpk")


class TestConvertHeadingNameToType:
    def test_invalid_parameters(self):
        try:
            _convert_heading_name_to_type(None)
            pytest.fail(
                "_convert_heading_name_to_type should have failed with\
                InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

    def test_returns_none_on_invalid_name(self):
        invalid_name1: str = "cod"
        invalid_name2: str = "invalid"
        invalid_name3: str = "123456"

        assert _convert_heading_name_to_type(invalid_name1) == HeadingType.NONE
        assert _convert_heading_name_to_type(invalid_name2) == HeadingType.NONE
        assert _convert_heading_name_to_type(invalid_name3) == HeadingType.NONE

    def test_returns_correct_type_for_valid_names(self):
        valid_name1: str = "data"
        valid_name2: str = "code"
        valid_name3: str = "gadgets"

        assert _convert_heading_name_to_type(valid_name1) == HeadingType.DATA
        assert _convert_heading_name_to_type(valid_name2) == HeadingType.CODE
        assert _convert_heading_name_to_type(valid_name3) == HeadingType.GADGETS


class TestSplitIntoHeadings:
    def test_invalid_parameters(self):
        try:
            _split_into_headings(None)
            pytest.fail(
                "_split_into_headings should have failed with\
                InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

    def test_comments(self):
        expected_result = MKPKLines(
            data=["[[data]]"],
            code=["[[code]]", "[main]"],
            gadgets=["[[gadgets]]"],
        )

        result: MKPKLines = _split_into_headings(COMMENTS)

        assert result == expected_result

    def test_empty_file(self):
        expected_result = MKPKLines()

        result: MKPKLines = _split_into_headings(EMPTY_FILE)

        assert result == expected_result

    def test_empty_headings(self):
        expected_result = MKPKLines(
            data=["[[data]]"],
            code=["[[code]]", "[main]"],
            gadgets=["[[gadgets]]"],
        )

        result: MKPKLines = _split_into_headings(EMPTY_HEADINGS)

        assert result == expected_result

    def test_misplaced_code(self):
        expected_result = MKPKLines(data=["[[data]]"], code=["[[code]]", "[main]"])

        result: MKPKLines = _split_into_headings(MISPLACED_CODE)

        assert result == expected_result

    def test_simple_code(self):
        expected_result = MKPKLines(
            data=["[[data]]"], code=["[[code]]", "[main]", "mov rax, 1"]
        )

        result: MKPKLines = _split_into_headings(SIMPLE_CODE)

        assert result == expected_result

    def test_simple_data(self):
        expected_result = MKPKLines(
            data=[
                "[[data]]",
                'value_1: "hello"',
                "value_2: 15",
                "value_3: 0x5678",
            ],
            code=["[[code]]", "[main]"],
        )

        result: MKPKLines = _split_into_headings(SIMPLE_DATA)

        assert result == expected_result

    def test_simple_gadget(self):
        expected_result = MKPKLines(
            data=["[[data]]", 'value: "hi"'],
            code=[
                "[[code]]",
                "[main]",
                "xor eax, eax",
                "mov rsi, 0xfeed",
                "pop",
            ],
            gadgets=["[[gadgets]]", "[0xcafefade]", "mov rsi, 0xfeed", "pop"],
        )

        result: MKPKLines = _split_into_headings(SIMPLE_GADGET)

        assert result == expected_result
