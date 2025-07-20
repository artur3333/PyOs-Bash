# Snake Package Manager commands
# Usage: sudo snakepkg <command> <package_name>
# Commands: install, remove, upgrade, list, available, info

import os
import sys
import package_manager
import auth

def run(args, fs):
    if not args or len(args) < 1:
        print("Missing operand.")
        return
    
    command = args[0].lower()

    if command == "install":
        if len(args) < 2:
            print("Missing package name.")
            return
        
        package_name = args[1]
        question = input(f"Do you want to install the package '{package_name}'? (Y/n): ")
        if question.lower() in ['y', 'yes', '']:
            package_manager.install_package(package_name)

    elif command == "remove":
        if len(args) < 2:
            print("Missing package name.")
            return

        package_name = args[1]
        question = input(f"Do you want to remove the package '{package_name}'? (Y/n): ")
        if question.lower() in ['y', 'yes', '']:
            package_manager.remove_package(package_name)

    elif command == "upgrade":
        if len(args) < 2:
            package_manager.upgrade_package()
        
        else:
            package_name = args[1]
            package_manager.upgrade_package(package_name)
    
    elif command == "list":
        package_manager.list_installed_packages()

    elif command == "available":
        package_manager.list_available_packages()

    elif command == "info":
        print("PyOs Package Manager - Version 1.0")
        print("Package Manager Commands: install, remove, upgrade, list, available, info")

    else:
        print(f"Unknown command: {command}.")
