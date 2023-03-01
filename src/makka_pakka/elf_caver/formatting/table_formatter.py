from typing import Dict
from typing import List

from makka_pakka.elf_caver.exceptions.exceptions import MKPKInvalidParameter


def print_table(
    *columns: List[List[str]],
    **kwargs: Dict,
) -> None:
    """
    Pretty prints table data.

    :param headers: Optional A list of the column headers in order. Length must
        be equal to number of data columns.
    :param alignment: Optional A list indicating the desired alignment for each column.
        Left='<', Right='>', Centre='^'. Length must be equal to number of data columns.
    :param offset: Optional The no. leading/ trailing spaces applied to a data column.
        For example a right aligned entry with an offset of 1 would have 1 space before
        the end of the column.
    :param padding: Optional The no. blank spaces to add to a column on top of the
        dynamically calculated size.
    :param columns: Lists of strings for the column data should be passed in order as
        variadic arguments

    For example a table containing columns for name, age would pass
    headers=["Name", "Age"] and two list arguments: the first containing the names, and
    the second containing the ages (as strings).
    """
    # Defaults #
    HEADERS: List[str] = kwargs["headers"] if "headers" in kwargs else []
    ALIGNMENT: List[str] = (
        kwargs["alignment"] if "alignment" in kwargs else ["<"] * len(columns)
    )
    OFFSET: int = kwargs["offset"] if "offset" in kwargs else 0
    PADDING: int = kwargs["padding"] if "padding" in kwargs else 0

    # Validation #
    FUNC_NAME: str = "print_table"
    if len(columns) == 0:
        raise MKPKInvalidParameter("columns", FUNC_NAME, columns)

    # All the columns must have the same number of entries.
    if len(set([len(column) for column in columns])) != 1:
        raise MKPKInvalidParameter("columns", FUNC_NAME, columns)

    # Ensure every data entry is a string.
    try:
        if not all([isinstance(data, str) for column in columns for data in column]):
            raise MKPKInvalidParameter("columns", FUNC_NAME, columns)
    except TypeError:
        # If *columns is malformed, i.e it is not a 2D array, then the encapsulated
        # check will fail, this is also an invalid parameter case.
        raise MKPKInvalidParameter("columns", FUNC_NAME, columns)

    # Validate the HEADERS, if applicable.
    if HEADERS:
        # Ensure the number of header equals the number of columns
        if len(HEADERS) != len(columns):
            raise MKPKInvalidParameter("HEADERS", FUNC_NAME, HEADERS)

    # Validate the ALIGNMENT indicators, if applicable.
    if ALIGNMENT:
        # Ensure the number of aligment idicators equals the number of columns
        if len(ALIGNMENT) != len(columns):
            raise MKPKInvalidParameter("ALIGNMENT", FUNC_NAME, ALIGNMENT)

        # Ensure ALIGNMENT characters are valid
        VALID_ALIGNMENT_CHARS: List[str] = ["<", "^", ">"]
        if not all(char in VALID_ALIGNMENT_CHARS for char in ALIGNMENT):
            raise MKPKInvalidParameter("ALIGNMENT", FUNC_NAME, ALIGNMENT)

    # Validate OFFSET and PADDING, if applicable.
    if not isinstance(OFFSET, int):
        raise MKPKInvalidParameter("OFFSET", FUNC_NAME, OFFSET)

    if not isinstance(PADDING, int):
        raise MKPKInvalidParameter("OFFSET", FUNC_NAME, PADDING)

    # Print header #
    NO_ROWS: int = len(columns[0])
    max_column_sizes: List[int] = []
    for i, column in enumerate(columns):
        # The width is the longest element + PADDING size
        max_column_sizes.append(
            max(
                *[len(entry) for entry in column],
                len(HEADERS[i]) if HEADERS else 0,
            )
            + PADDING
        )

    for i in range(len(columns)):
        print(
            "{:^{}}".format(HEADERS[i] if HEADERS else i, max_column_sizes[i]),
            end="",
        )

        # Print a seperator, but not for the last column
        if i != len(columns) - 1:
            print("|", end="")
    print("")

    # Then print a seperator line
    for i in range(len(columns)):
        print("-" * max_column_sizes[i], end="")

        if i != len(columns) - 1:
            print("+", end="")
    print("")

    # Print Data #
    for r in range(NO_ROWS):
        for c, entry in enumerate([column[r] for column in columns]):
            print(
                " " * (OFFSET if ALIGNMENT[c] == "<" else 0)
                + "{:{}{}}".format(
                    entry,
                    ALIGNMENT[c],
                    max_column_sizes[c] - (OFFSET if ALIGNMENT[c] in ["<", ">"] else 0),
                )
                + " " * (OFFSET if ALIGNMENT[c] == ">" else 0),
                end="",
            )

            if c != len(columns) - 1:
                print("|", end="")
        print("")


def table_rows_to_columns(*rows: List[List[str]]):
    """Convienience function for converting table rows into table columns, the correct
    format for print_table"""

    # Validation #
    if len(rows) == 0:
        raise MKPKInvalidParameter("rows", "table_rows_to_columns")

    # Ensure all rows are the same length
    if len(set([len(row) for row in rows])) != 1:
        raise MKPKInvalidParameter("rows", "table_rows_to_columns")

    # Conversion #
    ROW_LEN: int = len(rows[0])

    columns: List[List[str]] = []
    for i in range(ROW_LEN):
        column: List[str] = []
        for row in rows:
            column.append(row[i])

        columns.append(column)

    return columns


if __name__ == "__main__":
    data = [
        ["Apple", "Banana", "Cherry", "Dragon Fruit"],
        ["1", "2", "3", "4"],
        ["A", "B", "C", "D"],
    ]

    rows = [
        ["Alex", "22", "179"],
        ["Bobby", "24", "185"],
        ["Charlie", "30", "176"],
        ["Danielle", "25", "172"],
    ]

    columns: List[List[str]] = table_rows_to_columns(*rows)

    print_table(
        headers=["Name", "Age", "Height"],
        alignment=["^", "<", "<"],
        padding=2,
        offset=1,
        *columns,
    )
