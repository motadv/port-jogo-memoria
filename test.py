# GENERIC_MESSAGE = "#MSG"
# HEADER_LENGTH = 10

# SEPARATOR = "\./"


# def createMessage(message: str, flag: str = GENERIC_MESSAGE):
#     flagHeader = flag + SEPARATOR
#     data = flagHeader.encode() + message.encode()
#     header = f'{len(data):<{HEADER_LENGTH}}'.encode()
#     return header + data


# data = createMessage("Teste")


# header, info = data.decode().split()
# flag, message = info.split(sep=SEPARATOR)

# print(header)
# print(info)
# print(f'{flag} ||| {message}')

# # MSG ||| Teste
# # MSG\./Teste

import pickle
import socket
from Protocol.communicationProtocol import *

HOST = "26.44.38.67"
PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

client, _ = server_socket.accept()

client.send(createMessage(["teste", 2, {"nome": "marcos"}]))
