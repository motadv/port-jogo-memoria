import socket
import time
import pickle

# * Server socket TCP

#! SETTAR IP DO HOST <<<<<
HOST = "26.44.38.67"
PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

client_list = []

# region # * Funções do Jogo


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

# endregion

# region #* Dados do Jogos


dim = 4
nJogadores = 2
totalDePares = dim**2 / 2

paresEncontrados = 0
turno = 0

tabuleiro = novoTabuleiro(dim)
placar = novoPlacar(nJogadores)

# endregion

# region #* Messages Protocol
HEADER_LENGTH = 10


def receiveMessage(socket):
    try:
        message_header = socket.recv(HEADER_LENGTH)

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
    header = f'{len(data):<{HEADER_LENGTH}}'.encode()
    return header + data


def sendToAllClients(clientList: list, message: str):
    byteMessage = createMessage(message)
    print(f"Enviando para todos: {message}")
    for client in list:
        client.send(byteMessage)


def sendToClient(client: socket, message: str):
    print(f"Enviando para {client}: {message}")
    byteMessage = createMessage(message)
    client.send(byteMessage)


def sendToExcept(ignoredClient: socket, message: str):
    # Send to all clients exepct specified in parameter
    print(f"Enviando para todos exceto {ignoredClient}: {message}")
    byteMessage = createMessage(message)
    for client in client_list:
        if client != ignoredClient:
            client.send(byteMessage)


# endregion

# region #* Game Communication

REQUEST_USERNAME = "#REQUEST_USERNAME_INPUT"
REQUEST_GAME_INPUT = "#REQUEST_GAME_INPUT"
SEND_STATUS = "#STATUS"
SEND_TABULEIRO = "#TABULEIRO"
SEND_PLACAR = "#PLACAR"
SEND_VEZ = "#VEZ"


def createStatusInfo(tabuleiro, placar, turno):
    status = {'tabuleiro': tabuleiro, 'placar': placar, 'turno': turno}
    data = createMessage(pickle.dumps(status))
    return data

# endregion

# region #* Server Functions


def setupGame(tableDimension, playerNumber):
    print(f"Iniciando jogo!")

    nJogadores = playerNumber
    dim = tableDimension

    totalDePares = dim**2 / 2
    paresEncontrados = 0

    turno = 0

    tabuleiro = novoTabuleiro(dim)
    placar = novoPlacar(nJogadores)


def waitForPlayers():
    print(f"\n Esperando {nJogadores} jogadores")

    while True:
        client_socket, address = server_socket.accept()

        # ? Desnecessário porque limita conexão
        if len(client_list) >= nJogadores:
            client_socket.send(createMessage("Servidor cheio!"))
            client_socket.close()
            continue

        client_list.append(client_socket)
        print(f"Conexão com {address} estabelecida!")
        client_socket.send(createMessage(
            f"Conectado ao servidor!"))

        sendToAllClients(f"Jogadores: {len(client_list)}/{nJogadores}")
        print(f"Jogadores: {len(client_list)}/{nJogadores}")

        if len(client_list) >= nJogadores:
            sendToAllClients("Começando partida!")
            print("Começando partida!")
            break


def gameLoop():
    while True:
        sendToAllClients(client_list, f"Vez do jogador {turno+1}.\n")
        sendToExcept(turno, f"Esperando jogador...")

        print(f"Solicitando input do jogador {turno+1}")

        sendToClient(turno, f"\nEscolha uma peça:\n>")
        sendToClient(turno, REQUEST_GAME_INPUT)

        playerInput = receiveMessage(client_list[turno])
        if playerInput:
            msg = playerInput['data']
            print(f"Mensagem recebida do jogador {turno+1}: {msg}")

        time.sleep(0.5)

        turno = (turno + 1) % nJogadores


def endGame():
    pass


def terminateServer():
    server_socket.shutdown()
    server_socket.close()
# endregion


while True:
    setupGame()

    waitForPlayers()

    gameLoop()

    endGame()

terminateServer()
