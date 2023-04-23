import socket


#! SETTAR IP DO HOST <<<<<
HOST = "26.44.38.67"
PORT = 50000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# * Message Settings
# * Constantes utilizadas tanto por Cliente quanto por Servidor
# * Definem o tipo de mensagem que irá receber, seja ele um input ou tipo de dado do jogo


HEADER_LENGTH = 10
REQUEST_USERNAME = "#REQUEST_USERNAME_INPUT"
REQUEST_GAME_INPUT = "#REQUEST_GAME_INPUT"
SEND_STATUS = "#STATUS"
SEND_TABULEIRO = "#TABULEIRO"
SEND_PLACAR = "#PLACAR"
SEND_VEZ = "#VEZ"


# ? Função que garante que você está recebendo uma mensagem do tamanho correto
# ? para acessar o dado da mensagem, lembre de garantir que ela chegou
# ? E acesse por receiveMessage(...)['data']
# ? Caso não precise do header da mensagem na implementação
# ? implemente diretamente no retorno da função o acesso ao ['data']


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


while True:
    # Exemplo de Utilização do Código (Incompleto):
    # ? Se quiser modificar o estilo de implementação, avisa pra gente! Vai mudar alguma lógica com certeza
    # ? Servidor atualmente é incrívelmente dependente em receber exatamente o esperado por parte do client

    # Cliente constantemente lê mensagens do servidor
    msg = receiveMessage(client_socket)

    # Verifica se a mensagem foi recebida corretamente (False ou {header, data})
    if msg:
        # Acessando dado da mensagem
        msg = msg['data']
        if msg == REQUEST_GAME_INPUT:
            # Caso mensagem seja sinalização de INPUT, enviar para Servidor seu Input (Ele está travado esperando)
            msgToSend = createMessage(input("Enviar para server: "))
            if msgToSend:
                client_socket.send(msgToSend)
        elif msg == SEND_STATUS:
            # Caso seja uma sinalização de envio de dados, solicitar uma nova mensagem que já está sendo enviada pelo servidor
            msg = receiveMessage(client_socket)
            if msg:
                status = msg['data']
                # * Fazer o que quiser com o status
                pass
        elif msg == SEND_PLACAR:
            # Caso seja uma sinalização de envio de dados, solicitar uma nova mensagem que já está sendo enviada pelo servidor
            msg = receiveMessage(client_socket)
            if msg:
                placar = msg['data']
                # * Fazer o que quiser com o placar
                pass
