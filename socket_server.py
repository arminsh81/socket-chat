import socket
import threading
import argparse

parser = argparse.ArgumentParser(prog='Socket Server', usage='A python socket chat app, Server Side',
                                 description='Creates a python socket server where clients can connect to',
                                 epilog='Enjoy the server! :)',
                                 fromfile_prefix_chars='@')
parser.add_argument('-i', '--ip', default='localhost', type=str,
                    help='Server Ip to Create Server on - Defaults to localhost')
parser.add_argument('-p', '--port', default=1234, type=int,
                    help='Server port to Create Server on - Defaults to 1234')

args = parser.parse_args()
IP = args.ip
PORT = args.port

HEADER_SIZE = 10


def make_msg_with_header(msg):
    return f'{len(msg):<{HEADER_SIZE}}{msg}'


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))

clients_list = [server_socket]
client_usernames = {}


def accept_connections():
    global clients_list
    while True:
        server_socket.listen(5)
        client_socket, client_address = server_socket.accept()
        client_ip, client_port = client_address
        print(f'[Incoming Connection] From {client_ip}:{client_port}')
        client_socket.send(bytes(make_msg_with_header('Welcome To The Server'), 'utf-8'))
        clients_list.append(client_socket)
        threading.Thread(target=listen_for_messages, args=(client_socket, client_address)).start()


def listen_for_messages(client_socket: socket.socket, client_address):
    global client_usernames, clients_list
    while not client_usernames.get(client_socket):
        try:
            username_header = client_socket.recv(HEADER_SIZE)
            if username_header:
                username = client_socket.recv(int(username_header)).decode('utf-8')
                client_usernames[client_socket] = username
                broadcast(f'[JOIN]{username} Joined The Chat', client_socket)
                break
        except ConnectionResetError:
            print(f'[Disconnection] user {client_address[0]} Disconnected')
            clients_list.remove(client_socket)
            return
    while True:
        try:
            header = client_socket.recv(HEADER_SIZE)
            if header:
                msg = client_socket.recv(int(header)).decode('utf-8')
                msg = f'{client_usernames[client_socket]} > {msg}'
                broadcast(msg, client_socket)
                print(msg)
        except ConnectionResetError:
            print(f'[Disconnection] user {client_usernames[client_socket]} Disconnected')
            broadcast(f'[LEAVE]{client_usernames[client_socket]} Left The Chat', client_socket)
            clients_list.remove(client_socket)
            return


def broadcast(message, client_socket: socket.socket = None):
    global clients_list
    for client in clients_list:
        if client != client_socket:
            try:
                client.send(bytes(make_msg_with_header(message), 'utf-8'))
            except OSError:
                clients_list.remove(client)


threading.Thread(target=accept_connections).start()
print(f'Server is Up on {IP}:{PORT}')
