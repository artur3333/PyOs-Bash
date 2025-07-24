# Command to clear the terminal screen.
# Usage: clear
# Version: 1.0.0

import os

def run(args, fs):
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
