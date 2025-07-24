# Command to show the current user.
# Usage: whoami
# Version: 1.0.0

import auth

def run(args, fs):
    print(auth.get_current_user())
