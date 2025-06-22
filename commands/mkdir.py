import os
import state
import filesystem

def run(args, current_dir):
    if args:
        new_dir = filesystem.abs_path(args[0])
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        else:
            print(f"A subdirectory or file '{args[0]}' already exists.")
    else:
        print("The syntax of the command is incorrect.")