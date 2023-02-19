from typing import List

import pytest

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.linking.priority_list.priority_list import PriorityList
from makka_pakka.linking.priority_list.priority_list import PriorityType


@pytest.fixture
def three_items() -> PriorityList:
    return PriorityList(["one", "two", "three"])


class TestPriorityListInit:
    def test_invalid_parameters(self):
        try:
            PriorityList(None)
            pytest.fail(
                "__init__ should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_init_with_items(self):
        list_items = ["one", "two", "three"]
        priority = PriorityList(list_items)

        assert len(priority) == 3

        assert list(priority.items) == list_items

    def test_init_without_items(self):
        priority = PriorityList()

        assert len(priority) == 0

        assert not list(priority.items)


class TestInsertWithPriority:
    def test_invalid_parameters(self, three_items: PriorityList):
        mock_item = "hi"
        mock_priority = PriorityType.HIGH

        try:
            three_items.insert_with_priority(None, None)
            pytest.fail(
                "insert_with_priority should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            three_items.insert_with_priority(mock_item, None)
            pytest.fail(
                "insert_with_priority should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            three_items.insert_with_priority(None, mock_priority)
            pytest.fail(
                "insert_with_priority should have failed with MKPKInvalidParameter\
                but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_insert_with_priority_high(self, three_items: PriorityList):
        three_items.insert_with_priority("zero", PriorityType.HIGH)

        assert len(three_items) == 4

        assert next(three_items.yield_highest_priority()) == "zero"

    def test_insert_with_priority_low(self, three_items: PriorityList):
        three_items.insert_with_priority("four", PriorityType.LOW)

        assert len(three_items) == 4

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) != "four"
        assert next(gen_priority) != "four"
        assert next(gen_priority) != "four"
        assert next(gen_priority) == "four"

    def test_insert_with_priority_none(self, three_items: PriorityList):
        three_items.insert_with_priority("four", PriorityType.NONE)

        assert len(three_items) == 3

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) != "four"
        assert next(gen_priority) != "four"
        assert next(gen_priority) != "four"


class TestInsertHighestPriority:
    def test_invalid_parameters(self, three_items: PriorityList):
        try:
            three_items.insert_highest_priority(None)
            pytest.fail(
                "insert_highest_priority should have failed with\
                 MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_inserts_into_highest_priority(self, three_items: PriorityList):
        three_items.insert_highest_priority("zero")

        assert len(three_items) == 4

        assert next(three_items.yield_highest_priority()) == "zero"


class TestInsertLowestPriority:
    def test_invalid_parameters(self, three_items: PriorityList):
        try:
            three_items.insert_lowest_priority(None)
            pytest.fail(
                "insert_lowest_priority should have failed with\
                 MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_inserts_into_lowest_priority(self, three_items: PriorityList):
        three_items.insert_lowest_priority("four")

        assert len(three_items) == 4

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) != "four"
        assert next(gen_priority) != "four"
        assert next(gen_priority) != "four"
        assert next(gen_priority) == "four"


class TestYieldHighestPriority:
    def test_yield_in_priority_order(self, three_items: PriorityList):
        correct_order: List[str] = ["one", "two", "three"]

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) == correct_order[0]
        assert next(gen_priority) == correct_order[1]
        assert next(gen_priority) == correct_order[2]

        try:
            next(gen_priority)
            pytest.fail(
                "yield_highest_priority should have failed with\
                StopIteration due to exhausting all items in list, but did\
                    not."
            )
        except StopIteration:
            pass
