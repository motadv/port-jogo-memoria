import socket
import os
from Protocol.communicationProtocol import *

# ! SETTAR IP DO HOST <<<<<
HOST = "193.123.103.206"
PORT = 30000

# * Message Settings
# * Constantes utilizadas tanto por Cliente quanto por Servidor
# * Definem o tipo de mensagem que irá receber, seja ele um input ou tipo de dado do jogo

HEADER_LIST = {
    "HEADER_LENGTH": 10,
    "REQUEST_USERNAME": "#REQUEST_USERNAME_INPUT",
    "REQUEST_GAME_INPUT": "#REQUEST_GAME_INPUT",
    "SEND_STATUS": "#STATUS",
    "SEND_TABULEIRO": "#TABULEIRO",
    "SEND_PLACAR": "#PLACAR",
    "SEND_VEZ": "#VEZ",
    "SEND_WAIT": "#WAIT",
    "SEND_INPUT_ERROR": "#INPUT_ERROR",
}

ERROR_LIST = {
    "ERROR_INVALID_FORMAT": "#INVALID_FORMAT",
    "ERROR_IOOB": "#iOOB",
    "ERROR_JOOB": "#jOOB",
}


def limpa_tela() -> None:

    os.system('cls' if os.name == 'nt' else 'clear')


def imprime_tabuleiro(tabuleiro):

    # Limpa a tela
    limpa_tela()

    # Imprime coordenadas horizontais
    dim = len(tabuleiro)
    print("     ", end='')
    for i in range(0, dim):
        print(f"{i:2d} ", end='')

    print("")

    # Imprime separador horizontal
    print("-----", end='')
    for i in range(0, dim):
        print("---", end='')

    print("")

    for i in range(0, dim):

        # Imprime coordenadas verticais
        print(f"{i:2d} | ", end='')

        # Imprime conteudo da linha 'i'
        for j in range(0, dim):

            # Peca ja foi removida?
            if tabuleiro[i][j] == '-':

                # Sim.
                print(" - ", end='')

            # Peca esta levantada?
            elif tabuleiro[i][j] >= 0:

                # Sim, imprime valor.
                print(f"{tabuleiro[i][j]:2d} ", end='')
            else:

                # Nao, imprime '?'
                print(" ? ", end='')

        print()
    print()
    print()


def imprime_placar(placar):

    n_jogadores = len(placar)

    print("Placar:")
    print("---------------------")
    for i in range(0, n_jogadores):
        print(f"Jogador {i + 1}: {placar[i]:2d}")
    print()
    print()


def tratar_erro(erro: str) -> None:
    if erro == ERROR_INVALID_FORMAT:
        print('Coordenada inválida, use o formato "i j" (exemplo: 1 2).')
    elif erro == ERROR_IOOB:
        print('Coordenada i inválida.')
    elif erro == ERROR_JOOB:
        print('Coordenada j inválida.')
    elif erro == ERROR_OPEN_CARD:
        print('Coordenada já aberta.')


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))
msg = True

while msg:
    # Cliente constantemente lê mensagens do servidor
    msg = receiveMessage(client_socket)
    # Verifica se a mensagem foi recebida corretamente (False ou {header, data})
    if msg:
        flag, msg = msg
        if flag == SEND_MESSAGE:
            print(msg)
        elif flag == REQUEST_GAME_INPUT:
            # Caso mensagem seja sinalização de INPUT, enviar para Servidor seu Input (Ele está travado esperando)
            msgToSend = createMessage(
                input("Digite uma coordenada (exemplo: 1 2).\n > "))
            client_socket.send(msgToSend)
        elif flag == SEND_STATUS:
            print(f'Vez do jogador {msg["vez"]}')
            imprime_tabuleiro(msg["tabuleiro"])
            imprime_placar(msg["placar"])
        elif flag == SEND_WAIT:
            print(f'Esperando o jogador {msg}...')
        elif flag == SEND_INPUT_ERROR:
            tratar_erro(msg)
            print('Digite outra coordenada')
            print('> ', end='')
            new_message = createMessage(input())
            if new_message:
                client_socket.send(new_message)
        elif flag == SEND_RESULT:
            if len(msg) > 1:
                vencedores = str(msg)[1:-1]
                print(f"Empate! Os jogadores {vencedores} empataram!")
            else:
                print(f"Jogador {msg[0]} venceu!")

client_socket.close()
print("Desconectado do servidor.")
