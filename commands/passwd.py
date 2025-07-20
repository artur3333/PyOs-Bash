# Command to change the password of the current user
# Usage: passwd [<username>]

import getpass
import auth

def run(args, fs):

    if args:
        username = args[0]
    else:
        username = auth.get_current_user()
    
    auth.change_password(username)
