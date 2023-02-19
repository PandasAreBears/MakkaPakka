from pathlib import Path
from typing import List

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKParsingError
from makka_pakka.parsing.parse import _split_into_headings
from makka_pakka.parsing.parse_headings import parse_metadata
from makka_pakka.parsing.parsing_structures import MKPKLines
from makka_pakka.parsing.parsing_structures import MKPKMetaData

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/parsing")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_METADATA: str = str(RESOURCES_ROOT / "simple_metadata.mkpk")
MULTIPLE_METADATA: str = str(RESOURCES_ROOT / "multiple_metadata.mkpk")
REPEATED_METADATA: str = str(RESOURCES_ROOT / "repeated_metadata.mkpk")
INVALID_METADATA: str = str(RESOURCES_ROOT / "invalid_metadata.mkpk")
INVALID_METADATA_LABEL: str = str(RESOURCES_ROOT / "invalid_metadata_label.mkpk")


@pytest.fixture
def empty_headings() -> MKPKLines:
    return _split_into_headings(EMPTY_HEADINGS)


@pytest.fixture
def simple_metadata() -> MKPKLines:
    return _split_into_headings(SIMPLE_METADATA)


@pytest.fixture
def multiple_metadata() -> MKPKLines:
    return _split_into_headings(MULTIPLE_METADATA)


@pytest.fixture
def repeated_metadata() -> MKPKLines:
    return _split_into_headings(REPEATED_METADATA)


@pytest.fixture
def invalid_metadata() -> MKPKLines:
    return _split_into_headings(INVALID_METADATA)


@pytest.fixture
def invalid_metadata_label() -> MKPKLines:
    return _split_into_headings(INVALID_METADATA_LABEL)


def _assert_metadata_state_eq(metadata: MKPKMetaData, label: str, values: List[str]):
    assert metadata.label == label
    assert metadata.values == values


class TestParseMetadata:
    def test_invalid_parameters(self):
        try:
            parse_metadata(None)
            pytest.fail(
                "parse_metadata should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_simple_metadata(self, simple_metadata: MKPKLines):
        metadata: List[MKPKMetaData] = parse_metadata(simple_metadata.metadata)

        assert len(metadata) == 1

        _assert_metadata_state_eq(metadata[0], "link", ["other_file.mkpk"])

    def test_multiple_metadata(self, multiple_metadata: MKPKLines):
        metadata: List[MKPKMetaData] = parse_metadata(multiple_metadata.metadata)

        assert len(metadata) == 2

        _assert_metadata_state_eq(metadata[0], "link", ["other_file.mkpk"])
        _assert_metadata_state_eq(metadata[1], "name", ["my_file"])

    def test_repeated_metadata(self, repeated_metadata: MKPKLines):
        metadata: List[MKPKMetaData] = parse_metadata(repeated_metadata.metadata)

        assert len(metadata) == 1

        _assert_metadata_state_eq(
            metadata[0],
            "link",
            ["first_file.mkpk", "second_file.mkpk", "third_file.mkpk"],
        )

    def test_invalid_metadata(self, invalid_metadata: MKPKLines):
        try:
            parse_metadata(invalid_metadata.metadata)
            pytest.fail(
                "parse_metadata should have failed with MKPKParsingError\
                due to invalid metadata code, but did not."
            )
        except MKPKParsingError:
            pass

    def test_invalid_metadata_label(self, invalid_metadata_label: MKPKLines):
        try:
            parse_metadata(invalid_metadata_label.metadata)
            pytest.fail(
                "parse_metadata should have failed with MKPKParsingError\
                due to invalid label name, but did not."
            )
        except MKPKParsingError:
            pass
