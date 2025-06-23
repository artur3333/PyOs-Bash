# Command to move or rename files or directories
# Usage: mv <source> <destination>

import os
import shutil

def run(args, fs):
    if not args or len(args) < 2:
        print("Missing operand.")
        return

    source = fs.abs_path(args[0])
    destination = fs.abs_path(args[1])

    try:
        shutil.move(source, destination)
        print(f"Moved: {fs.rel_path(source)} to {fs.rel_path(destination)}")
        
    except FileNotFoundError:
        print(f"Cannot move '{fs.rel_path(source)}': No such file or directory")
