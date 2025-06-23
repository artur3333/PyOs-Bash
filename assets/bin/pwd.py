# Command to print the current working directory
# Usage: pwd

def run(args, fs):
    print(fs.rel_path(fs.current_dir))
