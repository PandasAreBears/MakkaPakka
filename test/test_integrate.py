from pathlib import Path
from typing import List

import pytest

from makka_pakka.exceptions.exceptions import MKPKIntegratingError
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.integrating.integrate import (
    _format_code_into_asm_function,
)
from makka_pakka.integrating.integrate import _translate_mkpkdata_to_asm
from makka_pakka.integrating.integrate import _write_code_to_file
from makka_pakka.integrating.integrate import integrate_makka_pakka
from makka_pakka.linking.linker import parse_link_and_merge
from makka_pakka.processing.process import process_makka_pakka
from makka_pakka.processing.processing_structures import MKPKCode

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/processing")
SIMPLE_FUNC_CALL: str = str(RESOURCES_ROOT / "simple_func_call.mkpk")
SF_DATA_REPLACEMENT: str = str(RESOURCES_ROOT / "single_file_data_replacement.mkpk")


@pytest.fixture
def simple_func_call() -> MKPKCode:
    parsed = parse_link_and_merge(SIMPLE_FUNC_CALL)
    return process_makka_pakka(parsed)


@pytest.fixture
def sf_data_replacement() -> MKPKCode:
    parsed = parse_link_and_merge(SF_DATA_REPLACEMENT)
    return process_makka_pakka(parsed)


class TestFormatCodeIntoAsmFunction:
    def test_invalid_parameters(self):
        try:
            _format_code_into_asm_function(None)
            pytest.fail(
                "_format_code_into_asm_function should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_formats_code(self, simple_func_call: MKPKCode):
        expected_code = [
            "Section .text",
            "    global _start",
            "_start:",
            "    mov rax, 1",
        ]

        code: MKPKCode = _format_code_into_asm_function(simple_func_call)

        assert code.code == expected_code


class TestTranslateMKPKDataToASM:
    def test_invalid_parameters(self):
        try:
            _translate_mkpkdata_to_asm(None)
            pytest.fail(
                "_translate_mkpkdata_to_asm should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_translates_data_to_asm(self, sf_data_replacement: MKPKCode):
        expected_data = ['data_1 db "hello", 0']

        data_asm: List[str] = _translate_mkpkdata_to_asm(sf_data_replacement.data)

        assert expected_data == data_asm


class TestWriteCodeToFile:
    def test_invalid_parameters(self, simple_func_call: MKPKCode):
        mock_output = "/tmp/hi"
        try:
            _write_code_to_file(None, None)
            pytest.fail(
                "_write_code_to_file should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _write_code_to_file(simple_func_call, None)
            pytest.fail(
                "_write_code_to_file should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _write_code_to_file(None, mock_output)
            pytest.fail(
                "_write_code_to_file should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_creates_file_with_path(self, simple_func_call: MKPKCode):
        output_path = "/tmp/new_file"

        _write_code_to_file(simple_func_call, output_path)

        # Check that the file exists
        assert Path(output_path).exists()

        read_code: List[str] = []
        with open(output_path, "r") as input_file:
            for line in input_file:
                read_code.append(line.replace("\n", ""))

        # Cleanup the file before asserting
        Path(output_path).unlink()

        assert simple_func_call.code == read_code

    def test_creates_file_without_path(self, simple_func_call: MKPKCode):
        output_path: str = _write_code_to_file(simple_func_call)

        # Check that the file exists
        assert Path(output_path).exists()

        read_code: List[str] = []
        with open(output_path, "r") as input_file:
            for line in input_file:
                read_code.append(line.replace("\n", ""))

        # Cleanup the file before asserting
        Path(output_path).unlink()

        assert simple_func_call.code == read_code

    def test_errors_on_invalid_path(self, simple_func_call: MKPKCode):
        invalid_path = "/a/b/c"

        try:
            _write_code_to_file(simple_func_call, invalid_path)
            pytest.fail(
                "_write_code_to_file should have failed with\
                        MKPKIntegratingError due to invalid filepath, \
                        but did not"
            )
        except MKPKIntegratingError:
            pass


class TestIntegrateMakkaPakka:
    def test_invalid_parameters(self, simple_func_call: MKPKCode):
        mock_output = "/tmp/hi"
        try:
            integrate_makka_pakka(None, None)
            pytest.fail(
                "integrate_makka_pakka should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            integrate_makka_pakka(simple_func_call, None)
            pytest.fail(
                "integrate_makka_pakka should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            integrate_makka_pakka(None, mock_output)
            pytest.fail(
                "integrate_makka_pakka should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    # TODO: Write more tests here once gadget replacement has been implemented.

    def test_writes_code_to_file(self, simple_func_call: MKPKCode):
        expected_code = [
            "Section .text",
            "    global _start",
            "_start:",
            "    mov rax, 1",
        ]

        output_path: str = integrate_makka_pakka(simple_func_call)

        # Check that the file exists
        assert Path(output_path).exists()

        read_code: List[str] = []
        with open(output_path, "r") as input_file:
            for line in input_file:
                if line != "\n":
                    read_code.append(line.replace("\n", ""))

        # Cleanup the file before asserting
        # Path(output_path).unlink()

        assert expected_code == read_code
