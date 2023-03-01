from typing import Any
from typing import List

from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKGadget


class MKPKArgumentSet:
    def __init__(self, *args) -> None:
        """
        MKPKArgumentSet constructor. Passed arguments are interpreted as the
        arguments for a MKPKFunction.

        :param args: A variable number of arguments passed to a MKPKFunction.
        """
        self.arguments = args

    def __getitem__(self, key: int) -> Any:
        return self.arguments[key]

    def __len__(self) -> int:
        return len(self.arguments)

    def __iter__(self):
        yield from self.arguments


class MKPKFunctionCall:
    def __init__(self, name: str, args: List[str]):
        """
        MKPKFunctionCall constructor.

        :param name: The name of the function that is being called.
        :param args: A list of arguments to be passed to the function. These are
            string stripped from the program text, and have not yet had their
            type interpretted.
        """
        self.name = name
        self.args = args


class MKPKCode:
    """Encapsulates the result of the processing phase."""

    def __init__(
        self, data: List[MKPKData], code: List[str], gadgets: MKPKGadget
    ) -> None:
        """
        MKPKCode constructor

        :param data: The data used in a makka pakka program.
        :param code: The processed code of a makka pakka program.
        :param gadgets: The gadgets to be inserted in the integrating phase.
        """
        self.data = data
        self.code = code
        self.gadgets = gadgets
