from pathlib import Path
from typing import List

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKParsingError
from makka_pakka.parsing.parse import _split_into_headings
from makka_pakka.parsing.parse_headings import parse_functions
from makka_pakka.parsing.parsing_structures import MKPKFunction
from makka_pakka.parsing.parsing_structures import MKPKLines

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/parsing")
EMPTY_FILE: str = str(RESOURCES_ROOT / "empty_file.mkpk")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_CODE: str = str(RESOURCES_ROOT / "simple_code.mkpk")
TWO_FUNCS_SINGLE_ARG: str = str(RESOURCES_ROOT / "single_argument.mkpk")
MULTIPLE_ARGS: str = str(RESOURCES_ROOT / "multiple_arguments.mkpk")
INVALID_ARG: str = str(RESOURCES_ROOT / "invalid_argument.mkpk")


@pytest.fixture
def empty_file() -> MKPKLines:
    return _split_into_headings(EMPTY_FILE)


@pytest.fixture
def empty_headings() -> MKPKLines:
    return _split_into_headings(EMPTY_HEADINGS)


@pytest.fixture
def simple_code_lines() -> MKPKLines:
    return _split_into_headings(SIMPLE_CODE)


@pytest.fixture
def two_funcs_single_arg() -> MKPKLines:
    return _split_into_headings(TWO_FUNCS_SINGLE_ARG)


@pytest.fixture
def mutiple_args() -> MKPKLines:
    return _split_into_headings(MULTIPLE_ARGS)


@pytest.fixture
def invalid_argument() -> MKPKLines:
    return _split_into_headings(INVALID_ARG)


def _assert_func_state_eq(
    func: MKPKFunction,
    name: str,
    is_main: bool,
    num_arguments: int,
    arguments: List[str],
    content: List[str],
):
    assert func.name == name
    assert func.is_main == is_main
    assert func.num_arguments == num_arguments
    assert func.arguments == arguments
    assert func.content == content


class TestParseFunctions:
    def test_invalid_parameters(self):
        try:
            parse_functions(None)
            pytest.fail(
                "parse_functions should have failed with\
                InvalidParamter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_empty_file_raises_error(self, empty_file: MKPKLines):
        functions = parse_functions(empty_file.code)

        assert len(functions) == 0

    def test_empty_headings(self, empty_headings: MKPKLines):
        functions = parse_functions(empty_headings.code)

        assert len(functions) == 0

    def test_parse_simple_code(self, simple_code_lines: MKPKLines):
        functions: List[MKPKFunction] = parse_functions(simple_code_lines.code)

        assert len(functions) == 1

        _assert_func_state_eq(functions[0], "main", True, 0, [], ["mov rax, 1"])

    def test_parse_two_funcs_single_arg(self, two_funcs_single_arg: MKPKLines):
        functions: List[MKPKFunction] = parse_functions(two_funcs_single_arg.code)

        assert len(functions) == 2

        _assert_func_state_eq(
            functions[0], "main", True, 0, [], ["mov rax, 1", "> func2 2"]
        )

        _assert_func_state_eq(
            functions[1], "func2", False, 1, ["val"], ["mov rax, ${val}"]
        )

    def test_multiple_args(self, mutiple_args: MKPKLines):
        functions: List[MKPKFunction] = parse_functions(mutiple_args.code)

        assert len(functions) == 2

        _assert_func_state_eq(
            functions[0], "main", True, 0, [], ["mov rax, 1", "> func2 2 3 6"]
        )
        _assert_func_state_eq(
            functions[1],
            "func2",
            False,
            3,
            ["arg1", "arg2", "arg3"],
            ["mov rax, ${arg1}"],
        )

    def test_invalid_function_argument(self, invalid_argument: MKPKLines):
        try:
            parse_functions(invalid_argument.code)
            pytest.fail(
                "parse_functions should have failed with MKPKParsingError\
                due to having an invalid argument name, but did not."
            )
        except MKPKParsingError:
            pass
