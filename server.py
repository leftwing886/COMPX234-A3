import socket
import threading
import time
from tuple_space import TupleSpace
from protocol import encode_response, decode_request

def handle_client(client_socket, addr, tuple_space):
    tuple_space.increment_client()
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            command, key, value = decode_request(data)
            if command == "R":
                success, result = tuple_space.read(key)
                response = encode_response(success, key, result, "READ")
            elif command == "G":
                success, result = tuple_space.get(key)
                response = encode_response(success, key, result, "GET")
            elif command == "P":
                success = tuple_space.put(key, value)
                response = encode_response(success, key, value, "PUT")
            client_socket.send(response.encode())
    finally:
        client_socket.close()

def print_stats(tuple_space):
    while True:
        stats = tuple_space.stats()
        print(f"Tuple Space Stats: {stats}")
        time.sleep(10)

def main(port):
    tuple_space = TupleSpace()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"Server listening on port {port}")

    stats_thread = threading.Thread(target=print_stats, args=(tuple_space,), daemon=True)
    stats_thread.start()

    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, addr, tuple_space)
            )
            client_thread.start()
    finally:
        server_socket.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    if not (50000 <= port <= 59999):
        print("Port must be between 50000 and 59999")
        sys.exit(1)
    main(port)
