# Command to remove files or directories.
# Usage: rm [-r] <file or directory1> <file or directory2> ...
# Version: 1.0.0

import os
import shutil

def run(args, fs):
    if not args:
        print("Missing operand.")
        return

    recursive = '-r' in args
    if recursive:
        args.remove('-r')

    for item in args:
        path = fs.abs_path(item)
        try:
            if os.path.isfile(path):
                os.remove(path)
                print(f"Removed file: {fs.rel_path(path)}")

            elif os.path.isdir(path):
                if recursive:
                    shutil.rmtree(path)
                    print(f"Removed directory: {fs.rel_path(path)}")

                else:
                    print(f"Cannot remove '{item}': Is a directory")
            
            else:
                print(f"Cannot remove '{item}': No such file or directory")
        
        except Exception as e:
            print(f"Error: {e}")
