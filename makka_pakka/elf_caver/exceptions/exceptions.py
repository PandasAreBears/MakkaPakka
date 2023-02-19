from typing import Any


class MKPKInvalidParameter(Exception):
    def __init__(self, name: str, func: str, value: Any):
        super().__init__(
            f"Parameter {name} passed to {func} is invalid.\nValue is {value}"
        )


class ByteExtractionFailed(Exception):
    pass


class InsufficientCodeCaves(Exception):
    pass
