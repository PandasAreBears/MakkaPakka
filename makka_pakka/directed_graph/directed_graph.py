from typing import List

from makka_pakka.directed_graph.node import Node
from makka_pakka.exceptions.exceptions import InvalidParameter


class DirectedGraph:
    """
    A stripped down implementation of a directed graph. This class is intended
    for use as a dependency tree strcuture; therefore, self loops and
    disconnected nodes are not implemented.
    """

    def __init__(self, root_name: str) -> None:
        """
        Directed graph constructor.
        :root_name: The text label for the root node in the directed graph.
        """
        if not isinstance(root_name, str):
            raise InvalidParameter("root_name", "__init__", root_name)

        self.root = Node(root_name)
        self.nodes: List[Node] = [self.root]

    def get_node_with_label(self, label: str) -> Node | None:
        """
        Gets the node in the directed graph with the specified label.
        :label: The label name to search for in the directed graph.
        :returns: The nodes with the specified label, or None if the node is
            not found.
        """
        if not isinstance(label, str):
            raise InvalidParameter("label", "get_node_with_label", label)

        for node in self.nodes:
            if node.label == label:
                return node

        return None

    def connect_to_node_with_label_create_if_not_exists(
        self, node: Node, label: str
    ) -> bool:
        """
        Connects a node to another node using its label for lookup. If a node
        doesn't exist with this label, then a new node is created (with the
        label), and a connection is made to this one.
        :node: The parent node to point to the child.
        :label: The label to search for a node with, or create a new node with.
        :returns: True if a node node is created, False if a node already
            exists with the label.
        """
        if not isinstance(node, Node) or node not in self.nodes:
            raise InvalidParameter(
                "node", "connect_to_node_with_label_create_if_not_exists", node
            )

        if not isinstance(label, str):
            raise InvalidParameter(
                "label",
                "connect_to_node_with_label_create_if_not_exists",
                label,
            )

        if label_node := self.get_node_with_label(label):
            self.connect_node_to_node(node, label_node)
            return False

        else:
            self.connect_new_node(node, label)
            return True

    def connect_node_to_node(self, connect_from: Node, connect_to: Node) -> bool:
        """
        Creates a directed connection between two nodes.
        :connect_from: The node to create the connection from.
        :connect_to: The node to create the connection to.
        :returns: False when the connection already exists.
        """
        if not isinstance(connect_from, Node):
            raise InvalidParameter("connect_from", "connect_node_to_node", connect_from)

        if not isinstance(connect_to, Node):
            raise InvalidParameter("connect_to", "connect_node_to_node", connect_to)

        return connect_from.add_connected_node(connect_to)

    def connect_new_node(self, parent: Node, new_node_label: str) -> Node:
        """
        Creates a new node, and points a parent node to it.
        :parent: The Node which should be connected to the new node.
        :new_node_label: The label for the new node to be created.
        :returns: The new node that was created.
        """
        if not isinstance(parent, Node):
            raise InvalidParameter("parent", "connect_new_node", parent)

        if not isinstance(new_node_label, str):
            raise InvalidParameter("new_node_label", "parent", new_node_label)

        new_node: Node = Node(new_node_label)

        parent.add_connected_node(new_node)
        self.nodes.append(new_node)

        return new_node

    def has_cyclic_dependency(self) -> List[Node]:
        """
        Determines if the graph has a cycle, i.e nodes that point to each other
        in a loop.
        :returns: A list of Nodes that form a cyclic loop. List is empty if
            there is no cycle in the graph.
        """
        cyclic_path_lock: bool = False
        cyclic_path: List[str] = []

        # Stores the backtrace from the root to the visited node.
        current_path: List[Node] = [self.root]

        def travel_to_connected(node: Node):
            nonlocal cyclic_path, cyclic_path_lock, current_path

            for adj_node in node.get_children():
                # If we try to visit a node that is already in the backtrace,
                # then there must be a cyclic dependency.
                if adj_node in current_path:
                    current_path.append(adj_node)

                    # Check if a cyclic path has already been set, if not
                    # then this is the shortest cyclic path.
                    if not cyclic_path_lock:
                        cyclic_path = [n.label for n in current_path]
                        cyclic_path_lock = True

                else:
                    current_path.append(adj_node)
                    travel_to_connected(adj_node)

                # All connected nodes have been visited, therefore pop the
                # current node from the backtrace.
                current_path.pop()

        travel_to_connected(self.root)

        return cyclic_path

    @staticmethod
    def get_cyclic_dependency_str(path: List[str]) -> str:
        """
        Gets a printable representation of the cyclic dependency returned
        from has_cyclic_dependency.
        :path: A list of string labels - the return result of
            has_cyclic_dependency.
        :return: A string representation of the cyclic dependency.
        """
        if not isinstance(path, list) or not all([isinstance(n, str) for n in path]):
            raise InvalidParameter("path", "get_cyclic_dependency_str", path)

        # Early breakout if there is no cyclic dependency.
        if len(path) == 0:
            return ""

        format_message = path[0]

        for label in path[1:]:
            format_message += f" --> {label}"

        return format_message
