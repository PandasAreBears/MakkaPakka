from pathlib import Path
from typing import List

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.linking.priority_list.priority_list import PriorityList
from makka_pakka.linking.priority_list.priority_list import PriorityType


class LinkerPath:
    """
    A class to store paths to directories that the linker should search in to
    find linkable makka pakka files.
    """

    # The default directories to look for linkable .mkpk files in.
    DEFAULT_LINKER_PATHS: List[str] = [
        "/usr/local/lib/mkpk/",
        str(Path.home()) + "/.local/lib/mkpk/",
        str(Path(__file__).parent.parent / "lib/"),
    ]

    def __init__(self, mkpk_main_filepath: str) -> None:
        """
        LinkerPath constructor. Uses constant class attribute DEFAULT_LINKER_PATHS
        to initialise a priority list.

        :param mkpk_main_filepath: The filepath to the main .mkpk file targeted by
            compilation. The parent directory will be used as the highest priority
            directory in linking.
        """
        if (
            not isinstance(mkpk_main_filepath, str)
            or not Path(mkpk_main_filepath).exists()
        ):
            raise MKPKInvalidParameter(
                "mkpk_main_filepath", "__init__", mkpk_main_filepath
            )

        parent_abs_path = str(Path(mkpk_main_filepath).parent.resolve()) + "/"

        self.linker_paths = PriorityList(self.DEFAULT_LINKER_PATHS)

        self.linker_paths.insert_with_priority(parent_abs_path, PriorityType.HIGH)

    def add_path_to_linker(self, dir_path: str, priority: PriorityType) -> None:
        """
        Adds a directory path to the linker paths with a specified priority.

        :param dir_path: The path to directory to add to the linker path.
        :param priority: The priority to give the new linker path.
        """
        if not isinstance(dir_path, str):
            raise MKPKInvalidParameter("dir_path", "add_path_to_linker", dir_path)

        # PriorityType is an underlying int.
        if not isinstance(priority, int):
            raise MKPKInvalidParameter("priority", "add_path_to_linker", priority)

        self.linker_paths.insert_with_priority(dir_path, priority)

    def find_mkpk_file(self, mkpk_filename: str) -> str:
        """
        Iterates through the stored linker paths to find a .mkpk file using
        its basename. If there are multiple files with the same basename in the
        linkable directories, then the higher priority directory path will be
        selected.

        :param mkpk_filename: The basename of the .mkpk file. e.g "file.mkpk".
        :return: The resolved absolute filepath of the passed .mkpk filename,
            or "" if not found.
        """
        if not isinstance(mkpk_filename, str):
            raise MKPKInvalidParameter("mkpk_filename", "find_mkpk_file", mkpk_filename)

        gen_linker_paths = self.linker_paths.yield_highest_priority()

        while True:
            dir_path: str = ""
            try:
                dir_path = next(gen_linker_paths)
            except StopIteration:
                # All possible directories have been exhausted, and the file
                # hasn't been found
                return ""

            possible_filepath = Path(dir_path) / mkpk_filename
            if possible_filepath.is_file():
                return str(possible_filepath)

    def __len__(self) -> int:
        return len(self.linker_paths)
