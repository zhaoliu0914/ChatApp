import os
import sys
import json
import socket
import logging
import configparser
import threading


ip_user = {}
active_users = {}

# communication json type:
LOGIN = "login"
LIST_USERS = "list_users"
BROADCAST = "broadcast"
GROUP_SENDING = "group_sending"
DIRECT_MESSAGE = "direct_message"

SUCCESS = "success"
FAIL = "fail"


def group_sending(client_json):
    message_type = client_json["type"]
    sender = client_json["sender"]
    message_content = client_json["content"]

    for user in active_users:
        connection = active_users[user]

        message = {"type": message_type,
                   "status": SUCCESS,
                   "sender": sender,
                   "content": message_content}

        message_json = json.dumps(message)
        message_json = message_json.encode(encoding="utf-8")
        connection.send(message_json)


def receiving_message(connection, client_ip):

    while True:
        # Keep looking and receiving JSON message from client
        client_data = connection.recv(1024)

        # client has closed the connection!!!
        if not client_data:
            # remove client ip, username, and connection from ip_user and active_users
            username = ip_user[client_ip]
            active_users.pop(username)
            ip_user.pop(client_ip)
            break

        client_data = client_data.decode(encoding="utf-8")
        print(f"Receive from {client_address}: {client_data}")

        client_json = json.loads(client_data)
        message_type = client_json["type"]

        if message_type == LOGIN:
            sender = client_json["sender"]
            message_content = client_json["content"]

            current_user = active_users.get(sender)
            if current_user is None:
                ip_user[client_ip] = sender
                active_users[sender] = connection

                message = {"type": message_type,
                           "status": SUCCESS,
                           "sender": "Server",
                           "content": "You are successfully login to server."}

            else:
                message = {"type": message_type,
                           "status": FAIL,
                           "sender": "Server",
                           "content": "The username has already been existed in the server."}

            message_json = json.dumps(message)
            message_json = message_json.encode(encoding="utf-8")
            connection.send(message_json)

        elif message_type == LIST_USERS:
            users = []
            for user in active_users:
                users.append(user)

            message = {"type": message_type,
                       "status": SUCCESS,
                       "sender": "Server",
                       "content": users}

            message_json = json.dumps(message)
            message_json = message_json.encode(encoding="utf-8")
            connection.send(message_json)

        elif message_type == GROUP_SENDING:
            group_sending(client_json=client_json)

        elif message_type == DIRECT_MESSAGE:
            try:
                sender = client_json["sender"]
                receiver = client_json["receiver"]
                message_content = client_json["content"]

                receiver_connection = active_users[receiver]

                message = {"type": message_type,
                           "status": SUCCESS,
                           "sender": sender,
                           "content": message_content}

                message_json = json.dumps(message)
                message_json = message_json.encode(encoding="utf-8")
                receiver_connection.send(message_json)
            except:
                print("Error occurs")


def server_notification():
    for line in sys.stdin:
        line = line.strip()
        line = line.encode(encoding="utf-8")
        connection.send(line)


if __name__ == '__main__':
    server_port = 8888
    print(f"Server is running at: ")
    print(f"Host Name: {socket.gethostname()}")
    print(f"Host IP: {socket.gethostbyname(socket.gethostname())}")
    print(f"Host Port: {server_port}")
    # Set up socket
    server_address = ("127.0.0.1", server_port)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(server_address)
    server.listen(5)

    sending_thread = threading.Thread(target=server_notification, args=())
    sending_thread.start()

    while True:
        # Wait for an incoming connection.
        # Return a new socket representing the connection, and the address of the client.
        connection, client_address = server.accept()

        client_ip = client_address[0]
        client_port = client_address[1]
        print(f"Connection accepted from {client_ip} : {client_port}")
        print(f"Connection accepted from {client_ip} : {client_port}")

        ip_user[client_ip] = None

        receiving_thread = threading.Thread(target=receiving_message, args=(connection, client_ip))

        receiving_thread.start()

