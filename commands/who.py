# Command to list all users.
# Usage: who
# Version: 1.0.0

import auth

def run(args, fs):
    auth.list_users()
