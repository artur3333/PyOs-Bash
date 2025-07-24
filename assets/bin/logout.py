# Command to log out of the current session.
# Usage: logout
# Version: 1.0.0

import auth

def run(args, fs):
    auth.logout()

    print("\nYou have been logged out successfully.\n")
