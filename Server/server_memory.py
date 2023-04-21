import socket
import time

# Game Logic

nJogadores = 2
vez = 0

# Server socket TCP

HOST = "26.44.38.67"
PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(0)

client_list = []

REQUEST_INPUT = "REQUEST_INPUT"


def sendToAllClients(message):
    byteMessage = str.encode(message)
    print(f"Enviando para todo: {message}")
    for client in client_list:
        client.send(byteMessage)


def sendToClient(client: int, message: str):
    print(f"Enviando para {client}: {message}")
    byteMessage = str.encode(message)
    client_list[client].send(byteMessage)


def sendToExcept(ignoredClient: int, message: str):
    # Send to all clients exepct specified in parameter
    print(f"Enviando para todos exceto {ignoredClient}: {message}")
    byteMessage = str.encode(message)
    for index, client in enumerate(client_list):
        if index != ignoredClient:
            client.send(byteMessage)


# Aceitando N clientes
while True:
    client_socket, address = server_socket.accept()

    # ? Desnecessário porque limita conexão
    if len(client_list) >= nJogadores:
        client_socket.send(str.encode("Servidor cheio!"))
        client_socket.close()
        continue

    client_list.append(client_socket)
    print(f"Conexão com {address} estabelecida!")
    client_socket.send(str.encode(
        f"Conectado ao servidor!"))

    sendToAllClients(f"Jogadores: {len(client_list)}/{nJogadores}")
    print(f"Jogadores: {len(client_list)}/{nJogadores}")

    if len(client_list) >= nJogadores:
        sendToAllClients("Começando partida!")
        print("Começando partida!")
        break

while True:
    # time.sleep(2)
    # sendToAllClients("Teste!")
    # print("Teste enviado!")

    # * sendToAllClients(Tabuleiro)
    sendToAllClients(f"Vez do jogador {vez+1}.\n")
    sendToExcept(vez, f"Esperando jogador...\n")

    print(f"Solicitando input do jogador {vez+1}")

    sendToClient(vez, f"Escolha uma peça:\n")
    sendToClient(vez, REQUEST_INPUT)

    msg = client_list[vez].recv(1024).decode()
    print(f"Mensagem recebida do jogador {vez+1}: {msg}")

    time.sleep(2)

    vez = (vez + 1) % nJogadores
