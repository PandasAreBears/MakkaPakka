from pathlib import Path
from typing import List

from makka_pakka import settings
from makka_pakka.directed_graph.directed_graph import DirectedGraph
from makka_pakka.directed_graph.node import Node
from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter
from makka_pakka.exceptions.exceptions import MKPKLinkingError
from makka_pakka.linking.linker_path import LinkerPath
from makka_pakka.linking.priority_list.priority_list import PriorityType
from makka_pakka.parsing.parse import parse_makka_pakka
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.parsing.parsing_structures import MKPKMetaData


def parse_link_and_merge(mkpk_filepath: str) -> MKPKIR:
    """
    Parses, links, and merges a main makka pakkka source file.

    :param mkpk_filepath: The filepath the main .mkpk source file to be parsed,
        linked, and merged.
    :return: A linked, and merged MKPKIR object.
    """
    if not isinstance(mkpk_filepath, str):
        raise MKPKInvalidParameter(
            "mkpk_filepath", "parse_link_and_merge", mkpk_filepath
        )

    unlinked_files: List[MKPKIR] = parse_with_linking(mkpk_filepath)

    return merge_MKPKIRs(unlinked_files)


def parse_with_linking(mkpk_filepath: str) -> List[MKPKIR]:
    """
    Parses a makka pakka source file, recursively linking with files found in
    the !link metadata directive.

    :param mkpk_filepath: The makka pakka source file to parse using recursive
        linking.
    :return: A list of MKPKIR objects which represent .mkpk files that have
        been parsed as dependencies of the main source file. The main source
        file will at index 0.
    :remark: Each IR object in the returned list is assigned a metadata
        attribute 'link_depth' which specifies the number of linked files
        between it and the main source file. A direct link from the source
        file will have value 1.
    """
    if not isinstance(mkpk_filepath, str):
        raise MKPKInvalidParameter("mkpk_filepath", "parse_with_linking", mkpk_filepath)

    linker_path: LinkerPath = LinkerPath(mkpk_filepath)

    # Initialise the linking graph for dependency loop checking. Root doesn't
    # represent a file, just a placeholder for the start of the graph.
    linking_graph: DirectedGraph = DirectedGraph("root")
    file_IRs: List[MKPKIR] = []
    link_depth: int = 0

    def parse_file(parent: Node, filename: str):
        nonlocal linker_path, linking_graph, file_IRs, link_depth

        full_file_path: str = str(Path(linker_path.find_mkpk_file(filename)).resolve())

        if not full_file_path or str(full_file_path) == str(Path("").resolve()):
            raise MKPKLinkingError(
                f"Couldn't find file with name {filename}",
                f"Couldn't link with file. Searched in directories\
                 {linker_path.linker_paths.items}",
                ErrorType.FATAL,
            )

        if settings.verbosity:
            print(f"Parsing mkpk file: {filename}")

        # Add to the graph, and check that this doesn't create a cyclic
        # dependency.
        created_new: bool = (
            linking_graph.connect_to_node_with_label_create_if_not_exists(
                parent, full_file_path
            )
        )
        if backtrace := linking_graph.has_cyclic_dependency():
            raise MKPKLinkingError(
                "Linking encountered a cyclic linking\
                dependency",
                f"The following cyclic dependency was found while linking\
                    makka pakka code\n:\
                         {DirectedGraph.get_cyclic_dependency_str(backtrace)}",
                ErrorType.FATAL,
            )

        # If the file already exists in the graph, then break as all symbols
        # from this file (and its dependencies) will have already been parsed.
        if not created_new:
            return

        # Parse the file, add it to the list of IR's, then recurse on all
        # linking dependencies.
        file_IR = parse_makka_pakka(full_file_path)

        # Add the 'link_depth' metadata attribute to the object.
        file_IR.metadata.append(MKPKMetaData("link_depth", str(link_depth)))

        file_IRs.append(file_IR)

        # There should be either 0 or 1 metadata objects with the label 'link'.
        link_md: MKPKMetaData = MKPKMetaData.get_metadata_with_label(
            file_IR.metadata, "link"
        )
        new_node = linking_graph.get_node_with_label(full_file_path)

        # Add the parsed file's parent directory to the linker path. This allows
        # all mkpk files to link with files relative to their own path.
        linker_path.add_path_to_linker(
            str(Path(full_file_path).parent.resolve()), PriorityType.LOW
        )

        if link_md:
            link_depth += 1
            for link_filename in link_md.values:
                parse_file(new_node, link_filename)

    parse_file(linking_graph.root, Path(mkpk_filepath).name)
    link_depth -= 1

    return file_IRs


def merge_MKPKIRs(mkpkirs: List[MKPKIR]) -> MKPKIR:
    """
    Merges a list of MKPKIR objects into a single MKPKIR. The returned object
    is then ready to be processed. This function is intended to be called
    using the result of parse_with_linking.
    This function is responsible for several validation checks:
    - Function names do not conflict
    - Data labels do not conflit
    - ROPGadget memory addresses do not conflict

    :param mkpkirs: The list of MKPKIR objects to be merged into one.
    :return: A MKPKIR object with all passed objects merged into it.
    """
    if not isinstance(mkpkirs, list) or not all(
        [isinstance(ir, MKPKIR) for ir in mkpkirs]
    ):
        raise MKPKInvalidParameter("mkpkirs", "merge_MKPKIRs", mkpkirs)

    """
    The merging process starts with the main source IR and individually
    copies the function names, data labels, and gadget memory
    locations into the combined IR object. Any conflicts in the name, labels,
    or memory locations will cause an error, detailing this conflict.
    """
    # Copy the main MKPKIR then delete it from the list before iteration.
    merged_IR: MKPKIR = mkpkirs[0]
    del mkpkirs[0]

    # Sort the IR by link depth, this will means the error message can contain
    # the filename of the deeper function (metadata of everything other than
    # main is lost in the merge).
    mkpkirs = sorted(
        mkpkirs,
        key=lambda ir: int(
            MKPKMetaData.get_metadata_with_label(ir.metadata, "link_depth").values[0]
        ),
    )

    # Merge each IR object into the main object, ensuring that there are no
    # conflicts in the function names, data labels, and gadget addreses.
    for ir in mkpkirs:
        _assert_no_conflict_in_functions(merged_IR, ir)
        _assert_no_conflict_in_data_labels(merged_IR, ir)
        _assert_no_conflict_in_gadget_addresses(merged_IR, ir)

        _combine_MKPKIRs(merged_IR, ir)

    return merged_IR


def _combine_MKPKIRs(lhs: MKPKIR, rhs: MKPKIR) -> MKPKIR:
    """
    Combines to MKPKIR objects into one.
    :param lhs: The first object to combine. The metadata of this object is kept.
    :param rhs: The second object to combine. The metadata of this object is lost.
    :return: The combined MKPKIR object.
    """
    if not isinstance(lhs, MKPKIR):
        raise MKPKInvalidParameter("lhs", "_combine_MKPKIRs", lhs)

    if not isinstance(rhs, MKPKIR):
        raise MKPKInvalidParameter("rhs", "_combine_MKPKIRs", rhs)

    for r_func in rhs.functions:
        lhs.functions.append(r_func)

    for r_data in rhs.data:
        lhs.data.append(r_data)

    for r_gadget in rhs.gadgets:
        lhs.gadgets.append(r_gadget)

    return lhs


def _assert_no_conflict_in_functions(lhs: MKPKIR, rhs: MKPKIR):
    """
    Asserts if there are conflicts in the function names' of MKPKIR objects.
    """
    if not isinstance(lhs, MKPKIR):
        raise MKPKInvalidParameter("lhs", "_assert_no_conflict_in_functions", lhs)

    if not isinstance(rhs, MKPKIR):
        raise MKPKInvalidParameter("rhs", "_assert_no_conflict_in_functions", rhs)

    for l_func in lhs.functions:
        for r_func in rhs.functions:
            if l_func.name == r_func.name:
                rhs_filename = MKPKMetaData.get_metadata_with_label(
                    rhs.metadata, "filename"
                ).values[0]
                raise MKPKLinkingError(
                    "Conflict in function name.",
                    f"The function name {l_func.name} appears in more than one\
                    file. The conflict occured while trying to link with\
                    {rhs_filename}.",
                    ErrorType.FATAL,
                )


def _assert_no_conflict_in_data_labels(lhs: MKPKIR, rhs: MKPKIR):
    """
    Asserts if there are conflicts in the data labels of MKPKIR objects.
    """
    if not isinstance(lhs, MKPKIR):
        raise MKPKInvalidParameter("lhs", "_assert_no_conflict_in_data_labels", lhs)

    if not isinstance(rhs, MKPKIR):
        raise MKPKInvalidParameter("rhs", "_assert_no_conflict_in_data_labels", rhs)

    for l_data in lhs.data:
        for r_data in rhs.data:
            if l_data.name == r_data.name:
                rhs_filename = MKPKMetaData.get_metadata_with_label(
                    rhs.metadata, "filename"
                ).values[0]
                raise MKPKLinkingError(
                    "Conflict in data label name.",
                    f"The data label {l_data.name} appears in more than one\
                    file. The conflict occured while trying to link with\
                    {rhs_filename}.",
                    ErrorType.FATAL,
                )


def _assert_no_conflict_in_gadget_addresses(lhs: MKPKIR, rhs: MKPKIR):
    """
    Asserts if there are conflicts in the ROP gadget memory locations of
    MKPKIR objects.
    """
    if not isinstance(lhs, MKPKIR):
        raise MKPKInvalidParameter(
            "lhs", "_assert_no_conflict_in_gadget_addresses", lhs
        )

    if not isinstance(rhs, MKPKIR):
        raise MKPKInvalidParameter(
            "rhs", "_assert_no_conflict_in_gadget_addresses", rhs
        )

    for l_gadget in lhs.gadgets:
        for r_gadget in rhs.gadgets:
            if r_gadget.memory_location == l_gadget.memory_location:
                rhs_filename = MKPKMetaData.get_metadata_with_label(
                    rhs.metadata, "filename"
                ).values[0]
                raise MKPKLinkingError(
                    "Conflict in ROP gadget address.",
                    f"The gadget address {r_gadget.memory_location} appears in\
                    more than one file. The conflict occured while trying to\
                    link with {rhs_filename}.",
                    ErrorType.FATAL,
                )
