# Command to open a text editor very (not) similar to nano.
# Usage: nano <filename>
# Version: 1.0.0

import os
import sys
import auth
import shutil

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def get_terminal_size():
    size = shutil.get_terminal_size(fallback=(24, 80))
    return size.lines, size.columns

def draw_editor(content, cursor_y, cursor_x, filename, status_msg="", scroll_offset=0, h_scroll_offset=0):
    clear_screen()

    terminal_height, terminal_width = get_terminal_size()
    content_height = terminal_height - 6

    line_num_width = max(3, len(str(len(content))))
    content_width = terminal_width - line_num_width - 2

    print(f"--- PyNano: {filename} ---")
    print("Ctrl+O = Save | Ctrl+X = Exit | Arrow keys = Navigate")
    print("-" * terminal_width)
    
    start_line = scroll_offset
    end_line = min(start_line + content_height, len(content))
    
    for i in range(start_line, end_line):
        line = content[i] if i < len(content) else ""
        line_num = i+1

        if len(line) > h_scroll_offset:
            visible_line = line[h_scroll_offset:h_scroll_offset + content_width]

        else:
            visible_line = ""

        if i == cursor_y:
            relative_cursor_x = cursor_x - h_scroll_offset
            if 0 <= relative_cursor_x <= len(visible_line):
                line_display = visible_line[:relative_cursor_x] + "█" + visible_line[relative_cursor_x:]

            else:
                line_display = visible_line

        else:
            line_display = visible_line
        
        what_display = f"{line_num:>{line_num_width}}: {line_display}"
        print(what_display[:terminal_width])
    
    remaining_lines = content_height - (end_line - start_line)
    for i in range(remaining_lines):
        empty = " " * (line_num_width + 2)
        print(empty[:terminal_width])
    
    print("-" * terminal_width)
    if status_msg:
        print(status_msg)

    else:
        print(f"Line {cursor_y+1}, Column {cursor_x+1}")

def get_input():
    try:
        if os.name == 'nt':
            import msvcrt
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch()

                    if key == b'\xe0' or key == b'\x00':

                        if msvcrt.kbhit():
                            special = msvcrt.getch()
                            if special == b'H': # Up
                                return 'UP'
                            
                            elif special == b'P': # Down
                                return 'DOWN'
                            
                            elif special == b'M': # Right
                                return 'RIGHT'
                            
                            elif special == b'K': # Left
                                return 'LEFT'
                            
                    else:
                        return key.decode('utf-8', errors='ignore')

        else:
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                key = sys.stdin.read(1)
                
                if key == '\x1b':
                    seq = sys.stdin.read(2)
                    if seq == '[A':
                        return 'UP'
                    elif seq == '[B':
                        return 'DOWN'
                    elif seq == '[C':
                        return 'RIGHT'
                    elif seq == '[D':
                        return 'LEFT'
                    else:
                        return 'ESC'
                else:
                    return key
                
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except:
        return input("Enter command (or type text): ")

def save_file(content, file_path):
    try:
        if not auth.check_permissions(file_path, action="write"):
            return False, "Permission denied."
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))

        return True, "File saved successfully."
    
    except Exception as e:
        return False, f"Error saving file: {str(e)}"
    
def calc_scroll_offset(cursor_y, scroll_offset, content_height):
    if cursor_y < scroll_offset:
        return cursor_y
    
    elif cursor_y >= scroll_offset + content_height:
        return cursor_y - content_height + 1
    
    return scroll_offset

def calc_h_scroll_offset(cursor_x, h_scroll_offset, content_width):
    if cursor_x < h_scroll_offset:
        return cursor_x
    
    elif cursor_x >= h_scroll_offset + content_width:
        return cursor_x - content_width + 1
    
    return h_scroll_offset

def run(args, fs):
    if not args:
        print("Missing filename argument.")
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
    scroll_offset = 0
    h_scroll_offset = 0
    modified = False
    status_msg = ""

    terminal_height, terminal_width = get_terminal_size()
    content_height = terminal_height - 6
    line_num_width = max(3, len(str(len(content))))
    content_width = terminal_width - line_num_width - 2
    
    while True:
        terminal_height, terminal_width = get_terminal_size()
        content_height = terminal_height - 6
        line_num_width = max(3, len(str(len(content))))
        content_width = terminal_width - line_num_width - 2

        if cursor_y >= len(content):
            cursor_y = len(content) - 1
        if cursor_y < 0:
            cursor_y = 0
        if cursor_x > len(content[cursor_y]):
            cursor_x = len(content[cursor_y])
        if cursor_x < 0:
            cursor_x = 0

        scroll_offset = calc_scroll_offset(cursor_y, scroll_offset, content_height)
        h_scroll_offset = calc_h_scroll_offset(cursor_x, h_scroll_offset, content_width)
        
        draw_editor(content, cursor_y, cursor_x, filename, status_msg, scroll_offset, h_scroll_offset)
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

            if key == 'UP':
                if cursor_y > 0:
                    cursor_y -= 1
                    cursor_x = min(cursor_x, len(content[cursor_y]))
                
            elif key == 'DOWN':
                if cursor_y < len(content) - 1:
                    cursor_y += 1
                    cursor_x = min(cursor_x, len(content[cursor_y]))
                    
            elif key == 'LEFT':
                if cursor_x > 0:
                    cursor_x -= 1
                elif cursor_y > 0:
                    cursor_y -= 1
                    cursor_x = len(content[cursor_y])
                
            elif key == 'RIGHT':
                if cursor_x < len(content[cursor_y]):
                    cursor_x += 1
                elif cursor_y < len(content) - 1:
                    cursor_y += 1
                    cursor_x = 0
            
            # Action keys
            elif ord(key) == 24: # Ctrl+X
                if modified:
                    choice = input("File has been modified. Save before exit? (y/n/cancel): ").strip().lower()

                    if choice == 'y':
                        success, msg = save_file(content, file_path)
                        print(msg)
                        if success:
                            break
                        
                    elif choice == 'cancel':
                        continue

                    elif choice == 'n':
                        break
                else:
                    break
            
            elif ord(key) == 15: # Ctrl+O
                success, msg = save_file(content, file_path)
                status_msg = msg
                if success:
                    modified = False
            
            elif ord(key) == 13 or ord(key) == 10: # Enter
                current_line = content[cursor_y]
                new_line = current_line[cursor_x:]
                content[cursor_y] = current_line[:cursor_x]
                content.insert(cursor_y + 1, new_line)
                cursor_y += 1
                cursor_x = 0
                modified = True
            
            elif ord(key) == 8 or ord(key) == 127: # Backspace
                if cursor_x > 0:
                    line = content[cursor_y]
                    content[cursor_y] = line[:cursor_x-1] + line[cursor_x:]
                    cursor_x -= 1
                    modified = True

                elif cursor_y > 0:
                    cursor_x = len(content[cursor_y - 1])
                    content[cursor_y - 1] += content[cursor_y]
                    content.pop(cursor_y)
                    cursor_y -= 1
                    modified = True
            
            elif ord(key) == 9: # Tab
                line = content[cursor_y]
                content[cursor_y] = line[:cursor_x] + "    " + line[cursor_x:]
                cursor_x += 4
                modified = True

            elif ord(key) >= 32 and ord(key) <= 126: # Other
                line = content[cursor_y]
                content[cursor_y] = line[:cursor_x] + key + line[cursor_x:]
                cursor_x += 1
                modified = True

            else:
                status_msg = f"Unknown key: {ord(key)}"
        
        except KeyboardInterrupt:
            print("\nUse Ctrl+X to exit")
            status_msg = "Use Ctrl+X to exit"

        except Exception as e:
            status_msg = f"Error: {str(e)}"
    
    clear_screen()
