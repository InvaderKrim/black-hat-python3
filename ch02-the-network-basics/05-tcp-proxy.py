#!/usr/bin/python3

import sys
import socket
import threading

def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((local_host,local_port))
    except:
        print ("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print ("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
        
    print ("[*] Listening on %s:%d" % (local_host, local_port))
    
    server.listen(5)
    
    while True:
        print("in the while loop")
        client_socket,addr = server.accept()
        print("client socket " + str(client_socket))
        print("client addr " + str(addr))
        #print out the local connection information 
        print("[==>] Received incoming connection %s:%d" % (addr[0],addr[1]))
        
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket,remote_host,remote_port,receive_first))
        
        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    #connect to the remote host
    print("in proxy handler function")
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("connecting...")
    remote_socket.connect((remote_host,remote_port))
    
    #receive data from the remote end if necessary
    if receive_first:
        print("in receive_first if block")
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        #send it to our response handler
        remote_buffer = response_handler(remote_buffer)
        
        #if we have data to send to our local client, send it
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)
            
    while True:
        #read from local host
        local_buffer = receive_from(client_socket)
        
        if len(local_buffer):
            print("[==>] Received %d bytes from localhost." % len(local_buiffer))
            hexdump(local_buffer)
            
            #send it t oour request handler
            local_buffer = request_handler(local_buffer)
            
            #send off the data to the remote host
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote")
            
            #receive back the response
            remote_buffer = receive_from(remote_socket)
            
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            
            #send to our response handler
            remote_buffer = response_handler(remote_buffer)
            
            #send the response to the local socket
            client_socket.send(remote_buffer)
            
            print("[<==] Sent to localhost.")
            
        #if no more data on either side, close the connections
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            
            break
        
def hexdump(src, length=16):
    print("in hex_dump function")
    print("src var " + str(src))
    result = []
    digits = 4 if isinstance(src, str) else 2
    
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = " ".join(["%0*X" % (digits, ord(x)) for x in s.decode("ascii")])
        text = "".join([x if 0x20 <= ord(x) < 0x7F else "." for x in s.decode("ascii")])
        result.append("%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text))
        
    print("\n".join(result))
    
def receive_from(connection):
    buffer = b''
    
    #we set a 2 second timeout; depending on your 
    #target this need to be adjusted
    connection.settimeout(20)
    print("in receive_from function")
    print("connection variable" + str(connection))
    try:
        #keep reading into the buffer until there's no more data
        #or we time out
        while True:
            data = connection.recv(4096)
            print("data" + str(data))
            if not data: print("HITTING BREAK POINT")
            if not data:
                break
            
            buffer += data
            print("buffer in progress: " + str(buffer))
    except:
        pass
    print("final buffer value: " + str(buffer))
    print ("returning buffer")
    return buffer

#modify any requests destined for the remote host
def response_handler(buffer):
    #perform packet modifications
    return buffer

def response_handler(buffer):
    #perform packet modifications
    return buffer
        
def main():
    
    #no fancy command-line parsing here
    if len(sys.argv[1:]) != 5:
        print("Usage: ./05-tcp-proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./05-tcp-proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
        
    #setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    #set up remote targets
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    #this tells our proxy to connect and receive data
    #before sending to the remote host
    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    elif "False" in receive_first:
        receive_first = False
    else:
        print("Usage: ./05-tcp-proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./05-tcp-proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
        
    #spin up listening socket
    server_loop(local_host,local_port,remote_host,remote_port,receive_first)
    
main()
    
