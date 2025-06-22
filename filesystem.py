import os
import state

def abs_path(path):
    new_path = os.path.abspath(os.path.join(state.current_dir, path))
    if new_path.startswith(state.ROOT_DIR):
        return new_path
    return state.current_dir

def change_directory(path):
    move = abs_path(path)
    if os.path.isdir(move):
        state.current_dir = move
    else:
        print("No such directory")

def prompt():
    now_path = state.current_dir.replace(state.ROOT_DIR, "~")
    return f"{now_path} $ "
