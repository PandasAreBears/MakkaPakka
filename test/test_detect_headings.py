import pytest

from makka_pakka.exceptions.exceptions import InvalidParameter
from makka_pakka.exceptions.exceptions import ParsingError
from makka_pakka.parsing.detect_headings import _detect_heading_in_line
from makka_pakka.parsing.headings import HeadingStyle


class TestDetectHeadings:
    def test_invalid_parameters(self):
        try:
            _detect_heading_in_line(None)
            pytest.fail(
                "_detect_heading_in_line should have failed with\
                InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

    def test_no_heading(self):
        heading_1: str = "hg vpawrthvdfivh"
        heading_2: str = "mov rax, 1"
        heading_3: str = "[not a heading."
        heading_4: str = "][ blah"
        heading_5: str = "sdlfkj]]"
        heading_6: str = "[[[hi]]]"

        assert _detect_heading_in_line(heading_1)[0] == HeadingStyle.NO_HEADING
        assert _detect_heading_in_line(heading_2)[0] == HeadingStyle.NO_HEADING
        assert _detect_heading_in_line(heading_3)[0] == HeadingStyle.NO_HEADING
        assert _detect_heading_in_line(heading_4)[0] == HeadingStyle.NO_HEADING
        assert _detect_heading_in_line(heading_5)[0] == HeadingStyle.NO_HEADING
        assert _detect_heading_in_line(heading_6)[0] == HeadingStyle.NO_HEADING

    def test_single_heading(self):
        heading_1: str = "[hello_world]"
        heading_2: str = "[097834]"
        heading_3: str = "[0xdeadbeef]"
        heading_4: str = "[asdfjkl234980]"

        assert _detect_heading_in_line(heading_1)[0] == HeadingStyle.SINGLE_HEADING
        assert _detect_heading_in_line(heading_2)[0] == HeadingStyle.SINGLE_HEADING
        assert _detect_heading_in_line(heading_3)[0] == HeadingStyle.SINGLE_HEADING
        assert _detect_heading_in_line(heading_4)[0] == HeadingStyle.SINGLE_HEADING

    def test_double_heading(self):
        heading_1: str = "[[code]]"
        heading_2: str = "[[hello_world1]]"
        heading_3: str = "[[64zoo]]"
        heading_4: str = "[[007]]"

        assert _detect_heading_in_line(heading_1)[0] == HeadingStyle.DOUBLE_HEADING
        assert _detect_heading_in_line(heading_2)[0] == HeadingStyle.DOUBLE_HEADING
        assert _detect_heading_in_line(heading_3)[0] == HeadingStyle.DOUBLE_HEADING
        assert _detect_heading_in_line(heading_4)[0] == HeadingStyle.DOUBLE_HEADING

    def test_invalid_heading_name_raises_error(self):
        heading_1: str = "[hello world]"
        heading_2: str = "[[cant_have_a_!]]"
        heading_3: str = "[[]]"

        try:
            _detect_heading_in_line(heading_1)
            pytest.fail(
                "_detect_heading_in_line with invalid heading name\
                should have failed with ParsingError but did not."
            )
        except ParsingError:
            pass

        try:
            _detect_heading_in_line(heading_2)
            pytest.fail(
                "_detect_heading_in_line with invalid heading name\
                should have failed with ParsingError but did not."
            )
        except ParsingError:
            pass

        try:
            _detect_heading_in_line(heading_3)
            pytest.fail(
                "_detect_heading_in_line with invalid heading name\
                should have failed with ParsingError but did not."
            )
        except ParsingError:
            pass
