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


def _ipv4_hex(address: str) -> str:
    """Little-endian hex of a dotted IPv4 address, as /proc/net/tcp prints it (127.0.0.1 -> 0100007F)."""
    parts = [int(x) for x in address.split(".")]
    if len(parts) != 4 or any(not 0 <= x <= 255 for x in parts):
        raise ValueError(f"not an IPv4 address: {address!r}")
    return "".join(f"{x:02X}" for x in reversed(parts))


def listening_inodes(proc_root: Path, port: int, address: str | None = None) -> set[str]:
    """LISTEN sockets on PORT. With ``address`` only sockets that can accept connections to that exact IPv4 address count: bound to it, to 0.0.0.0, to :: (dual-stack) or
    to its IPv4-mapped IPv6 form. A listener on a different address (for example ::1) never matches."""
    wanted_v4 = {_ipv4_hex(address), "00000000"} if address else None
    wanted_v6 = {"0" * 32, "0000000000000000FFFF0000" + _ipv4_hex(address)} if address else None
    inodes = set()
    for name in ("tcp", "tcp6"):
        table = proc_root / "net" / name
        if not table.is_file():
            continue
        for line in table.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            fields = line.split()
            if len(fields) > 9 and fields[3] == "0A" and int(fields[1].rsplit(":", 1)[1], 16) == port:
                local = fields[1].rsplit(":", 1)[0].upper()
                if wanted_v4 is not None and local not in (wanted_v4 if name == "tcp" else wanted_v6):
                    continue
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
    parser.add_argument("--address", help="exact IPv4 destination (for example 127.0.0.1): the proof is then about the listeners that can serve THAT address, and PID must hold ALL of them")
    args = parser.parse_args(argv)
    if not (args.proc_root / "net").is_dir() or not (args.proc_root / str(args.pid) / "fd").is_dir():
        print(f"cannot inspect {args.proc_root}: no /proc/net or no fd table for pid {args.pid}")
        return 2
    inodes = listening_inodes(args.proc_root, args.port, args.address)
    if args.address:
        owns = bool(inodes) and all(pid_holds(args.proc_root, args.pid, {inode}) for inode in inodes)
    else:
        owns = bool(inodes) and pid_holds(args.proc_root, args.pid, inodes)
    print(f"pid {args.pid} {'owns' if owns else 'does NOT own'} a listener on port {args.port} (listening inodes: {sorted(inodes)})")
    return 0 if owns else 1


if __name__ == "__main__":
    sys.exit(main())
