# Command to find files and directories
# Usage: find <name_pattern>

import os

def run(args, fs):
    if not args:
        print("Missing operand.")
        return
    
    pattern = args[0].lower()
    found = []

    for root, dirs, files in os.walk(fs.current_dir):
        for dir in dirs:
            if pattern in dir.lower():
                rel_path = fs.rel_path(os.path.join(root, dir))
                found.append(rel_path + '/')
        
        for file in files:
            if pattern in file.lower():
                rel_path = fs.rel_path(os.path.join(root, file))
                found.append(rel_path)
    
    if found:
        for item in found:
            print("- " + item)

    else:
        print(f"No such file or directory.")
