# Command to log out of the current session
# Usage: logout

import auth

def run(args, fs):
    auth.logout()

    print("\nYou have been logged out successfully.\n")
