# Command to copy files or directories
# Usage: cp [-r] <source> <destination>

import os
import shutil

def run(args, fs):
    if len(args) < 2:
        print("Missing operand.")
        return

    recursive = '-r' in args
    if recursive:
        args.remove('-r')
    
    if len(args) != 2:
        print("Invalid number of arguments.")
        return
    
    source = fs.abs_path(args[0])
    destination = fs.abs_path(args[1])

    try:
        if os.path.isfile(source):
            shutil.copy2(source, destination)
            print(f"Copied file: {fs.rel_path(source)} to {fs.rel_path(destination)}")
        
        elif os.path.isdir(source):
            if recursive:
                shutil.copytree(source, destination)
                print(f"Copied directory: {fs.rel_path(source)} to {fs.rel_path(destination)}")
            else:
                print(f"Cannot copy '{fs.rel_path(source)}': Is a directory")

    except FileNotFoundError:
        print(f"Cannot copy '{fs.rel_path(source)}': No such file or directory")
