import socket
import os
from dotenv import load_dotenv

load_dotenv()

def send_message_to_server(message):
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    print(HOST,PORT)
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # Connect to server
            client_socket.connect((HOST, PORT))

            # Send data to server
            client_socket.sendall(message.encode())

            # Receive data from server
            data = client_socket.recv(1024)
            print("Received from server:", data.decode())
    except ConnectionRefusedError:
        print("Connection failed. Make sure the server is running and reachable.")


# Usage example:
if __name__ == "__main__":
    message = input("Type message to send: ")
    send_message_to_server(message)