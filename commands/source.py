# Command to execute a shell command
# Usage: source <file>

import os
import json
import auth

def activate_virtualenv(venv_path, fs):
    abs_path = fs.abs_path(venv_path)

    if not os.path.exists(abs_path):
        print(f"Virtual environment '{venv_path}' does not exist.")
        return False
    
    activate_paths = (abs_path.endswith("/bin/activate") or abs_path.replace('\\', '/').endswith("/Scripts/activate"))
    
    if activate_paths:
        venv_path = os.path.dirname(os.path.dirname(abs_path))

        pyvenv_config = os.path.join(venv_path, "pyvenv.cfg")

        if not os.path.exists(pyvenv_config):
            print(f"'{venv_path}' is not a valid virtual environment.")
            return False

        venv_file = os.path.join("fs", "var", "current_venv.json")
        os.makedirs(os.path.dirname(venv_file), exist_ok=True)

        with open(venv_file, 'w') as file:
            json.dump({
                "current_venv": venv_path,
                "venv_name": os.path.basename(venv_path)
            }, file)

        print(f"Activated virtual environment: {fs.rel_path(venv_path)}")
        print("Use 'python deactivate' to deactivate the virtual environment")
        return True
    else:
        print(f"source is only for python virtual environments, for now :)")

def run(args, fs):
    if not args:
        print("Invalid operand.")
        return
    
    path = args[0]

    if not auth.check_permissions(fs.abs_path(path), action="read"):
        print("Permission denied")
        return
    
    activate_virtualenv(path, fs)
