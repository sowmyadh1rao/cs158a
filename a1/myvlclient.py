from socket import *

#check if prefix is int and is of correct length
def check_format(inputSentence)->bool:
    prefix=inputSentence[:2]
    try:
        stringSize = int(prefix)
    except ValueError:
        return False
    if len(inputSentence[2:]) == stringSize and inputSentence[2:].isascii():
        return True
    else:
        return False

#server and port to connect to
serverName = 'localhost'
serverPort = 12000

#get user Input
sentence = input('Enter a lowercase sentence: ')
length = int(sentence[:2])

#test if Input is of the right format
if check_format(sentence):
    # connect to server using TCP
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    clientSocket.sendall(sentence.encode())

#combine result from Server into one full sentence
    fullSentence = ''

    while length > 0:
        modifiedSentence = clientSocket.recv(64)
        if not modifiedSentence:
            break
        length = length - len(modifiedSentence.decode())
        fullSentence = fullSentence + modifiedSentence.decode()

    #Print the result
    print('From Server:',fullSentence)
    clientSocket.close()

else:
    print('Wrong format: Try Again')

