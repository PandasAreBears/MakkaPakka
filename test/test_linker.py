from pathlib import Path
from typing import List

import pytest

from makka_pakka.exceptions.exceptions import InvalidParameter
from makka_pakka.exceptions.exceptions import LinkingError
from makka_pakka.linking.linker import parse_with_linking
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.parsing.parsing_structures import MKPKMetaData

RESOURCES_ROOT: str = Path("test/resources/mkpk_files/linking")
SIMPLE_LINK: str = str(RESOURCES_ROOT / "simple_lib_call.mkpk")
LINK_WITH_COPY: str = str(RESOURCES_ROOT / "link_with_copy.mkpk")
COPY_FILE: str = str(RESOURCES_ROOT / "copy_me.mkpk")
CYCLIC_ROOT: str = str(RESOURCES_ROOT / "root_file.mkpk")


class TestParseWithLinking:
    def test_invalid_parameters(self):
        try:
            parse_with_linking(None)
            pytest.fail(
                "parse_with_linking should have failed with\
                InvalidParameters but did not."
            )
        except InvalidParameter:
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
        parent_dir: str = "~/.local/lib/mkpk/"
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

        except LinkingError as e:
            assert "cyclic" in str(e)
