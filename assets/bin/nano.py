# Text editor very (not) similar to nano.
# Usage: nano <filename>

import os
import sys
import auth

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def draw_editor(content, cursor_y, cursor_x, filename, status_msg=""):
    clear_screen()
    print(f"--- PyNano: {filename} ---")
    print("Ctrl+S = Save | Ctrl+X = Exit | ESC = Cancel")
    print("-" * 50)
    
    for i, line in enumerate(content):
        if i == cursor_y:
            display_line = line[:cursor_x] + "|" + line[cursor_x:]
            print(f"{i+1:3}: {display_line}")

        else:
            print(f"{i+1:3}: {line}")
    
    if cursor_y >= len(content):
        print(f"{cursor_y+1:3}: |")
    
    print("-" * 50)
    if status_msg:
        print(status_msg)

    else:
        print(f"Line {cursor_y+1}, Column {cursor_x+1}")

def get_input():
    try:
        if os.name == 'nt':
            import msvcrt
            return msvcrt.getch().decode('utf-8', errors='ignore')
        
        else:
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                return ch
            
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except:
        return input("Enter command (or type text): ")

def handle_special_keys():
    try:
        if os.name == 'nt':
            import msvcrt
            if msvcrt.kbhit():
                next_char = msvcrt.getch()

                if next_char in (b'\x00', b'\xe0'): # Special

                    if msvcrt.kbhit():
                        arrow_key = msvcrt.getch()
                        if arrow_key == b'H': # Up
                            return 'UP'
                        
                        elif arrow_key == b'P': # Down
                            return 'DOWN'
                        
                        elif arrow_key == b'M': # Right
                            return 'RIGHT'
                        
                        elif arrow_key == b'K': # Left
                            return 'LEFT'
        else:
            import termios, tty, select
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    next_char = sys.stdin.read(1)

                    if next_char == '[':
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            arrow_key = sys.stdin.read(1)

                            if arrow_key == 'A':
                                return 'UP'
                            
                            elif arrow_key == 'B':
                                return 'DOWN'
                            
                            elif arrow_key == 'C':
                                return 'RIGHT'
                            
                            elif arrow_key == 'D':
                                return 'LEFT'
                            
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except:
        pass
    
    return None

def save_file(content, file_path):
    try:
        if not auth.check_permissions(file_path, action="write"):
            return False, "Permission denied."
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))

        return True, "File saved successfully."
    
    except Exception as e:
        return False, f"Error saving file: {str(e)}"

def run(args, fs):
    if not args:
        print("Missing operand.")
        return
    
    filename = args[0]
    file_path = fs.abs_path(filename)
    
    if os.path.exists(file_path):
        if not auth.check_permissions(file_path, action="read"):
            print("Permission denied: cannot read file.")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().splitlines()

        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        content = [""]
    
    if not content:
        content = [""]
    
    cursor_y = 0
    cursor_x = 0
    status_msg = ""
    
    while True:
        if cursor_y >= len(content):
            cursor_y = len(content) - 1
        if cursor_y < 0:
            cursor_y = 0
        if cursor_x > len(content[cursor_y]):
            cursor_x = len(content[cursor_y])
        if cursor_x < 0:
            cursor_x = 0
        
        draw_editor(content, cursor_y, cursor_x, filename, status_msg)
        status_msg = ""
        
        try:
            key = get_input()
            
            if not key or len(key) == 0:
                continue
            
            if len(key) > 1:
                if key.lower() == 'exit' or key.lower() == 'quit':
                    break

                elif key.lower().startswith('save'):
                    success, msg = save_file(content, file_path)
                    status_msg = msg
                    continue

                else:
                    for char in key:
                        line = content[cursor_y]
                        content[cursor_y] = line[:cursor_x] + char + line[cursor_x:]
                        cursor_x += 1
                    continue
            
            # Action keys
            if ord(key) == 24: # Ctrl+X
                choice = input("\nSave before exit? (y/n): ").strip().lower()
                if choice == 'y' or choice == 'yes':
                    success, msg = save_file(content, file_path)
                    print(msg)
                break
            
            elif ord(key) == 19: # Ctrl+S
                success, msg = save_file(content, file_path)
                status_msg = msg
            
            elif ord(key) == 27: # ESC
                next_key = handle_special_keys()
                if next_key == 'UP' and cursor_y > 0:
                    cursor_y -= 1
                    cursor_x = min(cursor_x, len(content[cursor_y]))

                elif next_key == 'DOWN' and cursor_y < len(content) - 1:
                    cursor_y += 1
                    cursor_x = min(cursor_x, len(content[cursor_y]))

                elif next_key == 'LEFT' and cursor_x > 0:
                    cursor_x -= 1

                elif next_key == 'RIGHT' and cursor_x < len(content[cursor_y]):
                    cursor_x += 1

                else:
                    status_msg = "ESC pressed - use Ctrl+X to exit"
            
            elif ord(key) == 13 or ord(key) == 10: # Enter
                current_line = content[cursor_y]
                new_line = current_line[cursor_x:]
                content[cursor_y] = current_line[:cursor_x]
                content.insert(cursor_y + 1, new_line)
                cursor_y += 1
                cursor_x = 0
            
            elif ord(key) == 8 or ord(key) == 127: # Backspace
                if cursor_x > 0:
                    line = content[cursor_y]
                    content[cursor_y] = line[:cursor_x-1] + line[cursor_x:]
                    cursor_x -= 1

                elif cursor_y > 0:
                    cursor_x = len(content[cursor_y - 1])
                    content[cursor_y - 1] += content[cursor_y]
                    content.pop(cursor_y)
                    cursor_y -= 1
            
            elif ord(key) == 9: # Tab
                line = content[cursor_y]
                content[cursor_y] = line[:cursor_x] + "    " + line[cursor_x:]
                cursor_x += 4
            
            elif ord(key) >= 32 and ord(key) <= 126: # Other
                line = content[cursor_y]
                content[cursor_y] = line[:cursor_x] + key + line[cursor_x:]
                cursor_x += 1
            
            else:
                status_msg = f"Unknown key: {ord(key)}"
        
        except KeyboardInterrupt:
            choice = input("\nExit? (y/n): ").strip().lower()
            if choice == 'y' or choice == 'yes':
                break

        except Exception as e:
            status_msg = f"Error: {str(e)}"
    
    clear_screen()
