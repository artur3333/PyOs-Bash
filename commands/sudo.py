# Command to run a command with elevated privileges.
# Usage: sudo <command> [args...]
# Version: 1.0.0

import importlib
import auth
import getpass

def run(args, fs):
    if not args:
        print("Missing operand.")
        return

    command_name = args[0]
    command_args = args[1:]

    if not auth.is_current_root():
        password = getpass.getpass("[sudo] password for root: ")

        if not auth.verify_password("root", password):
            print("Incorrect password.")
            return
        
    original_user = auth.get_current_user()
    original_uid = auth.get_current_uid()
    original_is_root = auth.is_current_root()

    auth.sudo_override_root(True)

    try:
        command_name = args[0]
        command_args = args[1:]
        command_module = importlib.import_module(f"assets.bin.{command_name}")
        command_module.run(command_args, fs)

    except ModuleNotFoundError:
        print(f"Unknown command: {args[0]}")

    finally:
        auth.sudo_override_root(False, original_user, original_uid, original_is_root)
