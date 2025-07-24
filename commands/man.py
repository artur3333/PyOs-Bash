# Command line utility to display manual pages.
# Usage: man <command>
# Version: 1.0.0

import os

def get_manual(command, fs):
    path = os.path.join(fs.ROOT_DIR, "bin", f"{command}.py")

    if not os.path.exists(path):
        return None
    
    try:
        with open(path, 'r') as file:
            text = file.readlines()
        
        description = ""
        usage = ""
        version = ""

        for line in text:
            line = line.strip()

            if line.startswith("# Command "):
                description = line[2:].strip()

            elif line.startswith("# Usage: "):
                usage = line[9:].strip()

            elif line.startswith("# Version: "):
                version = line[11:].strip()

            elif line and not line.startswith("#"):
                break

        return {"description": description, "usage": usage, "version": version}

    except Exception as e:
        print(f"Error reading manual for {command}: {e}")
        return None

    return None
    
def manual(command, content):
    print(f"\n{command.upper()}(1)                    User Commands                    {command.upper()}(1)")
    print("-" * 80)

    if content.get("description"):
        print("\nNAME")
        print(f"    {command} - {content['description']}")

    if content.get("usage"):
        print("\nSYNOPSIS")
        print(f"    {content['usage']}")

    if content.get("version"):
        print("\nVERSION")
        print(f"    {content['version']}")
    
    else:
        print(f"    {command} command")

    print(f"\nPyOS -> {command}\n")

def run(args, fs):
    if not args:
        print("Missing command argument.")
        return
    
    command = args[0].lower()

    content = get_manual(command, fs)

    if content:
        manual(command, content)
    
    else:
        print(f"No manual entry for '{command}'.")
