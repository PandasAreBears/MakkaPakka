from pathlib import Path

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKProcessingError
from makka_pakka.linking.linker import parse_link_and_merge
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.processing.process import process_makka_pakka
from makka_pakka.processing.processing_structures import MKPKCode

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/processing")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_FUNC_CALL: str = str(RESOURCES_ROOT / "simple_func_call.mkpk")


@pytest.fixture
def empty_headings() -> MKPKIR:
    return parse_link_and_merge(EMPTY_HEADINGS)


@pytest.fixture
def simple_func_call() -> MKPKIR:
    return parse_link_and_merge(SIMPLE_FUNC_CALL)


class TestProcessMakkaPakka:
    def test_invalid_parameters(self):
        try:
            process_makka_pakka(None)
            pytest.fail(
                "process_makka_pakka should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_no_main(self, empty_headings: MKPKIR):
        try:
            process_makka_pakka(empty_headings)
            pytest.fail(
                "Expected to fail with MKPKProcessingError due to\
                        having no main function, but did not."
            )
        except MKPKProcessingError:
            pass

    def test_simple_file(self, simple_func_call: MKPKIR):
        processed: MKPKCode = process_makka_pakka(simple_func_call)

        assert processed.code == ["mov rax, 1"]
