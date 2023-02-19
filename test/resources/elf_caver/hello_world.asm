Section .text
   global _start
_start:
   mov eax, 1
   mov rdi, 1
   lea rsi, [rel s1]
   mov rdx, 7
   syscall
   xor edi, edi
   mov eax, 60
   syscall

s1 db "inject", 0
