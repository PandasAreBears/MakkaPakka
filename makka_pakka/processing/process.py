from typing import List

from makka_pakka.exceptions.exceptions import InvalidParameter
from makka_pakka.parsing.parsing_structures import MKPKIR
from makka_pakka.processing.data_replacement import process_data_replacement
from makka_pakka.processing.function_replacement import (
    process_function_replacement,
)
from makka_pakka.processing.processing_structures import MKPKCode


def process_makka_pakka(ir: MKPKIR) -> MKPKCode:
    """
    Runs the processing phase of makka pakka compilation.
    :ir: The MKPKIR object which was the result of the parsing phase.
    :returns: A MKPKCode object which has been processed.
    """
    if not isinstance(ir, MKPKIR):
        raise InvalidParameter("ir", "process_makka_pakka", ir)

    ir = process_data_replacement(ir)
    code: List[str] = process_function_replacement(ir)

    return MKPKCode(ir.data, code, ir.gadgets)
