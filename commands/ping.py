# Command to ping a host
# Usage: ping [-c <count>] <hostname>

import socket
import time
from ping3 import ping

def run(args, fs):
    if not args:
        print("Missing argument")
        return
    
    count = 4 # default ping count

    if '-c' in args:
        count_index = args.index('-c') + 1
        count = int(args[count_index])
        args.pop(count_index)
        args.remove('-c')

    hostname = args[0]

    print(f"PING {hostname}")

    try:
        ip = socket.gethostbyname(hostname)
        print(f"Pinging {ip} ({hostname})")

    except socket.gaierror:
        print(f"cannot resolve {hostname}: Unknown host")
        return
    
    success_count = 0
    total_time = 0
    min_time = float('inf')
    max_time = 0

    for i in range(count):
        try:
            result = ping(ip, timeout=3) # 3 seconds timeout

            if result is not None:
                ping_time = result * 1000
                print(f"Reply from {ip}: time={ping_time:.1f}ms")
                success_count += 1
                total_time += ping_time
                min_time = min(min_time, ping_time)
                max_time = max(max_time, ping_time)

            else:
                print(f"Request timeout for {ip}")
        
        except Exception as e:
            print(f"Ping error: {e}")

        if i < count - 1:
            time.sleep(1)
    
    print(f"\n--- {hostname} ping statistics ---")
    print(f"{count} packets transmitted, {success_count} received, {(count - success_count)} packet lost ({((count - success_count) / count) * 100:.1f}% loss)")

    if success_count > 0:
        avg_time = total_time / success_count
        print(f"Approximate round trip times (min/max/avg): {min_time:.1f}ms / {max_time:.1f}ms / {avg_time:.1f}ms")
