import importlib
import state
from filesystem import abs_path, change_directory, prompt


if __name__ == "__main__":
    while True:
        try:
            command = input(prompt()).strip()
            if not command:
                continue
            
            if command == "exit":
                print("Exiting the shell.")
                break

            try:
                command = command.split()
                command_name = command[0]
                args = command[1:]
                command_module = importlib.import_module(f"commands.{command_name}")
                command_module.run(args, state.current_dir)
            except ModuleNotFoundError:
                print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            print("\nUse the 'exit' command to quit...")
