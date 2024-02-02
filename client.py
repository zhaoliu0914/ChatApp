import sys
import json
import socket
import logging
import configparser
import threading

client = None


def receiving_message():
    while True:
        server_data = client.recv(1024)
        server_data.decode(encoding="utf-8")

        print(f"Receive from {server_ip}: {server_data}")


def sending_message():
    for line in sys.stdin:
        line = line.strip()
        line = line.encode(encoding="utf-8")
        client.send(line)


if __name__ == '__main__':
    server_ip = "172.27.67.88"
    server_address = (server_ip, 8888)

    # Set up socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_address)

    print(f"Connected to Server address: {server_address}")
    logging.info(f"Connected to Server address: {server_address}")

    receiving_thread = threading.Thread(target=receiving_message, args=())
    sending_thread = threading.Thread(target=sending_message, args=())

    receiving_thread.start()
    sending_thread.start()


