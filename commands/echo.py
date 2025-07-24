# Command to echo text to the console or write it to a file.
# Usage: echo [text] > <filename>
# Version: 1.0.0

def run(args, fs):
    if ">" in args:
        index = args.index(">")
        text = " ".join(args[:index])
        filename = fs.abs_path(args[index + 1])
        try:
            with open(filename, 'w') as file:
                file.write(text)

        except Exception as e:
            print(f"Error")
            
    else:
        print(" ".join(args))
