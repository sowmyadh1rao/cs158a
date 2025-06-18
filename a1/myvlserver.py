from socket import *
import select

#check if prefix is int and return prefix
def check_format(inputSentence)->(bool,int):
    prefix=inputSentence[:2]
    try:
        stringSize = int(prefix)
    except ValueError:
        return (False,-1)
    return (True,stringSize)


#Server Port address
serverPort = 12000

#receive from socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))

#listen with queue size 1
serverSocket.listen(1)

while True:
   #combine the input sentence into one full sentence
   fullSentence=''
   #accept
   cnSocket,addr = serverSocket.accept()
   print('Connected from', addr)

   #receive first text data and time out if no data after 5 seconds
   timeout = 5
   sentence = ''
   r, _, _ = select.select([cnSocket], [], [], timeout)
   if r:
       sentence = cnSocket.recv(64).decode()
   else:
       print(" Listening on Socket for 5 seconds, No data available within timeout.")
   if not sentence:
       continue

   (right_format,stringSize) = check_format(sentence)
   if right_format:
        lengthSentence = stringSize
        print('msg_len', lengthSentence)
#process
        if lengthSentence <= 62:
            capSentence = sentence[2:].upper()
            if len(capSentence) == lengthSentence and capSentence.isascii():
                fullSentence = fullSentence + capSentence
            else:
                fullSentence = 'ERROR'
        else:
            capSentence = sentence[2:].upper()
            if len(capSentence) == 62:
                fullSentence = fullSentence + capSentence
                remainingLengthSentence = lengthSentence-62

                while remainingLengthSentence > 0 :
                    timeout=5
                    pendingSentence=''
                    r, _, _ = select.select([cnSocket], [], [], timeout)
                    if r:
                        pendingSentence = cnSocket.recv(64).decode()
                    else:
                        print("Listening on Socket for 5 seconds, No data available within timeout.")
                    if not pendingSentence:
                        fullSentence = 'ERROR'
                        break
                    #get the next chunk of data
                    if remainingLengthSentence >= 64 :
                        if len(pendingSentence) == 64 :
                            fullSentence = fullSentence + pendingSentence.upper()
                        else:
                            fullSentence = 'ERROR'
                        remainingLengthSentence = remainingLengthSentence - len(pendingSentence)

                    else:
                        if len(pendingSentence) == remainingLengthSentence :
                            fullSentence = fullSentence + pendingSentence.upper()
                        else:
                            fullSentence = 'ERROR'
                        remainingLengthSentence = remainingLengthSentence - len(pendingSentence)
            else:
                    fullSentence = 'ERROR'
        with cnSocket:
            print('processed',fullSentence)
            cnSocket.sendall(fullSentence.encode())
            print('msg_len_sent',len(fullSentence))
#close
   cnSocket.close()
   print('Connection Closed')
#socket close
serverSocket.close()
