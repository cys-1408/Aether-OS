# Syscall Restrictions Rationale
@system-service covers the ABI these pure-Python services need (file IO, unix
sockets, threads) while blocking mount/ptrace/bpf/kernel-module surfaces.
MemoryDenyWriteExecute is safe because CPython does not JIT. RestrictNamespaces
blocks container-escape style escalation. CapabilityBoundingSet= empty removes
all root capabilities even if a bug granted elevated uid.
