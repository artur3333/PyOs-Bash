# Command to show the current date and time.
# Usage: date
# Version: 1.0.0

import time

def run(args, fs):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(current_time)
