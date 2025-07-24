# Command to display system uptime.
# Usage: uptime
# Version: 1.0.0

import auth
import time

def run(args, fs):
    uptime = auth.get_uptime()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    print(f"{current_time} up {uptime}, {len(auth.get_loggedin_users())} user/s, load average: 0.00, 0.00, 0.00")
