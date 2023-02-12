from typing import List
from typing import Union


class MKPKFunction:
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
        self.is_main = name == "main"
        self.num_arguments = len(arguments)
        self.arguments = arguments
        self.content = content

    def add_line_to_content(self, line: str):
        """
        Adds a line to the content of the function.
        :line: A string line to add to the content.
        """
        self.content.append(line)


class MKPKDataType:
    NONE = 0
    STR = 1
    INT = 2


class MKPKData:
    """A data structure to encapsulate constant data used in makka pakka"""

    def __init__(self, name: str, value: Union[int, str], type: MKPKDataType):
        """
        Data structure constructor.
        :name: A unique label assigned to the constant data.
        :value: The constant data itself.
        :type: The data type of the constant data.
        """
        self.name = name
        self.value = value
        self.type = type


class MKPKGadget:
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

    def add_line_to_content(self, line: str):
        """
        Adds a line to the content of the gadget.
        :line: A string line to add to the content.
        """
        self.content.append(line)


class MKPKMetaData:
    """A data structure to encapsulate metadata used in makka pakka"""

    def __init__(self, label: str, value: str) -> None:
        """
        Metadata Constructor.
        :label: The label to uniquely identify the meta data.
        :values: The values associated with the metadata label.
        """
        self.label: str = label
        self.values: List[str] = []
        self.append_value(value)

    def append_value(self, value: str):
        """
        Appends a value to the metadata label.
        :value: The value to append to the metadata label.
        """
        self.values.append(value)


class MKPKIR:
    """An intermediate representation of the makka pakka programming language
    to be populated during the parsing phase."""

    def __init__(self):
        self.data = List[MKPKData]
        self.functions = List[MKPKFunction]
        self.gadgets = List[MKPKGadget]

    def add_data(self, data: MKPKData):
        self.data.append(data)

    def add_function(self, function: MKPKFunction):
        self.functions.append(function)

    def add_gadget(self, gadget: MKPKGadget):
        self.gadgets.append(gadget)


class MKPKLines:
    """A data structure to hold the raw text lines from a .mkpk in their
    respective heading sections."""

    def __init__(
        self,
        data: List[str] = [],
        code: List[str] = [],
        gadgets: List[str] = [],
        metadata: List[str] = [],
    ):
        self.data: List[str] = data
        self.code: List[str] = code
        self.gadgets: List[str] = gadgets
        self.metadata: List[str] = metadata

    def add_data(self, line: str):
        """Adds a line to the data heading"""
        self.data.append(line)

    def add_code(self, line: str):
        """Adds a line to the code heading"""
        self.code.append(line)

    def add_gadget(self, line: str):
        """Add a line to the gadget heading"""
        self.gadgets.append(line)

    def add_metadata(self, line: str):
        """Add a line to the metadata heading"""
        self.metadata.append(line)

    def __eq__(self, other: object) -> bool:
        return (
            self.data == other.data
            and self.code == other.code
            and self.gadgets == other.gadgets
            and self.metadata == other.metadata
        )
