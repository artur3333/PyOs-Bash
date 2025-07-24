# Command to download files from internet.
# Usage: wget [-O <output_file>, -P <directory>, -q] <url>
# Version: 1.0.0

import os
import sys
import urllib.parse
import urllib.request
import time
import auth

def print_progress_bar(progress, downloaded, speed, eta, bar_length=50):
    filled_length = int(bar_length * progress / 100)
    
    bar = '=' * filled_length + '>' + ' ' * (bar_length - filled_length)
    
    sys.stdout.write(f"\r{int(progress):>3}% [{bar}] {downloaded / 1024:.2f} KB at {speed:.2f} KB/s, ETA: {int(eta)}s")
    sys.stdout.flush()


def run(args, fs):
    if not args:
        print("Missing argument.")
        return
    
    url = args[-1]
    output_file = None
    output_dir = None
    quiet = False

    if '-O' in args:
        output_file = args[args.index('-O') + 1]
        args.remove('-O')
        args.remove(output_file)
    
    if '-P' in args:
        output_dir = args[args.index('-P') + 1]
        args.remove('-P')
        args.remove(output_dir)
    
    if '-q' in args:
        quiet = True
        args.remove('-q')
    
    if not url.startswith(('http://', 'https://')):
        print("Invalid URL. Must start with http:// or https://")
        return
    
    try:
        if not output_file:
            parsed_url = urllib.parse.urlparse(url)
            output_file = os.path.basename(parsed_url.path)
            if not output_file:
                output_file = "index.html"
        
        if output_dir:
            output_dir_abs = fs.abs_path(output_dir)
            if not os.path.exists(output_dir_abs):
                print(f"Directory '{output_dir}' does not exist.")
                return
            
            output_path = os.path.join(output_dir_abs, output_file)

        else:
            output_path = fs.abs_path(output_file)

        output_dir_check = os.path.dirname(output_path)
        if not auth.check_permissions(output_dir_check, action="write"):
            print(f"Permission denied: Cannot write to '{output_dir_check}'")
            return
        
        if not quiet:
            print(f"Downloading: {url}")
            print(f"Saving to: {fs.rel_path(output_path)}")

        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'PyOs-Wget/1.0')

        start_time = time.time()

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                file_size = response.headers.get('Content-Length')
                if file_size:
                    file_size = int(file_size)
                
                downloaded = 0
                chunk_size = 8192

                with open(output_path, 'wb') as file:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        
                        file.write(chunk)
                        downloaded += len(chunk)

                        if not quiet:
                            if file_size:
                                progress = (downloaded / file_size) * 100
                                elapsed = time.time() - start_time
                                speed = downloaded / elapsed / 1024
                                eta = 0
                                if downloaded:
                                    eta = (file_size - downloaded) / (downloaded / elapsed)
                                print_progress_bar(progress, downloaded, speed, eta)
                        
                        elif not quiet:
                            print(f"Downloaded {downloaded} bytes", end='')
                if not quiet:
                    print()
                
                end_time = time.time()
                total_time = end_time - start_time

                if not quiet:
                    print(f"\nDownload completed in {total_time:.2f} seconds")
                    if file_size:
                        speed = downloaded / total_time / 1024
                        print(f"Average speed: {speed:.2f} KB/s")
                    
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            return
        
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return
        
        except Exception as e:
            print(f"Download error: {e}")
            return

    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
        if os.path.exists(output_path):
            os.remove(output_path)
            print("Partial file removed.")

        return
    
    except Exception as e:
        print(f"Error: {e}")
        return
