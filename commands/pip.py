# Pip command for python package management
# Usage: pip install <package_name> [<package_name> ...]
# Usage: pip uninstall <package_name> [<package_name> ...]
# Usage: pip list

import os
import json
import subprocess

def get_current_venv():
    venv = os.path.join("fs", "var", "current_venv.json")

    if os.path.exists(venv):
        try:
            with open(venv, 'r') as file:
                data = json.load(file)
                return data.get("current_venv"), data.get("venv_name")
            
        except:
            return None, None
        
    return None, None

def get_pip():
    current_venv, venv_name = get_current_venv()

    if current_venv:
        pip_path = os.path.join(current_venv, "Scripts", "pip.exe")
        if os.path.exists(pip_path):
            return pip_path

        pip_path = os.path.join(current_venv, "bin", "pip")
        if os.path.exists(pip_path):
            return pip_path

def update_packages_json(package_name, action="install"):
    current_venv, venv_name = get_current_venv()
    packages_json = os.path.join(current_venv, "lib", "packages.json")

    if not packages_json:
        return

    try:
        with open(packages_json, 'r') as file:
            packages = json.load(file)

    except:
        packages = {}

    if action == "install":
        pip = get_pip()
        try:
            result = subprocess.run([pip, "show", package_name], capture_output=True, text=True)
            version = "unknown"
            description = ""

            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()

                    elif line.startswith("Summary:"):
                        description = line.split(":", 1)[1].strip()

            packages[package_name] = {
                "version": version,
                "description": description
            }

        except Exception as e:
            print(f"Warning: Could not fetch version info for {package_name}: {e}")
            packages[package_name] = {
                "version": "unknown",
                "description": ""
            }

    elif action == "uninstall" and package_name in packages:
        del packages[package_name]

    try:
        with open(packages_json, 'w') as file:
            json.dump(packages, file, indent=2)

    except Exception as e:
        print(f"Warning: Could not update packages tracking file: {e}") 

def install_package(package_names):
    current_venv, venv_name = get_current_venv()

    if not current_venv:
        print("ERROR: pip install can only be used within a virtual environment.")
        print("Please create a virtual environment:")
        print("  python -m venv <name>")
        print("  source <name>/bin/activate")
        return False

    try:
        pip = get_pip()
        command = [pip, "install"] + package_names
        env = os.environ.copy()

        if current_venv:
            env['VIRTUAL_ENV'] = current_venv
            scripts_path = os.path.join(current_venv, 'Scripts')
            bin_path = os.path.join(current_venv, 'bin')

            if os.path.exists(scripts_path):
                env['PATH'] = scripts_path + os.pathsep + env.get('PATH', '')

            elif os.path.exists(bin_path):
                env['PATH'] = bin_path + os.pathsep + env.get('PATH', '')
        
        result = subprocess.run(command, env=env)

        if result.returncode == 0 and current_venv:
            for package_name in package_names:
                update_packages_json(package_name, "install")
        
        return result.returncode == 0

    except Exception as e:
        print(f"Error running pip install: {e}")
        return False
    
def uninstall_package(package_names):
    current_venv, venv_name = get_current_venv()

    if not current_venv:
        print("ERROR: pip install can only be used within a virtual environment.")
        print("Please create a virtual environment:")
        print("  python -m venv <name>")
        print("  source <name>/bin/activate")
        return False
    
    try:
        pip = get_pip()
        command = [pip, "uninstall", "-y"] + package_names
        env = os.environ.copy()

        if current_venv:
            env['VIRTUAL_ENV'] = current_venv
            scripts_path = os.path.join(current_venv, 'Scripts')
            bin_path = os.path.join(current_venv, 'bin')

            if os.path.exists(scripts_path):
                env['PATH'] = scripts_path + os.pathsep + env.get('PATH', '')
                
            elif os.path.exists(bin_path):
                env['PATH'] = bin_path + os.pathsep + env.get('PATH', '')

        result = subprocess.run(command, env=env)

        if result.returncode == 0 and current_venv:
            for package_name in package_names:
                update_packages_json(package_name, "uninstall")
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"Error running pip uninstall: {e}")
        return False
    
def list_packages():
    current_venv, venv_name = get_current_venv()
    if not current_venv:
        print("ERROR: pip list can only be used within a virtual environment.")
        print("Please create a virtual environment:")
        print("  python -m venv <name>")
        print("  source <name>/bin/activate")
        return False
    
    packages_json = os.path.join(current_venv, "lib", "packages.json")

    if not os.path.exists(packages_json):
        print("No packages installed in this virtual environment.")
        return False
    
    try:
        with open(packages_json, 'r') as file:
            packages = json.load(file)

        if not packages:
            print("No packages installed in this virtual environment.")
            return True
        
        print(f"Installed packages in {venv_name} virtual environment:")
        for package, info in packages.items():
            print(f"{package} - Version: {info['version']}, Description: {info['description']}")
        
        return True
    
    except Exception as e:
        print(f"Error reading packages file: {e}")
        return False
    
def run(args, fs):
    if not args:
        print("Missing arguments.")
    
    command = args[0].lower()

    if command == "install":
        if len(args) < 2:
            print("Usage: pip install <package_name> [<package_name> ...]")
            return
        
        package_names = args[1:]
        install_package(package_names)

    elif command == "uninstall":
        if len(args) < 2:
            print("Usage: pip uninstall <package_name> [<package_name> ...]")
            return
        
        package_names = args[1:]
        uninstall_package(package_names)

    elif command == "list":
        list_packages()

    else:
        print(f"Unknown command: {command} (for this pip integration)")
