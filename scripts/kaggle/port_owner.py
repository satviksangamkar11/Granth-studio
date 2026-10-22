"""Does process PID hold a LISTENING TCP socket on PORT? Linux /proc only, no extra tools.

  python port_owner.py PID PORT [--proc-root /proc]      exit 0 = yes, 1 = no, 2 = /proc cannot answer (treated as a refusal)

The GPU script uses this to prove that the server answering on the fresh port is the ComfyUI process it launched, instead of trusting
whatever responds. A listening socket is matched by inode: /proc/net/tcp{,6} rows in state 0A (LISTEN) on PORT, then PID's file
descriptors must include socket:[inode].
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def listening_inodes(proc_root: Path, port: int) -> set[str]:
    inodes = set()
    for name in ("tcp", "tcp6"):
        table = proc_root / "net" / name
        if not table.is_file():
            continue
        for line in table.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            fields = line.split()
            if len(fields) > 9 and fields[3] == "0A" and int(fields[1].rsplit(":", 1)[1], 16) == port:
                inodes.add(fields[9])
    return inodes


def pid_holds(proc_root: Path, pid: int, inodes: set[str]) -> bool:
    fd_dir = proc_root / str(pid) / "fd"
    wanted = {f"socket:[{inode}]" for inode in inodes}
    for entry in fd_dir.iterdir():
        try:
            if os.readlink(entry) in wanted:
                return True
        except OSError:
            continue
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pid", type=int)
    parser.add_argument("port", type=int)
    parser.add_argument("--proc-root", type=Path, default=Path("/proc"))
    args = parser.parse_args(argv)
    if not (args.proc_root / "net").is_dir() or not (args.proc_root / str(args.pid) / "fd").is_dir():
        print(f"cannot inspect {args.proc_root}: no /proc/net or no fd table for pid {args.pid}")
        return 2
    inodes = listening_inodes(args.proc_root, args.port)
    owns = bool(inodes) and pid_holds(args.proc_root, args.pid, inodes)
    print(f"pid {args.pid} {'owns' if owns else 'does NOT own'} a listener on port {args.port} (listening inodes: {sorted(inodes)})")
    return 0 if owns else 1


if __name__ == "__main__":
    sys.exit(main())
