# Command to read and display the contents of a file
# Usage: cat <filename>

def run(args, fs):
    if not args:
        print("No file specified.")
        return
    
    path = fs.abs_path(args[0])
    try:
        with open(path) as file:
            print(file.read())

    except FileNotFoundError:
        print("File not found.")
        return
    