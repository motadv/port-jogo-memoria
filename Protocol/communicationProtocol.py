import socket

# Módulo de padronização de protocolos do jogo da memória

# Importe fazendo from Protocol.communicationProtocol import *

# * Constantes de comunicação
# Dita o tamanho fixo em caracteres que o header terá
HEADER_LENGTH = 10

# Separador entre flag de comunicação e dado da mensagem
SEPARATOR = "\./"

# Flags de comunicação, ditam qual tipo de mensagem está sendo recebida
# SEND_ comunica que o envio de dados
SEND_MESSAGE = "#MSG"
SEND_STATUS = "#STATUS"
# ! TABULEIRO, PLACAR E VEZ NÃO SÃO MAIS UTILIZADOS E NÃO DEVEM SER TRATADOS
# ! AO INVÉS DELES, ENVIA-SE O DICT CONTENDO OS 3 NO STATUS
# SEND_TABULEIRO = "#TABULEIRO"
# SEND_PLACAR = "#PLACAR"
# SEND_VEZ = "#VEZ"
SEND_WAIT = "#WAIT"
SEND_RESULT = "#RESULT"
SEND_INPUT_ERROR = "#INPUT_ERROR"

# REQUEST_ comunica solicitação de input
REQUEST_USERNAME = "#REQUEST_USERNAME_INPUT"
REQUEST_GAME_INPUT = "#REQUEST_GAME_INPUT"

# ERROR_ comunica input inválido e solicita novo input
ERROR_INVALID_FORMAT = "#INVALID_FORMAT"
ERROR_IOOB = "#iOOB"
ERROR_JOOB = "#jOOB"
ERROR_OPEN_CARD = "#CARD_ALREADY_OPEN"

# Lista com todos os tipos de erros
ERROR_TYPE_LIST = [
    ERROR_INVALID_FORMAT,
    ERROR_IOOB,
    ERROR_JOOB,
    ERROR_OPEN_CARD,
]

# SIGNAL_ comunica jogada bem ou mal sucedida e envio da jogada
# Desde a ultima mudança de flags na mensagem, SIGNAL_ envia a
# ultima jogada feita e por isso também podem ser referenciados por
# SEND_
SIGNAL_INPUT_SUCCESS = "#SUCCESS"
SIGNAL_INPUT_FAIL = "#FAIL"

SEND_INPUT_SUCCESS = SIGNAL_INPUT_SUCCESS
SEND_INPUT_FAIL = SIGNAL_INPUT_FAIL

# Toda mensagem é composta de uma flag e uma mensagem
# É adicionado no começo de qualquer mensagem um header de tamanho fixo
# Esse header dita o tamanho total à ser recebido. Isso foi feito para
# garantir a mensagem individual no fluxo de comunicação TCP pois algumas
# mensagens eram agrupadas automaticamente pela API ou pelo transporte


def createMessage(message, flag: str = ''):
    # Se nenhuma flag for passada, a default é SEND_MESSAGE
    flag = flag if flag else SEND_MESSAGE
    if type(message) is str:
        message = message.encode()
    flagHeader = (flag + SEPARATOR).encode()
    data = flagHeader + message
    header = f'{len(data):<{HEADER_LENGTH}}'.encode()
    return header + data


# Toda mensagem recebida será destrinchada automaticamente em um objeto
# de mensagem contendo 3 campos, "header", "flag" e "data"
# "header" é somente o tamanho total de flag+data e pode ser ignorado
# "flag" dita a o tipo de comunicação recebida
# "data" é o conteúdo da mensagem em si


def receiveMessage(senderSocket: socket.socket):
    while True:
        try:
            message_header = senderSocket.recv(HEADER_LENGTH)

            if not len(message_header):
                return False

            message_length = int(message_header.decode())
            message = senderSocket.recv(message_length).decode()
            flag, data = message.split(SEPARATOR)
            return {
                "header": message_header,
                "flag": flag,
                "data": data
            }
        except socket.timeout:
            pass
        except Exception as exc:
            raise (exc)
