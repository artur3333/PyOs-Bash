# Command to run Python files
# Usage: python <file.py>
# Usage: python -m venv <path>
# Usage: python deactivate

import os
import sys
import subprocess
import auth
import json

current_venv = None

def load_current_venv():
    global current_venv
    venv = os.path.join("fs", "var", "current_venv.json")

    if os.path.exists(venv):
        try:
            with open(venv, 'r') as file:
                data = json.load(file)
                current_venv = data.get("current_venv")
            
        except:
            current_venv = None
    
    else:
        current_venv = None

def save_current_venv():
    venv = os.path.join("fs", "var", "current_venv.json")
    
    os.makedirs(os.path.dirname(venv), exist_ok=True)

    venv_name = None
    if current_venv:
        venv_name = os.path.basename(current_venv)

    with open(venv, 'w') as file:
        json.dump({
            "current_venv": current_venv,
            "venv_name": venv_name
        }, file)

def create_venv(path, fs):
    abs_path = fs.abs_path(path)

    if not auth.check_permissions(os.path.dirname(abs_path), action="write"):
        print("Permission denied.")
        return False
    
    if os.path.exists(abs_path):
        print(f"Virtual environment '{path}' already exists.")
        return False
    
    try:
        result = subprocess.run([sys.executable, "-m", "venv", abs_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error creating virtual environment: {result.stderr}")
            return False

        packages_file = os.path.join(abs_path, "lib", "packages.json")
        os.makedirs(os.path.dirname(packages_file), exist_ok=True)
        with open(packages_file, 'w') as file:
            json.dump({}, file)
        
        print(f"Virtual environment created at {fs.rel_path(abs_path)}")
        return True
    
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False

def deactivate_venv(fs):
    global current_venv

    rel_path = fs.rel_path(current_venv)

    if current_venv:
        print(f"Deactivated virtual environment: {rel_path}")
        current_venv = None
        save_current_venv()
        return True
    
    else:
        print("No virtual environment is currently active.")
        return False
    
def get_python():
    if current_venv:
        path = os.path.join(current_venv, "Scripts", "python.exe")
        if os.path.exists(path):
            return path
        
        path = os.path.join(current_venv, "bin", "python")
        if os.path.exists(path):
            return path
    
    return sys.executable

def run_python_file(file_path, fs, args=None):
    if args is None:
        args = []

    abs_path = fs.abs_path(file_path)

    if not auth.check_permissions(abs_path, action="read"):
        print("Permission denied.")
        return False
    
    if not os.path.exists(abs_path):
        print(f"Python file '{file_path}' does not exist.")
        return False

    if not abs_path.endswith('.py'):
        print("Not a Python file.")
        return False
    
    try:
        py = get_python()
        command = [py, abs_path] + args
        env = os.environ.copy()

        if current_venv:
            env["VIRTUAL_ENV"] = current_venv
            scripts_path = os.path.join(current_venv, 'Scripts')
            bin_path = os.path.join(current_venv, 'bin')

            if os.path.exists(scripts_path):
                env['PATH'] = scripts_path + os.pathsep + env.get('PATH', '')

            elif os.path.exists(bin_path):
                env['PATH'] = bin_path + os.pathsep + env.get('PATH', '')

        result = subprocess.run(command, env=env)
        return result.returncode == 0
    
    except Exception as e:
        print(f"Error running Python file: {e}")
        return False

def run(args, fs):
    load_current_venv()

    if not args:
        print("Invalid operand.")
        return
    
    if args[0] == "deactivate":
        deactivate_venv(fs)
        return
    
    if args[0] == "-m":
        if len(args) < 2:
            print("Invalid usage.")
            return
        
        module_name = args[1]

        if module_name == "venv":
            if len(args) < 3:
                print("Specify a path for the virtual environment.")
                return
            
            create_venv(args[2], fs)
            return
        
    path = args[0]
    if len(args) > 1:
        file_args = args[1:]
    else:
        file_args = []
    
    run_python_file(path, fs, file_args)
