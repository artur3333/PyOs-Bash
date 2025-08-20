import os
import time
import sys
from os_setup import setup

sys.dont_write_bytecode = True

if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)

else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_PATH)

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
        if os.environ.get("PYOS_RUNNING") == "1":
            sys.exit(0)
        
        os.environ["PYOS_RUNNING"] = "1"
        
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

        load_kernel()
        time.sleep(1)

        with open(kernel_path, 'r') as file:
            kernel_code = compile(file.read(), kernel_path, 'exec')
        
        kernel_globals = {"__file__": kernel_path, "__name__": "__main__"}

        exec(kernel_code, kernel_globals)

    except FileNotFoundError as e:
        print(e)
        print("Please ensure the kernel file is present in the /boot/ directory.")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
