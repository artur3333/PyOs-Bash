# Command to display the directory tree structure.
# Usage: tree [directory]
# Version: 1.0.0

import os

def run(args, fs):
    def print_tree(path, prefix=""):
        items = sorted(os.listdir(path))
        
        directories = []
        files = []
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                directories.append(item)
            else:
                files.append(item)
        
        all_items = directories + files
        
        for i, item in enumerate(all_items):
            is_last = (i == len(all_items) - 1)
            
            if is_last:
                current_prefix = "└── "
                next_prefix = "    "

            else:
                current_prefix = "├── "
                next_prefix = "│   "

            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                item += "/"
            else:
                item = item

            print(prefix + current_prefix + item)
            
            if os.path.isdir(item_path):
                print_tree(item_path, prefix + next_prefix)
    
    start_path = fs.current_dir
    if args:
        start_path = fs.abs_path(args[0])
        if not os.path.isdir(start_path):
            print("Not a directory:", fs.rel_path(start_path))
            return
    
    print(os.path.basename(start_path))
    print_tree(start_path)
