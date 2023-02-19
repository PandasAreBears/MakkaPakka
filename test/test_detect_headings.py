from typing import Callable

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKNameError
from makka_pakka.exceptions.exceptions import MKPKParsingError
from makka_pakka.parsing.detect_headings import _assert_valid_mkpk_name
from makka_pakka.parsing.detect_headings import detect_heading_in_line
from makka_pakka.parsing.detect_headings import HeadingStyle


class TestDetectHeadingInLine:
    def test_invalid_parameters(self):
        try:
            detect_heading_in_line(None)
            pytest.fail(
                "_detect_heading_in_line should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_no_heading(self):
        heading_1: str = "hg vpawrthvdfivh"
        heading_2: str = "mov rax, 1"
        heading_3: str = "[not a heading."
        heading_4: str = "][ blah"
        heading_5: str = "sdlfkj]]"
        heading_6: str = "[[[hi]]]"

        assert detect_heading_in_line(heading_1)[0] == HeadingStyle.NO_HEADING
        assert detect_heading_in_line(heading_2)[0] == HeadingStyle.NO_HEADING
        assert detect_heading_in_line(heading_3)[0] == HeadingStyle.NO_HEADING
        assert detect_heading_in_line(heading_4)[0] == HeadingStyle.NO_HEADING
        assert detect_heading_in_line(heading_5)[0] == HeadingStyle.NO_HEADING
        assert detect_heading_in_line(heading_6)[0] == HeadingStyle.NO_HEADING

    def test_single_heading(self):
        heading_1: str = "[hello_world]"
        heading_2: str = "[097834]"
        heading_3: str = "[0xdeadbeef]"
        heading_4: str = "[asdfjkl234980]"

        assert detect_heading_in_line(heading_1)[0] == HeadingStyle.SINGLE_HEADING
        assert detect_heading_in_line(heading_2)[0] == HeadingStyle.SINGLE_HEADING
        assert detect_heading_in_line(heading_3)[0] == HeadingStyle.SINGLE_HEADING
        assert detect_heading_in_line(heading_4)[0] == HeadingStyle.SINGLE_HEADING

    def test_double_heading(self):
        heading_1: str = "[[code]]"
        heading_2: str = "[[hello_world1]]"
        heading_3: str = "[[64zoo]]"
        heading_4: str = "[[007]]"

        assert detect_heading_in_line(heading_1)[0] == HeadingStyle.DOUBLE_HEADING
        assert detect_heading_in_line(heading_2)[0] == HeadingStyle.DOUBLE_HEADING
        assert detect_heading_in_line(heading_3)[0] == HeadingStyle.DOUBLE_HEADING
        assert detect_heading_in_line(heading_4)[0] == HeadingStyle.DOUBLE_HEADING

    def test_invalid_heading_name_raises_error(self):
        heading_1: str = "[hello world]"
        heading_2: str = "[[cant_have_a_!]]"
        heading_3: str = "[[]]"

        try:
            detect_heading_in_line(heading_1)
            pytest.fail(
                "_detect_heading_in_line with invalid heading name\
                should have failed with MKPKParsingError but did not."
            )
        except MKPKParsingError:
            pass

        try:
            detect_heading_in_line(heading_2)
            pytest.fail(
                "_detect_heading_in_line with invalid heading name\
                should have failed with MKPKParsingError but did not."
            )
        except MKPKParsingError:
            pass

        try:
            detect_heading_in_line(heading_3)
            pytest.fail(
                "_detect_heading_in_line with invalid heading name\
                should have failed with MKPKParsingError but did not."
            )
        except MKPKParsingError:
            pass


class TestAssertValidHeadingName:
    def test_invalid_parameters(self):
        mock_name = "code"
        mock_line = "[[code]]"
        try:
            _assert_valid_mkpk_name(None, None)
            pytest.fail(
                "_assert_valid_mkpk_name should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_valid_mkpk_name(mock_name, None)
            pytest.fail(
                "_assert_valid_mkpk_name should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _assert_valid_mkpk_name(None, mock_line)
            pytest.fail(
                "_assert_valid_mkpk_name should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_errors_when_name_is_invalid(self):
        get_mock_line: Callable[[str], str] = lambda name: f"[[{name}]]"
        invalid_name1: str = "cod?"
        invalid_name2: str = "in-valid"
        invalid_name3: str = "123456 "
        invalid_name4: str = "*HI"

        try:
            _assert_valid_mkpk_name(invalid_name1, get_mock_line(invalid_name1))
            pytest.fail(
                "_assert_valid_mkpk_name should have raised\
                MKPKParsingError but did not."
            )
        except MKPKNameError:
            pass

        try:
            _assert_valid_mkpk_name(invalid_name2, get_mock_line(invalid_name2))
            pytest.fail(
                "_assert_valid_mkpk_name should have raised\
                MKPKParsingError but did not."
            )
        except MKPKNameError:
            pass

        try:
            _assert_valid_mkpk_name(invalid_name3, get_mock_line(invalid_name3))
            pytest.fail(
                "_assert_valid_mkpk_name should have raised\
                MKPKParsingError but did not."
            )
        except MKPKNameError:
            pass

        try:
            _assert_valid_mkpk_name(invalid_name4, get_mock_line(invalid_name4))
            pytest.fail(
                "_assert_valid_mkpk_name should have raised\
                MKPKParsingError but did not."
            )
        except MKPKNameError:
            pass

    def test_does_not_error_when_name_is_valid(self):
        get_mock_line: Callable[[str], str] = lambda name: f"[[{name}]]"
        valid_name1: str = "data"
        valid_name2: str = "code"
        valid_name3: str = "gadget"

        _assert_valid_mkpk_name(valid_name1, get_mock_line(valid_name1))
        _assert_valid_mkpk_name(valid_name2, get_mock_line(valid_name2))
        _assert_valid_mkpk_name(valid_name3, get_mock_line(valid_name3))
