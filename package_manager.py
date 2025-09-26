import os
import sys
import json
import requests
import hashlib
import shutil
import auth

PACKAGE_SERVER = "https://artur33.dev/pyos/packages"
PACKAGE_JSON_FILE = os.path.join("fs", "var", "packages.json")
BIN_DIR = os.path.join("fs", "bin")
TEMP_DIR = os.path.join("fs", "tmp")

def load_package_json():
    if os.path.exists(PACKAGE_JSON_FILE):
        try:
            with open(PACKAGE_JSON_FILE, 'r') as file:
                return json.load(file)

        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read packages.json: {e}")
            return {}

    return {}

def clear_package_cache(package_name):
    package = f"fs.bin.{package_name}"
    if package in sys.modules:
        del sys.modules[package]
        print(f"Cleared {package_name} from cache.")
    else:
        print(f"{package_name} is not loaded in cache.")

def save_package_json(data):
    with open(PACKAGE_JSON_FILE, 'w') as file:
        json.dump(data, file, indent=2)

    return True

def fetch_package_list():
    try:
        response = requests.get(f"{PACKAGE_SERVER}/packages.json", timeout=30)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching package list: {e}")
        return None
    
def download_package(package_name, package_info):
    try:
        url = f"{PACKAGE_SERVER}/{package_info['file']}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        if 'hash' in package_info:
            calculated_hash = hashlib.sha256(response.content).hexdigest()
            if calculated_hash != package_info['hash']:
                print(f"Hash mismatch for package '{package_name}'.")
                return None
        
        return response.content
    
    except requests.RequestException as e:
        print(f"Error downloading package '{package_name}': {e}")
        return None

def install_package(package_name):
    if not auth.is_current_root():
        print("Permission denied: You must be root to install packages.")
        return False
    
    print(f"Fetching package information for '{package_name}'...")

    available_packages = fetch_package_list()

    if not available_packages:
        print("Failed to fetch package list from server.")
        return False
    
    if package_name not in available_packages:
        print(f"Package '{package_name}' not found.")
        return False
    
    package_info = available_packages[package_name]
    local_package_json = load_package_json()

    if package_name in local_package_json:
        print(f"Package '{package_name}' is already installed.")
        return False

    print(f"Installing {package_name} v{package_info['version']}...")

    package_content = download_package(package_name, package_info)
    
    if not package_content:
        return False
    
    package_path = os.path.join(BIN_DIR, f"{package_name}.py")

    try:
        with open(package_path, 'wb') as package_file:
            package_file.write(package_content)
        
        os.chmod(package_path, 0o755)  # Make the script executable?

        local_package_json[package_name] = {
            "version": package_info['version'],
            "description": package_info.get('description', ''),
            "file": f"{package_name}.py",
            "source": "PyOS Package Server"
        }

        if not save_package_json(local_package_json):
            if os.path.exists(package_path):
                os.remove(package_path)

            return False
        
        auth.update_permissions(package_path, "root")

        print(f"Package '{package_name}' installed successfully.")
        return True
    
    except Exception as e:
        print(f"Error installing package '{package_name}': {e}")
        if os.path.exists(package_path):
            os.remove(package_path)
        return False
    
def remove_package(package_name):
    if not auth.is_current_root():
        print("Permission denied: You must be root to remove packages.")
        return False
    
    local_package_json = load_package_json()

    if package_name not in local_package_json:
        print(f"Package '{package_name}' is not installed.")
        return False
    
    package_info = local_package_json[package_name]
    package_path = os.path.join(BIN_DIR, package_info['file'])

    try:
        clear_package_cache(package_name)

        if os.path.exists(package_path):
            os.remove(package_path)
            print(f"Removed package file: {package_path}")
        
        del local_package_json[package_name]

        if not save_package_json(local_package_json):
            print("Warning: Could not update package registry.")
            return False

        print(f"Package '{package_name}' removed successfully.")
        return True
    
    except Exception as e:
        print(f"Error removing package '{package_name}': {e}")
        return False
    
def upgrade_package(package_name = None):
    if not auth.is_current_root():
        print("Permission denied: You must be root to upgrade packages.")
        return False
    
    local_package_json = load_package_json()

    if package_name is None:
        print("Checking for updates for all installed packages...")
        available_packages = fetch_package_list()
    
        if not available_packages:
            print("Failed to fetch package list from server.")
            return False
        
        updates = []

        for name, info in local_package_json.items():
            if name in available_packages:
                current_version = info['version']
                latest_version = available_packages[name]['version']
                
                if current_version != latest_version:
                    updates.append((name, current_version, latest_version))
        
        if not updates:
            print("All installed packages are up to date.")
            return True
        
        print(f"Found {len(updates)} packages to update:")
        for name, current, latest in updates:
            print(f"{name}: v{current} -> v{latest}")

        success = 0
        
        response = input("Do you want to upgrade all packages? (Y/n): ").strip().lower()
        if response in ['y', 'yes', '']:
            for name, current, latest in updates:
                print(f"\nUpgrading {name}...")
                if upgrade_single_package(name):
                    success += 1
            
            print(f"\nSuccessfully upgraded {success}/{len(updates)} packages.")
            return success == len(updates)

        else:
            print("Upgrade cancelled.")
            return False

    else:
        print(f"Upgrading package '{package_name}'...")
        if package_name not in local_package_json:
            print(f"Package '{package_name}' is not installed.")
            return False
        
        return upgrade_single_package(package_name)
    
def upgrade_single_package(package_name):
    local_package_json = load_package_json()
    available_packages = fetch_package_list()

    if not available_packages:
        print("Failed to fetch package list from server.")
        return False

    if package_name not in available_packages:
        print(f"Package '{package_name}' not found.")
        return False

    current_version = local_package_json[package_name]['version']
    latest_version = available_packages[package_name]['version']

    if current_version == latest_version:
        print(f"Package '{package_name}' is already up to date (v{current_version}).")
        return False

    print(f"Upgrading {package_name} from v{current_version} to v{latest_version}...")

    if remove_package(package_name):
        return install_package(package_name)

    return False

def list_installed_packages():
    local_package_json = load_package_json()
    
    if not local_package_json:
        print("No packages installed.")
        return
    
    print("Installed packages:")
    for package_name, info in local_package_json.items():
        print(f"{package_name} (v{info['version']}): {info.get('description', 'No description available')}")

def list_available_packages():
    print("Fetching available packages...")

    available_packages = fetch_package_list()
    local_package_json = load_package_json()

    if not available_packages:
        print("No available packages found.")
        return

    print("Available packages:")
    for name, info in available_packages.items():
        status = ""
        if name in local_package_json:
            status = "(installed)"
        else:
            status = ""
        
        print(f"{name} (v{info['version']}): {info.get('description', 'No description available')} {status}")
