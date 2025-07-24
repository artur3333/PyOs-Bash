# Command to change the current working directory.
# Usage: cd <directory>
# Version: 1.0.0

def run(args, fs):
    if args:
        fs.change_directory(args[0])
