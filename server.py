import socket
import ssl
import subprocess
import sys
import os

IP = "127.0.0.1"
PORT = 5000

# Define a list of authorized usernames and passwords
AUTHORIZED_USERS = {"user1": "password1", "user2": "password2"}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen(5)

print('Server is listening for connections...', flush=True)


def authenticate(client_socket):
    while True:
        username = client_socket.recv(1024).decode().strip()
        password = client_socket.recv(1024).decode().strip()

        if username in AUTHORIZED_USERS and AUTHORIZED_USERS[username] == password:
            client_socket.sendall("\nAuthentication successful".encode())
            return True
        else:
            client_socket.sendall("\nInvalid username or password. Please try again.".encode())


def receive_file(client_socket, filename):
    with open(filename, "wb") as f:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            f.write(data)


def send_file(client_socket, filename):
    with open(filename, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            client_socket.sendall(data)
    client_socket.sendall("file_sent".encode())


def change_directory(client_socket, command):
    directory = command.split(maxsplit=1)
    if len(directory) > 1:
        directory = directory[1]
        try:
            os.chdir(directory)
            response = f"Changed directory to {directory}"
        except Exception as e:
            response = f"Failed to change directory: {str(e)}"
    else:
        directory = os.getcwd()
        response = f"Current directory: {directory}"
    client_socket.sendall(response.encode())


def list_directory(client_socket):
    try:
        files = os.listdir('.')
        response = "\n".join(files)
    except Exception as e:
        response = f"Failed to list directory: {str(e)}"
    client_socket.sendall(response.encode())


def create_file(client_socket, filename):
    try:
        open(filename, 'a').close()
        response = f"Created file: {filename}"
    except Exception as e:
        response = f"Failed to create file: {str(e)}"
    client_socket.sendall(response.encode())


def delete_file(client_socket, filename):
    try:
        os.remove(filename)
        response = f"Deleted file: {filename}"
    except Exception as e:
        response = f"Failed to delete file: {str(e)}"
    client_socket.sendall(response.encode())


def rename_file(client_socket, command):
    filenames = command.split(maxsplit=2)
    if len(filenames) == 3:
        old_name = filenames[1]
        new_name = filenames[2]
        try:
            os.rename(old_name, new_name)
            response = f"Renamed file {old_name} to {new_name}"
        except Exception as e:
            response = f"Failed to rename file: {str(e)}"
    else:
        response = "Invalid syntax. Usage: rename old_name new_name"
    client_socket.sendall(response.encode())
    
def handle_command(client_socket, command):
    commands = {
    "quit": lambda: sys.exit(0),
    "send_file": lambda: receive_file(client_socket, command.split()[1]),
    "receive_file": lambda: send_file(client_socket, command.split()[1]),
    "cd": lambda: change_directory(client_socket, command),
    "ls": lambda: list_directory(client_socket),
    "create_file": lambda: create_file(client_socket, command.split()[1]),
    "delete_file": lambda: delete_file(client_socket, command.split()[1]),
    "rename_file": lambda: rename_file(client_socket, command),
    }

    if command.split()[0] in commands:
        commands[command.split()[0]]()
    else:
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
        
        error_message = f"Error: Unrecognized command '{command.split()[0]}'.\n{output.decode()}"
        client_socket.sendall(error_message.encode())

while True:
    client_socket, client_address = server.accept()
    print(f"Received connection from {client_address}", flush=True)

    # Authenticate the client
    if not authenticate(client_socket):
        client_socket.close()
        continue

    # Receive and execute commands from the client
    while True:
        command = client_socket.recv(1024).decode().strip()
        if not command:
            break
        handle_command(client_socket, command)

    # Close the connection
    client_socket.close()

server.close()

