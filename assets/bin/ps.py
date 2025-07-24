# Command to display the processes running on the system.
# Usage: ps [<options>]
# Version: 1.0.0

import os

def run(args, fs): # For now it's a base implementation, because for now the system doesn't support processes.
    print("  PID TTY          TIME CMD")
    print("  --- ---          ---- ---")

    processes = [
        {"pid": 1, "tty": "tty1", "time": "00:00:01", "cmd": "sys"}
    ]

    for process in processes:
        print(f"{process['pid']:5} {process['tty']:8} {process['time']:8} {process['cmd']}")

    print(f"\n{len(processes)} processes running.")
