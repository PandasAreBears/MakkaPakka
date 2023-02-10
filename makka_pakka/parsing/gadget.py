from typing import List


class Gadget:
    """A data structure to encapsulate ROP gadgets used in makka pakka."""

    def __init__(self, memory_location: str, content: List[str]) -> None:
        """
        Gadget Constructor.
        :memory_location: The virtual memory address of the ROP gadget in the
            target binary.
        :content: A list of assembly lines at that address, up until a ret is
            reached.
        """
        self.memory_location = memory_location
        self.content = content
