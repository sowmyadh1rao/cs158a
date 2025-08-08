import socket
import ssl

RESPONSE_FILE_NAME = 'response.html'

def main():

    # connect to server www.google.com on port 443
    host_name = "www.google.com"
    port_number = 443

    # send HTTP to host_name/port_number
    http_request = f"GET / HTTP/1.1\r\nHost: {host_name}\r\nConnection: close\r\n\r\n"
    http_response = b""

    # create ssl
    context = ssl.create_default_context()
    with socket.create_connection((host_name, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=host_name) as ssl_sock:
            # Send an http get request
            ssl_sock.sendall(http_request.encode())

            # receive data from socket
            while True:
                received_data = ssl_sock.recv(1024)
                if not received_data:
                    break
                http_response += received_data

    # Save the response to a RESPONSE_FILE_NAME
    try:
        with open(RESPONSE_FILE_NAME, "wb") as f:
            f.write(http_response)
        print("HTML response saved in "+RESPONSE_FILE_NAME)
    except FileNotFoundError:
        print("Enter a valid file name")

if __name__ == "__main__":
    main()
















