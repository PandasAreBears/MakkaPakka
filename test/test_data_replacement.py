import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKProcessingError
from makka_pakka.linking.linker import parse_link_and_merge
from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.parsing.parsing_structures import MKPKFunction
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.processing.data_replacement import (
    _extract_data_references,
)
from makka_pakka.processing.data_replacement import (
    _extract_label_from_reference,
)
from makka_pakka.processing.data_replacement import (
    _replace_reference_with_value,
)
from makka_pakka.processing.data_replacement import (
    process_data_replacement,
)

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/processing")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SF_DATA_REPLACEMENT: str = str(RESOURCES_ROOT / "single_file_data_replacement.mkpk")
LINK_DATA_REPLACEMENT: str = str(RESOURCES_ROOT / "main_data_replacement.mkpk")
UNRESOLVED_DATA: str = str(RESOURCES_ROOT / "unresolved_data.mkpk")


@pytest.fixture
def empty_headings():
    return parse_link_and_merge(EMPTY_HEADINGS)


@pytest.fixture
def sf_data_replacement():
    return parse_link_and_merge(SF_DATA_REPLACEMENT)


@pytest.fixture
def linked_data_replacement():
    return parse_link_and_merge(LINK_DATA_REPLACEMENT)


@pytest.fixture
def unresolved_data():
    return parse_link_and_merge(UNRESOLVED_DATA)


class TestProcessDataReplacement:
    def test_invalid_parameters(self):
        try:
            process_data_replacement(None)
            pytest.fail(
                "proccess_data_replacement should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_no_replacement_on_empty_heading(self, empty_headings: MKPKIR):
        replaced_ir = process_data_replacement(empty_headings)

        # No change is expected, as there's nothing to replace.
        assert replaced_ir == empty_headings

    def test_replacement_in_single_file(self, sf_data_replacement: MKPKIR):
        replaced_ir = process_data_replacement(sf_data_replacement)

        rp_main_func = MKPKFunction.get_function_with_name(
            replaced_ir.functions, "main"
        )

        assert rp_main_func.content == [
            "mov rax, 2",
            "mov ecx, data_1",
            "xor eax, 2",
        ]

    def test_replacement_in_linked_file(self, linked_data_replacement: MKPKIR):
        replaced_ir = process_data_replacement(linked_data_replacement)

        rp_main_func = MKPKFunction.get_function_with_name(
            replaced_ir.functions, "main"
        )

        assert rp_main_func.content == ["mov rax, 5"]

    def test_unresolved_data(self, unresolved_data: MKPKIR):
        replaced_ir = process_data_replacement(unresolved_data)

        # Despite there being a data reference in the code, the data resolver
        # should do nothing with it, as there's no corresponding label. The
        # function resolve may still be able to resolve the label (with
        # function arguments).
        assert replaced_ir == unresolved_data


class TestExtractDataReferences:
    def test_invalid_parameters(self):
        try:
            _extract_data_references(None)
            pytest.fail(
                "_extract_data_references should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_extracts_no_data_reference(self):
        mock_code_line = "mov rax, }${sdkljfs{"

        # Expecting an empty list return
        assert not _extract_data_references(mock_code_line)

    def test_extracts_single_data_reference(self):
        mock_code_line = "mov rax, ${value}"
        refs = _extract_data_references(mock_code_line)

        assert len(refs) == 1
        assert refs[0] == "${value}"

    def test_extracts_multiple_data_reference(self):
        mock_code_line = "mov ${name}, ${value_a} + ${value_b}"
        refs = _extract_data_references(mock_code_line)

        assert len(refs) == 3
        assert refs[0] == "${name}"
        assert refs[1] == "${value_a}"
        assert refs[2] == "${value_b}"


class TestExtractLabelFromReference:
    def test_invalid_parameters(self):
        try:
            _extract_label_from_reference(None)
            pytest.fail(
                "_extract_label_from_reference should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_raises_error_on_invalid_input(self):
        invalid_input_1 = "${value}a"
        invalid_input_2 = "{handle}"
        invalid_input_3 = "${test{"
        invalid_input_4 = "${!}"
        invalid_input_5 = "${name?}"

        try:
            _extract_label_from_reference(invalid_input_1)
            pytest.fail(
                "_extract_label_from_reference should have failed\
                        with MKPKInvalidParameter due to malformed data\
                        reference, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _extract_label_from_reference(invalid_input_2)
            pytest.fail(
                "_extract_label_from_reference should have failed\
                        with MKPKInvalidParameter due to malformed data\
                        reference, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _extract_label_from_reference(invalid_input_3)
            pytest.fail(
                "_extract_label_from_reference should have failed\
                        with MKPKInvalidParameter due to malformed data\
                        reference, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _extract_label_from_reference(invalid_input_4)
            pytest.fail(
                "_extract_label_from_reference should have failed\
                        with MKPKProcessingError due to malformed data\
                        label in reference, but did not."
            )
        except MKPKProcessingError:
            pass

        try:
            _extract_label_from_reference(invalid_input_5)
            pytest.fail(
                "_extract_label_from_reference should have failed\
                        with MKPKProcessingError due to malformed data\
                        label in reference, but did not."
            )
        except MKPKProcessingError:
            pass

    def test_handles_valid_input(self):
        valid_input_1 = "${value}"
        valid_input_2 = "${0123456789}"
        valid_input_3 = "${snake_case_value}"

        assert "value" == _extract_label_from_reference(valid_input_1)
        assert "0123456789" == _extract_label_from_reference(valid_input_2)
        assert "snake_case_value" == _extract_label_from_reference(valid_input_3)


class TestReplaceReferenceWithValue:
    def test_invalid_parameters(self):
        mock_code_line = "mov rax, ${value}"
        mock_data_reference = "${value}"
        mock_value = MKPKData("num", 1, MKPKDataType.INT)

        try:
            _replace_reference_with_value(None, None, None)
            pytest.fail(
                "_replace_reference_with_value should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _replace_reference_with_value(mock_code_line, mock_data_reference, None)
            pytest.fail(
                "_replace_reference_with_value should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _replace_reference_with_value(mock_code_line, None, mock_value)
            pytest.fail(
                "_replace_reference_with_value should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _replace_reference_with_value(None, mock_data_reference, mock_value)
            pytest.fail(
                "_replace_reference_with_value should have failed with\
                        MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_replaces_valid_reference_with_int(self):
        code_line = "mov rax, ${num}"
        data_reference = "${num}"
        value = MKPKData("num", 1, MKPKDataType.INT)

        replaced_code_line = _replace_reference_with_value(
            code_line, data_reference, value
        )

        assert replaced_code_line == "mov rax, 1"

    def test_replaces_valid_reference_with_string(self):
        code_line = "mov rax, ${string}"
        data_reference = "${string}"
        value = MKPKData("string", "hello", MKPKDataType.STR)

        replaced_code_line = _replace_reference_with_value(
            code_line, data_reference, value
        )

        assert replaced_code_line == "mov rax, string"

    def test_replaces_valid_reference_with_register(self):
        code_line = "mov rax, ${reg}"
        data_reference = "${reg}"
        value = MKPKData("ecx", "", MKPKDataType.REGISTER)

        replaced_code_line = _replace_reference_with_value(
            code_line, data_reference, value
        )

        assert replaced_code_line == "mov rax, ecx"

    def test_invalid_replacement_generates_warning(self):
        code_line = "mov rax, ${no_label}"
        data_reference = "${not_matching}"
        value = MKPKData("no_label", "invalid", MKPKDataType.STR)

        stdout = io.StringIO()

        with redirect_stdout(stdout):
            _replace_reference_with_value(code_line, data_reference, value)

        output = stdout.getvalue()

        assert "Warning" in output
