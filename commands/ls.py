import os

def run(args, current_dir):
    all_items = '-a' in args
    for item in os.listdir(current_dir):
        if not all_items and item.startswith('.'):
            continue
        item_path = os.path.join(current_dir, item)
        if os.path.isdir(item_path):
            print(f"{item}/")
        else:
            print(item)
