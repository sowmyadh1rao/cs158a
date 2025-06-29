import threading
import socket

# mychatServer.py

# This chat server accepts connection for the chat clients.
# Client then sends messages to the Chat Server.
# Chat server forwards the messages to the other chat clients.

list_of_clients={}
buf_size=1024
port_index =1


# forwards messages sent by one client to all other clients

def forward_messages_to_other_clients(message, sender):
    for client in list_of_clients:
        if client!= sender:
            try:
                client.send(message.encode())
            except:
                print(f'Could not send message {message} to client {client}')


def get_message_from_client(cnSocket):
    # addr is a list and client port number is in index 1
    address=list_of_clients[cnSocket]
    cp = address[port_index]

    # continuously read messages from the client socket
    while True:
        try:
            # buffer size is 1024. Receive 1024 bytes from the client and process it
            m = cnSocket.recv(buf_size).decode()
            if not m:
                # if client disconnects, then break from this loop
                break
            # if messages stripped, then exit from the loop
            if m.strip().upper() == "EXIT":
                print(f"Exited {cp}")
                break
            print(f"{cp}: {m}")
            forward_messages_to_other_clients(f"{cp}: {m}", cnSocket)
        except:
            # Exception in processing message disconnect from the server
            print(f'Client {cp} Disconnected from server')
            break
    # safely close the client socket
    cnSocket.close()
    del list_of_clients[cnSocket]
    print(f'Client {cp} Disconnected from server')



def begin():
    # Create and configure the server socket
    ser_port = 12000
    ser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ser_socket.bind(('', ser_port))
    ser_socket.listen()

    print(f"Server is up and listening on Port : {ser_port}")

    # Accept client Connection continuously
    while True:
        try:
            cnSocket, address = ser_socket.accept()

            # Save client socket and address in a map to get it later.

            list_of_clients[cnSocket]=address
            print(f"Client {address} connected.")
            threading.Thread(target=get_message_from_client, args=(cnSocket,),daemon=True).start()
        except:
            print(f'A client Disconnected from server')


if __name__ == '__main__':
    begin()

