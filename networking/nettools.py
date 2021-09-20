#!/usr/bin/python3
from _typeshed import Self
import argparse 
import socket 
import shlex 
import subprocess 
import sys 
import textwrap 
import threading
from typing_extensions import TypeVarTuple

def execute(cmd):
    # runs the command and returns the output
    cmd = cmd.strip()
    if not cmd:
        return

    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)
    return output.decode()

class Netcat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1 ) 

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        else:
            try:
                while True:
                    reciv_len =1 
                    response = ''
                    data = self.socket.recv(4096)
                    reciv_len = len(data)
                    response += data
                    if(reciv_len < 4096):
                        break
                    if response:
                        print(f'{response}')
                        buffer = input('> ')
                        buffer += '\n'
                    self.socket.send(buffer.encode()) 

            except KeyboardInterrupt:
                print("[-] User terminated")
                self.socket.close()
                sys.exit()
    
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        while True:
            try:
                client_socket = self.socket.accept()
                client_thread = threading.Thread(target=self.handle , args= client_socket)
                client_thread.start()
            except :
                print("[-] Something went Wrong")
                self.socket.close()
                sys.exit()


if __name__ == '__main__':
    # We use the argparse module from the standard library to create a command line interface
    parser = argparse.ArgumentParser(description='Net Tools',  formatter_class=argparse.RawDescriptionHelpFormatter,  #
    epilog=textwrap.dedent(
        '''
        netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell 
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file 
        netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd" # execute command 
        echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135 
        netcat.py -t 192.168.1.108 -p 5555 # connect to server
        '''
    ))

    '''
    - `-c` setup interactive shell
    - `-e` executes one specific command
    - `-h` indicates that a listner should be setup
    - `-p` specifies the port on which to communicate
    - `-t` specifies the target IP
    - `-u` specifies the name of file to upload
    - the `-c` , `-e` and `-u` args imply the `-l` argument because those args apply to only listener side of communication
    - the sender side makes the connection to listener so it needs only the `-t` and `-p` args to define the target listener

    '''

    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen') 
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port') 
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP') 
    parser.add_argument('-u', '--upload', help='upload file') 

    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        sys.stdin.read()

    nc = Netcat(args , buffer.encode()) 
    nc.run()