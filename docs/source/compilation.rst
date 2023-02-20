**Compilation Process**
=======================

Phases
------
Compilation is split into three phases - Parsing, Processing, and Integrating.
This section will guide the reader though the steps that taken in each phase.

Parsing
-------
*Objective: Translate text from a .mkpk file into an intermediate
representation.*

Step 1: Heading Detection
^^^^^^^^^^^^^^^^^^^^^^^^^
In the first step, a simple iteration of the file is performed where headings,
defined using [[heading]] are detected, and stored as a state which determines
where to put the lines underneath the heading. As a result, there will be an
optional set of lines for each - metadata, data, code, gadgets.

Step 2: Parse Functions
^^^^^^^^^^^^^^^^^^^^^^^
Code lines collected under the functions heading are parsed into
MKPKFunction objects. This stores the name of the function, its arguments, and
the code lines beneath it. The following is the class definition of
MKPKFunction:

.. code-block:: python

    class MKPKFunction:
    """A data strcture to encapsulate code functions used in makka pakka."""

    def __init__(self, name: str, arguments: List[str], content: List[str]):
        """
        Code structure constructor.

        :param name: A unique function name for the section of code.
        :param arugments: A list of unique names for arguements that this function
            expects.
        :param content: A list of lines of makka pakka code.
        """
        self.name = name
        self.is_main = name == "main"
        self.num_arguments = len(arguments)
        self.arguments = arguments
        self.content = content

Step 3: Parse Data
^^^^^^^^^^^^^^^^^^
Data definitions collected under the data heading are parsed into MKPKData
objects. This contains the name of the data label, its value, and its
interpretted data type - the following is the class definition of MKPKDataType
and MKPKData:

.. code-block:: python

    class MKPKDataType:
        """
        Identifies the data type of a MKPKData object.
        """

        NONE = 0
        STR = 1
        INT = 2


    class MKPKData:
        """A data structure to encapsulate constant data used in makka pakka"""

        def __init__(self, name: str, value: Union[int, str], type: MKPKDataType):
            """
            Data structure constructor.

            :param name: A unique label assigned to the constant data.
            :param value: The constant data itself.
            :param type: The data type of the constant data.
            """
            self.name = name
            self.value = value
            self.type = type

Step 4: Parse Gadgets
^^^^^^^^^^^^^^^^^^^^^
Gadget definitions collected under the gadget heading are parsed into
MKPKGadget objects. This contains the virtual memory address of the gadget,
and instructions before a 'ret' at that address. The following is the class
definition of MKPKGadget:

.. code-block:: python

    class MKPKGadget:
        """A data structure to encapsulate ROP gadgets used in makka pakka."""

        def __init__(self, memory_location: str, content: List[str]) -> None:
            """
            Gadget Constructor.

            :param memory_location: The virtual memory address of the ROP gadget in the
                target binary.
            :param content: A list of assembly lines at that address, up until a ret is
                reached.
            """
            self.memory_location = memory_location
            self.content = content

Step 5: Parse Metadata
^^^^^^^^^^^^^^^^^^^^^^
Metadata is considered all lines in the source file that are no defined under
a heading - i.e. at the top of a file. Metadata is parsed into MKPKMetaData
objects, which has the following definition.

.. code-block:: python

    class MKPKMetaData:
        """A data structure to encapsulate metadata used in makka pakka"""

        def __init__(self, label: str, value: str) -> None:
            """
            Metadata Constructor.

            :param label: The label to uniquely identify the meta data.
            :param values: The values associated with the metadata label.
            """
            self.label: str = label
            self.values: List[str] = []

Step 6: Collate Structures
^^^^^^^^^^^^^^^^^^^^^^^^^^
The objects from step 2-5 are then collected into a single object - MKPKIR.
This is the complete intermediate representation of the makka pakka programming
language. The following is the class definition:

.. code-block:: python

    class MKPKIR:
        """An intermediate representation of the makka pakka programming language
        to be populated during the parsing phase."""

        def __init__(self):
            self.data: List[MKPKData] = []
            self.functions: List[MKPKFunction] = []
            self.gadgets: List[MKPKGadget] = []
            self.metadata: List[MKPKMetaData] = []

.. note::
    All data structures used to compile makka pakka can be found in
    :doc:`data_structures`.

Linking
-------
*Objective: Resolve reference to external files, and parse their contents.*

Step 1: Discover Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Linking starts with metadata labels. Files that link with other files use the
'!link {mkpk_filename}' directive. Therefore, the first step is to extract the
filenames that the current file expects to link with.

Step 2: Find Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^
Makka pakka then attempts to find the files that are specified for linking.
This is done by searching in the directories defined in
makka_pakka.linking.linker_path (shown below). The directory of the main source
file is added to the default linker paths at runtime with the highest priority.
The linking priority logic is abstracted by the PriorityList implementation in
makka_pakka.linking.priority_list. If a linked file is not found during this
process, then a MKPKLinkingError will be raised.

.. code-block:: python

    # The default directories to look for linkable .mkpk files in.
    DEFAULT_LINKER_PATHS: List[str] = [
        "/usr/local/lib/mkpk/",
        str(Path.home()) + "/.local/lib/mkpk/",
        str(Path(__file__).parent.parent.parent / "lib/"),
    ]

Step 3: Parse Dependency
^^^^^^^^^^^^^^^^^^^^^^^^
Once the dependency is found, the process starts again -
i.e. the file is parsed into a MKPKIR, then, if this file also contains link
directives, these will be resolved.

To avoid cyclic dependencies causing an infinite linking loop, a custom
DirectedGraph structure is used, implemented in
makka_pakka.directed_graph.directed_graph. The diagram below illustrates an
acceptable, and an unacceptable dependency graph. In the unacceptable case, a
MKPKCyclicDependency error will be raised.

.. image:: _images/cyclic_deps.png
    :alt: Cyclic Dependency Graphs

Step 4: Merge IR Symbols
^^^^^^^^^^^^^^^^^^^^^^^^
The overall goal of the parsing phase is to create a single MKPKIR object that
can be used as an input into the processing phase. When linking is performed,
makka pakka ends up with multiple MKPKIR objects which can contain conflicting
symbols (function names etc.). To resolve this issue, all MKPKIR objects are
merged into the main object (the one created as a result of parsing the main
source file.). If there is a conflict in symbols, then a MKPKLinkingError will
be raised.

.. note::
    In the future, namespacing may be implemented to prevent common conflicts.
    For now, libraries implement their data labels and function name in full
    uppercase. This means user programs are safe to use the entire lowercase
    namespace.


Processing
----------
*Objective: Resolve references data labels and functions.*

Integrating
-----------
*Objective: Replace suitable instruction sequences with ROP calls, and write
the program to file.*
