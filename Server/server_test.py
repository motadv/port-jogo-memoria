import socket

# Settar conexão por socket TCP

HOST = socket.gethostname()
PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

while True:
    client_socket, address = server_socket.accept()
    print(f"Conexão com {address} estabelecida!")
    client_socket.send(str.encode("Conectado ao servidor!"))

    client_socket.close()
