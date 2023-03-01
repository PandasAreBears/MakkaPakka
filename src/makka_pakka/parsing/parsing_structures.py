from __future__ import annotations

from typing import List
from typing import Union


class MKPKFunction:
    """A data strcture to encapsulate code functions used in makka pakka."""

    def __init__(self, name: str, arguments: List[str], content: List[str]):
        """
        Code structure constructor.

        :param name: A unique function name for the section of code.
        :param arugments: A list of unique names for arguements that this function
            expects.
        :param content: A list of lines of makka pakka code.
        """
        self.name = name
        self.is_main = name == "main"
        self.num_arguments = len(arguments)
        self.arguments = arguments
        self.content = content

    def add_line_to_content(self, line: str):
        """
        Adds a line to the content of the function.

        :param line: A string line to add to the content.
        """
        self.content.append(line)

    @staticmethod
    def get_function_with_name(
        functions: List[MKPKFunction], name: str
    ) -> MKPKFunction:
        """
        Gets the MKPKFunction object with the given name from a list of
        MKPKFunction objects.

        :param functions: The list of MKPKFunction objects to find the label in.
        :param label: The label to search for in the list of MKPKFunction objects.
        :return: The MKPKFunction object with the passed label, or None if the
            label was not found.
        """
        label_objs: List[MKPKFunction] = list(
            filter(lambda d: d.name == name, functions)
        )

        return label_objs[0] if label_objs else None


class MKPKDataType:
    """
    Identifies the data type of a MKPKData object.
    """

    NONE = 0
    STR = 1
    INT = 2
    REGISTER = 3


class MKPKData:
    """A data structure to encapsulate constant data used in makka pakka"""

    def __init__(self, name: str, value: Union[int, str], type: MKPKDataType):
        """
        Data structure constructor.

        :param name: A unique label assigned to the constant data.
        :param value: The constant data itself.
        :param type: The data type of the constant data.
        """
        self.name = name
        self.value = value
        self.type = type

    @staticmethod
    def get_data_with_label(data: List[MKPKData], label: str) -> MKPKData:
        """
        Gets the MKPKData object with the given label from a list of
        MKPKData objects.

        :param data: The list of MKPKData objects to find the label in.
        :param label: The label to search for in the list of MKPKData objects.
        :return: The MKPKData object with the passed label, or None if the
            label was not found.
        """
        label_objs: List[MKPKData] = list(filter(lambda d: d.name == label, data))

        return label_objs[0] if label_objs else None


class MKPKGadget:
    """A data structure to encapsulate ROP gadgets used in makka pakka."""

    def __init__(self, memory_location: str, content: List[str]) -> None:
        """
        Gadget Constructor.

        :param memory_location: The virtual memory address of the ROP gadget in the
            target binary.
        :param content: A list of assembly lines at that address, up until a ret is
            reached.
        """
        self.memory_location = memory_location
        self.content = content

    def add_line_to_content(self, line: str):
        """
        Adds a line to the content of the gadget.

        :param line: A string line to add to the content.
        """
        self.content.append(line)


class MKPKMetaData:
    """A data structure to encapsulate metadata used in makka pakka"""

    def __init__(self, label: str, value: str) -> None:
        """
        Metadata Constructor.

        :param label: The label to uniquely identify the meta data.
        :param values: The values associated with the metadata label.
        """
        self.label: str = label
        self.values: List[str] = []
        self.append_value(value)

    def append_value(self, value: str):
        """
        Appends a value to the metadata label.

        :param value: The value to append to the metadata label.
        """
        self.values.append(value)

    @staticmethod
    def get_metadata_with_label(
        metadatas: List[MKPKMetaData], label: str
    ) -> MKPKMetaData:
        """
        Gets the MKPKMetaData object with the given label from a list of
        MKPKMetaData objects.

        :param metadatas: The list of MKPKMetaData objects to find the label in.
        :param label: The label to search for in the list of MKPKMetaData objects.
        :return: The MKPKMetaData object with the passed label, or None if the
            label was not found.
        """
        label_objs: List[MKPKMetaData] = list(
            filter(lambda md: md.label == label, metadatas)
        )

        return label_objs[0] if label_objs else None


class MKPKIR:
    """An intermediate representation of the makka pakka programming language
    to be populated during the parsing phase."""

    def __init__(self):
        self.data: List[MKPKData] = []
        self.functions: List[MKPKFunction] = []
        self.gadgets: List[MKPKGadget] = []
        self.metadata: List[MKPKMetaData] = []

    def add_data(self, data: MKPKData):
        self.data.append(data)

    def add_function(self, function: MKPKFunction):
        self.functions.append(function)

    def add_gadget(self, gadget: MKPKGadget):
        self.gadgets.append(gadget)

    def __eq__(self, other: MKPKIR):
        return (
            self.data == other.data
            and self.functions == other.functions
            and self.gadgets == other.gadgets
            and self.metadata == other.metadata
        )


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
