import socket
import os
from dotenv import load_dotenv

load_dotenv()

# Define host and port
HOST = os.getenv("SOCKET_SERVER_HOST")
PORT = int(os.getenv("SOCKET_SERVER_PORT"))

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Connect to server
    client_socket.connect((HOST, PORT))

    while True:
        # Get user input
        message = input("Type message to send (type 'exit' to quit): ")

        if message.lower() == 'exit':
            break

        # Send data to server
        client_socket.sendall(message.encode())

        # Receive data from server
        data = client_socket.recv(1024)
        print("Received from server:", data.decode())
