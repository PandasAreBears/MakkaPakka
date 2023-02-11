from typing import Any

from termcolor import colored


class ErrorType:
    # An error to indicate that something went wrong, but it may not affect the
    # further execution of the program.
    WARNING = 0
    # An error to indicate that something went wrong, and the program is
    # unlikely to be able to continue execution.
    ERROR = 1
    # An error to indicate a critical problem, the program will stop
    # immediately.
    FATAL = 2


class InvalidParameter(Exception):
    def __init__(self, name: str, func: str, value: Any):
        super().__init__(
            f"Parameter {name} passed to {func} is invalid.\nValue is {value}"
        )


class ParsingError(Exception):
    """Alerts the caller of an error while parsing makka pakka code."""

    def __init__(self, headline: str, description: str, type: int) -> None:
        """
        Parsing error constructor.
        :headline: The headline of what went wrong.
        :description: A more detailed explaination of how to fix what went
            wrong.
        :type: An ErrorType indicating the severity of the problem.
        """

        self.type = type

        def format_message(hline: str, desc: str, type: int) -> str:
            """Formats the error message."""
            message: str = ""

            match type:
                case ErrorType.WARNING:
                    message += colored("Warning\n", "yellow")
                case ErrorType.ERROR:
                    message += colored("Error\n", "red")
                case ErrorType.FATAL:
                    message += colored("Fatal\n", "red", attrs=["bold"])

            message += hline + "\n"
            message += "> " + desc + "\n"

            return message

        match type:
            case ErrorType.FATAL | ErrorType.ERROR:
                super().__init__(format_message(headline, description, type))
            case ErrorType.WARNING:
                print(format_message(headline, description, type))
