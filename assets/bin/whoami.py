# Command to show the current user
# Usage: whoami

import auth

def run(args, fs):
    print(auth.get_current_user())
