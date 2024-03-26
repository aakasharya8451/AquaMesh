import sys
import os
import json

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import socket
import threading
from dotenv import load_dotenv
from src.kafka.producer import produce_messages

load_dotenv()

# Define host and port
HOST = os.getenv("SOCKET_SERVER_HOST")
PORT = int(os.getenv("SOCKET_SERVER_PORT"))


# Function to handle each client connection
def handle_client(client_socket, client_address):
    print("Connected by", client_address)
    with client_socket:
        while True:
            # Receive data from client
            data = client_socket.recv(1024)
            if not data:
                break

            # Print received data
            received = data.decode()
            # print(type(received))
            partition_no = json.loads(received)["arduinoID"]
            # print(partition_no)
            produce_messages(received, partition_no)
            # produce_messages(received, 0)
            print("Received: succ: ", received)

            # Echo the data back to client
            client_socket.sendall(data)


# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the address
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen(5)

    print("Server is listening on", PORT)

    while True:
        # Accept incoming connection
        client_socket, client_address = server_socket.accept()

        # Start a new thread to handle the client connection
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address))
        client_thread.start()