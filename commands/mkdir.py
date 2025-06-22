# Command for creating directories
# Usage: mkdir <directory_name1> <directory_name2> ...

import os

def run(args, fs):
    if not args:
        print("Missing operand.")
        return
    
    for name in args:
        new_dir = fs.abs_path(name)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        else:
            print(f"A subdirectory or file '{name}' already exists.")
