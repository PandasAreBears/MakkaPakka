.. MakkaPakka documentation master file, created by
   sphinx-quickstart on Fri Feb 10 20:31:33 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MakkaPakka Documentation
========================
**Overview**
------------
**Makka pakka** is a programming language which transpiles into Intel
Assembly. It implements additional features on top of traditional
assembly, such as:

- Functions
- Automatic linking
- ROP replacement

The language was built to make it easier to write programs that sit in code
caves. Code cave code must be position independant, therefore, when written
correctly, all makka pakka code will translate into position independant NASM.

For instructions on how to install makka pakka, check out the :doc:`installation`
documentation.

Think something's missing? It probably is... check out the doc:`todo` page to
find out what's coming soon.

.. note::

   This project was made for research purposes and should not be used for
   malicious code injection.

Documentation Contents
^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   installation
   usage
   language_spec
   examples
   compilation
   data_structures
   public_api
   private_api
   todo



Indices and tables
==================

* :ref:`genindex`
