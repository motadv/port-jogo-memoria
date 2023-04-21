import socket

HOST = "26.44.38.67"
PORT = 50000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

REQUEST_INPUT = "REQUEST_INPUT"

while True:
    msg = s.recv(1024).decode()  # ? Definir tamanho da mensagem

    if msg == REQUEST_INPUT:
        sendMessage = input("Enviar para server: ")
        s.send(sendMessage.encode())
        continue

    print(msg)
