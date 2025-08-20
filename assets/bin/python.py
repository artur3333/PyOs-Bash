# Command to run Python files.
# Usage: python <file.py> / python -m venv <path> / python deactivate
# Version: 1.1.0

import os
import sys
import subprocess
import auth
import json
import shutil

current_venv = None

def load_current_venv():
    global current_venv
    venv = os.path.join("fs", "var", "current_venv.json")

    if os.path.exists(venv):
        try:
            with open(venv, 'r', encoding='utf-8') as file:
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

    with open(venv, 'w', encoding='utf-8') as file:
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
        python_exe = get_system_python()

        if python_exe is None:
            print("ERROR: No system Python installation found!")
            print("Virtual environments require Python to be installed on the system.")
            print("Please install Python from https://python.org")
            print("\nNote: You can still run Python files without a virtual environment.")
            return False
        
        print(f"Creating virtual environment using system Python...")

        result = subprocess.run([python_exe, "-m", "venv", abs_path], capture_output=True, text=True)

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
        if not getattr(sys, 'frozen', False):
            path = os.path.join(current_venv, "Scripts", "python.exe")

        if os.path.exists(path):
            return path
        
        path = os.path.join(current_venv, "bin", "python")
        if os.path.exists(path):
            return path
    
    return sys.executable

def get_system_python():
    pys = ['python', 'python3', 'python.exe']

    for py in pys:
        python_exe = shutil.which(py)
        if python_exe:
            if "WindowsApps" not in python_exe:
                if "Microsoft" not in python_exe:
                    try:
                        result = subprocess.run([python_exe, "--version"], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0 and "Python" in result.stdout:
                            return python_exe
                    
                    except:
                        continue
    
    return None

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
        if current_venv:
            venv_python = None

            venv_scripts = os.path.join(current_venv, 'Scripts', 'python.exe')

            if os.path.exists(venv_scripts):
                venv_python = venv_scripts

            else:
                venv_bin = os.path.join(current_venv, 'bin', 'python')
                if os.path.exists(venv_bin):
                    venv_python = venv_bin

            if venv_python:
                command = [venv_python, abs_path] + args
                env = os.environ.copy()
                env['VIRTUAL_ENV'] = current_venv
                venv_dir = os.path.dirname(venv_python)
                env['PATH'] = venv_dir + os.pathsep + env.get('PATH', '')

                result = subprocess.run(command, env=env)
                return result.returncode == 0
            
            else:
                print("ERROR: Virtual environment Python interpreter not found!")
                return False
        
        if getattr(sys, 'frozen', False):
            return run_python_in(abs_path, args)
        
        py = get_python()

        if py is None:
            print("ERROR: Python interpreter not found!")
            return False
        
        command = [py, abs_path] + args
        result = subprocess.run(command)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running Python file: {e}")
        return False

def run_python_in(file_path, args):
    try:
        old_argv = sys.argv
        sys.argv = [file_path] + args

        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()

        file_globals = {'__file__': file_path, '__name__': '__main__', '__builtins__': __builtins__}

        exec(code, file_globals)

        return True
    
    except SystemExit as e:
        return e.code == 0
    
    except Exception as e:
        print(f"Error executing Python code: {e}")
        return False

    finally:
        sys.argv = old_argv

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
