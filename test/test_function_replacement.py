from pathlib import Path
from typing import List

import pytest

from makka_pakka.exceptions.exceptions import MKPKCyclicDependency
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKNameError
from makka_pakka.exceptions.exceptions import MKPKProcessingError
from makka_pakka.linking.linker import parse_link_and_merge
from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.parsing.parsing_structures import MKPKFunction
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.processing.function_replacement import (
    _assert_correct_num_of_args,
)
from makka_pakka.processing.function_replacement import (
    _get_function_by_name_or_assert,
)
from makka_pakka.processing.function_replacement import (
    _get_line_as_function_call,
)
from makka_pakka.processing.function_replacement import (
    _get_ref_value_from_arguments,
)
from makka_pakka.processing.function_replacement import (
    _parse_line_as_function_call,
)
from makka_pakka.processing.function_replacement import (
    process_function_replacement,
)
from makka_pakka.processing.processing_structures import MKPKArgumentSet
from makka_pakka.processing.processing_structures import MKPKFunctionCall
from test.test_parse_data import _assert_data_state_eq
from test.test_parse_functions import _assert_func_state_eq

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/processing")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_FUNC_CALL: str = str(RESOURCES_ROOT / "simple_func_call.mkpk")
SIMPLE_FUNC_WITH_ARGS: str = str(RESOURCES_ROOT / "simple_func_with_args.mkpk")
INVALID_ARG_REF: str = str(RESOURCES_ROOT / "invalid_arg_ref.mkpk")
INT_ARG: str = str(RESOURCES_ROOT / "int_arg.mkpk")
LABEL_ARG: str = str(RESOURCES_ROOT / "label_arg.mkpk")
REGISTER_ARG: str = str(RESOURCES_ROOT / "register_arg_ref.mkpk")
MULTIPLE_ARGS: str = str(RESOURCES_ROOT / "multiple_arguments.mkpk")
DEEP_FUNC_REPL: str = str(RESOURCES_ROOT / "deep_function_replacement.mkpk")
CYCLIC_FUNC_CALLS: str = str(RESOURCES_ROOT / "cyclic_func_calls.mkpk")
STR_LABEL_ARG: str = str(RESOURCES_ROOT / "str_label_arg.mkpk")


@pytest.fixture
def empty_headings() -> MKPKIR:
    return parse_link_and_merge(EMPTY_HEADINGS)


@pytest.fixture
def simple_func_call() -> MKPKIR:
    return parse_link_and_merge(SIMPLE_FUNC_CALL)


@pytest.fixture
def simple_func_with_args() -> MKPKIR:
    return parse_link_and_merge(SIMPLE_FUNC_WITH_ARGS)


@pytest.fixture
def int_arg() -> MKPKIR:
    return parse_link_and_merge(INT_ARG)


@pytest.fixture
def label_arg() -> MKPKIR:
    return parse_link_and_merge(LABEL_ARG)


@pytest.fixture
def register_arg() -> MKPKIR:
    return parse_link_and_merge(REGISTER_ARG)


@pytest.fixture
def str_label_arg() -> MKPKIR:
    return parse_link_and_merge(STR_LABEL_ARG)


@pytest.fixture
def invalid_arg_ref() -> MKPKIR:
    return parse_link_and_merge(INVALID_ARG_REF)


@pytest.fixture
def multiple_args() -> MKPKIR:
    return parse_link_and_merge(MULTIPLE_ARGS)


@pytest.fixture
def deep_func_repl() -> MKPKIR:
    return parse_link_and_merge(DEEP_FUNC_REPL)


@pytest.fixture
def cyclic_func_call() -> MKPKIR:
    return parse_link_and_merge(CYCLIC_FUNC_CALLS)


def _assert_function_call_state_eq(
    func_call: MKPKFunctionCall, name: str, args: List[str]
):
    assert func_call.name == name
    assert func_call.args == args


class TestGetFunctionByNameOrAssert:
    def test_invalid_parameters(self, simple_func_call: MKPKIR):
        mock_functions = simple_func_call.functions
        mock_name = "blah"
        try:
            _get_function_by_name_or_assert(None, None)
            pytest.fail(
                "_get_function_by_name_or_assert should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _get_function_by_name_or_assert(mock_functions, None)
            pytest.fail(
                "_get_function_by_name_or_assert should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _get_function_by_name_or_assert(None, mock_name)
            pytest.fail(
                "_get_function_by_name_or_assert should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_gets_func_with_valid_name(self, simple_func_call: MKPKIR):
        func: MKPKFunction = _get_function_by_name_or_assert(
            simple_func_call.functions, "sub_func"
        )

        _assert_func_state_eq(func, "sub_func", False, 0, [], ["mov rax, 1"])

    def test_asserts_with_invalid_name(self, simple_func_call: MKPKIR):
        try:
            _get_function_by_name_or_assert(simple_func_call.functions, "invalid")
            pytest.fail(
                "_get_function_by_name_or_assert should have failed\
                        with MKPKProcessingError due to invalid function name,\
                        but did not."
            )
        except MKPKProcessingError:
            pass


class TestGetRefValueFromArguments:
    def test_invalid_parameters(self, simple_func_with_args: MKPKIR):
        mock_data_reference = "${arg1}"
        mock_func = simple_func_with_args.functions[1]
        mock_args = MKPKArgumentSet(1, 2, 3)
        mock_data = simple_func_with_args.data

        try:
            _get_ref_value_from_arguments(None, None, None, None)
            pytest.fail(
                "_get_ref_value_from_arguments should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _get_ref_value_from_arguments(
                mock_data_reference, mock_func, mock_args, None
            )
            pytest.fail(
                "_get_ref_value_from_arguments should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _get_ref_value_from_arguments(
                mock_data_reference, mock_func, None, mock_data
            )
            pytest.fail(
                "_get_ref_value_from_arguments should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _get_ref_value_from_arguments(
                mock_data_reference, None, mock_args, mock_data
            )
            pytest.fail(
                "_get_ref_value_from_arguments should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _get_ref_value_from_arguments(None, mock_func, mock_args, mock_data)
            pytest.fail(
                "_get_ref_value_from_arguments should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_asserts_on_invalid_reference(self, invalid_arg_ref: MKPKIR):
        try:
            _get_ref_value_from_arguments(
                "${not_here}",
                invalid_arg_ref.functions[1],
                MKPKArgumentSet(1),
                invalid_arg_ref.data,
            )
            pytest.fail(
                "_get_ref_value_from_arguments should have failed\
                        with MKPKProcessingError due to invalid data reference\
                        , but did not."
            )
        except MKPKProcessingError:
            pass

    def test_resolves_integer_arg(self, int_arg: MKPKIR):
        data: MKPKData = _get_ref_value_from_arguments(
            "${arg}", int_arg.functions[1], MKPKArgumentSet("1"), int_arg.data
        )
        _assert_data_state_eq(data, "", 1, MKPKDataType.INT)

    def test_resolves_int_label_arg(self, label_arg: MKPKIR):
        data: MKPKData = _get_ref_value_from_arguments(
            "${arg}",
            label_arg.functions[1],
            MKPKArgumentSet('"pick_me"'),
            label_arg.data,
        )

        _assert_data_state_eq(data, "pick_me", 1, MKPKDataType.INT)

    def test_resolves_register_arg(self, register_arg: MKPKIR):
        data: MKPKData = _get_ref_value_from_arguments(
            "${arg}",
            register_arg.functions[1],
            MKPKArgumentSet("rax"),
            register_arg.data,
        )

        _assert_data_state_eq(data, "rax", "", MKPKDataType.REGISTER)

    def test_resolves_str_label_arg(self, str_label_arg: MKPKIR):
        data: MKPKData = _get_ref_value_from_arguments(
            "${arg}",
            str_label_arg.functions[1],
            MKPKArgumentSet('"pick_me_str"'),
            str_label_arg.data,
        )

        _assert_data_state_eq(data, "pick_me_str", "", MKPKDataType.STR)


class TestAssertCorrectNumOfArgs:
    def test_invalid_parameters(self, simple_func_call: MKPKIR):
        mock_curr_func = simple_func_call.functions[1]
        mock_passed_args = MKPKArgumentSet("1")

        try:
            _assert_correct_num_of_args(None, None)
            pytest.fail(
                "_assert_correct_num_of_args should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_correct_num_of_args(mock_curr_func, None)
            pytest.fail(
                "_assert_correct_num_of_args should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_correct_num_of_args(None, mock_passed_args)
            pytest.fail(
                "_assert_correct_num_of_args should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_does_not_assert_on_equal_args(self, multiple_args: MKPKIR):
        _assert_correct_num_of_args(
            multiple_args.functions[1], MKPKArgumentSet("1", "2", "3")
        )

    def test_asserts_on_unequal_args(self, multiple_args: MKPKIR):
        try:
            _assert_correct_num_of_args(
                multiple_args.functions[1], MKPKArgumentSet("1", "2")
            )
            pytest.fail(
                "_assert_correct_num_of_args should have failed with\
                        MKPKProcessingError due to unequal num. args, but\
                        did not."
            )
        except MKPKProcessingError:
            pass


class TestParseLineAsFunctionCall:
    def test_invalid_parameters(self):
        try:
            _parse_line_as_function_call(None)
            pytest.fail(
                "_parse_line_as_function_call should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_no_call_directive_asserts(self):
        # This is test that there's no '>' at the start of the line
        test_line = "not_a_func_call"

        try:
            _parse_line_as_function_call(test_line)
            pytest.fail(
                "_parse_line_as_function_call should have failed with\
                        MKPKProcessingError due to the line not having the \
                        function call directive '>', but did not."
            )
        except MKPKProcessingError:
            pass

    def test_no_function_name_asserts(self):
        test_line = ">"

        try:
            _parse_line_as_function_call(test_line)
            pytest.fail(
                "_parse_line_as_function_call should have failed with\
                        MKPKProcessingError due to the line not having a\
                        function name, but did not."
            )
        except MKPKProcessingError:
            pass

    def test_invalid_function_name(self):
        test_line = "> bad!name"

        try:
            _parse_line_as_function_call(test_line)
            pytest.fail(
                "_parse_line_as_function_call should have failed with\
                        MKPKNameError due to the line not having a\
                        invalid function name, but did not."
            )
        except MKPKNameError:
            pass

    def test_generates_func_call_without_args(self):
        test_line = "> func_name"

        gen_func_call: MKPKFunctionCall = _parse_line_as_function_call(test_line)

        _assert_function_call_state_eq(gen_func_call, "func_name", [])

    def test_generates_func_call_with_args(self):
        test_line = "> func arg1 arg2 arg3"

        gen_func_call: MKPKFunctionCall = _parse_line_as_function_call(test_line)

        _assert_function_call_state_eq(gen_func_call, "func", ["arg1", "arg2", "arg3"])


class TestGetLineAsFunctionCall:
    def test_invalid_parameters(self):
        try:
            _get_line_as_function_call(None)
            pytest.fail(
                "_get_line_as_function_call should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_returns_on_valid_line(self):
        test_line = "> func arg1 arg2 arg3"

        func_call: MKPKFunctionCall = _get_line_as_function_call(test_line)

        _assert_function_call_state_eq(func_call, "func", ["arg1", "arg2", "arg3"])

    def test_returns_non_invalid_line(self):
        test_line = "mov rax, 1"

        assert None is _get_line_as_function_call(test_line)


class TestProcessFunctionReplacement:
    def test_invalid_parameters(self):
        try:
            _get_line_as_function_call(None)
            pytest.fail(
                "_get_line_as_function_call should have failed\
                        with MKPKInvalidParameter, but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_simple_func_call(self, simple_func_call: MKPKIR):
        expected_code: List[str] = ["mov rax, 1"]

        code: List[str] = process_function_replacement(simple_func_call)

        assert expected_code == code

    def test_func_call_with_int_args(self, int_arg: MKPKIR):
        expected_code: List[str] = ["mov rax, 1"]

        code: List[str] = process_function_replacement(int_arg)

        assert expected_code == code

    def test_func_call_with_int_label_args(self, label_arg: MKPKIR):
        expected_code: List[str] = ["mov rax, 1"]

        code: List[str] = process_function_replacement(label_arg)

        assert expected_code == code

    def test_deep_func_replacement(self, deep_func_repl: MKPKIR):
        expected_code: List[str] = [
            "xor eax, eax",
            "mov ecx, 3",
            "add rbp, 4",
            "mov rsi, 2",
        ]

        code: List[str] = process_function_replacement(deep_func_repl)

        assert expected_code == code

    def test_cyclic_func_calls(self, cyclic_func_call: MKPKIR):
        try:
            process_function_replacement(cyclic_func_call)
            pytest.fail(
                "process_function_replacement should have failed with\
                        MKPKCyclicDependency due to cyclic function calls,\
                        but did not."
            )
        except MKPKCyclicDependency:
            pass
