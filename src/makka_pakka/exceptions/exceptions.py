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


class MKPKInvalidParameter(Exception):
    """
    Alerts the callers when a parameter passed to MakkaPakka function is
    invalid, likely because it is of the incorrect type.
    """

    def __init__(self, name: str, func: str, value: Any):
        super().__init__(
            f"Parameter {name} passed to {func} is invalid.\nValue is {value}"
        )


class MKPKError(Exception):
    """An exception class which standardised the format of MakkaPakka error
    messgaes."""

    def __init__(self, headline: str, description: str, type: int) -> None:
        """
        Makka Pakka error constructor.

        :param headline: The headline of what went wrong.
        :param description: A more detailed explaination of how to fix what went
            wrong.
        :param type: An ErrorType indicating the severity of the problem.
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


class MKPKParsingError(MKPKError):
    """Alerts the caller of an error while parsing makka pakka code."""

    def __init__(self, headline: str, description: str, type: int) -> None:
        """
        Parsing error constructor.

        :param headline: The headline of what went wrong.
        :param description: A more detailed explaination of how to fix what went
            wrong.
        :param type: An ErrorType indicating the severity of the problem.
        """

        super().__init__(headline, description, type)


class MKPKLinkingError(MKPKError):
    """Alerts the caller of an error while linking makka pakka code."""

    def __init__(self, headline: str, description: str, type: int) -> None:
        """
        Linking error constructor.

        :param headline: The headline of what went wrong.
        :param description: A more detailed explaination of how to fix what went
            wrong.
        :param type: An ErrorType indicating the severity of the problem.
        """

        super().__init__(headline, description, type)


class MKPKProcessingError(MKPKError):
    """Alerts the caller of an error while processing makka pakka code."""

    def __init__(self, headline: str, description: str, type: int) -> None:
        """
        Processing error constructor.

        :param headline: The headline of what went wrong.
        :param description: A more detailed explaination of how to fix what went
            wrong.
        :param type: An ErrorType indicating the severity of the problem.
        """

        super().__init__(headline, description, type)


class MKPKIntegratingError(MKPKError):
    """Alerts the caller of an error while integrating makka pakka code."""

    def __init__(self, headline: str, description: str, type: int) -> None:
        """
        Integrating error constructor.

        :param headline: The headline of what went wrong.
        :param description: A more detailed explaination of how to fix what went
            wrong.
        :param type: An ErrorType indicating the severity of the problem.
        """

        super().__init__(headline, description, type)


class MKPKNameError(MKPKError):
    """Alerts the caller of an error in a name used in makka pakka code."""

    def __init__(self, headline: str, description: str, type: int) -> None:
        """
        Name error constructor.

        :param headline: The headline of what went wrong.
        :param description: A more detailed explaination of how to fix what went
            wrong.
        :param type: An ErrorType indicating the severity of the problem.
        """
        self.headline = headline
        self.description = description
        self.type = type
        super().__init__(self.headline, self.description, self.type)


class MKPKCyclicDependency(MKPKError):
    """
    Alerts the caller when a cyclic dependency is detected in a DirectedGraph.
    """

    def __init__(self, headline: str, description: str, type: int) -> None:
        """
        Cyclic dependency error constructor.

        :param headline: The headline of what went wrong.
        :param description: A more detailed explaination of how to fix what went
            wrong.
        :param type: An ErrorType indicating the severity of the problem.
        """
        self.headline = headline
        self.description = description
        self.type = type
        super().__init__(self.headline, self.description, self.type)
