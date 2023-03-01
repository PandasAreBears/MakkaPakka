================
**syscall.mkpk**
================

Contents
^^^^^^^^
| :ref:`syscall-linking`
| :ref:`syscall-data`
| :ref:`syscall-functions`

.. _syscall-linking:

Linking
^^^^^^^

.. code-block::

    !link stdlib/syscall.mkpk

Links with
^^^^^^^^^^
| *None*

.. _syscall-data:

Data
^^^^
| _RDONLY: 0x0
| O_WRONLY: 0x1
| O_RDWR: 0x2
|
| *Standard file streams.*
| STDIN: 0
| STDOUT: 1
| STDERR: 2
|
| *The size of struct stat. Defined in stat.h.*
| STAT_STRUCT_SIZE: 144
|
| *The 'whence' options for lseek(2). Defined in unistd.h.*
| SEEK_SET: 0
| SEEK_CUR: 1
| SEEK_END: 2
|
| *The memory protect flags. Defined in mman-linux.h.*
| PROT_NONE: 0x0
| PROT_READ: 0x1
| PROT_WRITE: 0x2
| PROT_EXEC: 0x4
|
| *The flags defining the visibility of updates to mmap's.*
| MAP_SHARED: 0x1
| MAP_PRIVATE: 0x2
|
| *The size of struct sigaction. Defined in signal.h.*
| SIGACTION_STRUCT_SIZE: 152
|
| *The results of a test for access permissions. Defined in unistd.h.*
| R_OK: 0x4
| W_OK: 0x2
| X_OK: 0x1
| F_OK: 0x0
|
| *The flags for msync. Defined in mman-linux.h.*
| MS_ASYNC: 0x1
| MS_INVALIDATE: 0x2
| MS_SYNC: 0x4
|
| *The size of a struct timespec. Defined in time.h.*
| STRUCT_TIMESPEC_SIZE: 16
|
| *The size of a struct itimerval. Defined in sys*
| STRUCT_ITIMERVAL_SIZE: 32
|
| *The types of timer. Defined in sys*
| ITIMER_REAL: 0
| ITIMER_VIRTUAL: 1
| ITIMER_PROF: 2
|
| *The socket protocol families. Defined in sys/socket.h*
| AF_UNSPEC:0
| AF_LOCAL: 1
| AF_UNIX: 1
| AF_FILE: 1
| AF_INET: 2
| AF_AX25: 3
| AF_IPX4: 4
| AF_APPLETALK: 5
| AF_NETROM: 6
| AF_BRIDGE: 7
| AF_ATMPVC: 8
| AF_X25: 9
| AF_INET6: 10
| AF_ROSE: 11
| AF_DECnet: 12
| AF_NETBEUI: 13
| AF_SECURITY: 14
| AF_KEY: 15
| AF_NETLINK: 16
| AF_ROUTE: 16
| AF_PACKET: 17
| AF_ASH: 18
| AF_ECONET: 19
| AF_ATMSVC: 20
| AF_RDS: 21
| AF_SNA: 22
| AF_IRDA: 23
| AF_PPPOX: 24
| AF_WANPIPE: 25
| AF_LLC: 26
| AF_IB: 27
| AF_MPLS: 28
| AF_CAN: 29
| AF_TIPC: 30
| AF_BLUETOOTH: 31
| AF_IUCV: 32
| AF_RXRPC: 33
| AF_ISDN: 34
| AF_PHONET: 35
| AF_IEEE802154: 36
| AF_CAIF: 37
| AF_ALG: 38
| AF_NFC: 39
| AF_VSOCK: 40
| AF_KCM: 41
| AF_QIPCRTR: 42
| AF_SMC: 43
| AF_XDP: 44
| AF_MCTP: 45
|
| *The socket type definitions. Defined in sys/socket.h.*
| SOCK_STREAM: 1
| SOCK_DGRAM: 2
| SOCK_RAW: 3
| SOCK_RDM: 4
| SOCK_SEQPACKET: 5
| SOCK_DCCP: 6
| SOCK_PACKET: 10
|
| *The size of a struct sockaddr. Defined in sys/socket.h.*
| STRUCT_SOCKADDR_SIZE: 16
|
| *The shutdown type definitions. Defined in sys/socket.h.*
| SHUT_RD: 0
| SHUT_WR: 1
| SHUT_RDWR: 2
|
| *The signal type definitions. Defined in signal.h.*
| SIGHUP: 1
| SIGINT: 2
| SIGQUIT: 3
| SIGILL: 4
| SIGTRAP: 5
| SIGABRT: 6
| SIGFPE: 8
| SIGKILL: 9
| SIGSEGV: 11
| SIGPIPE: 13
| SIGALRM: 14
| SIGTERM: 15

.. _syscall-functions:

Functions
^^^^^^^^^
| [sys_read] fd count
| *Reads data from a file descriptor.*
| Parameters:
| - fd: The file descriptor to read from.
| - count: The number of bytes to read into the buffer.
| Consequences:
| - A {count} size buffer on the stack, populated with data read from the fd.
|
| [sys_write] msg len fd
| *Writes data to a file descriptor.*
| Parameters:
| - msg: A pointer to a string of the message to write.
| - len: The length of the pointed to string.
| - fd: The file descriptor to write to.
|
| [sys_open] filename flags
| *Opens a file.*
| Parameters:
| - filename: A pointer to a filepath string to open.
| - flags: Flags specifying the mode to open the file with.
| Consequences:
| - rax contains a file descriptor for the opened file.
|
| [sys_close] fd
| *Closes a file.*
| Parameters:
| - fd: The file descriptor to close.
|
| [sys_stat] filepath
| *Gets a file's status.*
| Parameters:
| - filepath: The path to the file to perform the stat operation on.
| Consequences:
| - A ${STAT_STRUCT_SIZE} size buffer on the stack, populated with a
| stat struct.
|
| [sys_fstat] fd
| *Gets a file descriptor's status.*
| Parameters:
| - fd: The file descriptor of the file to perform the stat operation on.
| Consequences:
| - A ${STAT_STRUCT_SIZE} size buffer on the stack, populated with a
| stat struct.
|
| [sys_lstat] filepath
| *Get a file's status, even if it's a symlink.*
| Parameters:
| - filepath: The path to the file to perform the stat operation on.
| Consequences:
| - A ${STAT_STRUCT_SIZE} size buffer on the stack, populated with a
| stat struct.
|
| [sys_poll] ufds timeout
| *Waits for an event on a file descriptor.*
| Parameters:
| - ufds: A struct pollfd pointer to poll with.
| - timeout: The amount of time in milliseconds that poll() should block
| waiting for a fd to become ready.
|
| [sys_lseek] fd offset whence
| *Reposition read/write file offset.*
| Parameters:
| - fd: The file descriptor to offset into.
| - offset: The offset to seek into the file.
| - whence: A directive for how to move to the offset.
|
| [sys_mmap] addr length prot flags fd offset
| *Map files or devices into memory.*
| Parameters:
| - addr: The starting address of the new mapping.
| - length: The length of the new mapping.
| - prot: The memory protection of the mapping.
| - flags: Determines whether updates to the mapping are visible to other
| processes.
| - fd: The file descriptor to load into memory.
| - offset: The offset of the fd to start at.
|
| [sys_mprotect] addr len prot
| *Set protection on a region of memory.*
| Parameters:
| - addr: The start address of the memory region to protect.
| - len: The length of the memory region to protect.
| - prot: The new protection flags.
|
| [sys_munmap] addr len
| *Unmap files or devices into memory.*
| Parameters:
| - addr: The start address of the region to unmap.
| - len: The length of the region to unmap.
|
| [sys_brk] addr
| *Change the data segment size.*
| Parameters:
| - addr: The address to set the end of the data segment to.
|
| [sys_rt_sigaction] signum act
| *Examine and change a signal action.*
| Parameters:
| - signum: The signal to change the action for.
| - act: A struct sigaction pointer to use as the new action.
| Consequences:
| - A struct sigaction for the old action is pushed onto the stack. The size
| is ${SIGACTION_STRUCT_SIZE}.
|
| [sys_ioctl] fd request
| *Make a request to a control device.*
| Parameters:
| - fd: The file descriptor to make a request to.
| - request: The request code to make to the file.
|
| [sys_pread64] fd size offset
| *Read from a file descriptor at a given offset.*
| Parameters:
| - fd: The file descriptor to read from.
| - size: The number of bytes to read from the file.
| - offset: The offset in the file to start reading from.
| Consequences:
| - A buffer of ${size} is allocated to the stack, containing the read bytes.
|
|
| [sys_pwrite64] fd buf size offset
| *Write to a file descriptor at a given offset.*
| Parameters:
| - fd: The file descriptor to write to.
| - buf: The buffer of characters to write to the file.
| - size: The size of the buffer.
| - offset: The offset to start writing at.
|
| [sys_access] filepath mode
| *Check a user's permissions for a file.*
| Parameters:
| - filepath: The path to the file to check the access for.
| - mode: The mode to check the access for.
| Consequnces:
| - The result of the access check is stored in rax.
|
| [sys_sched_yield]
| *Yield the processor.*
|
| [sys_mremap] old_addr old_len new_len flags new_addr
| *Remap a virtual memory address.*
| Parameters:
| - old_addr: The start address of the existing memory map.
| - old_len: The length of the existing memory map.
| - new_len: The length of the new memory map.
| - flags: The flag to pass to the mremap operation.
| - new_addr: The start address of the new memory map.
|
| [sys_msync] addr length flags
| *Syncronise a file with a memory map.*
| Parameters:
| - addr: The start address of the memory region to sync.
| - length: The length of the memory region to sync.
| - flags: Flags specifying how to sync the region.
|
| [sys_dup] oldfd
| *Duplicate a file descriptor*
| Parameters:
| - oldfd: The old file descriptor.
| Consequences:
| - The new fd is stored in rax.
|
| [sys_dup2] oldfd newfd
| *Duplicate a file descriptor*
| Parameters:
| - oldfd: The old file descriptor.
| - newfd: The new file descriptor to make refer to the old fd.
|
| [sys_pause]
| *Wait for a signal.*
|
| [sys_nanosleep] req
| *High-resolution sleep.*
| Parameters:
| - req: A struct timespec pointer indicating the amount of time to sleep.
| Consequences:
| - Allocates a ${STRUCT_TIMESPEC_SIZE} buffer on the stack containing a
| struct timespec indicating the amount of time left to sleep, only if
| the sleep is interrupted.
|
| [sys_getitimer] which
| *Get of set the value of an interval timer.*
| Parameters:
| - which: The type of timer.
| Consequenes:
| - Allocates a ${STRUCT_ITIMERVAL_SIZE} buffer on the stack containing a
| struct itimerval indicating the time remaining until the timer signals.
|
| [sys_alarm] seconds
| *Set an alarm clock for delivery of a signal.*
| Parameters:
| - seconds: The number of seconds before the SIGALRM is delivered.
|
| [sys_setitimer] which new_value
| *Get or set value of an interval timer.*
| Parameters:
| - which: The type of timer.
| - new_value: A struct itimerval pointer to set the timer to.
| Consequences:
| - Allocates a ${STRUCT_ITIMERVAL_SIZE} buffer to the stack containing a
| struct itimerval with the old itimerval struct that has been replaced.
|
| [sys_getpid]
| *Get the pid of the current process.*
| Consequences:
| - Stores the pid of the calling process into rax
|
| [sys_sendfile] out_fd in_fd offset count
| *Transfer data between file descriptors.*
| Parameters:
| - out_fd: The fd to move data from.
| - in_fd: The fd to move data to.
| - offset: A pointer to an offset value to start copying data from in
| out_fd.
| - count: The number of bytes to copy from out_fd to in_fd.
|
| [sys_socket] domain type protocol
| *Create an endpoint for commuincation.*
| Parameters:
| - domain: Specifies the communication domain, this selects the protocol
| family whilch will be used for communication.
| - type: Specifies the communication semantics.
| - protocol: The particular protocol to be used with the socket.
| Consequences:
| - rax holds a file descriptor for the newly opened socket.
|
| [sys_connect] sockfd addr addrlen
| *Initiate a connection to a socket.*
| Parameters:
| - sockfd: The socket to connect with.
| - addr: A struct sockaddr pointer specifying the addr to connect to.
| - addrlen: The size of addr.
|
| [sys_accept] sockfd
| *Accept a connection on a socket.*
| Parameters:
| - sockfd: The socket listening for incoming connections.
| Consequences:
| - Allocates a ${STRUCT_SOCKADDR_SIZE} buffer to the stack containing a
| struct sockaddr of the connected client.
|
| [sys_sendto] sockfd buf len flags dest_addr dest_len
| *Send a message on a socket.*
| Parameters:
| - sockfd: The socket to send the message from.
| - buf: The buffer containing the message to send.
| - len: The size of the buffer containing the message.
| - flags: Flags controlling the send process.
| - dest_addr: A sockaddr pointer with the destination address to send the
| message to.
| - addr_len: The length of the dest_addr struct.
|
| [sys_shutdown] sockfd how
| *Shut down part of a full-duplex connection.*
| Parameters:
| - sockfd: The socket fd to be shutdown.
| - how: A flag indicating how to shut the socket down.
|
| [sys_bind] sockfd addr addrlen
| *Bind a name to a socket.*
| Parameters:
| - sockfd: The socket fd to bind on.
| - addr: A sockaddr pointer to specifying the address to bind to.
| - addrlen: The size of addr.
|
| [sys_listen] sockfd backlog
| *Listen for connections on a socket.*
| Parameters:
| - sockfd: The socket fd to mark as listening.
| - backlog: The maximum length to which the queue of pending connections
| may grow.
|
| [sys_fork]
| *Create a child process.*
|
| [sys_execve] filename argv envp
| *Execute a program.*
| Parameters:
| - filename: The filename of the program to execute.
| - argv: A pointer to a list of string arguments for the program.
| - envp: A pointer to a list of string environment variables.
|
| [sys_exit]
| *Terminate the calling process.*
|
| [sys_kill] pid sig
| *Send signal to a process.*
| Parameters:
| - pid: The id of the process to send the signal to.
| - sig: The signal to send to the process.
