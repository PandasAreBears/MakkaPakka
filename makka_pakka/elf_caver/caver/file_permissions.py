from makka_pakka.elf_caver.exceptions.exceptions import MKPKInvalidParameter


def permission_to_str(value: int) -> str:
    """
    Converts a permission integer into its string form.

    :param value: The permission integer to convert to a permission string.
    :return: The permission string e.g "RW" or "RX"
    """
    if value > 0o10 or value < 0:
        raise MKPKInvalidParameter("value", "permission_to_str", value)

    flags = ""
    flags += "R" if value & 0b100 else ""
    flags += "W" if value & 0b010 else ""
    flags += "X" if value & 0b001 else ""
    return flags


def is_executable(value: int) -> bool:
    """Returns true when a permission integer indicates it is executable"""
    if value > 0o10 or value < 0:
        raise MKPKInvalidParameter("value", "permission_to_str", value)

    return value & 0b001


def is_writable(value: int) -> bool:
    """Returns true when a permission integer indicates it is writable"""
    if value > 0o10 or value < 0:
        raise MKPKInvalidParameter("value", "permission_to_str", value)

    return value & 0b010


def is_readable(value: int) -> bool:
    if value > 0o10 or value < 0:
        raise MKPKInvalidParameter("value", "permission_to_str", value)

    return value & 0b100
