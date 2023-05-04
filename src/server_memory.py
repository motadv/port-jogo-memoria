import socket
import time
import random
from Protocol.communicationProtocol import *

# * Server socket TCP

#! SETTAR IP DO HOST <<<<<
HOST = socket.gethostname()
PORT = 30000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(1)
server_socket.bind((HOST, PORT))
server_socket.listen()

client_list = []


def terminateServer():
    print("Closing server...")

    server_socket.close()


def endGame():
    for i in range(len(client_list)):
        client_list[i].close()

    client_list.clear()


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
            raise exc

    else:
        sendToAllClients(client_list, "Começando partida!")
        print("Começando partida!")
        time.sleep(2)


def sendToAllClients(clients, message="", flag=SEND_MESSAGE):
    byteMessage = createMessage(message, flag)
    print(f"Enviando para todos: {message}")
    for client in clients:
        client.send(byteMessage)


def sendToClient(client, message="", flag=SEND_MESSAGE):
    byteMessage = createMessage(message, flag)
    print(f"Enviando para cliente: {message} : {byteMessage}")
    client.send(byteMessage)


def sendToExcept(clients: list, ignoredClient, message="", flag=SEND_MESSAGE):
    # Send to all clients exepct specified in parameter
    print(f"Enviando para todos exceto um: {message}")
    byteMessage = createMessage(message, flag)
    for client in clients:
        if client != ignoredClient:
            client.send(byteMessage)


# * Funções do Jogo


def createStatus(tabuleiro, placar, vez):
    status = {
        'tabuleiro': tabuleiro,
        'placar': placar,
        'vez': vez
    }
    return status


def chooseCard(client, tabuleiro):
    try:
        # Send first input request
        sendToClient(client, flag=REQUEST_GAME_INPUT)
        _, msg = receiveMessage(client)
        playerInput = validateInput(msg)
        if playerInput not in ERROR_TYPE_LIST:
            playerInput = abrePeca(tabuleiro, playerInput)

        while playerInput in ERROR_TYPE_LIST:
            sendToClient(client, message=playerInput, flag=SEND_INPUT_ERROR)
            _, msg = receiveMessage(client)
            playerInput = validateInput(msg)
            if playerInput not in ERROR_TYPE_LIST:
                playerInput = abrePeca(tabuleiro, playerInput)
        else:
            return playerInput

    except socket.timeout:
        pass
    except Exception as exc:
        raise (exc)


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


def gameLoop(nJogadores, dim):

    vez = 0
    tabuleiro = novoTabuleiro(dim)
    placar = novoPlacar(nJogadores)
    totalDePares = dim**2 / 2
    paresEncontrados = 0

    try:
        while paresEncontrados < totalDePares:

            playerSocket = client_list[vez]
            playerNumber = vez+1

            print(f"Sending Status to all players")
            sendToAllClients(clients=client_list, message=createStatus(
                tabuleiro, placar, vez), flag=SEND_STATUS)

            print(f"Sending wait message to all players")
            sendToExcept(client_list, playerSocket,
                         str(playerNumber), flag=SEND_WAIT)

            print(f"Requesting first input from {playerNumber}")
            i1, j1 = chooseCard(playerSocket, tabuleiro)

            sendToAllClients(clients=client_list, message=createStatus(
                tabuleiro, placar, vez), flag=SEND_STATUS)

            print(f"Requesting second input from {playerNumber}")
            i2, j2 = chooseCard(playerSocket, tabuleiro)

            sendToAllClients(clients=client_list, message=createStatus(
                tabuleiro, placar, vez), flag=SEND_STATUS)

            # * Padrão decidido = ((i1,j1),(i2,j2))
            jogada = {
                "jogador": vez+1,
                "jogada": ((i1, j1), (i2, j2))
            }

            if tabuleiro[i1][j1] == tabuleiro[i2][j2]:
                # * Handle player acertar tentativa
                sendToAllClients(
                    client_list,
                    jogada,
                    SEND_INPUT_SUCCESS
                )

                incrementaPlacar(placar, vez)
                paresEncontrados += 1

                removePeca(tabuleiro, i1, j1)
                removePeca(tabuleiro, i2, j2)

                time.sleep(5)
            else:
                # * Handle player errar tentativa
                sendToAllClients(
                    client_list,
                    jogada,
                    SEND_INPUT_FAIL)

                time.sleep(3)

                fechaPeca(tabuleiro, i1, j1)
                fechaPeca(tabuleiro, i2, j2)

                vez = (vez + 1) % nJogadores

        maxScore = max(placar)
        vencedores = []

        for i in range(nJogadores):
            if placar[i] == maxScore:
                vencedores.append(i+1)

        sendToAllClients(client_list, vencedores, SEND_RESULT)

    except socket.timeout:
        pass
    except Exception as exc:
        raise (exc)


# * SERVIDOR INICIADO
print(f"Servidor Iniciado!")


try:
    nJogadores = int(input("Quantos jogadores na mesa? (Enter para 1)\n>"))
except:
    print("Definindo valor padrão = 1")
    nJogadores = 1

try:
    dim = int(input("Qual a dimensão do tabuleiro? (Par < 10, Enter para 4)\n>"))
    if dim >= 10 or dim % 2 == 1:
        print("Tabuleiro deve ser menor que 10x10 e de tamanho par")
        print("Definindo valor padrão = 4")
        dim = 4
except:
    print("Tabuleiro deve ser menor que 10x10 e de tamanho par")
    print("Definindo valor padrão = 4")
    dim = 4

    # nJogadores = int(input("Insira o número máximo de jogadores\n >"))
    # dim = int(input("Insira a dimensão do tabuleiro de jogo\n >"))


while True:
    try:
        print(f"\nComeçando novo jogo!\n")
        print(f"Máximo de jogadores: {nJogadores}")
        print(f"Dimensão do tabuleiro: {dim}")

        #  Aceitando N clientes
        print(f"Esperando {nJogadores} jogadores")
        acceptClients(nJogadores)

        gameLoop(nJogadores, dim)

        endGame()

    except Exception as exc:
        print("\n EXCEPTION RAISED:")
        print(str(exc))
        print()
        pass
    finally:
        terminateServer()
        break
