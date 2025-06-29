import threading
from socket import *

#server and port to connect to
serverName = 'localhost'
serverPort = 12000
# SOCK_STREAM means that this is a TCP socket
clientSocket = socket(AF_INET, SOCK_STREAM)
# Buffer size for receiving messages.
buf_size=1024

# Chat Server sends the messages that it receives from other Chat Clients
# Chat Client must Print the message received from the server
# Chat Clients continuously listens to the server and Print and messages received from the Server
def display_messages_from_server():
   while True:
       try:
           # receive the chats sent by the serv
           m =  clientSocket.recv(buf_size).decode()
           print(m)
       except:
           print('Error receiving msg from Server')
           break

# Chat client must connect to the server on start up
# And send messages that the user types to the server
def begin():
    try:
        clientSocket.connect((serverName, serverPort))
    except:
        print(f'Error connecting to server {serverName} on port {serverPort}')
        return

    print('Successfully connected to the server. Type "exit" to leave.')
    threading.Thread(target=display_messages_from_server, args=(), daemon=True).start()

    #Continuously forward messages received from the user to the server.
    while True:
        input_text = input()
        if input_text.strip().upper()=="EXIT":
            clientSocket.send(input_text.encode())
            break
        try:
            clientSocket.sendall(input_text.encode())
        except:
            print('Error sending message to the server, So will Break')
            break

    # Close Client Socket safely
    clientSocket.close()
    print('Client Socket Closed')

# execution begins here
if __name__ == '__main__':
    begin()
