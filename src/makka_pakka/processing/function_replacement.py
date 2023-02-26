from typing import List

from makka_pakka.directed_graph.directed_graph import DirectedGraph
from makka_pakka.directed_graph.directed_graph import Node
from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKParsingError
from makka_pakka.exceptions.exceptions import MKPKProcessingError
from makka_pakka.parsing.detect_headings import _assert_valid_mkpk_name
from makka_pakka.parsing.parse_headings import _interpret_data_type
from makka_pakka.parsing.parsing_structures import MKPKData
from makka_pakka.parsing.parsing_structures import MKPKDataType
from makka_pakka.parsing.parsing_structures import MKPKFunction
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.processing.data_replacement import _extract_data_references
from makka_pakka.processing.data_replacement import (
    _extract_label_from_reference,
)
from makka_pakka.processing.data_replacement import (
    _replace_reference_with_value,
)
from makka_pakka.processing.processing_structures import MKPKArgumentSet
from makka_pakka.processing.processing_structures import MKPKFunctionCall


def process_function_replacement(mkpkir: MKPKIR) -> List[str]:
    """
    Replaces any function references with the code resolved at the reference.
    For example:
    [[code]]
    [main]
    mov rax, 1
    func_1 2

    [func_1] arg1
    mov ecx, ${arg1}

    Will become:
    [[code]]
    [main]
    mov rax, 1
    mov ecx, 2

    :param mkpkir: The MKPKIR object to replace function references in.
    :return: A list of processed code lines, ready to be executed.
    """
    if not isinstance(mkpkir, MKPKIR):
        raise MKPKInvalidParameter("mkpkir", "process_function_replacement", mkpkir)

    """
    Function replacement is implemented as a recursive macro replacement.
    Each line in the main function is checked sequentially for references to
    other functions. To avoid cyclic dependencies, a DirectedGraph monitors
    the function calls.

    If the line contains a data reference that is still unresolved:
        - Check the current MKPKArgumentSet, and try to replace the value.
        - If the label doesn't exist then raise a MKPKProcessingError

    When a function call is encountered:
        - The function call is add to the DirectedGraph and a check is made for
            a cyclic loop.
        - Arguments passed to the function call are pushed on a stack as a
            MKPKArgumentSet
        - The function resolver is recursively called to resolve the
            encoutered function, inserting its result in-place.
    """
    # The main function takes no arguments, so initialise with an empty
    # MKPKArgumentSet.
    argument_stack: List[MKPKArgumentSet] = [MKPKArgumentSet()]

    # The directed graph is for checking for cyclic dependencies, 'root' is not
    # a function call, but a placeholder for the start for the call stack.
    func_call_graph: DirectedGraph = DirectedGraph("root")

    # The top-level collection of code lines. Code lines are added as functions
    # and data references are resolved.
    code: List[str] = []

    def process_code(parent: Node, current_func: MKPKFunction):
        nonlocal argument_stack, func_call_graph, code

        _assert_correct_num_of_args(current_func, argument_stack[-1])

        for code_line in current_func.content:
            refs: List[str] = _extract_data_references(code_line)

            # If there's a data reference, then check if the label is in the
            # function arguments. Get the argument value from the arugments
            # stack.
            if refs:
                for ref in refs:
                    # Get the value to replace the reference with.
                    replace_value: str = _get_ref_value_from_arguments(
                        ref, current_func, argument_stack[-1], mkpkir.data
                    )
                    code_line = _replace_reference_with_value(
                        code_line, ref, replace_value
                    )

            # If the line is a function call.
            if func_call := _get_line_as_function_call(code_line):
                # Check that the function call is being made to a resolved
                # function.
                next_func: MKPKFunction = _get_function_by_name_or_assert(
                    mkpkir.functions, func_call.name
                )

                # Push the arguments onto the argument stack.
                argument_stack += [MKPKArgumentSet(*func_call.args)]

                # Create a new node in the DirectedGraph and check for cyclic
                # function calls
                func_call_graph.create_and_assert_no_cycle(parent, func_call.name)

                # Recursively call this function
                process_code(
                    func_call_graph.get_node_with_label(func_call.name),
                    next_func,
                )

            else:
                # Add the code line to the top-level code.
                code += [code_line]

        # Move out of function call, so unwind stack by one.
        argument_stack.pop()

    # Store the current function
    first_function: MKPKFunction = _get_function_by_name_or_assert(
        mkpkir.functions, "main"
    )

    process_code(func_call_graph.root, first_function)

    return code


def _get_line_as_function_call(code_line: str) -> MKPKFunctionCall | None:
    """
    Attempts to interpret a code line as a function call.

    :param code_line: The code line to interpret as a function call.
    :return: Retruns an MKPKFunctionCall object if the line is a function
        call, or None if it is not.
    """
    if not isinstance(code_line, str):
        raise MKPKInvalidParameter("code_line", "_get_line_as_function_call", code_line)

    try:
        return _parse_line_as_function_call(code_line)
    except MKPKProcessingError:
        return None


def _parse_line_as_function_call(code_line: str) -> MKPKFunctionCall:
    """
    Parses a code line as a MKPKFunctionCall.

    :param code_line: The code line to interpret as a function call.
    :return: The parsed MKPKFunctionCall object.
    :raises:
        *MKPKProcessingError* - When the line is not a function call.
        *MKPKNameError* - When a name in the function call is invalid.
    """
    if not isinstance(code_line, str):
        raise MKPKInvalidParameter(
            "code_line", "_parse_line_as_function_call", code_line
        )

    # Function call are always prefixed by a '>'
    if not code_line[0] == ">":
        raise MKPKProcessingError(
            "Invalid function all syntax.",
            "Tried to interpret a code line as a function, but couldn't\
            because the line doesn't start with a '>'.",
            ErrorType.FATAL,
        )

    parts = code_line[1:].split(" ")
    # Filter out all empty strings
    parts = list(filter(lambda i: i != "", parts))

    if len(parts) < 1:
        raise MKPKProcessingError(
            "Invalid function call syntax.",
            "Tried to interpret a code line as a function, but couldn't\
            because the line doesn't contain a function name.",
            ErrorType.FATAL,
        )

    # The first part should be the name of the function that is being called.
    _assert_valid_mkpk_name(parts[0], code_line)

    # The args are not interpreted yet, so dont need to be validated
    return MKPKFunctionCall(parts[0], parts[1:])


def _assert_correct_num_of_args(curr_func: MKPKFunction, passed_args: MKPKArgumentSet):
    """
    Asserts that the number arguments passed to a MKPKFunction is equal to the
    number of expected arguments.
    """
    if not isinstance(curr_func, MKPKFunction):
        raise MKPKInvalidParameter(
            "curr_func", "_assert_correct_num_of_args", curr_func
        )
    if not isinstance(passed_args, MKPKArgumentSet):
        raise MKPKInvalidParameter(
            "passed_args", "_assert_correct_num_of_args", passed_args
        )

    if curr_func.num_arguments != len(passed_args):
        raise MKPKProcessingError(
            "Incorrect number of arguments.",
            f"{len(passed_args)} were passed to {curr_func.name}, but\
                {curr_func.num_arguments} were expected.",
            ErrorType.FATAL,
        )


def _get_ref_value_from_arguments(
    data_reference: str,
    func: MKPKFunction,
    args: MKPKArgumentSet,
    data: List[MKPKData],
) -> MKPKData:
    """
    Resolves the value of a data reference using the function's arguments.

    :param data_reference: The data reference to resolve.
    :param func: The function that the data reference was found in.
    :param args: The arguments passed to the function.
    :param data: The data labels defined in the program. These are used to make a
        reference to existing data in a function call.
    :return: The MKPKData that the data reference should be replaced with.
    :raises:
        *MKPKProcessingError* - When the data reference couldn't be resolved.
    """
    if not isinstance(data_reference, str):
        raise MKPKInvalidParameter(
            "data_reference", "_get_ref_value_from_arguments", data_reference
        )
    if not isinstance(func, MKPKFunction):
        raise MKPKInvalidParameter("func", "_get_ref_value_from_arguments", func)
    if not isinstance(args, MKPKArgumentSet):
        raise MKPKInvalidParameter("args", "_get_ref_value_from_arguments", args)
    if not isinstance(data, list) or not all([isinstance(d, MKPKData) for d in data]):
        raise MKPKInvalidParameter("data", "_get_ref_value_from_arguments", data)

    # All data references have been resolved by this point,
    # so this can only be an argument reference. If it isn't,
    # then it cannot be resolved.
    label = _extract_label_from_reference(data_reference)
    arg_index: int = None
    try:
        arg_index = func.arguments.index(label)
    except ValueError:
        raise MKPKProcessingError(
            "Unable to resolve data reference.",
            f"The data reference ${label} couldn't be resolved\
            from the data labels or function arguments.",
            ErrorType.FATAL,
        )

    # Try to interpret the argument value. Passing empty line parameter as it
    # is only used for the error, which is re-raised.
    parsed_value, data_type = None, None
    try:
        parsed_value, data_type = _interpret_data_type(args[arg_index], "")
    except MKPKParsingError:
        raise MKPKProcessingError(
            "Unable to interpret argument value.",
            f"The argument value {args[arg_index]} couldn't be interpretted\
            as a MKPKDataType",
            ErrorType.FATAL,
        )

    """
    Strings passed as function arguments are interpreted as as label that has
    already been defined in the program, they are therefore replaced by a
    relative call to the label. Integers can be directly replaced.
    """
    resolved_data: MKPKData = None
    match data_type:
        case MKPKDataType.STR:
            # Check that there is a label with this name.
            refd_data: MKPKData = MKPKData.get_data_with_label(data, parsed_value)
            if refd_data is None:
                raise MKPKProcessingError(
                    "Couldn't resolve reference to data made in function \
                        argument",
                    f"Couldn't resolve the reference ${parsed_value} passed as\
                    a parameter to function {func.name}",
                    ErrorType.FATAL,
                )

            # If the data at the label is a string type, then replace with a
            # relative reference, else replace with the value directly.
            match refd_data.type:
                case MKPKDataType.STR:
                    resolved_data = MKPKData(parsed_value, "", data_type)
                case MKPKDataType.INT:
                    resolved_data = refd_data

        case MKPKDataType.INT:
            # Empty name, as this is an int so will be directly replaced
            resolved_data = MKPKData("", parsed_value, data_type)

        case MKPKDataType.REGISTER:
            # Replace the reference with the name of the register.
            resolved_data = MKPKData(parsed_value, "", data_type)

    return resolved_data


def _get_function_by_name_or_assert(
    functions: List[MKPKFunction], name: str
) -> MKPKFunction:
    """
    Gets a function by name or asserts a ProcessingError if the function is not
      found.

    :param functions: A list of MKPKFunction objects to search for the name in.
    :param name: The function name to search for.
    :return: The MKPKFunction object with the specified name.
    :raises:
        *ProcessingError* - When the function name is not found.
    """
    if not isinstance(functions, list) or not all(
        [isinstance(f, MKPKFunction) for f in functions]
    ):
        raise MKPKInvalidParameter(
            "functions", "_get_function_by_name_or_assert", functions
        )

    if not isinstance(name, str):
        raise MKPKInvalidParameter("name", "_get_function_by_name_or_assert", name)

    func = MKPKFunction.get_function_with_name(functions, name)
    if not func:
        raise MKPKProcessingError(
            "Unable to resolve function name.",
            f"The function name {name} was expected while processing but\
                  couldn't be found",
            ErrorType.FATAL,
        )

    return func
