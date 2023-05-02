import socket
from Protocol.communicationProtocol import *

HOST = "26.44.38.67"
PORT = 50000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

message = receiveMessage(client_socket)
print(message['data'])
