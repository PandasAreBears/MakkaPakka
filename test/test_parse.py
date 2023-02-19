from pathlib import Path

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.parsing.detect_headings import HeadingType
from makka_pakka.parsing.parse import _convert_heading_name_to_type
from makka_pakka.parsing.parse import _split_into_headings
from makka_pakka.parsing.parse import parse_makka_pakka
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.parsing.parsing_structures import MKPKLines
from test.test_parse_data import _assert_data_state_eq
from test.test_parse_functions import _assert_func_state_eq
from test.test_parse_gadgets import _assert_gadget_state_eq
from test.test_parse_metadata import _assert_metadata_state_eq

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/parsing")
EMPTY_FILE: str = str(RESOURCES_ROOT / "empty_file.mkpk")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_CODE: str = str(RESOURCES_ROOT / "simple_code.mkpk")
SIMPLE_DATA: str = str(RESOURCES_ROOT / "simple_data.mkpk")
SIMPLE_GADGET: str = str(RESOURCES_ROOT / "simple_gadget.mkpk")
MISPLACED_CODE: str = str(RESOURCES_ROOT / "misplaced_code.mkpk")
COMMENTS: str = str(RESOURCES_ROOT / "comments.mkpk")
SIMPLE_MKPK: str = str(RESOURCES_ROOT / "simple_mkpk_file.mkpk")


class TestParseMakkaPakka:
    def test_invalid_parameters(self):
        try:
            parse_makka_pakka(None)

            pytest.fail(
                "parse_makka_pakka should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_simple_mkpk_file(self):
        im_repr: MKPKIR = parse_makka_pakka(SIMPLE_MKPK)

        assert len(im_repr.metadata) == 3
        assert len(im_repr.data) == 1
        assert len(im_repr.functions) == 2
        assert len(im_repr.gadgets) == 1

        _assert_metadata_state_eq(im_repr.metadata[0], "author", ["Alex J"])
        _assert_metadata_state_eq(
            im_repr.metadata[1], "link", ["my_other_file.mkpk", "stdlib.mkpk"]
        )
        _assert_metadata_state_eq(
            im_repr.metadata[2], "filename", ["simple_mkpk_file.mkpk"]
        )

        _assert_data_state_eq(im_repr.data[0], "name", "Alex", MKPKDataType.STR)

        _assert_func_state_eq(
            im_repr.functions[0],
            "main",
            True,
            0,
            [],
            ["mov rax, ${name}", "> my_func 1 2 3", "xor eax, eax", "pop"],
        )
        _assert_func_state_eq(
            im_repr.functions[1],
            "my_func",
            False,
            3,
            ["arg1", "hi", "panda"],
            ["mov al, ${arg1}", "mov ah, ${hi}", "xor rsi, ${panda}"],
        )

        _assert_gadget_state_eq(
            im_repr.gadgets[0], "0xabc123ef", ["xor eax, eax", "pop"]
        )


class TestConvertHeadingNameToType:
    def test_invalid_parameters(self):
        try:
            _convert_heading_name_to_type(None)
            pytest.fail(
                "_convert_heading_name_to_type should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
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
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_comments(self):
        expected_result = MKPKLines(
            data=["[[data]]"],
            code=["[[code]]", "[main]"],
            gadgets=["[[gadgets]]"],
        )

        result: MKPKLines = _split_into_headings(COMMENTS)

        assert result == expected_result

    def test_empty_headings(self):
        expected_result = MKPKLines(
            data=["[[data]]"],
            code=["[[code]]"],
            gadgets=["[[gadgets]]"],
        )

        result: MKPKLines = _split_into_headings(EMPTY_HEADINGS)

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
