import socket
import time
import random
import pickle

# * Server socket TCP

#! SETTAR IP DO HOST <<<<<
HOST = "26.44.38.67"
PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(1)
server_socket.bind((HOST, PORT))
server_socket.listen()

client_list = []


def terminateServer():
    print("Closing server...")
    server_socket.close()


# * Message Settings

HEADER_LENGTH = 10
REQUEST_USERNAME = "#REQUEST_USERNAME_INPUT"
REQUEST_GAME_INPUT = "#REQUEST_GAME_INPUT"
SEND_STATUS = "#STATUS"
SEND_TABULEIRO = "#TABULEIRO"
SEND_PLACAR = "#PLACAR"
SEND_VEZ = "#VEZ"
SEND_WAIT = "#WAIT"
SEND_INPUT_ERROR = "#INPUT_ERROR"

ERROR_INVALID_FORMAT = "#INVALID_FORMAT"
ERROR_IOOB = "#iOOB"
ERROR_JOOB = "#jOOB"

ERROR_TYPE_LIST = [ERROR_INVALID_FORMAT, ERROR_IOOB, ERROR_JOOB]


def receiveMessage(senderSocket):
    while True:
        try:
            message_header = senderSocket.recv(HEADER_LENGTH)

            if not len(message_header):
                return False

            message_length = int(message_header.decode())
            return {
                "header": message_header,
                "data": senderSocket.recv(message_length).decode()
            }
        except socket.timeout:
            pass
        except Exception as exc:
            print(f'ReceiveMessage ERROR: {str(exc)}')
            raise (exc)


def createMessage(message: str):
    data = message.encode()
    header = f'{len(data):<{HEADER_LENGTH}}'.encode()
    return header + data


def sendToAllClients(client_list, message: str):
    byteMessage = createMessage(message)
    print(f"Enviando para todos: {message}")
    for client in client_list:
        client.send(byteMessage)


def sendToClient(client, message: str):
    byteMessage = createMessage(message)
    print(f"Enviando para cliente: {message} : {byteMessage}")
    client.send(byteMessage)


def sendToExcept(client_list: list, ignoredClient, message: str):
    # Send to all clients exepct specified in parameter
    print(f"Enviando para todos exceto um: {message}")
    byteMessage = createMessage(message)
    for client in client_list:
        if client != ignoredClient:
            client.send(byteMessage)


def chooseCard(client):
    # Send first input request
    sendToClient(client, REQUEST_GAME_INPUT)
    # Get input from player
    try:
        msg = receiveMessage(client)
        if msg:
            playerInput = validateInput(msg['data'])

            while playerInput in ERROR_TYPE_LIST:
                # Send error type to player
                sendToClient(client, SEND_INPUT_ERROR)
                sendToClient(client, playerInput)

                # Get new input from player
                msg = receiveMessage(client)
                if msg:
                    playerInput = validateInput(msg['data'])

            else:
                return playerInput

    except socket.timeout:
        pass
    except Exception as exc:
        raise (exc)

    print(f'Não houve mensagem, saindo do ChooseCard | msg = {msg}')


def validateInput(playerInput: str):
    try:
        i = int(playerInput.split(' ')[0])
        j = int(playerInput.split(' ')[1])
    except ValueError:
        return ERROR_INVALID_FORMAT

    if i < 0 or i >= dim:
        return ERROR_IOOB

    if j < 0 or j >= dim:
        return ERROR_JOOB

    return (i, j)


def createStatus(tabuleiro, placar, vez):
    status = {
        'tabuleiro': tabuleiro,
        'placar': placar,
        'vez': vez
    }
    byt = pickle.dumps(status)
    return byt


# * Funções do Jogo


def novoTabuleiro(dim):
    # Cria um tabuleiro vazio.
    tabuleiro = []
    for i in range(0, dim):

        linha = []
        for j in range(0, dim):

            linha.append(0)

        tabuleiro.append(linha)

    # Cria uma lista de todas as posicoes do tabuleiro. Util para
    # sortearmos posicoes aleatoriamente para as pecas.
    posicoesDisponiveis = []
    for i in range(0, dim):

        for j in range(0, dim):

            posicoesDisponiveis.append((i, j))

    # Varre todas as pecas que serao colocadas no
    # tabuleiro e posiciona cada par de pecas iguais
    # em posicoes aleatorias.
        # * ALTERAÇÃO DO PORT: LIMITE SUPERIOR DO RANGE FORÇADAMENTE CONVERTIDO PRA INTEIRO
    for j in range(0, int(dim / 2)):
        for i in range(1, dim + 1):

            # Sorteio da posicao da segunda peca com valor 'i'
            maximo = len(posicoesDisponiveis)
            indiceAleatorio = random.randint(0, maximo - 1)
            rI, rJ = posicoesDisponiveis.pop(indiceAleatorio)

            tabuleiro[rI][rJ] = -i

            # Sorteio da posicao da segunda peca com valor 'i'
            maximo = len(posicoesDisponiveis)
            indiceAleatorio = random.randint(0, maximo - 1)
            rI, rJ = posicoesDisponiveis.pop(indiceAleatorio)

            tabuleiro[rI][rJ] = -i

    return tabuleiro


def novoPlacar(nJogadores):
    return [0] * nJogadores


def novoJogo(dim, nJogadores):
    jogo = {
        'dim': dim,
        'nJogadores': 2,
        'totalDePares': dim**2 / 2,

        'paresEncontrados': 0,
        'turno': 0,

        'tabuleiro': novoTabuleiro(dim),
        'placar': novoPlacar(nJogadores),
    }

    return jogo


def acceptClients(nJogadores):
    while len(client_list) < nJogadores:
        try:
            client_socket, address = server_socket.accept()

            # ? Desnecessário porque limita conexão
            if len(client_list) >= nJogadores:
                sendToClient(client_socket, f"Servidor cheio!")
                client_socket.close()
                continue

            client_list.append(client_socket)
            print(f"Conexão com {address} estabelecida!")

            # !Aparentemente, não se sabe o porquê, mas a primeira mensagem não é mostrada pelo cliente
            # client_socket.send(createMessage(''))
            sendToClient(client_socket, f"Conectado ao servidor!")
            sendToClient(client_socket, f"Você é o jogador {len(client_list)}")

            print(f"Jogadores: {len(client_list)}/{nJogadores}")
            sendToAllClients(
                client_list, f"Jogadores: {len(client_list)}/{nJogadores}")
        except socket.timeout:
            pass
        except Exception as exc:
            print(str(exc))

    else:
        sendToAllClients(client_list, "Começando partida!")
        print("Começando partida!")
        time.sleep(2)


def gameLoop(nJogadores, dim):

    turno = 0
    tabuleiro = novoTabuleiro(dim)
    placar = novoPlacar(nJogadores)
    totalDePares = dim**2 / 2
    paresEncontrados = 0

    try:
        while True:

            playerSocket = client_list[turno]
            playerNumber = turno+1

            print(f"Sending Status to all players")
            sendToAllClients(
                client_list, f"Tabuleiro {dim}x{dim}, Turno: {turno}\n")
            # sendToAllClients(SEND_STATUS)
            # sendToAllClients(createStatus(tabuleiro, placar, turno))

            print(f"Sending wait message to all players")
            sendToExcept(client_list, playerSocket, SEND_WAIT)
            sendToExcept(client_list, playerSocket, str(playerNumber))

            selectedCards = []

            print(f"Requesting first input from {playerNumber}")
            firstCard = chooseCard(playerSocket)
            selectedCards.append(firstCard)

            print(f"Requesting second input from {playerNumber}")
            secondCard = chooseCard(playerSocket)
            selectedCards.append(secondCard)

            # TODO Game logic com a escolha do player

            sendToAllClients(
                client_list, f"Jogador {turno+1} fez a jogada: {selectedCards}")

            turno = (turno + 1) % nJogadores

            time.sleep(2)
    except socket.timeout:
        pass
    except Exception as exc:
        raise (exc)


# * SERVIDOR INICIADO
print(f"Servidor Iniciado!")


nJogadores = 2
dim = 4
# nJogadores = int(input("Insira o número máximo de jogadores\n >"))
# dim = int(input("Insira a dimensão do tabuleiro de jogo\n >"))

try:
    while True:
        print(f"Começando novo jogo!\n")
        print(f"Máximo de jogadores: {nJogadores}")
        print(f"Dimensão do tabuleiro: {dim}")

        #  Aceitando N clientes
        print(f"Esperando {nJogadores} jogadores")
        acceptClients(nJogadores)

        gameLoop(nJogadores, dim)
except Exception as exc:
    print(str(exc))
    terminateServer()
