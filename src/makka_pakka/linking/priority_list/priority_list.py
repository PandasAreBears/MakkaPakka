from typing import Generator
from typing import List

from makka_pakka.exceptions.exceptions import MKPKInvalidParameter


class PriorityType:
    NONE = 0
    HIGH = 1
    LOW = 2


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
            raise MKPKInvalidParameter("default_items", "__init__", default_items)

        self.items = default_items

    def insert_with_priority(self, item: str, priority: PriorityType) -> None:
        """
        Inserts an item into the priority list with the specified priority.
        :item: The item to insert into the priority list.
        :priority: A PriorityType specifying the priority to insert to item
            with.
        """
        if not isinstance(item, str):
            raise MKPKInvalidParameter("item", "insert_with_priority", item)

        # PriorityType is an underlying int
        if not isinstance(priority, int):
            raise MKPKInvalidParameter("priority", "insert_with_priority", priority)

        match priority:
            case PriorityType.HIGH:
                self.insert_highest_priority(item)
            case PriorityType.LOW:
                self.insert_lowest_priority(item)

    def insert_highest_priority(self, item: str) -> None:
        """
        Inserts an item into the priority list with the highest priority.
        :item: The item to give the highest priority in the priority list.
        """
        if not isinstance(item, str):
            raise MKPKInvalidParameter("item", "insert_highest_priority", item)

        self.items = [item] + self.items

    def insert_lowest_priority(self, item: str) -> None:
        """
        Inserts an item into the priority list with the lowest priority.
        :item: The item to give the lowest priority in the priority list.
        """
        if not isinstance(item, str):
            raise MKPKInvalidParameter("item", "insert_lowest_priority", item)

        self.items += [item]

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
