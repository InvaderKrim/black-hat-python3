#!/usr/bin/python3

import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print(f"[*] Listening on {bind_ip}:{bind_port}")

def handle_client(client_socket):

    #print out what the client sends
    request = client_socket.recv(1024)
    request = request.decode()

    print(f"[*] Received: {request}")

    #send return message
    ack = "ACK!".encode()
    client_socket.send(ack)

    client_socket.close()

while True:

    client,addr = server.accept()

    print(f"[*] Accepted connection from: {addr[0]}:{addr[1]}")

    #spin up client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()
