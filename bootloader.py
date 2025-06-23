import os
import time

FILE_SYSTEM = "fs"

def load_kernel():
    global kernel_path
    kernel_path = os.path.join(FILE_SYSTEM, "boot", "kernel.py")
    if not os.path.exists(kernel_path):
        raise FileNotFoundError(f"Kernel file not in /boot/")

if __name__ == "__main__":
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
            
        load_kernel()
        print("Kernel loaded successfully.")
        time.sleep(1)
        exec(open(kernel_path).read())

    except FileNotFoundError as e:
        print(e)
        print("Please ensure the kernel file is present in the /boot/ directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
