import random
import pickle
import threading
from constServer import *
import socket, sys, argparse


class Server():

    def __init__(self, nBits=5, portNo=8080):
        host = '0.0.0.0'
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.bind((host, portNo))

        self.members = {}
        self.addresses = {}
        self.pid = {}
        self.nBits = nBits
        self.MAXPROC = pow(2, nBits)

    def join(self, subgroup):
        try:
            members = self.members[subgroup]
        except KeyError:
            self.members[subgroup] = members = []

        newpid = random.choice(list(set([i for i in range(self.MAXPROC)]) - set(members)))
        self.members[subgroup].append(newpid)

        try:
            self.members['members'].append(newpid)
        except KeyError:
            self.members['members'] = []
            self.members['members'].append(newpid)
        return newpid

    def leave(self, subgroup, pid):
        assert pid in self.members['members'], ''
        self.members[subgroup].remove(pid)
        self.members['members'].remove(pid)


    def exists(self, pid):
        return pid in self.members['members']

    def bind(self, node, pid):
        self.addresses[pid] = node

    def subgroup(self, subgroup):
        return [i for i in self.members[subgroup]]

    def manageClient(self, conn, node):
        while True:
            msg = conn.recv(BUFFERSIZE)
            if len(msg) == 0:
                conn.close()
                break
            command, message = pickle.loads(msg)

            #print(command, message)

            if command == JOIN:
                pid = self.join(message)
                self.pid[node] = pid
                print(f'Server: node {node} has joined with id {pid}')
                conn.send(pickle.dumps(pid))
            elif command == LEAVE:
                pid = self.pid[node]
                self.leave(message, pid)
                conn.close()
            elif command == EXISTS:
                pid = self.pid[node]
                ans = self.exists(pid)
                conn.send(pickle.dumps(ans))
            elif command == SUBGROUP:
                arr = self.subgroup(message)
                conn.send(pickle.dumps(arr))
            elif command == NBITS:
                conn.send(pickle.dumps(self.nBits))
            elif command == BIND:
                pid = self.pid[node]
                self.bind(message, pid)
                print(f'Server: node {node} binded to address {message}')
            elif command == ADDRESS:
                print(f'Server: Asked for address of node {message}')
                conn.send(pickle.dumps(self.addresses[message]))
            elif command == DISCONNECT:
                conn.close()
                break

    def run(self):
        self.socket.listen()

        while True:
            conn, node = self.socket.accept()
            threading.Thread(target=self.manageClient, args=(conn, node)).start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8080, required=False, type=int, help='Server incoming communications port')
    parser.add_argument('--bits', default=5, required=False, type=int, help='Number of chord bits')
    args = parser.parse_args()

    port = args.port
    bits = args.bits

    server = Server(nBits=bits, portNo=port)
    server.run()

