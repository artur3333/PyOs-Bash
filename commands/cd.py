import os
import filesystem

def run(args, current_dir):
    if args:
        filesystem.change_directory(args[0])