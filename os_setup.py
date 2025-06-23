import os
import time
import json
import hashlib
import getpass
import shutil

FILE_SYSTEM = "fs"
SYSTEM_CONFIG = os.path.join(FILE_SYSTEM, "etc", "system.conf")
PASSWD_FILE = os.path.join(FILE_SYSTEM, "etc", "passwd")
SHADOW_FILE = os.path.join(FILE_SYSTEM, "etc", "shadow")
PERMISSIONS_FILE = os.path.join(FILE_SYSTEM, "etc", "permissions.json")

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

def create_system_config(hostname):
    config = {
        "os_name": "PyOS",
        "version": "0.1",
        "maintainer": "artur33",
        "default_shell": "bash",
        "default_editor": "nano",
        "timezone": "UTC",
        "locale": "en_US.UTF-8",
        "hostname": hostname,
        "first_boot": False,
        "installation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    print("\nCreating system configuration file...")
    with open(SYSTEM_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)

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
    source = "assets/bin"
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
    source = "assets/boot/kernel.py"
    destination_boot = os.path.join(FILE_SYSTEM, "boot", "kernel.py")
    if os.path.exists(source):
        shutil.copy(source, destination_boot)
        print("Done.\n")
        print("------------------------------")
    else:
        print("Kernel file not found. Please ensure it exists in the assets/boot directory.")
        print("Fatal error: Kernel setup failed")
        exit(1)

def create_permissions_file(username):
    print("\nCreating permissions file...")
    permissions = {
        "/": {"owner": "root"},
        "/root": {"owner": "root"},
        f"/home/{username}": {"owner": username},
        "/bin": {"owner": "root"},
        "/etc": {"owner": "root"},
    }

    with open(PERMISSIONS_FILE, 'w') as file:
        json.dump(permissions, file, indent=2)
    print("Permissions file created.")

def setup():
    print("\n------ First Boot Setup ------")
    print("\nRunning first boot setup...")

    create_file_structure()
    kernel_setup()
    hostname = input("\nEnter hostname for this system: ").strip() or "pyos"
    setup_root_user()
    username = setup_normal_user()
    create_system_config(hostname)
    default_commands()
    create_permissions_file(username)
    print("\nFirst boot setup complete. PyOS is ready to use!")
    time.sleep(5)
