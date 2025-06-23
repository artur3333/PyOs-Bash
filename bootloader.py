import os
import time
import sys
from os_setup import setup

sys.dont_write_bytecode = True

FILE_SYSTEM = "fs"

def load_kernel():
    global kernel_path
    kernel_path = os.path.join(FILE_SYSTEM, "boot", "kernel.py")
    if not os.path.exists(FILE_SYSTEM):
        print(f"File System does not exist. Running setup...")
        setup()

    if not os.path.exists(kernel_path):
        raise FileNotFoundError(f"Kernel file not found at /boot/. Please ensure it exists in the /boot/ directory.")
    
    print("Kernel loaded successfully.")

if __name__ == "__main__":
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

        load_kernel()
        time.sleep(1)
        exec(open(kernel_path).read())

    except FileNotFoundError as e:
        print(e)
        print("Please ensure the kernel file is present in the /boot/ directory.")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
