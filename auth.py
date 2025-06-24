import os
import json
import hashlib
import getpass
import shutil
import time

FILE_SYSTEM = "fs"
ROOT_DIR = os.path.abspath(FILE_SYSTEM)
PASSWD_FILE = os.path.join(ROOT_DIR, "etc", "passwd")
SHADOW_FILE = os.path.join(ROOT_DIR, "etc", "shadow")
PERMISSIONS_FILE = os.path.join(ROOT_DIR, "etc", "permissions.json")
SESSIONS_FILE = os.path.join(ROOT_DIR, "var", "sessions.json")

current_user = None
current_uid = None
is_root = False


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def rel_path(path=None):
    if path is None:
        return "/"

    rel = path.replace(ROOT_DIR, "").replace('\\', '/')
    if not rel:
        return "/"
    
    if not rel.startswith('/'):
        rel = '/' + rel

    return rel


def load_users():
    users = {}
    if os.path.exists(PASSWD_FILE):
        with open(PASSWD_FILE, 'r') as file:
            for line in file:
                line = line.strip().split(':')
                if len(line) >= 6:
                    username = line[0]
                    uid = int(line[2])
                    home = line[5]
                    users[username] = {
                        'uid': uid,
                        'home': home
                    }

    return users


def load_passwords():
    passwords = {}
    if os.path.exists(SHADOW_FILE):
        with open(SHADOW_FILE, 'r') as file:
            for line in file:
                line = line.strip().split(':')
                if len(line) >= 2:
                    username = line[0]
                    password_hash = line[1]
                    passwords[username] = password_hash

    return passwords


def verify_password(username, password):
    passwords = load_passwords()

    if username in passwords:
        return passwords[username] == hash_password(password)
    
    return False


def log_session(username, action):
    sessions = {}
    
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'r') as file:
            sessions = json.load(file)
    
    if username not in sessions:
        sessions[username] = []
    
    session_entry = {
        'username': username,
        'action': action,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    sessions[username].append(session_entry)
    
    with open(SESSIONS_FILE, 'w') as file:
        json.dump(sessions, file, indent=2)


def login():
    global current_user, current_uid, is_root

    users = load_users()

    username = input("Username: ").strip()
    
    if username not in users:
        print("User not found.")
        return False
    
    password = getpass.getpass("Password: ")
    
    if not verify_password(username, password):
        print("Invalid password.")
        return False
    
    current_user = username
    current_uid = users[username]['uid']
    is_root = (current_uid == 0)

    log_session(username, "login")

    print(f"\nWelcome, {current_user}!\n")

    return True


def logout():
    global current_user, current_uid, is_root

    if current_user is None:
        print("No user is currently logged in.")
        return False
    
    if current_user:
        log_session(current_user, "logout")
        
        print(f"Goodbye, {current_user}!")

    current_user = None
    current_uid = None
    is_root = False


'''def switch_user(username): #TODO: 'su' command
    global current_user, current_uid, is_root

    if current_user is None:
        print("No user is currently logged in.")
        return False
    
    users = load_users()
    if username not in users:
        print("User not found.")
        return False
    
    current_user = username
    current_uid = users[username]['uid']
    is_root = (current_uid == 0)

    log_session(username, "switch_user")
    print(f"Switched to user {username}.")

    return True'''


def create_user(username, password):
    users = load_users()
    if username in users:
        print("User already exists.")
        return False
    
    next_uid = 1000
    for user_data in users.values():
        if user_data['uid'] >= next_uid:
            next_uid = user_data['uid'] + 1
    
    home_directory = f"/home/{username}"

    home_path = os.path.join(FILE_SYSTEM, home_directory.lstrip('/'))
    os.makedirs(home_path, exist_ok=True)

    with open(PASSWD_FILE, 'a') as passwd_file:
        passwd_file.write(f"{username}:x:{next_uid}:{next_uid}:{username} user:{home_path}:/bin/bash\n")
    
    password_hash = hash_password(password)
    with open(SHADOW_FILE, 'a') as shadow_file:
        shadow_file.write(f"{username}:{password_hash}:0:99999:7:::\n")

    update_permissions(home_directory, username)

    print(f"User '{username}' created successfully.")

    return True


def delete_user(username):
    if username == "root":
        print("Cannot delete the root user.")
        return False
    
    if username == current_user:
        print("Cannot delete the currently logged-in user.")
        return False
    
    users = load_users()
    if username not in users:
        print("User not found.")
        return False
    
    new = []
    with open(PASSWD_FILE, 'r') as passwd_file:
        for line in passwd_file:
            if not line.startswith(username + ":"):
                new.append(line)

    with open(PASSWD_FILE, 'w') as passwd_file:
        passwd_file.writelines(new)
    
    new = []
    with open(SHADOW_FILE, 'r') as shadow_file:
        for line in shadow_file:
            if not line.startswith(username + ":"):
                new.append(line)
    
    with open(SHADOW_FILE, 'w') as shadow_file:
        shadow_file.writelines(new)
    
    home_path = users[username]['home']
    if os.path.exists(home_path):
        shutil.rmtree(home_path)
        print(f"Home directory '{home_path}' deleted.")
    
    with open(PERMISSIONS_FILE, 'r') as perm_file:
        permissions = json.load(perm_file)

    home_virtual_path = rel_path(home_path)
    updated_permissions = {}

    for path, info in permissions.items():
        owner = info.get('owner', "")

        if owner != username and not path.startswith(home_virtual_path):
            updated_permissions[path] = info

    with open(PERMISSIONS_FILE, 'w') as perm_file:
        json.dump(updated_permissions, perm_file, indent=2)
            
    print(f"User '{username}' deleted successfully.")

    return True


def change_password(username = None):
    if username is None:
        username = current_user
    
    if username != current_user and not is_root:
        print("You can only change your own password.")
        return False
    
    if username == current_user and not is_root:
        old_password = getpass.getpass("Old Password: ")
        
        if not verify_password(username, old_password):
            print("Invalid old password.")
            return False
    
    new_password = getpass.getpass("New Password: ")
    confirm_password = getpass.getpass("Confirm New Password: ")

    if new_password != confirm_password:
        print("Passwords do not match.")
        return False
    
    new = []
    pass_hash = hash_password(new_password)

    with open(SHADOW_FILE, 'r') as shadow_file:
        for line in shadow_file:
            if line.startswith(username + ":"):
                parts = line.strip().split(':')
                parts[1] = pass_hash
                new.append(':'.join(parts) + '\n')

            else:
                new.append(line)
    
    with open(SHADOW_FILE, 'w') as shadow_file:
        shadow_file.writelines(new)

    print(f"Password for user '{username}' changed successfully.")

    return True


def update_permissions(path, owner):
    permissions = {}
    
    if os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, 'r') as file:
            permissions = json.load(file)
    
    permissions[path] = {
        'owner': owner,
        'access': 'private'
    }

    with open(PERMISSIONS_FILE, 'w') as file:
        json.dump(permissions, file, indent=2)


def check_permissions(path, action=None): # TODO: Implement action-based permissions
    if is_root:
        return True

    virtual_path = rel_path(path)

    with open(PERMISSIONS_FILE, 'r') as file:
        permissions = json.load(file)

    current_path = virtual_path
    while True:
        if current_path in permissions:
            rule = permissions[current_path]
            owner = rule.get("owner")
            access = rule.get("access", "owner-only")

            if owner == current_user:
                return True

            if access == "public":
                return True

            return False

        parent = os.path.dirname(current_path)

        if parent == current_path:
            break

        current_path = parent

    return False


def sudo_override_root(enable, original_user=None, original_uid=None, original_is_root=None):
    global current_user, current_uid, is_root

    if enable:
        current_user = "root"
        current_uid = 0
        is_root = True

    else:
        current_user = original_user
        current_uid = original_uid
        is_root = original_is_root


def list_users():
    users = load_users()

    if not users:
        print("No users found.")
        return
    
    print("Users:")

    for username, data in users.items():
        print(f" - {username} (UID: {data['uid']}, Home: {rel_path(data['home'])})")

    print("\nTotal Users:", len(users))


def get_current_user():
    return current_user


def get_current_uid():
    return current_uid


def is_current_root():
    return is_root
