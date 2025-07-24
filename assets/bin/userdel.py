# Command to delete a user.
# Usage: userdel <username>
# Version: 1.0.0

import auth

def run(args, fs):
    if not auth.is_current_root():
        print("Permission denied: Only root can delete users.")
        return
    
    if len(args) < 1:
        print("Missing operand.")
        return
    
    username = args[0]
    
    if not username:
        print("Username cannot be empty.")
        return
    
    auth.delete_user(username)
