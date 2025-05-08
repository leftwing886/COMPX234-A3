import socket
import sys

def process_request(line):
    """Parse a request line and return protocol message or None if invalid."""
    parts = line.strip().split(' ', 2)
    if not parts:
        return None
    cmd = parts[0].upper()
    if cmd not in {'READ', 'GET', 'PUT'}:
        print(f"Invalid command in line: '{line.strip()}'")
        return None

    if cmd in {'READ', 'GET'} and len(parts) == 2:
        key = parts[1]
        if len(key) > 999:
            print(f"Key too long: '{key}'")
            return None
        msg = f"{len(f'R {key}'):03d} R {key}" if cmd == 'READ' else f"{len(f'G {key}'):03d} G {key}"
        return cmd, key, '', msg
    elif cmd == 'PUT' and len(parts) == 3:
        key, value = parts[1], parts[2]
        if len(key) > 999 or len(value) > 999:
            print(f"Key or value too long: key='{key}', value='{value}'")
            return None
        combined = f"{key} {value}"
        if len(combined) > 970:
            print(f"Combined key and value size exceeds 970 characters for '{line}'")
            return None
        msg = f"{len(f'P {key} {value}'):03d} P {key} {value}"
        return cmd, key, value, msg
    print(f"Invalid request format: '{line.strip()}'")
    return None

def process_file(hostname, port, request_file):
    """Process a single request file."""
    try:
        with open(request_file, 'r', encoding='utf-8') as f:
            requests = f.readlines()
    except Exception as e:
        print(f"Error reading request file {request_file}: {e}")
        return False

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((hostname, port))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return False

    try:
        for line in requests:
            line = line.strip()
            if not line:
                continue
            request = process_request(line)
            if not request:
                print(f"Skipping invalid request in {request_file}: '{line}'")
                continue

            cmd, key, value, msg = request
            print(f"Sending: '{msg}'")
            client.send(msg.encode('utf-8'))
            response = client.recv(999).decode('utf-8').strip()
            print(f"Response: '{response}'")
            if cmd == 'PUT':
                print(f"PUT {key} {value} ({request_file}): {response[4:]}")
            elif cmd == 'READ':
                print(f"READ {key} ({request_file}): {response[4:]}")
            elif cmd == 'GET':
                print(f"GET {key} ({request_file}): {response[4:]}")
    except Exception as e:
        print(f"Error during communication for {request_file}: {e}")
        return False
    finally:
        client.close()
    return True

def main():
    if len(sys.argv) != 4:
        print("Usage: python client.py <hostname> <port> <request_file>")
        sys.exit(1)

    hostname, port, request_file = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    if not (50000 <= port <= 59999):
        print("Port must be between 50000 and 59999")
        sys.exit(1)

    process_file(hostname, port, request_file)

if __name__ == "__main__":
    main()
