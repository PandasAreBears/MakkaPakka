import pytest

from makka_pakka.directed_graph.directed_graph import DirectedGraph
from makka_pakka.directed_graph.node import Node
from makka_pakka.exceptions.exceptions import MKPKCyclicDependency
from makka_pakka.exceptions.exceptions import MKPKInvalidParameter


@pytest.fixture
def empty_graph():
    return DirectedGraph("root")


@pytest.fixture
def linear_three_nodes():
    graph = DirectedGraph("one")
    two = graph.connect_new_node(graph.root, "two")
    graph.connect_new_node(two, "three")

    return graph


@pytest.fixture
def one_to_many():
    graph = DirectedGraph("one")
    two = graph.connect_new_node(graph.root, "two")
    graph.connect_new_node(two, "three")
    graph.connect_new_node(two, "four")
    graph.connect_new_node(two, "five")

    return graph


@pytest.fixture
def simple_cyclic_dependency():
    graph = DirectedGraph("one")
    two = graph.connect_new_node(graph.root, "two")
    graph.connect_node_to_node(two, graph.root)

    return graph


@pytest.fixture
def long_cyclic_dependency():
    graph = DirectedGraph("one")

    prev: Node = graph.root
    for i in range(100):
        prev = graph.connect_new_node(prev, str(i))

    graph.connect_node_to_node(prev, graph.get_node_with_label("50"))

    return graph


@pytest.fixture
def complex_graph_no_cyclic_dep():
    graph = DirectedGraph("one")

    two = graph.connect_new_node(graph.root, "two")
    three = graph.connect_new_node(two, "three")
    four = graph.connect_new_node(two, "four")
    five = graph.connect_new_node(three, "five")
    graph.connect_node_to_node(four, five)
    graph.connect_new_node(five, "six")

    return graph


@pytest.fixture
def multi_length_cyclic_dependencies():
    graph = DirectedGraph("one")
    two = graph.connect_new_node(graph.root, "two")
    three = graph.connect_new_node(two, "three")
    graph.connect_node_to_node(three, graph.root)
    four = graph.connect_new_node(three, "four")
    five = graph.connect_new_node(four, "five")
    six = graph.connect_new_node(five, "six")
    graph.connect_node_to_node(six, graph.root)

    return graph


class TestDirectedGraphConstructor:
    def test_invalid_parameters(self):
        try:
            DirectedGraph(None)
            pytest.fail(
                "DirectedGraph should have failed with MKPKInvalidParameter\
            but did not."
            )
        except MKPKInvalidParameter:
            pass


class TestGetNodeWithLabel:
    def test_invalid_parameter(self, empty_graph: DirectedGraph):
        try:
            empty_graph.get_node_with_label(None)
            pytest.fail(
                "get_node_with_label should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_gets_node_with_label(self, linear_three_nodes: DirectedGraph):
        node = linear_three_nodes.get_node_with_label("three")

        assert node.label == "three"

    def test_returns_none_on_invalid_label(self, linear_three_nodes: DirectedGraph):
        node = linear_three_nodes.get_node_with_label("four")

        assert not node


class TestConnectToNodeWithLabelCreateIfNotExists:
    def test_invalid_parameters(self, empty_graph: DirectedGraph):
        mock_node = empty_graph.root
        mock_invalid_node = Node("hi")
        mock_label = "hello"
        try:
            empty_graph.connect_to_node_with_label_create_if_not_exists(None, None)
            pytest.fail(
                "connect_to_node_with_label_create_if_not_exists should\
                have failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            empty_graph.connect_to_node_with_label_create_if_not_exists(mock_node, None)
            pytest.fail(
                "connect_to_node_with_label_create_if_not_exists should\
                have failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            empty_graph.connect_to_node_with_label_create_if_not_exists(
                None, mock_label
            )
            pytest.fail(
                "connect_to_node_with_label_create_if_not_exists should\
                have failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            empty_graph.connect_to_node_with_label_create_if_not_exists(
                mock_invalid_node, mock_label
            )
            pytest.fail(
                "connect_to_node_with_label_create_if_not_exists should\
                have failed with MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_creates_new_node_when_label_invalid(
        self, linear_three_nodes: DirectedGraph
    ):
        initial_len: int = len(linear_three_nodes.nodes)
        result: bool = (
            linear_three_nodes.connect_to_node_with_label_create_if_not_exists(
                linear_three_nodes.root, "invalid"
            )
        )

        assert result

        assert len(linear_three_nodes.nodes) == initial_len + 1

    def test_adds_existing_node(self, linear_three_nodes: DirectedGraph):
        initial_len: int = len(linear_three_nodes.nodes)
        root_num_children: int = len(linear_three_nodes.root.get_children())
        # This shouldn't create a new node, so false is expected.
        result: bool = (
            linear_three_nodes.connect_to_node_with_label_create_if_not_exists(
                linear_three_nodes.root, "three"
            )
        )

        assert not result

        assert initial_len == len(linear_three_nodes.nodes)

        assert len(linear_three_nodes.root.get_children()) == root_num_children + 1

    def test_does_not_duplicate_connection(self, linear_three_nodes: DirectedGraph):
        initial_len: int = len(linear_three_nodes.nodes)
        root_num_children: int = len(linear_three_nodes.root.get_children())
        # This shouldn't create a new node, so false is expected.
        result: bool = (
            linear_three_nodes.connect_to_node_with_label_create_if_not_exists(
                linear_three_nodes.root, "two"
            )
        )

        assert not result

        assert initial_len == len(linear_three_nodes.nodes)

        assert root_num_children == len(linear_three_nodes.root.get_children())


class TestConnectNewNode:
    def test_invalid_parameters(self, empty_graph: DirectedGraph):
        mock_parent: Node = empty_graph.root
        mock_new_label = "new_label"

        try:
            empty_graph.connect_new_node(None, None)
            pytest.fail(
                "connect_new_node should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            empty_graph.connect_new_node(mock_parent, None)
            pytest.fail(
                "connect_new_node should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            empty_graph.connect_new_node(None, mock_new_label)
            pytest.fail(
                "connect_new_node should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_connects_new_node(self, empty_graph: DirectedGraph):
        initial_len: int = len(empty_graph.nodes)
        root_num_children: int = len(empty_graph.root.get_children())

        new_node: Node = empty_graph.connect_new_node(empty_graph.root, "new_label")

        assert new_node

        assert len(empty_graph.nodes) == initial_len + 1

        assert len(empty_graph.root.get_children()) == root_num_children + 1

        assert new_node in empty_graph.root.get_children()


class TestHasCyclicDependency:
    def test_no_cyclic_dep_in_linear_graph(self, linear_three_nodes: DirectedGraph):
        assert not linear_three_nodes.has_cyclic_dependency()

    def test_no_cyclic_dep_in_one_to_many(self, one_to_many: DirectedGraph):
        assert not one_to_many.has_cyclic_dependency()

    def test_no_cyclic_dep_complex_graph(
        self, complex_graph_no_cyclic_dep: DirectedGraph
    ):
        assert not complex_graph_no_cyclic_dep.has_cyclic_dependency()

    def test_simple_cyclic_dep(self, simple_cyclic_dependency: DirectedGraph):
        path = simple_cyclic_dependency.has_cyclic_dependency()

        assert path

        assert path == ["one", "two", "one"]

    def test_long_cyclic_dep(self, long_cyclic_dependency: DirectedGraph):
        path = long_cyclic_dependency.has_cyclic_dependency()

        assert path

        # root node + 100 nodes + repeated node == 102
        assert len(path) == 102

    def test_multiple_cyclic_deps_returns_shortest(
        self, multi_length_cyclic_dependencies: DirectedGraph
    ):
        path = multi_length_cyclic_dependencies.has_cyclic_dependency()

        assert path

        assert path == ["one", "two", "three", "one"]


class TestCreateAndAssertNoCycle:
    def test_invalid_parameters(self, linear_three_nodes: DirectedGraph):
        mock_parent = linear_three_nodes.root
        mock_label = "new_label"

        try:
            linear_three_nodes.create_and_assert_no_cycle(None, None)
            pytest.fail(
                "create_and_assert_no_cycle should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            linear_three_nodes.create_and_assert_no_cycle(mock_parent, None)
            pytest.fail(
                "create_and_assert_no_cycle should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            linear_three_nodes.create_and_assert_no_cycle(None, mock_label)
            pytest.fail(
                "create_and_assert_no_cycle should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_does_not_error_on_new_node(self, linear_three_nodes: DirectedGraph):
        new_label = "four"
        linear_three_nodes.create_and_assert_no_cycle(
            linear_three_nodes.root, new_label
        )

        assert len(linear_three_nodes.nodes) == 4
        assert linear_three_nodes.get_node_with_label(new_label)

    def test_throws_on_cyclic_dependency(self, linear_three_nodes: DirectedGraph):
        three_node = linear_three_nodes.get_node_with_label("three")

        try:
            linear_three_nodes.create_and_assert_no_cycle(three_node, "one")
            pytest.fail(
                "create_and_assert_no_cycle should have failed with\
                        MKPKCyclicDependency, but did not."
            )
        except MKPKCyclicDependency:
            pass


class TestGetCyclicDependencyStr:
    def test_invalid_parameters(self):
        try:
            DirectedGraph.get_cyclic_dependency_str(None)
            pytest.fail(
                "get_cyclic_dependency_str should have failed with\
                MKPKInvalidParameter but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_simple_cyclic_dep(self, simple_cyclic_dependency: DirectedGraph):
        path = simple_cyclic_dependency.has_cyclic_dependency()

        path_str = DirectedGraph.get_cyclic_dependency_str(path)

        assert path_str == "one --> two --> one"
