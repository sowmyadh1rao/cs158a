import socket
import sys
import threading
import uuid
import json
import time


#CONFIG_FILE_NAME="config3.txt"
LOG_FILE_NAME="log3.txt"
# Format of the Message (UUID , flag) as per the assignment instructions
class Message:
    def __init__(self, uid: uuid.UUID, flag: int):
        self.uuid = uid
        self.flag = flag

    def to_json(self):
        return json.dumps({"uuid": self.uuid, "flag": self.flag},default=str)

    @staticmethod
    def convert_message_from_json( json_str: str):
        obj = json.loads(json_str)
        return Message(uuid.UUID(obj["uuid"]), obj["flag"])

#Server with all the functionality
class Node:
    def __init__(self, h, p, peer_host, peer_port):
        self.UUID = uuid.uuid4()
        self.host = h
        self.port = p
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock = None
        self.state = 0
        self.leader_id = None
        self.initiated = False
        threading.Thread(target=self._start_server).start()
        self.send_myUUID()

    # Sends my uuid to the peer host. Sleep and Retry connection to Peer Server in case server is not up.
    def send_myUUID(self):
        with open(LOG_FILE_NAME, "a") as f:
            f.write(f"Sent:(MY UUID) uuid={self.UUID}, flag={self.state}\n")
        time.sleep(10)
        print('My UUID',self.UUID)
        attmpt = 0
        max_atmt = 5
        while attmpt < max_atmt:
            try:
                self.peer_sock.connect((self.peer_host, int(self.peer_port)))
                self.peer_sock.send(Message(self.UUID, self.state).to_json().encode())
                self.peer_sock.send("\n".encode())
                self.initiated = True
                print("Connected to Peer server- ",self.peer_host, " : " ,int(self.peer_port))
                break
            except ConnectionRefusedError:
                attmpt += 1
                wait_count = 2 ** attmpt
                print(f"Connection failed. Retrying in {wait_count} seconds...")
                time.sleep(wait_count)
        else:
            print("Server is unavailable after multiple attempts.")

    # Send message to the peer . Log with "Sent:" in the log file
    def send_message(self,input_message: Message):
        with open(LOG_FILE_NAME, "a") as f:
            f.write(f"Sent: uuid={input_message.uuid}, flag={input_message.flag}\n")
            while not self.initiated:
                time.sleep(1)

            self.peer_sock.send(input_message.to_json().encode())
            self.peer_sock.send("\n".encode())
            self.initiated = True

    # Write to the log but no messages sent to the peer node
    def log_on_noaction(self,input_message: Message, compareString : str):
        with open(LOG_FILE_NAME, "a") as f:
            line = f"Received and Ignored: uuid={input_message.uuid}, flag={input_message.flag}, {compareString}, state={self.state}"
            if self.state == 1:
                line += f", leader is decided to {self.leader_id}"
            f.write("\n" + line + "\n")

    def process_client_request(self,input_message: Message):
        #Compare if the input uuid is same , greater or less
        cmp = "same" if input_message.uuid == self.UUID else ("greater" if input_message.uuid > self.UUID else "less")

        self.log_on_receive(input_message,cmp)

        if self.state == 0 :
            if input_message.flag == 0:
                if input_message.uuid == self.UUID:
                    self.state = 1
                    self.leader_id = input_message.uuid
                    input_message.flag = 1
                    self.send_message(input_message)
                elif input_message.uuid > self.UUID:
                    self.send_message(input_message)
                elif not self.initiated:
                    input_message.uuid = self.UUID
                    self.send_message(input_message)
                else:
                    self.log_on_noaction(input_message,cmp)
            else:
                self.leader_id = input_message.uuid
                self.state = 1
                self.send_message(input_message)
        else:
            self.log_on_noaction(input_message,cmp)

    # Received input Message from the client
    def log_on_receive(self, m: Message, c: str):
        with open(LOG_FILE_NAME, "a") as f:
            line = f"Received: uuid={m.uuid}, flag={m.flag}, {c}, state={self.state}"
            if self.state == 1:
                line += f"self.state == 1, leader is decided to {self.leader_id}"
            f.write("\n" + line + "\n")

    # \n is used as a delimiter to indicate end of Json (uuid,flag)
    def recv_line(self,read_sock, bf=b'', bsize=1024):
        while True:
            d = read_sock.recv(bsize)
            if not d:
                return None, bf
            bf += d
            if b'\n' in bf:
                line, _, rest = bf.partition(b'\n')
                return line.decode(), rest

    def server_shutdown(self):
        print(f"leader is {self.leader_id}")
        self.peer_sock.close()
        self.client_sock = None
        self.server_sock.close()

    # Server started and waiting for client to join. The messages from the clients are then processed
    def _start_server(self):
        print("Starting server ... ")
        try:
            self.server_sock.bind((self.host, int(self.port)))
            self.server_sock.listen(1)
            client_sock = None
            addr = None
            print(f"Server started on {self.host}:{self.port}, waiting for connection...")
            client_sock, addr = self.server_sock.accept()
            print(f"Connection from {addr}")

            while True:
                try:
                    buffer = b''
                    while True:
                        result, buffer = self.recv_line(client_sock)
                        if result is None:
                            break

                        msg = Message.convert_message_from_json(str(result))
                        self.process_client_request(msg)

                except Exception as a:
                    print(f'Error receiving or processing client messages :{a}')
                    break


        except Exception as e:
            print(f"Server failed to start: {e}")
        finally:
            self.server_sock.close()

# Extract host, port, peer host, peer port from the config file name given in the Command line arguement
def extract_from_file(config_path:str):
        with open(config_path) as given_file:
            h, p = given_file.readline().strip().split(',')
            p_h, p_p = given_file.readline().strip().split(',')
            return h.strip(),p.strip(),p_h.strip(),p_p.strip()



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python myleprocess.py <arg1> <arg2>")
        sys.exit(1)

    CONFIG_FILE_NAME = sys.argv[1].strip()
    LOG_FILE_NAME = sys.argv[2].strip()

    print("Config file name:",CONFIG_FILE_NAME)
    print("Log file name:",LOG_FILE_NAME)

    (host, port, peer_h, peer_p) = extract_from_file(CONFIG_FILE_NAME)

    print("Host: ", host)
    print("Port: ", port)
    print("Peer Host: ", peer_h)
    print("Peer Port: ", peer_p)
    n=Node(host,port,peer_h,peer_p)

    while n.state == 0 or n.leader_id is None:
        time.sleep(1)
    time.sleep(2)

    print('----Leader ID elected---- ',n.leader_id)

    with open(LOG_FILE_NAME, "a") as fLast:
        l = f" Leader is decided to {n.leader_id}"
        fLast.write("\n" + l + "\n")





