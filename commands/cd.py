# Command to change the current working directory
# Usage: cd <directory>

def run(args, fs):
    if args:
        fs.change_directory(args[0])
