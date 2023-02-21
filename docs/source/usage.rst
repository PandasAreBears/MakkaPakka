=========
**Usage**
=========

.. note::
    To use these commands, you must first install makka pakka. Check out the
    :doc:`installation` page for instructions.

Compilation
-----------
Compilation is used to describe the transpiling of makka pakka into assembly,
and then automatically compiling, and packing the result into a target binary's
code cave.

The compiler is run using the mkpk.py file. The following is the help output:

.. code-block::

    Usage: mkpk [OPTIONS] MKPK_FILEPATH TARGET_BINARY

    Options:
    -o, --output-file TEXT  The filepath to output the injected binary to.
    -n, --patch-entrypoint  Patches the entrypoint to point to injected code.
    -e, --patch-exit        Patches the process exit to point to the injected
                            code.
    -v, --verbose           Logs a verbose output to stdout.
    --help                  Show this message and exit.

Code Caver
----------
The code caver program can be used as a submodule of the makka pakka
programming language. This can be used to implant any Intel assembly code into
a target binary.

The code caver is run using the elf_caver.py file. The following is the help
output:

.. code-block::

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
    --help                  Show this message and exit.

Transpiler
----------
Transpiling a makka pakka program into Intel assembly can be done as a
standalone process. This is likely to be useful within a scripting tool,
such as to pack bytes into multiple target binaries without having to
re-compile the program for every file.

.. code-block::

    Usage: mkpk-transpile [OPTIONS] MKPK_FILEPATH

    Options:
    -o, --output TEXT  The filepath to output the translated makka pakka code.
    --help             Show this message and exit.
            Show this message and exit.


.. seealso::
    - :doc:`installation`
    - :doc:`examples`
    - :doc:`language_spec`
