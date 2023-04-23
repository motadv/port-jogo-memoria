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
ERROR_OPEN_CARD = "#CARD_ALREADY_OPEN"

ERROR_TYPE_LIST = [ERROR_INVALID_FORMAT,
                   ERROR_IOOB, ERROR_JOOB, ERROR_OPEN_CARD]

SEND_INPUT_SUCCESS = "#SUCCESS"
SEND_INPUT_FAIL = "#FAIL"

SEND_RESULT_DRAW = "#DRAW"
SEND_RESULT_WINNER = "#WINNER"


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


# * Funções do Jogo


def createStatus(tabuleiro, placar, vez):
    status = {
        'tabuleiro': tabuleiro,
        'placar': placar,
        'vez': vez
    }
    byt = pickle.dumps(status)
    return byt


def chooseCard(client, tabuleiro):
    # Send first input request
    sendToClient(client, REQUEST_GAME_INPUT)
    # Get input from player
    try:
        msg = receiveMessage(client)
        if msg:
            playerInput = validateInput(msg['data'], tabuleiro)

            if playerInput not in ERROR_TYPE_LIST:
                abrePeca(tabuleiro, playerInput)

            while playerInput in ERROR_TYPE_LIST:
                # Send error type to player
                sendToClient(client, SEND_INPUT_ERROR)
                sendToClient(client, playerInput)

                # Get new input from player
                msg = receiveMessage(client)
                if msg:
                    playerInput = validateInput(msg['data'], tabuleiro)

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

    return i, j


def abrePeca(tabuleiro, peca: tuple[int, int]):
    i, j = peca

    if tabuleiro[i][j] == '-':
        return ERROR_OPEN_CARD
    elif tabuleiro[i][j] < 0:
        tabuleiro[i][j] = -tabuleiro[i][j]
        return peca

    return ERROR_OPEN_CARD


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


def incrementaPlacar(placar, jogador):

    placar[jogador] = placar[jogador] + 1


def removePeca(tabuleiro, i, j):

    if tabuleiro[i][j] == '-':
        return False
    else:
        tabuleiro[i][j] = "-"
        return True


def fechaPeca(tabuleiro, i, j):

    if tabuleiro[i][j] == '-':
        return False
    elif tabuleiro[i][j] > 0:
        tabuleiro[i][j] = -tabuleiro[i][j]
        return True

    return False


def temp_sendStatus(clientList, tabuleiro, placar, vez):
    sendToAllClients(clientList, SEND_TABULEIRO)
    sendToAllClients(clientList, tabuleiro)

    sendToAllClients(clientList, SEND_PLACAR)
    sendToAllClients(clientList, placar)

    sendToAllClients(clientList, SEND_VEZ)
    sendToAllClients(clientList, vez)


def gameLoop(nJogadores, dim):

    turno = 0
    tabuleiro = novoTabuleiro(dim)
    placar = novoPlacar(nJogadores)
    totalDePares = dim**2 / 2
    paresEncontrados = 0

    try:
        while paresEncontrados < totalDePares:

            playerSocket = client_list[turno]
            playerNumber = turno+1

            print(f"Sending Status to all players")
            temp_sendStatus(client_list, tabuleiro, placar, turno)
            # sendToAllClients(SEND_STATUS)
            # sendToAllClients(createStatus(tabuleiro, placar, turno))

            print(f"Sending wait message to all players")
            sendToExcept(client_list, playerSocket, SEND_WAIT)
            sendToExcept(client_list, playerSocket, str(playerNumber))

            print(f"Requesting first input from {playerNumber}")
            i1, j1 = chooseCard(playerSocket)

            temp_sendStatus(client_list, tabuleiro, placar, turno)

            print(f"Requesting second input from {playerNumber}")
            i2, j2 = chooseCard(playerSocket)

            temp_sendStatus(client_list, tabuleiro, placar, turno)

            sendToAllClients(
                client_list, f"Jogador {turno+1} escolheu as peças: {(i1, j1)} {(i2, j2)}")

            if tabuleiro[i1][j1] == tabuleiro[i2][j2]:
                # TODO: Handle player acertar tentativa
                sendToAllClients(client_list, SEND_INPUT_SUCCESS)

                incrementaPlacar(placar, turno)
                paresEncontrados += 1

                removePeca(tabuleiro, i1, j1)
                removePeca(tabuleiro, i2, j2)

                time.sleep(5)
            else:
                # TODO: Handle player errar tentativa
                sendToAllClients(client_list, SEND_INPUT_FAIL)

                time.sleep(3)

                fechaPeca(tabuleiro, i1, j1)
                fechaPeca(tabuleiro, i2, j2)

                turno = (turno + 1) % nJogadores

        maxScore = max(placar)
        vencedores = []

        for i in range(placar):
            if placar[i] == maxScore:
                vencedores.append(playerNumber)

        if len(vencedores) > 1:
            sendToAllClients(client_list, SEND_RESULT_DRAW)
            sendToAllClients(client_list, vencedores)
        else:
            sendToAllClients(client_list, SEND_RESULT_WINNER)
            sendToAllClients(client_list, vencedores[0])

    except socket.timeout:
        pass
    except Exception as exc:
        raise (exc)


# * SERVIDOR INICIADO
print(f"Servidor Iniciado!")


nJogadores = 1
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
