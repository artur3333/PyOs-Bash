# Command to switch user.
# Usage: su [<username>]
# Version: 1.0.0

import auth

def run(args, fs):
    if not args:
        print("No username provided.")
        return
    
    username = args[0]

    auth.switch_user(username)
