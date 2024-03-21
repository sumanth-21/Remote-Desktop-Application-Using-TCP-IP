import socket
import ssl
import subprocess
import sys

IP = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((IP, PORT))


# Function to authenticate the client
def authenticate():
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")

        client.sendall(username.encode())
        client.sendall(password.encode())

        response = client.recv(1024).decode()
        print(response)

        if response == "\nAuthentication successful":
            return True
        else:
            continue

# Authenticate the client before allowing commands
authenticated = authenticate()
if not authenticated:
    client.close()
    sys.exit(0)

def send_file(filename):
    client.sendall(f"send_file {filename}".encode())
    with open(filename, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            client.sendall(data)
    client.sendall("file_sent".encode())

def receive_file(filename):
    client.sendall(f"receive_file {filename}".encode())
    with open(filename, "wb") as f:
        while True:
            data = client.recv(1024)
            if not data:
                break
            if data == b"file_sent":
                print(f"{filename} recieved successfully")
                break
            f.write(data)

while True:
    try:
        command = input("Enter a command (or type 'quit' to exit): ")
        if not command:
            continue

        if command == "quit":
            client.sendall(command.encode())
            client.close()
            sys.exit(0)
        elif command == "send_file":
            filename = input("Enter the filename: ")
            send_file(filename)
        elif command == "receive_file":
            filename = input("Enter the filename: ")
            receive_file(filename)
        elif command.startswith("cd"):
            client.sendall(command.encode())
            response = client.recv(1024).decode()
            print(response)
        else:
            client.sendall(command.encode())
            result = client.recv(4096).decode()
            print(result)
    except Exception as e:
        print(f"Error: {str(e)}")

client.close()