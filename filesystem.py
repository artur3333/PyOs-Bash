import os
import json
import auth

class FileSystem:
    def __init__(self):
        self.ROOT_DIR = os.path.abspath("fs")
        self.current_dir = self.ROOT_DIR
        self.current_user = "sys"
        self.hostname = "pyos"
        self.load_system_config()
    
    def load_system_config(self): # Load system configuration
        config_path = os.path.join(self.ROOT_DIR, "etc", "system.conf")
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                config = json.load(file)
                self.hostname = config.get("hostname", "pyos")
        else:
            print("System configuration file not found. Using default hostname 'pyos'.")

    def abs_path(self, path): # Convert a given path to an absolute path
        if path.startswith('~'): # Handle home directory
            if path == '~':
                path = '/home'

            elif path.startswith('~/'): # Handle home directory with subpath
                path = '/home' + path[1:]

            else: # Handle home directory with username
                username = path[1:].split('/')[0]
                rest = path[len(username)+1:]
                path = f"/home/{username}{rest}"
        
        path = path.replace('\\', '/') # Normalize path separators
        
        if path.startswith("/"): # If the path is absolute
            new_path = os.path.join(self.ROOT_DIR, path[1:])

        else: # If the path is relative
            new_path = os.path.join(self.current_dir, path)
        
        new_path = os.path.abspath(new_path)
        
        if new_path.startswith(self.ROOT_DIR): # Ensure the path is within the root directory
            return new_path
        
        return self.current_dir

    def change_directory(self, path): # Change the current directory to the specified path
        move = self.abs_path(path)

        if not auth.check_permissions(move, action="read"):
            print("Permission denied.")
            return False
            
        if os.path.isdir(move):
            self.current_dir = move
            return True
        else:
            print("No such directory.")
            return False
    
    def rel_path(self, path=None): # Get the relative path from the root directory (to the specified path)
        if path is None:
            path = self.current_dir

        rel = path.replace(self.ROOT_DIR, "").replace('\\', '/')
        if not rel:
            return "/"
        
        if not rel.startswith('/'):
            rel = '/' + rel

        return rel
    
    def prompt_path(self): # Get the path to display in the prompt
        rel = self.rel_path()

        if rel.startswith('/home/'):
            if len(rel.split('/')) >= 3:
                parts = rel.split('/')
                if len(parts) == 3:
                    return "~"
                
                else:
                    return "~/" + '/'.join(parts[3:])
        
        return rel
    
    def prompt(self): # Shell prompt
        
        self.current_user = auth.get_current_user()

        user_host = f"\033[38;2;30;211;154m{self.current_user}@{self.hostname}\033[0m"
        path = f"\033[36m{self.prompt_path()}\033[0m"

        if auth.is_current_root():
            character = "#"
        else:
            character = "$"

        return f"{user_host}:{path}{character} "
