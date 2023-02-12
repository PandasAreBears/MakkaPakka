from __future__ import annotations

from typing import List
from uuid import uuid4


class Node:
    """A generic node implementation for a directed graph."""

    def __init__(self, label: str):
        self.label = label
        self.connected: List[Node] = []
        self._unique = uuid4()

    def add_connected_node(self, node: Node) -> bool:
        """
        Adds a node to the connected nodes store.
        :node: The node to add to the connected nodes.
        :returns: False when the node is already in the connected nodes list.
        """
        if node not in self.connected:
            self.connected.append(node)
            return True

        return False

    def get_children(self) -> List[Node]:
        """Returns all the nodes that this node points to.
        :returns: A list of child nodes."""
        return self.connected

    def get_node_from_children(self, label: str) -> Node | None:
        """
        Returns the child node which the specified label. Returns None if no
        children have the specified label.
        :label: The label to search for in the child nodes.
        :returns: The child node with the specified label, or None if no
            children have the label.
        """
        for child in self.get_children():
            if child.label == label:
                return child

        return False

    def __eq__(self, other: Node):
        return self._unique == other._unique
