**Installation**
================

.. note::
    Makka Pakka only works on Linux. Trying to run it on other operating
    systems will not work.

Installation
------------
Makka Pakka is distributed as a package on
`PyPi <pypi.org/project/MakkaPakka>`_.

To install, use pip:

.. code-block::

    pip install MakkaPakka

You should then have access to three commands: mkpk, mkpk-transpile, and
elf-caver.

Test them out!
.. code-block::

    mkpk --help
    Usage: mkpk [OPTIONS] MKPK_FILEPATH TARGET_BINARY

    Options:
    -o, --output-file TEXT  The filepath to output the injected binary to.
    -n, --patch-entrypoint  Patches the entrypoint to point to injected code.
    -e, --patch-exit        Patches the process exit to point to the injected
                            code.
    -v, --verbose           Logs a verbose output to stdout.
    --help                  Show this message and exit.

.. code-block::

    mkpk-transpile --help
    Usage: mkpk-transpile [OPTIONS] MKPK_FILEPATH

    Options:
    -o, --output TEXT  The filepath to output the translated makka pakka code.
    --help             Show this message and exit

.. code-block::

    elf-caver --help
    Usage: elf-caver [OPTIONS]

    Options:
    -a, --asm-file TEXT     The filepath of the .asm file to inject.  [required]
    -t, --target-file TEXT  The filepath of the binary to inject into.
                            [required]
    -o, --output-file TEXT  The filepath to output the injected binary to.
                            [required]
    -n, --patch-entrypoint  (Optional) Patches the entrypoint to point to
                            injected code.
    -e, --patch-exit        (Optional) Patches the process exit to point to the
                            injected code.
    --help

Development Installation
------------------------
If you wish to contribute to Makka Pakka, then these are the instruction for
downloading the source and setting up the dev environment.

Prerequisite installs:

- Python 3.10+
- Netwide Assembler (NASM)

Clone the git repository and configure the environment.

.. code-block:: console

    cd <your directory>
    git clone https://github.com/PandasAreBears/MakkaPakka

.. code-block:: console

    cd MakkaPakka
    source configure.sh


At this point you can use Makka Pakka from within this directory.

.. code-block:: console

    python3 src/makka_pakka/mkpk.py --help


.. seealso::
    - :doc:`usage`
    - :doc:`examples`
    - :doc:`language_spec`
