import sys
import json
import socket
import logging
import configparser
import threading


# Server configuration
server_ip = "192.168.1.132"
server_port = 8888
server_address = (server_ip, server_port)

# client socket
client = None

# communication json type:
LOGIN = "login"
LIST_USERS = "list_users"
BROADCAST = "broadcast"
GROUP_SENDING = "group_sending"
DIRECT_MESSAGE = "direct_message"

SUCCESS = "success"

# user infor
user_name = None
host_name = socket.gethostname()
host_ip = socket.gethostbyname(socket.gethostname())


def help_information():
    print("[show] : display all help/available information")
    print("[list] : display all active users in the server")
    print("[dm:<receiver>]<message> : direct message <message> to <receiver>")
    print("<message> : group message <message> to all active users in the server")


def receiving_message():
    while True:
        # receive response from server
        server_data = client.recv(1024)
        server_data = server_data.decode(encoding="utf-8")
        server_json = json.loads(server_data)
        response_type = server_json["type"]
        response_status = server_json["status"]
        response_sender = server_json["sender"]
        response_content = server_json["content"]

        print(f"{response_sender}: {response_content}")


def sending_message():
    for line in sys.stdin:
        line = line.strip()

        if len(line) == 0:
            print("You cannot send empty message to the Server!")
            continue

        elif line == "[show]":
            help_information()

        elif line == "[list]":
            try:
                message_json = format_communication_json(LIST_USERS, None, line)
                client.send(message_json)
            except:
                print("There some errors occurs.")
                print("Please exit the program and then restart again!")

        elif line.startswith("[dm:"):
            try:
                # get the receiver and content from input string.
                line_str = str.split("[dm:")
                #print(f"strarr[0] = {line_str[0]}")
                #print(f"strarr[1] = {line_str[1]}")
                receiver_content = line_str[1].split("]")
                #print(f"str_message[0] = {receiver_content[0]}")
                #print(f"str_message[1] = {receiver_content[1]}")

                receiver = receiver_content[0]
                content = receiver_content[1]

                # send message to server
                message_json = format_communication_json(DIRECT_MESSAGE, receiver, content)
                client.send(message_json)
            except:
                print("You have entered wrong format message.")
                print("Please enter again!")
                help_information()
                continue
        else:
            try:
                # send message to server
                message_json = format_communication_json(GROUP_SENDING, None, line)
                client.send(message_json)
            except:
                print("There some errors occurs.")
                print("Please exit the program and then restart again!")


def format_communication_json(type, receiver, content):
    if type == LOGIN:
        message = {"type": type,
                   "sender": content,
                   "content": content}

    elif type == DIRECT_MESSAGE:
        message = {"type": type,
                   "sender": user_name,
                   "receiver": receiver,
                   "content": content}

    else:
        message = {"type": type,
                   "sender": user_name,
                   "content": content}

    message_json = json.dumps(message)
    message_json = message_json.encode(encoding="utf-8")

    return message_json


if __name__ == '__main__':

    print(f"Host Name: {host_name}")
    print(f"Host IP: {host_ip}")
    help_information()

    # Set up socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_address)

    print(f"Connected to Server address: {server_address}")
    logging.info(f"Connected to Server address: {server_address}")

    # Verify username
    print(f"Please enter your username to login to server({server_ip}): ")
    for line in sys.stdin:
        line = line.strip()

        if len(line) == 0:
            print("username cannot be empty!")
            print(f"Please enter your username to login to server({server_ip}): ")
            continue

        # send username to server
        message_json = format_communication_json(LOGIN, None, line)
        client.send(message_json)

        # receive response from server
        server_data = client.recv(1024)
        server_data = server_data.decode(encoding="utf-8")
        server_json = json.loads(server_data)
        response_type = server_json["type"]
        response_status = server_json["status"]

        # check the status returned by server
        if response_status == SUCCESS:
            user_name = line
            print("You have successfully login to Server")
            break
        else:
            user_name = None
            print("Your user name is either duplicated or un-available.")
            print("Please enter a new/available to login to server:")
        #server_parameter = server_json["parameter"]

    receiving_thread = threading.Thread(target=receiving_message, args=())
    sending_thread = threading.Thread(target=sending_message, args=())

    receiving_thread.start()
    sending_thread.start()


