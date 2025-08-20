# Command to show the current date and time.
# Usage: date
# Version: 1.1.0

import json
from datetime import datetime, timezone, timedelta

def run(args, fs):
    try:
        config_path = fs.abs_path('/etc/system.conf')
        with open(config_path, 'r') as f:
            config = json.load(f)
        timezone_str = config.get('timezone', 'UTC')
        
    except Exception as e:
        timezone_str = 'UTC'

    tz = timezone.utc

    if isinstance(timezone_str, str):
        if timezone_str == 'UTC':
            tz = timezone.utc

        elif timezone_str.startswith('UTC+') or timezone_str.startswith('UTC-'):
            try:
                offset_str = timezone_str[3:]
                if offset_str.startswith('+'):
                    sign = 1
                    offset = int(offset_str[1:])

                elif offset_str.startswith('-'):
                    sign = -1
                    offset = int(offset_str[1:])

                else:
                    sign = 1
                    offset = 0

                tz = timezone(timedelta(hours=sign * offset))

            except Exception:
                tz = timezone.utc

    now = datetime.now(tz)
    print(now.strftime('%Y-%m-%d %H:%M:%S'))
