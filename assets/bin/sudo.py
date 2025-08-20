# Command to run a command with elevated privileges.
# Usage: sudo <command> [args...]
# Version: 1.0.1

import importlib
import auth
import getpass
import os
import sys
import importlib.util

def load_module(name):
    module_name = f"pyos_cmd_{name}"
    command_path = os.path.abspath(os.path.join("fs", "bin", f"{name}.py"))
    
    if not os.path.exists(command_path):
        return None
    
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, command_path)
    if not spec or not spec.loader:
        return None
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run(args, fs):
    if not args:
        print("Missing operand.")
        return

    if not auth.is_current_root():
        password = getpass.getpass("[sudo] password for root: ")

        if not auth.verify_password("root", password):
            print("Incorrect password.")
            return
        
    original_user = auth.get_current_user()
    original_uid = auth.get_current_uid()
    original_is_root = auth.is_current_root()

    auth.sudo_override_root(True)

    try:
        command_name = args[0]
        command_args = args[1:]
        command_module = load_module(command_name)

        if not command_module:
            print(f"Unknown command: {command_name}")
            return
        
        command_module.run(command_args, fs)

    except ModuleNotFoundError:
        print(f"Unknown command: {args[0]}")

    finally:
        auth.sudo_override_root(False, original_user, original_uid, original_is_root)
