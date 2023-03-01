================
**network.mkpk**
================

Contents
^^^^^^^^
| :ref:`network-linking`
| :ref:`network-data`
| :ref:`network-functions`

.. _network-linking:

Linking
^^^^^^^

.. code-block::

    !link stdlib/network.mkpk

Links with
^^^^^^^^^^
| - :doc:`lib_syscall`

.. _network-data:

Data
^^^^
| *No Data*

.. _network-functions:

Functions
^^^^^^^^^
| [sockaddr_init] addr port protocol
| *Populates a struct sockaddr on the stack.*
| Parameters:
| - addr: The address of the socket.
| - port: The port of the socket.
| - protocol: The protocol of the socket.
|
| [dup_stdstreams] fd
| *Duplicates stdin, stdout, stderr into a single fd.*
| Parameters:
| - fd: The fd to duplicate the stdstreams into.
