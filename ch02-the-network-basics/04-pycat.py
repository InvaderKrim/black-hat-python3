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

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination

    if not len(sys.argv[1:]):
        usage()
    elif str(sys.argv[1:]).find("-") == -1:
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

main()
