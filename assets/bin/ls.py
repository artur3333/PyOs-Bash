# Command to list files and directories in the current directory
# Usage: ls [-a]

import os

def run(args, fs):
    all_items = '-a' in args
    for item in os.listdir(fs.current_dir):
        if not all_items and item.startswith('.'):
            continue
        item_path = os.path.join(fs.current_dir, item)

        if os.path.isdir(item_path):
            print(f"{item}/")

        else:
            print(item)
