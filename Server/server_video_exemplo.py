# https://www.youtube.com/watch?v=CV7_stUWvBQ&list=PL6yCaejUzyZ3EtSvkwcYK5A3Fj2n1TVmV&index=4

import socket
import select

HEADER_LENGHT = 10
HOST = socket.gethostname()
PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGHT)

        if not len(message_header):
            return False

        message_length = int(message_header.decode().strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)

            clients[client_socket] = user

            print(
                f"Nova conexão aceita de {client_address[0]}:{client_address[1]} user: {user['data'].decode()}")
        else:
            message = receive_message(notified_socket)

            if message is False:
                print(
                    f"Conexão treminada com {clients[notified_socket]['data'].decode()}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(
                f"Mensagem recebida de {user['data'].decode()}: {message['data'].decode()}")

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(
                        user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        # * lidar com erro de conexão
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
