# Command to remove directories.
# Usage: rmdir <directory_name1> <directory_name2> ...
# Version: 1.0.1

import os

def run(args, fs):
    if not args:
        print("Missing operand.")
        return
    
    for name in args:
        dir_to_remove = fs.abs_path(name)
        if os.path.exists(dir_to_remove):
            if os.path.isdir(dir_to_remove):
                try:
                    os.rmdir(dir_to_remove)
                except OSError as e:
                    print(f"Error removing directory probably due to it not being empty.")
            else:
                print("The directory name is invalid or it is not a directory.")
        else:
            print(f"The system cannot find the file specified.")
