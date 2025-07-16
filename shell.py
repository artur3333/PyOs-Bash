import importlib
from filesystem import FileSystem
import auth

fs = FileSystem()

def shell():
    while True:
        try:
            if not auth.get_current_user():
                if auth.login():
                    continue

            command = input(fs.prompt()).strip()
            if not command:
                continue
            
            if command == "exit":
                print("Exiting the shell.")
                auth.logout()
                break

            try:
                command = command.split()
                command_name = command[0]
                args = command[1:]
                command_module = importlib.import_module(f"fs.bin.{command_name}")

                if not check_module_permissions(command_module):
                    print(f"Permission denied: {command_name}")
                    continue

                command_module.run(args, fs)
                
            except ModuleNotFoundError:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nUse the 'exit' command to quit...")

def check_module_permissions(module):
    if auth.is_current_root():
        return True
    
    root_commands = {
        'useradd', 'userdel'
    }

    user_commands = {
        'cd', 'ls', 'find', 'tree', 'cat', 'echo', 'mkdir',
        'rmdir', 'rm', 'cp', 'mv', 'touch', 'clear', 'logout',
        'whoami', 'pwd', 'who', "sudo", 'passwd', 'neofetch',
        'nano', 'uptime', 'su', 'last', 'ps', 'date'
    }

    if module.__name__.split('.')[-1] in root_commands:
        return False
    
    if module.__name__.split('.')[-1] in user_commands:
        return True
    
