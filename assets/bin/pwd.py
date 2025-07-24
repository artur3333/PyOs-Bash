# Command to print the current working directory.
# Usage: pwd
# Version: 1.0.0

def run(args, fs):
    print(fs.rel_path(fs.current_dir))
