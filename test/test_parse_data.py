from pathlib import Path
from typing import Any

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKParsingError
from makka_pakka.parsing.parse import _split_into_headings
from makka_pakka.parsing.parse_headings import _interpret_data_type
from makka_pakka.parsing.parse_headings import parse_data
from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.parsing.parsing_structures import MKPKLines

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/parsing")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_DATA: str = str(RESOURCES_ROOT / "simple_data.mkpk")
INVALID_DATA_NAME: str = str(RESOURCES_ROOT / "invalid_data_name.mkpk")
INVALID_DATA_INT: str = str(RESOURCES_ROOT / "invalid_data_int.mkpk")
INVALID_DATA_HEX: str = str(RESOURCES_ROOT / "invalid_data_hex.mkpk")


@pytest.fixture
def empty_headings() -> MKPKLines:
    return _split_into_headings(EMPTY_HEADINGS)


@pytest.fixture
def simple_data_lines() -> MKPKLines:
    return _split_into_headings(SIMPLE_DATA)


@pytest.fixture
def invalid_data_name_lines() -> MKPKLines:
    return _split_into_headings(INVALID_DATA_NAME)


@pytest.fixture
def invalid_data_int_lines() -> MKPKLines:
    return _split_into_headings(INVALID_DATA_INT)


@pytest.fixture
def invalid_data_hex_lines() -> MKPKLines:
    return _split_into_headings(INVALID_DATA_HEX)


def _assert_data_state_eq(data: MKPKData, name: str, value: Any, type: MKPKDataType):
    assert data.name == name
    assert data.value == value
    assert data.type == type


class TestParseData:
    def test_invalid_parameters(self):
        try:
            parse_data(None)
            pytest.fail(
                "parse_data should have failed with error\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_empty_headings(self, empty_headings: MKPKLines):
        data = parse_data(empty_headings.data)

        assert len(data) == 0

    def test_simple_data(self, simple_data_lines: MKPKLines):
        data = parse_data(simple_data_lines.data)

        assert len(data) == 3

        _assert_data_state_eq(data[0], "value_1", "hello", MKPKDataType.STR)
        _assert_data_state_eq(data[1], "value_2", 15, MKPKDataType.INT)
        _assert_data_state_eq(data[2], "value_3", 0x5678, MKPKDataType.INT)

    def test_invalid_data_name_raises_error(self, invalid_data_name_lines: MKPKLines):
        try:
            parse_data(invalid_data_name_lines.data)
            pytest.fail(
                "parse_data should have failed with MKPKParsingError\
                due to an invalid data name, but did not."
            )
        except MKPKParsingError:
            pass

    def test_invalid_data_int_raises_error(self, invalid_data_int_lines: MKPKLines):
        try:
            parse_data(invalid_data_int_lines.data)
            pytest.fail(
                "parse_data should have failed with MKPKParsingError\
                due to an invalid int value, but did not."
            )
        except MKPKParsingError:
            pass

    def test_invalid_data_hex_raises_error(self, invalid_data_hex_lines: MKPKLines):
        try:
            parse_data(invalid_data_hex_lines.data)
            pytest.fail(
                "parse_data should have failed with MKPKParsingError\
                due to an invalid hex value, but did not."
            )
        except MKPKParsingError:
            pass


class TestInterpretDataType:
    def test_invalid_parameters(self):
        mock_value = 1
        mock_line = "hi"
        try:
            _interpret_data_type(None, None)
            pytest.fail(
                "_interpret_data_type should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _interpret_data_type(mock_value, None)
            pytest.fail(
                "_interpret_data_type should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _interpret_data_type(None, mock_line)
            pytest.fail(
                "_interpret_data_type should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_interprets_string(self):
        test_string = '"hello"'

        (value, data_type) = _interpret_data_type(test_string, "")

        assert value == "hello"
        assert data_type == MKPKDataType.STR

    def test_interprets_decimal_int(self):
        test_int = "123"

        (value, data_type) = _interpret_data_type(test_int, "")

        assert value == 123
        assert data_type == MKPKDataType.INT

    def test_interprets_hex_int(self):
        test_int = "0x123"

        (value, data_type) = _interpret_data_type(test_int, "")

        assert value == 0x123
        assert data_type == MKPKDataType.INT

    def test_interprets_register(self):
        test_register = "rax"

        (value, data_type) = _interpret_data_type(test_register, "")

        assert value == "rax"
        assert data_type == MKPKDataType.REGISTER

    def test_raises_error_on_invalid_value(self):
        invalid_value1 = "unquoted_string"
        invalid_value2 = "0xhhh"

        try:
            _interpret_data_type(invalid_value1, "")
            pytest.fail(
                "_interpret_data_type should have failed with\
                        MKPKParsingError due to invalid data value, but\
                        did not."
            )
        except MKPKParsingError:
            pass

        try:
            _interpret_data_type(invalid_value2, "")
            pytest.fail(
                "_interpret_data_type should have failed with\
                        MKPKParsingError due to invalid data value, but\
                        did not."
            )
        except MKPKParsingError:
            pass
