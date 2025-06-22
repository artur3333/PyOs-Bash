import os

class FileSystem:
    def __init__(self):
        self.ROOT_DIR = os.path.abspath("fs")
        self.current_dir = self.ROOT_DIR

    def abs_path(self, path):
        new_path = os.path.abspath(os.path.join(self.current_dir, path))
        if new_path.startswith(self.ROOT_DIR):
            return new_path
        return self.current_dir

    def change_directory(self, path):
        move = self.abs_path(path)
        if os.path.isdir(move):
            self.current_dir = move
        else:
            print("No such directory")

    def rel_path(self, path):
        if path.startswith(self.ROOT_DIR):
            return path.replace(self.ROOT_DIR, "~").replace("\\", "/")
        return path

    def prompt(self):
        now_path = self.current_dir.replace(self.ROOT_DIR, "~")
        return f"{now_path.replace('\\', '/')} $ "
