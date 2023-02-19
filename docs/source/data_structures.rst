**Data Structures**
===================

This page details the data structures used for the translation of Makka Pakka
to assembly. Structures are split into their phase of compilation. More
information about the phases of compilation can be found in the
:doc:`compilation` page.

.. seealso::
   - :doc:`public_api`

Parsing Structures
------------------

.. autoclass:: makka_pakka.parsing.parsing_structures.MKPKFunction

.. autoclass:: makka_pakka.parsing.parsing_structures.MKPKData

.. autoclass:: makka_pakka.parsing.parsing_structures.MKPKDataType

.. autoclass:: makka_pakka.parsing.parsing_structures.MKPKGadget

.. autoclass:: makka_pakka.parsing.parsing_structures.MKPKMetaData

.. autoclass:: makka_pakka.parsing.parsing_structures.MKPKIR

.. autoclass:: makka_pakka.parsing.parsing_structures.MKPKLines

Processing Structures
---------------------

.. automodule:: makka_pakka.processing.processing_structures
   :members:

Exceptions
----------

.. automodule:: makka_pakka.exceptions.exceptions
   :members:
