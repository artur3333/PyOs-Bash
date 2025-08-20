import os
import time
import json
import hashlib
import getpass
import shutil
import sys

FILE_SYSTEM = "fs"
SYSTEM_CONFIG = os.path.join(FILE_SYSTEM, "etc", "system.conf")
PASSWD_FILE = os.path.join(FILE_SYSTEM, "etc", "passwd")
SHADOW_FILE = os.path.join(FILE_SYSTEM, "etc", "shadow")
PERMISSIONS_FILE = os.path.join(FILE_SYSTEM, "etc", "permissions.json")
SESSIONS_FILE = os.path.join(FILE_SYSTEM, "var", "sessions.json")
PACKAGES_FILE = os.path.join(FILE_SYSTEM, "var", "packages.json")

if getattr(sys, 'frozen', False):
    ASSETS_BASE_PATH = os.path.join(sys._MEIPASS, 'assets')
    
else:
    ASSETS_BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

def create_file_structure():
    directories = [
        "bin",
        "sbin",
        "etc",
        "home",
        "root",
        "var/log",
        "var/tmp",
        "tmp",
        "boot",
        "usr/bin",
        "usr/sbin",
        "usr/lib",
        "dev",
        "proc",
        "sys",
        "lib",
        "opt",
        "mnt",
        "media"
    ]

    print("\nCreating file system structure...")
    for directory in directories:
        path = os.path.join(FILE_SYSTEM, directory)
        os.makedirs(path, exist_ok=True)

    print("Done.")

def create_system_config(hostname, timezone):
    config = {
        "os_name": "PyOS",
        "version": "0.1",
        "maintainer": "artur33",
        "default_shell": "bash",
        "default_editor": "nano",
        "timezone": timezone,
        "locale": "en_US.UTF-8",
        "hostname": hostname,
        "first_boot": False,
        "installation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    print("\nCreating system configuration file...")
    with open(SYSTEM_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)

    print("Done.")

def create_sessions_file():
    print("\nCreating sessions file...")
    sessions = {}
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)
    print("Done.")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def setup_root_user():
    print("\n-- Root User Setup --")
    while True:
        password = getpass.getpass("Enter root password: ")
        confirm_password = getpass.getpass("Confirm root password: ")

        if password == confirm_password:
            hashed_password = hash_password(password)

            with open(PASSWD_FILE, 'w') as file:
                file.write(f"root:x:0:0:root:/root:/bin/bash\n")

            with open(SHADOW_FILE, 'w') as file:
                file.write(f"root:{hashed_password}:0:99999:7:::\n")

            print("Root user setup complete.")
            break
        else:
            print("Passwords do not match. Please try again.")
        
    print("\nRoot user [OK]")

def setup_normal_user():
    print("\n-- User Setup --")
    username = input("Enter username: ").strip()
    if not username:
        print("Username cannot be empty. Invalid username.")
        return

    user_home = os.path.join(FILE_SYSTEM, "home", username)
    os.makedirs(user_home, exist_ok=True)

    while True:
        password = getpass.getpass(f"Enter password for {username}: ")
        confirm_password = getpass.getpass(f"Confirm password for {username}: ")

        if password == confirm_password and password.strip():
            hashed_password = hash_password(password)

            with open(PASSWD_FILE, 'a') as file:
                file.write(f"{username}:x:1000:1000:{username} user:{user_home}:/bin/bash\n")

            with open(SHADOW_FILE, 'a') as file:
                file.write(f"{username}:{hashed_password}:0:99999:7:::\n")

            print(f"\nUser '{username}' created.")
            break
        else:
            print("Passwords do not match or are empty. Please try again.")

    print("\nUser [OK]")
    return username

def default_commands():
    print("\nSetting up default commands...")
    source = os.path.join(ASSETS_BASE_PATH, "bin")
    destination_bin = os.path.join(FILE_SYSTEM, "bin")
    #destination_sbin = os.path.join(FILE_SYSTEM, "sbin")
    if os.path.exists(source):
        for item in os.listdir(source):
            src_path = os.path.join(source, item)
            dest_path = os.path.join(destination_bin, item)
            shutil.copy(src_path, dest_path)
            print(f"Copied {item} to /bin")
    else:
        print(f"Source directory does not exist. Skipping command setup.")

def kernel_setup():
    print("\nSetting up kernel...")
    source = os.path.join(ASSETS_BASE_PATH, "boot", "kernel.py")
    destination_boot = os.path.join(FILE_SYSTEM, "boot", "kernel.py")
    if os.path.exists(source):
        shutil.copy(source, destination_boot)
        print("Done.\n")
        print("------------------------------")
    else:
        print("Kernel file not found. Please ensure it exists in the assets/boot directory.")
        print("Fatal error: Kernel setup failed")
        sys.exit(1)

def create_permissions_file(username):
    print("\nCreating permissions file...")
    permissions = {
        "/": {"owner": "root", "access": "public"},
        "/root": {"owner": "root", "access": "private"},
        f"/home/{username}": {"owner": username, "access": "private"},
    }

    with open(PERMISSIONS_FILE, 'w') as file:
        json.dump(permissions, file, indent=2)
    print("Done.")

def get_info(package_path, package_name):
    try:
        with open(package_path, 'r') as file:
            text = file.readlines()

        description = ""
        version = "1.0.0" # default

        for line in text:
            line = line.strip()

            if line.startswith("# Command "):
                description = line[2:].strip()

            elif line.startswith("# Version: "):
                version = line[11:].strip()
            
            elif line and not line.startswith("#"):
                break

        if not description:
            description = f"{package_name} package"

        return {"description": description, "version": version}
    
    except Exception as e:
        print(f"Error reading package info for {package_name}: {e}")
        return {"description": f"{package_name} package", "version": version}

def create_packages_file():
    print("\nCreating packages JSON...")
    packages = {}
    
    for package in os.listdir(os.path.join(FILE_SYSTEM, "bin")):
        if package.endswith(".py"):
            package_name = package[:-3] # no .py extension
            package_path = os.path.join(FILE_SYSTEM, "bin", package)

            info = get_info(package_path, package_name)

            packages[package_name] = {
                "version": info.get("version"),
                "description": info.get("description"),
                "file": package,
                "source": "default"
            }

            print(f"Registered package: {package_name}")
    
    with open(PACKAGES_FILE, 'w') as file:
        json.dump(packages, file, indent=2)

    print(f"Packages JSON created with {len(packages)} default packages.")
    print("Done.")

def setup():
    print("\n------ First Boot Setup ------")
    print("\nRunning first boot setup...")

    create_file_structure()
    kernel_setup()
    hostname = input("\nEnter hostname for this system: ").strip() or "pyos"
    timezone = input("Enter timezone (e.g. UTC, UTC+2, UTC-5) [default: UTC]: ").strip() or "UTC"
    setup_root_user()
    username = setup_normal_user()
    create_system_config(hostname, timezone)
    default_commands()
    create_permissions_file(username)
    create_sessions_file()
    create_packages_file()
    print("\nFirst boot setup complete. PyOS is ready to use!")
    time.sleep(5)
