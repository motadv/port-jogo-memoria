# GENERIC_MESSAGE = "#MSG"
# HEADER_LENGTH = 10

# SEPARATOR = "\./"


# def createMessage(message: str, flag: str = GENERIC_MESSAGE):
#     flagHeader = flag + SEPARATOR
#     data = flagHeader.encode() + message.encode()
#     header = f'{len(data):<{HEADER_LENGTH}}'.encode()
#     return header + data


# data = createMessage("Teste")


# header, info = data.decode().split()
# flag, message = info.split(sep=SEPARATOR)

# print(header)
# print(info)
# print(f'{flag} ||| {message}')

# # MSG ||| Teste
# # MSG\./Teste

if not int(""):
    print("False")
else:
    print("True")
