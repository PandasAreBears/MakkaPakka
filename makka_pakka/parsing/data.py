from typing import Union


class DataTypes:
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
