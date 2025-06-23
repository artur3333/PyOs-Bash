# Command to create empty files or update timestamps
# Usage: touch <file1> <file2> ...

import os

def run(args, fs):
    if not args:
        print("Missing file operand.")
        return
    
    for name in args:
        path = fs.abs_path(name)
        try:
            with open(path, 'a'):
                os.utime(path, None)

            print(f"Touched: {fs.rel_path(path)}")
        
        except Exception as e:
            print(f"Error touching '{name}': {e}")
