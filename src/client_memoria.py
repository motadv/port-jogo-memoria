import socket
import os

# ! SETTAR IP DO HOST <<<<<
HOST = "26.44.38.67"
PORT = 50000

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


# ? Função que garante que você está recebendo uma mensagem do tamanho correto
# ? para acessar o dado da mensagem, lembre de garantir que ela chegou
# ? E acesse por receiveMessage(...)['data']
# ? Caso não precise do header da mensagem na implementação
# ? implemente diretamente no retorno da função o acesso ao ['data']

def receiveMessage(socket):
    try:
        message_header = socket.recv(HEADER_LIST["HEADER_LENGTH"])

        if not len(message_header):
            return False

        message_length = int(message_header.decode())

        return {
            "header": message_header,
            "data": socket.recv(message_length).decode()
        }
    except:
        return False


def createMessage(message: str):
    data = message.encode()
    header = f'{len(data):<{HEADER_LIST["HEADER_LENGTH"]}}'.encode()
    return header + data


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
    if erro == ERROR_LIST["ERROR_INVALID_FORMAT"]:
        print('Coordenada inválida, use o formato "i j" (exemplo: 1 2).')
    elif erro == ERROR_LIST["ERROR_IOOB"]:
        print('Coordenada i inválida.')
    elif erro == ERROR_LIST["ERROR_JOOB"]:
        print('Coordenada j inválida.')


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))
msg = True

while msg:
    # Cliente constantemente lê mensagens do servidor
    msg = receiveMessage(client_socket)

    # Verifica se a mensagem foi recebida corretamente (False ou {header, data})
    if msg:
        # Acessando dado da mensagem
        msg = msg['data']

        if msg not in HEADER_LIST.values():
            print(msg)

        if msg == HEADER_LIST["REQUEST_GAME_INPUT"]:
            # Caso mensagem seja sinalização de INPUT, enviar para Servidor seu Input (Ele está travado esperando)
            msgToSend = createMessage(
                input("Digite uma coordenada (exemplo: 1 2).\n > "))
            if msgToSend:
                client_socket.send(msgToSend)
        elif msg == HEADER_LIST["SEND_VEZ"]:
            # Caso seja uma sinalização de envio de dados, solicitar uma nova mensagem que já está sendo enviada pelo servidor
            msg = receiveMessage(client_socket)
            if msg:
                vez = msg['data']
                print(f'Vez do jogador {vez}')
        elif msg == HEADER_LIST["SEND_PLACAR"]:
            # Caso seja uma sinalização de envio de dados, solicitar uma nova mensagem que já está sendo enviada pelo servidor
            msg = receiveMessage(client_socket)
            if msg:
                placar = msg['data']
                placar_lista = eval(placar)
                imprime_placar(placar_lista)
        elif msg == HEADER_LIST["SEND_TABULEIRO"]:
            # Caso seja uma sinalização de envio de dados, solicitar uma nova mensagem que já está sendo enviada pelo servidor
            msg = receiveMessage(client_socket)
            if msg:
                tabuleiro = msg['data']
                tabuleiro_lista = eval(tabuleiro)
                imprime_tabuleiro(tabuleiro_lista)
        elif msg == HEADER_LIST["SEND_WAIT"]:
            msg = receiveMessage(client_socket)
            if msg:
                jogador = msg['data']
                print(f'Esperando o jogador {jogador}...')
        elif msg == HEADER_LIST["SEND_INPUT_ERROR"]:
            msg = receiveMessage(client_socket)
            if msg:
                erro = msg['data']
                tratar_erro(erro)
                print('Digite uma nova coordenada.')
                print('> ', end='')
                new_message = createMessage(input())
                if new_message:
                    client_socket.send(new_message)


client_socket.close()
print("Desconectado do servidor.")
