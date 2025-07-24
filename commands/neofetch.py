# Command to display system information.
# Usage: neofetch
# Version: 1.0.0

import os
import platform
from datetime import datetime
import json
import cpuinfo
import psutil
import auth

def get_os_info():
    path = os.path.join("fs", "etc", "system.conf")
    if os.path.exists(path):
        with open(path, 'r') as file:
            config = json.load(file)
            return f"{config.get('os_name', 'PyOS')} {config.get('version', '0.1')}"
        
    return "Unknown"

def get_shell():
    path = os.path.join("fs", "etc", "system.conf")
    if os.path.exists(path):
        with open(path, 'r') as file:
            config = json.load(file)
            return config.get('default_shell', 'bash')
    
    return "Unknown"

def get_install_date():
    path = os.path.join("fs", "etc", "system.conf")
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)
            install_time = datetime.strptime(config['installation_date'], "%Y-%m-%d %H:%M:%S")
            uptime = datetime.now() - install_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m"

    return "Unknown"

def get_package_count(): # commands bin
    path = os.path.join("fs", "bin")
    if os.path.exists(path):
        return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
    
    return 0

def get_cpu_info():
    try:
        cpu = cpuinfo.get_cpu_info()

        if 'brand' in cpu:
            return cpu['brand']
        
        elif 'brand_raw' in cpu:
            return cpu['brand_raw']
        
        else:
            return "Unknown CPU"
        
    except Exception as e:
        return f"Error retrieving CPU info: {str(e)}"
    
def get_memory_info():
    try:
        total_memory = psutil.virtual_memory().total
        total_memory_gb = total_memory / (1024 ** 3) # convert

        return f"{total_memory_gb:.2f} GB"

    except Exception as e:
        return f"Error retrieving memory info: {str(e)}"
    
def get_uptime():
    return auth.get_uptime()
    
def run(args, fs):
    os_info = get_os_info()
    shell = get_shell()
    host = fs.hostname
    user = fs.current_user
    install_date = get_install_date()
    uptime = get_uptime()
    package_count = get_package_count()
    cpu_info = get_cpu_info()
    memory_info = get_memory_info()
    dash_count = len(user) + len(host) + 1

    ascii_art = r"""
_____________________________
      ___         ___  __    
     / _ \_   _  /___\/ _\   
    / /_)/ | | |//  //\ \    
   / ___/| |_| / \_// _\ \   
   \/     \__, \___/  \__/   
          |___/              
_____________________________
    """

    art_lines = ascii_art.strip().split('\n')

    info_lines = [
        f"\033[1;36m{user}@{host}\033[0m",
        f"{'-' * dash_count}",
        f"OS: {os_info}",
        f"Shell: {shell}",
        f"Kernel: Python {platform.python_version()}",
        f"Uptime: {uptime}",
        f"Installed: {install_date} ago",
        f"Packages: {package_count}",
        f"Terminal: PyOS Terminal",
        f"CPU: {cpu_info}",
        f"Total Memory: {memory_info}",
    ]

    max_lines = max(len(art_lines), len(info_lines))

    for i in range(max_lines):

        if i < len(art_lines):
            art = art_lines[i]
        else:
            art = ""
        
        if i < len(info_lines):
            info = info_lines[i]
        else:
            info = ""

        print(f"{art.ljust(30)}{info}")
