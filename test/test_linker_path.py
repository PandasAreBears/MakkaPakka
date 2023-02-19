from pathlib import Path

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.linking.linker_path import LinkerPath
from makka_pakka.linking.priority_list.priority_list import PriorityType

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/linking")
EMPTY_HEADINGS: str = str(RESOURCES_ROOT / "empty_headings.mkpk")
SIMPLE_LINK: str = str(RESOURCES_ROOT / "simple_lib_call.mkpk")


@pytest.fixture
def default_linker_path() -> LinkerPath:
    return LinkerPath(EMPTY_HEADINGS)


class TestLinkerPathInit:
    def test_invalid_parameters(self):
        try:
            LinkerPath(None)
            pytest.fail(
                "__init__ should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_init_creates_default_paths(self):
        linker_paths = LinkerPath(EMPTY_HEADINGS)

        # The EMPTY_HEADINGS path should be added to the linker paths.
        assert len(linker_paths) == len(LinkerPath.DEFAULT_LINKER_PATHS) + 1


class TestAddPathToLinker:
    def test_invaild_parameters(self, default_linker_path: LinkerPath):
        mock_path = str(Path.home()) + "/.local/lib/mkpk/"
        mock_priority = PriorityType.HIGH

        try:
            default_linker_path.add_path_to_linker(None, None)
            pytest.fail(
                "add_path_to_linker should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            default_linker_path.add_path_to_linker(mock_path, None)
            pytest.fail(
                "add_path_to_linker should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            default_linker_path.add_path_to_linker(None, mock_priority)
            pytest.fail(
                "add_path_to_linker should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_adds_path_to_linker(self, default_linker_path: LinkerPath):
        initial_len: int = len(default_linker_path)

        new_dir_path: str = str(Path.home()) + "/.local/lib/mkpk/"
        default_linker_path.add_path_to_linker(new_dir_path, PriorityType.HIGH)

        assert len(default_linker_path) == initial_len + 1

        # Create an empty .mkpk file in the directory, and check if the linker
        # will resolve with the added path.
        Path(new_dir_path).mkdir(parents=True, exist_ok=True)
        new_file_name: str = "add_test.mkpk"
        Path(new_dir_path + new_file_name).touch()

        resolved_mkpk_filepath = default_linker_path.find_mkpk_file(new_file_name)
        assert resolved_mkpk_filepath == new_dir_path + new_file_name

        # Cleanup
        Path(new_dir_path + new_file_name).unlink()


class TestFindMKPKFile:
    def test_invalid_parameters(self, default_linker_path: LinkerPath):
        try:
            default_linker_path.find_mkpk_file(None)
            pytest.fail(
                "find_mkpk_file should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_finds_other_file_in_main_directory(self, default_linker_path: LinkerPath):
        resolved_mkpk_file = default_linker_path.find_mkpk_file("simple_lib_call.mkpk")

        assert str(Path(SIMPLE_LINK).absolute()) == resolved_mkpk_file
