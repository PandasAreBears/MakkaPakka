from pathlib import Path
from typing import List

from makka_pakka.directed_graph.directed_graph import DirectedGraph
from makka_pakka.directed_graph.node import Node
from makka_pakka.exceptions.exceptions import ErrorType
from makka_pakka.exceptions.exceptions import LinkingError
from makka_pakka.linking.linker_path import LinkerPath
from makka_pakka.parsing.parse import parse_makka_pakka
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.parsing.parsing_structures import MKPKMetaData


def parse_with_linking(mkpk_filepath: str) -> List[MKPKIR]:
    """
    Parses a makka pakka source file, recursively linking with files found in
    the !link metadata directive.
    :mkpk_filepath: The makka pakka source file to parse using recursive
        linking.
    :returns: A list of MKPKIR objects which represent .mkpk files that have
        been parsed as dependencies of the main source file. The main source
        file will at index 0.
    :remark: Each IR object in the returned list is assigned a metadata
        attribute 'link_depth' which specifies the number of linked files
        between it and the main source file. A direct link from the source
        file will have value 1.
    """
    # Initialise the linking graph for dependency loop checking. Root doesn't
    # represent a file, just a placeholder for the start of the graph.
    linker_path: LinkerPath = LinkerPath(mkpk_filepath)

    linking_graph: DirectedGraph = DirectedGraph("root")
    file_IRs: List[MKPKIR] = []

    def parse_file(parent: Node, filename: str):
        nonlocal linker_path, linking_graph, file_IRs

        full_file_path: str = linker_path.find_mkpk_file(filename)
        if not full_file_path:
            raise LinkingError(
                f"Couldn't find file with name {filename}",
                f"Couldn't link with file. Searched in directories\
                 {linker_path.linker_paths.items}",
                ErrorType.FATAL,
            )

        # Add to the graph, and check that this doesn't create a cyclic
        # dependency.
        linking_graph.connect_to_node_with_label_create_if_not_exists(
            parent, full_file_path
        )
        if backtrace := linking_graph.has_cyclic_dependency():
            raise LinkingError(
                "Linking encountered a cyclic linking\
                dependency",
                f"The following cyclic dependency was found while linking\
                    makka pakka code\n:\
                         {DirectedGraph.get_cyclic_dependency_str(backtrace)}",
                ErrorType.FATAL,
            )

        # Parse the file, add it to the list of IR's, then recurse on all
        # linking dependencies.
        file_IR = parse_makka_pakka(full_file_path)
        file_IRs.append(file_IR)

        # There should be either 0 or 1 metadata objects with the label 'link'.
        link_md: MKPKMetaData = MKPKMetaData.get_metadata_with_label(
            file_IR.metadata, "link"
        )
        new_node = linking_graph.get_node_with_label(full_file_path)

        if link_md:
            for link_filename in link_md.values:
                parse_file(new_node, link_filename)

    parse_file(linking_graph.root, Path(mkpk_filepath).name)

    return file_IRs


def merge_MKPKIRs(mkpkirs: List[MKPKIR]) -> MKPKIR:
    """
    Merges a list of MKPKIR objects into a single MKPKIR. The returned object
    is then ready to be processed. This function is intended to be called
    using the result of parse_with_linking.
    :mkpkirs: The list of MKPKIR objects to be merged into one.
    :returns: A MKPKIR object with all passed objects merged into it.
    """
    pass
