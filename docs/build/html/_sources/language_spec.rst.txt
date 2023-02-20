**Language Features**
=====================

Introduction
------------
Makka Pakka is a programming language which is a superset* of Intel assembly -
any program written in assembly can be transformed into a makka pakka program
with a few minor changes. Makka pakka transpiles into Intel assembly, and
is assembled using the Netwide Asssembler (NASM). Makka pakka's relationship
with Intel assembly is much like how Typescript relates to Javascript.

Makka Pakka programs are specifically designed to be embedded within a linux
executable (ELF) file. The language contains a sub-module which
automatically implants the program bytes into a code cave of a target program.
A code cave is a section of null bytes that are not used by an ELF file. These
arise due to the necessity to page align program segments, therefore can be
found in almost any ELF file to some capacity.

Makka Pakka programs have no runtime. Therefore language features are best
compared to macros in C-like languages. The transpiling process will simply
replace any function and data references with the code itself. This may at
first seem bloated, as calling the same function many time will lead to
repeated code. However, this inefficiency will be removed by the optimisation
of NASM.

Basics
------
Makka pakka files are created using the .mkpk file extension. The below code
section shows an example makka pakka file. Don't worry if this doesn't make
sense now, reading through this page will slowly build-up your knowledge of
language features used here. Notice how no assembly is required here, all
functionality is defered to the standard library to abstract the complexity
of low-level lanuage.

.. code-block::

    !link stdlib/network.mkpk
    !link stdlib/syscall.mkpk
    !link stdlib/execve.mkpk

    [[data]]
    exit_msg: "Connection Terminated"
    port: 0xb315
    addr: 0x0100007f

    [[code]]
    [main]
    > socket
    > connect "addr" "port"
    > dup2
    > bin_sh
    > sys_write "exit_msg" 22
    > sys_exit

Headings
--------
Headings are used to define the sections of a program. There are three standard
headings - data, code, and gadgets. A fourth special heading can be used to
define metadata. The metadata heading is implicitly defined at the top of a
file. Once another heading has been used, metadata can no longer be defined.

- Data: Defines a location in the source file where data labels have defined.
- Code: Defines a location in the source file where code has been written.
- Gadgets: Defines a location in the source file where ROP gadgets have been
    defined.

Headings can be placed in any order, and may be defined multiple times.

The below code illustrates how headings are used to organise a makka pakka
source file.

.. code-block::

    # Metadata must be defined here.

    [[data]]
    # Data labels go here.

    [[code]]
    # Code is written here.

    [[gadgets]]
    # Gadgets are defined here.

    [[data]]
    # Another data section! Order is not important.

Data Labels
-----------
Data labels are used to define constant data in a makka pakka program. It is
best to think of these as #define macros in C. During transpilation, any
references to these data will be replaced with the literal value, or a pointer
to a data defintion.

Data labels are defined using the syntax 'label: value' where label is an
indentifier used to reference the value from the code section. The value may be
either a string, or an integer (decimal or hex).

Strings
^^^^^^^
String values are defined by enclosing text with double quotes - i.e "string".
The following is an example of a string definition.

.. code-block::

    [[data]]
    fruit: "Apple"

Integer
^^^^^^^
Integer values are defined using the either a decimal (base 10) integer, or a
hexadecimal value prefixed with 0x. The following is an example of decimal and
hex integer definitions:

.. code-block::

    [[data]]
    magic: 42
    cow: 0xb33f

Code Section
------------
The code heading is the main part of a makka pakka program. Here, instructions
are defined to implement custom program logic and features.

The Main Function
^^^^^^^^^^^^^^^^^
The main function is the starting place for every makka pakka program. This
is equivalent to C-like languages, where the main() function the starting point
for the user program.

Functions are defined using single square bracket, e.g [func_name]. In the main
function's case, this will be [main]. The following is an example of defining
the main function.

.. code-block::

    [[code]]
    [main]
    # First instruction here.

.. note::
    Functions must be defined under the code heading - [[code]].

Assembly
^^^^^^^^
Makka pakka is a superset of Intel assembly. That means knowledge of writing
programs in Intel assembly is important for writing programs in makka pakka.
Assembly instructions can be written into a makka pakka function exactly like
a regular .asm file.

.. code-block::

    [[code]]
    [main]
    xor eax, eax
    mov rax, 1
    # Your useful instructions here.

Data References
^^^^^^^^^^^^^^^
Time to make your data definitions useful! To reference data that has been
defined under the [[data]] heading, wrap the data label in ${<label name>}.
This syntax will be familiar to bash script users.

When transpiled, references to integer values will be directly replaced with
the integer value. References to strings will be replaced with a pointer to a
data definition of that string.

.. code-block::

    [[data]]
    my_value: 0xfeed

    [[code]]
    [main]
    mov rax, ${my_value}

Comments
^^^^^^^^
Comments are made using a '#' at the start of a line. You may have already
noticed them throughout this page! Inline comments are not currently supported.

Functions
^^^^^^^^^
Functions are the most important feature in makka pakka. They define a short
section of reusable code, which can be called from anywhere in the program. You
should already be familiar with the [main] function - all other functions are
defined in the same way; using a single square bracket [func_name]. The
following is an example of a function defintion.

.. code-block::

    [[code]]
    [my_func]
    # Do a thing here.
    xor rsi, rs

Functions are called using a single '>' followed by the function name. For
example:

.. code-block::

    [[code]]
    [main]
    # My function call.
    > my_func

    # Call it twice!
    > my_func

    [my_func]
    # Do a thing here.
    xor rsi, rsi

Function Arguments
^^^^^^^^^^^^^^^^^^
Functions can also accept arguments. These are directly replaced in the code
during the transpilation. To define a parameter for a function, simply write
the name of the parameter after the closing square bracket in the function
definition - e.g. [my_func] my_arg. The argument is then passed to the
function by appending the value after the function call, seperated by a space,
e.g '> my_func 5'. The argument's value can then be used with the same syntax
as data references; makka pakka will automatically resolve whether data
originates from a label or an argument. Multiple arguments are defined by
seperating argument names by a space. The following code demonstrates this:

.. code-block::

    [[data]]
    my_other_num: 0x50

    [[code]]
    [main]
    # Passing the values 33 and 0x10 to my_func.
    > my_func 33 0x10

    [my_func] my_num second_num
    mov rax, ${my_num}
    mov rsi, ${second_num}
    mov ecx, ${my_other_num}

On top of this, data labels can be used to pass values to functions. This is
done using the syntax '> my_func "<label_name_here>"'. For example, in the
following code, rax will be replaced with a pointer to the string defined at
label 'greeting' ("hi").

.. code-block::

    [[data]]
    greeting: "hi"

    [[code]]
    [main]
    # Passing an argument by label.
    > my_func "greeting"

    [my_func] message
    mov rax, ${message}


Metadata
--------
Metadata is data about a makka pakka file that doesn't directly contribute
to the compiled makka pakka program. Nevertheless, metadata is necessary for
writing maintainable programs. A piece of metadata is defined at the top of a
file (before any heading) using a '!' at the start of the line. Metadata labels
use the following structure: '!<label> <value goes here>'. Mulitple piece of
metadata can be defined under the same label, by repeating the definition.
For example, a piece of metadata about Makka Pakka and friends would be:

.. code-block::

    !name Makka Pakka
    !friend Iggle Piggle
    !friend Upsy Daisy
    !friend The Tombilboos

    [[code]]
    # Code goes here.

Linking
^^^^^^^
Linking makka pakka files is performed using the '!link' metadata label. User
libraries must be stored in one of: the same directory as the main source file,
/usr/local/lib/mkpk/, or ~/.local/lib/mkpk/.

Makka pakka has a standard library of common functions. These can be linked
using '!link stdlib/<stdlib_filename.mkpk>'.

The following is a simple program that splits its functionality across multiple
.mkpk files:

.. code-block::

    --- main.mkpk ---
    !link other.mkpk

    [[code]]
    [main]
    > other_func

    --- other.mkpk ---
    [[code]]
    [other_func]
    mov rax, 1

The following is an example of using a function from the standard library:

.. code-block::

    !link stdlib/syscall.mkpk

    [[data]]
    msg: "Hello, world!"

    [[code]]
    [main]
    > sys_write "msg" 14

.. seealso::
    - :doc:`usage`
    - :doc:`examples`
    - :doc:`compilation`
