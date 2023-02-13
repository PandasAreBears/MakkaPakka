from typing import List

import pytest

from makka_pakka.exceptions.exceptions import InvalidParameter
from makka_pakka.linking.priority_list.priority_list import PriorityList


@pytest.fixture
def three_items() -> PriorityList:
    return PriorityList(["one", "two", "three"])


class TestPriorityListInit:
    def test_invalid_parameters(self):
        try:
            PriorityList(None)
            pytest.fail(
                "__init__ should have failed with InvalidParameter\
                but did not."
            )
        except InvalidParameter:
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


class TestInsertHighestPriority:
    def test_invalid_parameters(self, three_items: PriorityList):
        try:
            three_items.insert_highest_priority(None)
            pytest.fail(
                "insert_highest_priority should have failed with\
                 InvalidParameter but did not."
            )
        except InvalidParameter:
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
                 InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

    def test_inserts_into_lowest_priority(self, three_items: PriorityList):
        three_items.insert_lowest_priority("four")

        assert len(three_items) == 4

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) != "four"
        assert next(gen_priority) != "four"
        assert next(gen_priority) != "four"
        assert next(gen_priority) == "four"


class TestInsertAboveItem:
    def test_invalid_parameters(self, three_items: PriorityList):
        mock_new_item = "hello"
        mock_existing_item = "one"
        try:
            three_items.insert_above_item(None, None)
            pytest.fail(
                "insert_above_item should have failed with\
                 InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

        try:
            three_items.insert_above_item(mock_new_item, None)
            pytest.fail(
                "insert_above_item should have failed with\
                 InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

        try:
            three_items.insert_above_item(None, mock_existing_item)
            pytest.fail(
                "insert_above_item should have failed with\
                 InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

    def test_inserts_item_above_existing(self, three_items: PriorityList):
        assert three_items.insert_above_item("1.5", "two")

        assert len(three_items) == 4

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) != "1.5"
        assert next(gen_priority) == "1.5"
        assert next(gen_priority) != "1.5"
        assert next(gen_priority) != "1.5"

    def test_does_not_insert_above_invalid_item(self, three_items: PriorityList):
        assert not three_items.insert_above_item("3.5", "four")

        assert len(three_items) == 3

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) != "3.5"
        assert next(gen_priority) != "3.5"
        assert next(gen_priority) != "3.5"


class TestInsertBelowItem:
    def test_invalid_parameters(self, three_items: PriorityList):
        mock_new_item = "hello"
        mock_existing_item = "one"
        try:
            three_items.insert_below_item(None, None)
            pytest.fail(
                "insert_below_item should have failed with\
                 InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

        try:
            three_items.insert_below_item(mock_new_item, None)
            pytest.fail(
                "insert_below_item hould have failed with\
                 InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

        try:
            three_items.insert_below_item(None, mock_existing_item)
            pytest.fail(
                "insert_below_item hould have failed with\
                 InvalidParameter but did not."
            )
        except InvalidParameter:
            pass

    def test_inserts_item_below_existing(self, three_items: PriorityList):
        assert three_items.insert_below_item("2.5", "two")

        assert len(three_items) == 4

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) != "2.5"
        assert next(gen_priority) != "2.5"
        assert next(gen_priority) == "2.5"
        assert next(gen_priority) != "2.5"

    def test_does_not_insert_below_invalid_item(self, three_items: PriorityList):
        assert not three_items.insert_below_item("4.5", "four")

        assert len(three_items) == 3

        gen_priority = three_items.yield_highest_priority()
        assert next(gen_priority) != "4.5"
        assert next(gen_priority) != "4.5"
        assert next(gen_priority) != "4.5"


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
