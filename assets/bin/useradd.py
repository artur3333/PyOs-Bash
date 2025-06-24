# Command to add a new user
# Usage: useradd <username>

import getpass
import auth

def run(args, fs):
    if not auth.is_current_root():
        print("Permission denied: Only root can add users.")
        return

    if len(args) < 1:
        print("Missing operand.")
        return

    username = args[0]
    
    if not username:
        print("Username cannot be empty.")
        return
    
    password = getpass.getpass("Enter password for new user: ")
    confirm_password = getpass.getpass("Confirm password: ")
    if password != confirm_password:
        print("Passwords do not match. User not added.")
        return
        
    else:
        confirm_password = password
    
    if not confirm_password:
        print("Password cannot be empty. User not added.")
        return
    
    auth.create_user(username, password)

