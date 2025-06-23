import time
import sys
import os
from shell import shell

def progress_bar():
    bar_length = 10
    for i in range(bar_length):
        time.sleep(0.1)
        filled_length = int(bar_length * (i + 1) / bar_length)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f'\r[{bar}] {i + 1}/{bar_length}')
        sys.stdout.flush()
    print()

def display_ascii_art():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    art = """
       ___         ___  __    
      / _ \_   _  /___\/ _\   
     / /_)/ | | |//  //\ \    
    / ___/| |_| / \_// _\ \   
    \/     \__, \___/  \__/   
           |___/              
    """
    print(f"\033[1;36m{art}\033[0m")

def boot():
    display_ascii_art()
    print("\033[1;32mWelcome to PyOS...\033[0m")
    print("Initializing, please wait...")
    
    progress_bar()
    
    print("\033[1;32mPyOS Booted Successfully!\033[0m")
    time.sleep(0.5)

if __name__ == "__main__":
    boot()
    shell()
