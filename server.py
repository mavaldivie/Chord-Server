import random
import pickle
import threading
from constServer import *
import socket, sys


class Server():

    def __init__(self, nBits=5, hostIP='localhost', portNo=8080):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.bind((hostIP, portNo))

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
        return

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
                #print(f'binded {pid} to {msg}')
            elif command == ADDRESS:
                conn.send(pickle.dumps(self.addresses[message]))
            elif command == DISCONNECT:
                conn.close()
                break

    def run(self):
        self.socket.listen()

        while True:
            conn, node = self.socket.accept()
            threading.Thread(target=self.manageClient, args=(conn, node)).start()







    '''
    def sendTo(self, destinationSet, message, caller):
        caller = self.pid[caller]
        assert caller in self.members['members'], ''
        for i in destinationSet:
            assert str(i) in self.members['members'], ''
            self.channel.rpush(f'{str(caller)}:{str(i)}', pickle.dumps(message))

    def sendToAll(self, message):
        caller = self.osmembers[os.getpid()]
        assert self.channel.sismember('members', str(caller)), ''
        for i in [int(j) for j in self.channel.smembers('members')]:
            self.channel.rpush(f'{str(caller)}:{str(i)}', pickle.dumps(message))

    def recvFromAny(self, timeout=0):
        caller = self.osmembers[os.getpid()]
        assert self.channel.sismember('members', str(caller)), ''
        members = [int(i) for i in self.channel.smembers('members')]
        xchan = [f'{str(i)}:{str(caller)}' for i in members]
        msg = self.channel.blpop(xchan, timeout)
        if msg:
            #print(msg[0].decode())
            #x = msg[0].split("'")[1]
            #y = pickle.loads(msg[1])
            return [msg[0].decode().split(":")[0], pickle.loads(msg[1])]

    def recvFrom(self, senderSet, timeout=0):
        caller = self.osmembers[os.getpid()]
        assert self.channel.sismember('members', str(caller)), ''
        for i in senderSet:
            assert self.channel.sismember('members', str(i)), ''
        xchan = [f'{str(i)}:{str(caller)}' for i in senderSet]
        msg = self.channel.blpop(xchan, timeout)
        if msg:
            return [msg[0].decode().split(":")[0], pickle.loads(msg[1])]
    '''


if __name__ == '__main__':
    host, port = sys.argv[1].split(':')
    port = int(port)

    bits = 5
    if len(sys.argv) > 2:
        bits = sys.argv[2]

    server = Server(nBits=bits, hostIP=host, portNo=port)
    server.run()

