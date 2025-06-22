import os
import filesystem

def run(args, current_dir):
    if args:
        dir_to_remove = filesystem.abs_path(args[0])
        if os.path.exists(dir_to_remove):
            if os.path.isdir(dir_to_remove):
                try:
                    os.rmdir(dir_to_remove)
                except OSError as e:
                    print(f"Error removing directory '{args[0]}': {e}")
            else:
                print("The directory name is invalid or it is not a directory.")
        else:
            print(f"The system cannot find the file specified.")
    else:
        print("The syntax of the command is incorrect.")
