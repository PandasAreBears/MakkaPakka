from typing import List


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
