import os
import sys
import json
import socket
import logging
import configparser
import threading


def receiving_message(connection, client_address):
    while True:
        # Keep looking and receiving JSON message from client until receiving "QUITTING" command
        # If command from client is "QUITTING", then the "response" element is "QUITTING" and "parameter" element is empty.
        client_data = connection.recv(1024)
        client_data = client_data.decode(encoding="utf-8")

        print(f"Receive from {client_address}: {client_data}")


def sending_message(connection, client_address):
    for line in sys.stdin:
        line = line.strip()
        line = line.encode(encoding="utf-8")
        connection.send(line)


if __name__ == '__main__':
    # Set up socket
    server_address = ("172.27.67.88", 8888)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(server_address)
    server.listen(5)

    while True:
        # Wait for an incoming connection.
        # Return a new socket representing the connection, and the address of the client.
        connection, client_address = server.accept()

        print(f"Connection accepted from {client_address}")
        logging.info(f"Connection accepted from {client_address}")

        receiving_thread = threading.Thread(target=receiving_message, args=(connection, client_address))
        sending_thread = threading.Thread(target=sending_message, args=(connection, client_address))

        receiving_thread.start()
        sending_thread.start()
