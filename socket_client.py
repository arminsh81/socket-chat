import argparse
import os
import socket
import time
from threading import Thread

parser = argparse.ArgumentParser(prog='Socket Client', usage='A python socket chat app, Client side',
                                 description='''Connects to a python socket server
You can 
Use !quit for quiting the chat''', epilog='Enjoy the client! :)',
                                 fromfile_prefix_chars='@')
parser.add_argument('-i', '--ip', default='localhost', type=str,
                    help='Server Ip to Connect - Defaults to localhost')
parser.add_argument('-p', '--port', default=1234, type=int,
                    help='Server port to Connect - Defaults to 1234')

args = parser.parse_args()

IP = args.ip
PORT = args.port
HEADER_SIZE = 10
print(f'Connecting to socket server on {IP}:{PORT}')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((IP, PORT))
except ConnectionRefusedError:
    print('Connection Could not be Established With the server')
    exit()
username = input('Enter Your Username: ')


def make_msg_with_header(msg):
    return f'{len(msg):<{HEADER_SIZE}}{msg}'


client_socket.send(bytes(make_msg_with_header(username), 'utf-8'))


def recieve_msgs():
    while True:
        try:
            header = client_socket.recv(HEADER_SIZE)
            if header:
                msg = client_socket.recv(int(header))
                print(msg.decode('utf-8'))
        except ConnectionResetError:
            print('Server IS down! Comeback Later')
            os._exit(0)


def send_msgs():
    while True:
        new_msg = input(f'{username} > ')
        if new_msg == '!quit':
            os._exit(0)
        client_socket.send(bytes(make_msg_with_header(new_msg), 'utf-8'))


Thread(target=recieve_msgs).start()
time.sleep(0.5)
Thread(target=send_msgs).start()
