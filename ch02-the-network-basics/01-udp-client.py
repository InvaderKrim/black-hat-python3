#!/usr/bin/python3

import socket

#define target ip address and port
target_server = ("127.0.0.1",80)

#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(target_server)

#send some data
message = "AAABBBCCC".encode()
client.sendto(message,target_server)

#receive some data
data,addr = client.recvfrom(4096)
data = data.decode()

print(data)
