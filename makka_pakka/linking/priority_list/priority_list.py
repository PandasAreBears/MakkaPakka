from typing import Generator
from typing import List

from makka_pakka.exceptions.exceptions import InvalidParameter


class PriorityList:
    """
    A class to prioritise string items in a list, intended for archiving
    directories that the makka pakka linker search for linked files.
    """

    def __init__(self, default_items: List[str] = []) -> None:
        """
        Priority list constructor.
        :default_items: The default items to put in the priority list. Lower
            indexes are a higher priority.
        """
        if not isinstance(default_items, list) or not all(
            [isinstance(i, str) for i in default_items]
        ):
            raise InvalidParameter("default_items", "__init__", default_items)

        self.items = default_items

    def insert_highest_priority(self, item: str) -> None:
        """
        Inserts an item into the priority list with the highest priority.
        :item: The item to give the highest priority in the priority list.
        """
        if not isinstance(item, str):
            raise InvalidParameter("item", "insert_highest_priority", item)

        self.items = [item] + self.items

    def insert_lowest_priority(self, item: str) -> None:
        """
        Inserts an item into the priority list with the lowest priority.
        :item: The item to give the lowest priority in the priority list.
        """
        if not isinstance(item, str):
            raise InvalidParameter("item", "insert_lowest_priority", item)

        self.items += [item]

    def insert_above_item(self, new_item: str, existing_item: str) -> bool:
        """
        Inserts an item above an item that already exists in the priority list.
        :new_item: The new item to place above another item in the list.
        :existing_item: The item to use an anchor to place the new item above.
        :returns: False if the existing item is not already in the priority
            list, in this case the new item will not be added.
        """
        if not isinstance(new_item, str):
            raise InvalidParameter("new_item", "insert_above_item", new_item)

        if not isinstance(existing_item, str):
            raise InvalidParameter("existing_item", "insert_above_item", existing_item)

        existing_item_index: int = -1
        try:
            # .index raises ValueError when item not in list
            existing_item_index = self.items.index(existing_item)
        except ValueError:
            return False

        self.items.insert(existing_item_index, new_item)
        return True

    def insert_below_item(self, new_item: str, existing_item: str) -> bool:
        """
        Inserts an item below an item that already exists in the priority list.
        :new_item: The new item to place below another item in the list.
        :existing_item: The item to use an anchor to place the new item below.
        :returns: False if the existing item is not already in the priority
            list, in this case the new item will not be added.
        """
        if not isinstance(new_item, str):
            raise InvalidParameter("new_item", "insert_below_item", new_item)

        if not isinstance(existing_item, str):
            raise InvalidParameter("existing_item", "insert_below_item", existing_item)

        existing_item_index: int = -1
        try:
            # .index raises ValueError when item not in list
            existing_item_index = self.items.index(existing_item)
        except ValueError:
            return False

        self.items.insert(existing_item_index + 1, new_item)
        return True

    def yield_highest_priority(self) -> Generator[str, None, None]:
        """
        Generates the items in priority order, starting with the highest
        priority.
        :returns: A generator of the items in highest priority order.
        """
        for item in self.items:
            yield item

    def __len__(self) -> int:
        return len(self.items)
