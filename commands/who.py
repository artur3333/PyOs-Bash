# Command to list all users
# Usage: who

import auth

def run(args, fs):
    auth.list_users()
