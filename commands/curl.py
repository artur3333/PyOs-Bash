# Command to transfer data from or to a server.
# Usage: curl [-X <method>, -H <header>, -d <data>, -o <output_file>, -i, -s] <url>
# Version: 1.0.0

import urllib.request

def run(args, fs):
    if not args:
        print("Missing argument.")
        return

    url = args[-1]
    method = 'GET'
    headers = {}
    data = None
    output_file = None
    include_headers = False
    silent = False

    if '-X' in args:
        method = args[args.index('-X') + 1].upper()
        args.remove('-X')
        args.remove(method)

    if '-H' in args:
        headers = {}
        while '-H' in args:
            i = args.index('-H')
            j = i + 1
            while j < len(args) and not args[j].startswith('-') and not args[j].startswith('http'):
                j += 1
            
            header_str = ' '.join(args[i+1:j]).strip('\'"')
            del args[i:j]
            
            if ':' not in header_str:
                print(f"Invalid header format: {header_str}")
                return
            
            key, value = map(str.strip, header_str.split(':', 1))
            if not key or not value:
                print(f"Invalid header key or value: {header_str}")
                return
            
            headers[key] = value

    if '-d' in args:
        data_arg = args[args.index('-d') + 1]
        args.remove('-d')
        args.remove(data_arg)
        data_arg = data_arg.strip('\'"')
        
        if data_arg.startswith('@'):
            with open(data_arg[1:], 'r') as f:
                data = f.read()

        else:
            data = data_arg
    
    if '-o' in args:
        output_file = args[args.index('-o') + 1]
        args.remove('-o')
        args.remove(output_file)
    
    if '-i' in args:
        include_headers = True
        args.remove('-i')
    
    if '-s' in args:
        silent = True
        args.remove('-s')
    
    if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
    
    try:
        if data:
            if isinstance(data, str):
                data = data.encode('utf-8')
        
        request = urllib.request.Request(url, data=data, method=method)

        headers.setdefault('User-Agent', 'curl/8.15.0')
        headers.setdefault('Accept', '*/*')

        for key, value in headers.items():
            request.add_header(key, value)
        
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status_code = response.getcode()
                response_headers = response.getheaders()

                if output_file:
                    output_path = fs.abs_path(output_file)
                    with open(output_path, 'wb') as file:
                        if include_headers:
                            file.write(f"HTTP/1.1 {status_code} {response.reason}\n".encode())
                            
                            for h, v in response_headers:
                                file.write(f"{h}: {v}\n".encode())
                            file.write(b'\n')

                        while True:
                            chunk = response.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)

                    if not silent:
                        print(f"Saved to: {fs.rel_path(output_path)}")

                else:
                    if include_headers:
                        print(f"HTTP/1.1 {status_code} {response.reason}")
                        for h, v in response_headers:
                            print(f"{h}: {v}")

                        print()

                    while True:
                        chunk = response.read(1)
                        if not chunk:
                            break

                        print(chunk.decode('utf-8', errors='ignore'), end='', flush=True)

            print()

        except urllib.error.HTTPError as e:
            if not silent:
                print(f"HTTP Error: {e.code} - {e.reason}")
                
            if include_headers:
                print(f"HTTP/1.1 {e.code} {e.reason}")
                for header, value in e.headers.items():
                    print(f"{header}: {value}")
            return
        
        except urllib.error.URLError as e:
            if not silent:
                print(f"URL Error: {e.reason}")
            return
    
    except KeyboardInterrupt:
        if not silent:
            print("\nOperation cancelled by user.")
    
    except Exception as e:
        if not silent:
            print(f"Error: {str(e)}")
