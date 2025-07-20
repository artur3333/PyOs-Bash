import importlib
import os
import sys
import json
from filesystem import FileSystem
import auth

fs = FileSystem()

def get_installed_packages():
    package_json = os.path.join("fs", "var", "packages.json")
    if not os.path.exists(package_json):
        try:
            with open(package_json, 'r') as file:
                packages = json.load(file)
                return set(packages.keys())
            
        except (json.JSONDecodeError, IOError):
            return set()
    return set()

def is_package_available(package_name):
    commands = {}

    if package_name in commands:
        return True
    
    command_path = os.path.join("fs", "bin", f"{package_name}.py")
    if not os.path.exists(command_path):
        return False

    installed_packages = get_installed_packages()

    return package_name in installed_packages

def shell():
    while True:
        try:
            if not auth.get_current_user():
                if auth.login():
                    continue

            command = input(fs.prompt()).strip()
            if not command:
                continue
            
            if command == "exit":
                print("Exiting the shell.")
                auth.logout()
                break

            try:
                command = command.split()
                command_name = command[0]
                args = command[1:]
                command_module = importlib.import_module(f"fs.bin.{command_name}")

                if not check_module_permissions(command_module):
                    print(f"Permission denied: {command_name}")
                    continue

                command_module.run(args, fs)
                
            except ModuleNotFoundError:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nUse the 'exit' command to quit...")

def check_module_permissions(module):
    if auth.is_current_root():
        return True
    
    root_commands = {
        'useradd', 'userdel'
    }

    command_name = module.__name__.split('.')[-1]
    
    if command_name in root_commands:
        return False
    
    return True
