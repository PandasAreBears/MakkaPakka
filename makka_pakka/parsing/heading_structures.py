from typing import List
from typing import Union


class Code:
    """A data strcture to encapsulate code functions used in makka pakka."""

    def __init__(self, name: str, arguments: List[str], content: List[str]):
        """
        Code structure constructor.
        :name: A unique function name for the section of code.
        :arugments: A list of unique names for arguements that this function
            expects.
        :content: A list of lines of makka pakka code.
        """
        self.name = name
        self.is_name = name == "main"
        self.num_arguments = len(arguments)
        self.arguments: arguments
        self.content = content


class DataType:
    TYPE_STR = 0
    TYPE_INT = 1


class Data:
    """A data structure to encapsulate constant data used in makka pakka"""

    def __init__(self, name: str, value: Union[int, str], type: int):
        """
        Data structure constructor.
        :name: A unique label assigned to the constant data.
        :value: The constant data itself.
        :type: The data type of the constant data.
        """
        self.name = name
        self.value = value
        self.type = type


class Gadget:
    """A data structure to encapsulate ROP gadgets used in makka pakka."""

    def __init__(self, memory_location: str, content: List[str]) -> None:
        """
        Gadget Constructor.
        :memory_location: The virtual memory address of the ROP gadget in the
            target binary.
        :content: A list of assembly lines at that address, up until a ret is
            reached.
        """
        self.memory_location = memory_location
        self.content = content
