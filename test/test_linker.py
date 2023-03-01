from pathlib import Path
from typing import List

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKLinkingError
from makka_pakka.linking.linker import _assert_no_conflict_in_data_labels
from makka_pakka.linking.linker import _assert_no_conflict_in_functions
from makka_pakka.linking.linker import (
    _assert_no_conflict_in_gadget_addresses,
)
from makka_pakka.linking.linker import _combine_MKPKIRs
from makka_pakka.linking.linker import merge_MKPKIRs
from makka_pakka.linking.linker import parse_link_and_merge
from makka_pakka.linking.linker import parse_with_linking
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.parsing.parsing_structures import MKPKMetaData
from test.test_parse_data import _assert_data_state_eq
from test.test_parse_functions import _assert_func_state_eq
from test.test_parse_gadgets import _assert_gadget_state_eq

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/linking")
EMPTY_FILE: str = str(RESOURCES_ROOT / "empty_file.mkpk")
SIMPLE_LINK: str = str(RESOURCES_ROOT / "simple_lib_call.mkpk")
LINK_WITH_COPY: str = str(RESOURCES_ROOT / "link_with_copy.mkpk")
COPY_FILE: str = str(RESOURCES_ROOT / "copy_me.mkpk")
CYCLIC_ROOT: str = str(RESOURCES_ROOT / "root_file.mkpk")
CLEAN_MERGE: str = str(RESOURCES_ROOT / "clean_merge_main.mkpk")
UNCLEAN_MERGE: str = str(RESOURCES_ROOT / "unclean_merge_main.mkpk")
UNLINKED_FILE: str = str(RESOURCES_ROOT / "unlinked_file.mkpk")
MULTIPART_ROOT: str = str(RESOURCES_ROOT / "multipart_a.mkpk")


@pytest.fixture
def clean_merge() -> List[MKPKIR]:
    parsed_files = parse_with_linking(CLEAN_MERGE)
    assert len(parsed_files) == 2

    return parsed_files


@pytest.fixture
def unclean_merge() -> List[MKPKIR]:
    parsed_files = parse_with_linking(UNCLEAN_MERGE)
    assert len(parsed_files) == 2

    return parsed_files


@pytest.fixture
def unlinked_file() -> List[MKPKIR]:
    parsed_files = parse_with_linking(UNLINKED_FILE)
    assert len(parsed_files) == 1

    return parsed_files


@pytest.fixture
def multipart_merge() -> List[MKPKIR]:
    parsed_files = parse_with_linking(MULTIPART_ROOT)
    assert len(parsed_files) == 4

    return parsed_files


class TestParseLinkAndMerge:
    def test_invalid_parameters(self):
        try:
            parse_link_and_merge(None)

            pytest.fail(
                "parse_makka_pakka should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_empty_file(self):
        file_ir = parse_link_and_merge(EMPTY_FILE)

        assert len(file_ir.functions) == 0
        assert len(file_ir.data) == 0
        assert len(file_ir.gadgets) == 0

    def test_multipart_merge(self):
        file_ir = parse_link_and_merge(MULTIPART_ROOT)

        # The accuracy of this merge is more throughly tested in the
        # subfunction unit tests, this test is just checking that all the parts
        # are linked together correctly.
        assert len(file_ir.functions) == 8
        assert len(file_ir.data) == 8
        assert len(file_ir.gadgets) == 4


class TestParseWithLinking:
    def test_invalid_parameters(self):
        try:
            parse_with_linking(None)
            pytest.fail(
                "parse_with_linking should have failed with\
                MKPKInvalidParameters but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_simple_linking_succeeds(self):
        mkpkirs: List[MKPKIR] = parse_with_linking(SIMPLE_LINK)

        assert len(mkpkirs) == 2

        assert MKPKMetaData.get_metadata_with_label(
            mkpkirs[0].metadata, "filename"
        ).values == ["simple_lib_call.mkpk"]

        assert MKPKMetaData.get_metadata_with_label(
            mkpkirs[0].metadata, "link_depth"
        ).values == ["0"]

        assert MKPKMetaData.get_metadata_with_label(
            mkpkirs[1].metadata, "filename"
        ).values == ["lib_a.mkpk"]

        assert MKPKMetaData.get_metadata_with_label(
            mkpkirs[1].metadata, "link_depth"
        ).values == ["1"]

    def test_finds_file_in_lib_dir(self):
        # A system mkpk library path as defined by LinkerPath
        parent_dir: str = str(Path.home()) + "/.local/lib/mkpk/"
        Path(parent_dir).mkdir(parents=True, exist_ok=True)

        # Move the copy file, then delete from the test directory.
        basename: str = Path(COPY_FILE).name
        Path(COPY_FILE).rename(parent_dir + basename)

        # Check that the copy file is no longer in the local dir.
        assert not Path(COPY_FILE).exists()

        error: Exception = None
        try:
            parse_with_linking(LINK_WITH_COPY)
        except Exception as e:
            error = e

        # Clean up by moving the copied file back to the local dir.
        Path(parent_dir + basename).rename(COPY_FILE)

        # Only check for an error after cleanup.
        assert not error

    def test_detects_cyclic_linking(self):
        try:
            parse_with_linking(CYCLIC_ROOT)

        except MKPKLinkingError as e:
            assert "cyclic" in str(e)


class TestAssertNoConflictInFunctions:
    def test_invalid_parameters(self, clean_merge: List[MKPKIR]):
        mock_ir1 = clean_merge[0]
        mock_ir2 = clean_merge[1]

        try:
            _assert_no_conflict_in_functions(None, None)
            pytest.fail(
                "_assert_no_conflict_in_functions should have failed\
                       with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_no_conflict_in_functions(mock_ir1, None)
            pytest.fail(
                "_assert_no_conflict_in_functions should have failed\
                       with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_no_conflict_in_functions(None, mock_ir2)
            pytest.fail(
                "_assert_no_conflict_in_functions should have failed\
                       with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_does_not_assert_on_clean_merge(self, clean_merge: List[MKPKIR]):
        _assert_no_conflict_in_functions(clean_merge[0], clean_merge[1])

    def test_asserts_on_unclean_merge(self, unclean_merge: List[MKPKIR]):
        try:
            _assert_no_conflict_in_functions(unclean_merge[0], unclean_merge[1])
            pytest.fail(
                "_assert_no_conflict_in_functions should have failed\
                        with MKPKLinkingError due to duplicate function names in\
                        linked file, but did not."
            )
        except MKPKLinkingError:
            pass


class TestAssertNoConflictInDataLabels:
    def test_invalid_parameters(self, clean_merge: List[MKPKIR]):
        mock_ir1 = clean_merge[0]
        mock_ir2 = clean_merge[1]

        try:
            _assert_no_conflict_in_data_labels(None, None)
            pytest.fail(
                "_assert_no_conflict_in_data_labels should have failed\
                       with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_no_conflict_in_data_labels(mock_ir1, None)
            pytest.fail(
                "_assert_no_conflict_in_data_labels should have failed\
                       with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_no_conflict_in_data_labels(None, mock_ir2)
            pytest.fail(
                "_assert_no_conflict_in_data_labels should have failed\
                       with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_does_not_assert_on_clean_merge(self, clean_merge: List[MKPKIR]):
        _assert_no_conflict_in_data_labels(clean_merge[0], clean_merge[1])

    def test_asserts_on_unclean_merge(self, unclean_merge: List[MKPKIR]):
        try:
            _assert_no_conflict_in_data_labels(unclean_merge[0], unclean_merge[1])
            pytest.fail(
                "_assert_no_conflict_in_data_labels should have failed\
                        with MKPKLinkingError due to duplicate data labels in\
                        linked file, but did not."
            )
        except MKPKLinkingError:
            pass


class TestAssertNoConflictInGadgetAddresses:
    def test_invalid_parameters(self, clean_merge: List[MKPKIR]):
        mock_ir1 = clean_merge[0]
        mock_ir2 = clean_merge[1]

        try:
            _assert_no_conflict_in_gadget_addresses(None, None)
            pytest.fail(
                "_assert_no_conflict_in_gadget_addresses should have\
                            failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_no_conflict_in_gadget_addresses(mock_ir1, None)
            pytest.fail(
                "_assert_no_conflict_in_gadget_addresses should have\
                            failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_no_conflict_in_gadget_addresses(None, mock_ir2)
            pytest.fail(
                "_assert_no_conflict_in_gadget_addresses should have\
                            failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_does_not_assert_on_clean_merge(self, clean_merge: List[MKPKIR]):
        _assert_no_conflict_in_gadget_addresses(clean_merge[0], clean_merge[1])

    def test_asserts_on_unclean_merge(self, unclean_merge: List[MKPKIR]):
        try:
            _assert_no_conflict_in_gadget_addresses(unclean_merge[0], unclean_merge[1])
            pytest.fail(
                "_assert_no_conflict_in_gadget_addreseses should have failed\
                        with MKPKLinkingError due to duplicate gadget memory\
                        addresses in linked file, but did not."
            )
        except MKPKLinkingError:
            pass


class TestCombineMKPKIRs:
    def test_invalid_parameters(self, clean_merge: List[MKPKIR]):
        mock_ir1 = clean_merge[0]
        mock_ir2 = clean_merge[1]

        try:
            _combine_MKPKIRs(None, None)
            pytest.fail(
                "_combine_MKPKIRs should have\
                            failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _combine_MKPKIRs(mock_ir1, None)
            pytest.fail(
                "_combine_MKPKIRs should have\
                            failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _combine_MKPKIRs(None, mock_ir2)
            pytest.fail(
                "_combine_MKPKIRs should have\
                            failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_combines_functions(self, clean_merge: List[MKPKIR]):
        expected_funcs: List[str] = ["main", "func_a", "func_b", "func_c"]

        ir_all: MKPKIR = _combine_MKPKIRs(clean_merge[0], clean_merge[1])

        assert len(ir_all.functions) == len(expected_funcs)

        assert sorted(expected_funcs) == sorted([f.name for f in ir_all.functions])

    def test_combines_data_labels(self, clean_merge: List[MKPKIR]):
        expected_labels: List[str] = ["panda", "giraffe", "lion", "platypus"]

        ir_all: MKPKIR = _combine_MKPKIRs(clean_merge[0], clean_merge[1])

        assert len(expected_labels) == len(ir_all.data)

        assert sorted(expected_labels) == sorted([d.name for d in ir_all.data])

    def test_combines_gadget_addresses(self, clean_merge: List[MKPKIR]):
        expected_addresses: List[str] = ["0xabcdef12", "0x09876543"]

        ir_all: MKPKIR = _combine_MKPKIRs(clean_merge[0], clean_merge[1])

        assert len(expected_addresses) == len(ir_all.gadgets)

        assert sorted(expected_addresses) == sorted(
            [g.memory_location for g in ir_all.gadgets]
        )


class TestMergeMKPKIRs:
    def test_invalid_parameters(self):
        try:
            merge_MKPKIRs(None)
            pytest.fail(
                "merge_MKPKIRs should have\
                            failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_merge_unlinked_file(self, unlinked_file: List[MKPKIR]):
        merged_ir: MKPKIR = merge_MKPKIRs(unlinked_file)

        assert len(merged_ir.functions) == 1
        assert len(merged_ir.data) == 1
        assert len(merged_ir.gadgets) == 1

        _assert_func_state_eq(
            merged_ir.functions[0], "main", True, 0, [], ["mov rax, 15"]
        )
        _assert_data_state_eq(merged_ir.data[0], "hi", "hello", MKPKDataType.STR)
        _assert_gadget_state_eq(merged_ir.gadgets[0], "0xbbbbbbbb", ["xor $1, $1"])

    def test_clean_merge(self, clean_merge: List[MKPKIR]):
        merged_ir: MKPKIR = merge_MKPKIRs(clean_merge)

        expected_functions: List[str] = ["main", "func_a", "func_b", "func_c"]
        expected_labels: List[str] = ["panda", "giraffe", "lion", "platypus"]
        expected_addresses: List[str] = ["0xabcdef12", "0x09876543"]

        assert len(merged_ir.functions) == len(expected_functions)
        assert len(merged_ir.data) == len(expected_labels)
        assert len(merged_ir.gadgets) == len(expected_addresses)

        assert sorted(expected_functions) == sorted(
            [f.name for f in merged_ir.functions]
        )
        assert sorted(expected_labels) == sorted([d.name for d in merged_ir.data])
        assert sorted(expected_addresses) == sorted(
            [g.memory_location for g in merged_ir.gadgets]
        )

    def test_multipart_merge(self, multipart_merge: List[MKPKIR]):
        merged_ir: MKPKIR = merge_MKPKIRs(multipart_merge)

        expected_functions: List[str] = [
            "main",
            "blue",
            "green",
            "yellow",
            "orange",
            "purple",
            "red",
            "pink",
        ]
        expected_labels: List[str] = [
            "apple",
            "banana",
            "cherry",
            "dragon",
            "elder",
            "fig",
            "grape",
            "hack",
        ]
        expected_addresses: List[str] = [
            "0x11111111",
            "0x22222222",
            "0x33333333",
            "0x44444444",
        ]

        assert len(merged_ir.functions) == len(expected_functions)
        assert len(merged_ir.data) == len(expected_labels)
        assert len(merged_ir.gadgets) == len(expected_addresses)

        assert sorted(expected_functions) == sorted(
            [f.name for f in merged_ir.functions]
        )
        assert sorted(expected_labels) == sorted([d.name for d in merged_ir.data])
        assert sorted(expected_addresses) == sorted(
            [g.memory_location for g in merged_ir.gadgets]
        )
