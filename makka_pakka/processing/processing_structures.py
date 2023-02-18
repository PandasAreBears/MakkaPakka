from typing import Any
from typing import List


class MKPKArgumentSet:
    def __init__(self, *args) -> None:
        """
        MKPKArgumentSet constructor. Passed arguments are interpreted as the
        arguments for a MKPKFunction.
        :args: A variable number of arguments passed to a MKPKFunction.
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
        :name: The name of the function that is being called.
        :args: A list of arguments to be passed to the function. These are
            string stripped from the program text, and have not yet had their
            type interpretted.
        """
        self.name = name
        self.args = args
