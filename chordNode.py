import server #-
import random, math #-
from constChord import * #-
from constServer import *
import socket, zmq
import pickle, sys, time, threading

#-
class ChordNode:
#-
  def __init__(self, serverHost, serverPort, nodeHost, nodePort):
    self.nodeIP = f'tcp://{nodeHost}:{nodePort}'
    self.context = zmq.Context()
    self.listenSocket = self.context.socket(zmq.REP)
    self.listenSocket.bind(self.nodeIP)
    self.talkSocket = self.context.socket(zmq.REQ)

    self.serverIP = (serverHost, serverPort)
    self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    self.socket.connect(self.serverIP)

    self.socket.send(pickle.dumps((JOIN, 'node')))
    self.nodeID = pickle.loads(self.socket.recv(BUFFERSIZE))  # Find out who you are         #-

    self.socket.send(pickle.dumps((NBITS, ' ')))
    self.nBits   = pickle.loads(self.socket.recv(BUFFERSIZE))              # Num of bits for the ID space #-
    self.MAXPROC = pow(2, self.nBits)                                      # Maximum num of processes     #-

    self.nodeIP = f'tcp://{nodeHost}:{nodePort}'
    self.socket.send(pickle.dumps((BIND, self.nodeIP)))

    self.FT      = [None for _ in range(self.nBits+1)]                     # FT[0] is predecessor #-
    self.nodeSet = []                                                      # Nodes discovered so far     #-
    self.addresses = {}

    self.running = True

  def subgroup(self, subgroup):
    self.socket.send(pickle.dumps((SUBGROUP, subgroup)))
    return pickle.loads(self.socket.recv(BUFFERSIZE))

  def address(self, pid):
    try:
      add = self.addresses[pid]
    except KeyError:
      self.socket.send(pickle.dumps((ADDRESS, pid)))
      add = pickle.loads(self.socket.recv(BUFFERSIZE))
      self.addresses[pid] = add
    return add

  def inbetween(self, key: int, lwb: int, upb: int):                                         #-
    if lwb <= upb:                                                            #-
      return lwb <= key and key < upb                                         #-
    else:                                                                     #- 
      return (lwb <= key and key < upb + self.MAXPROC) or (lwb <= key + self.MAXPROC and key < upb)                        #-
#-
  def addNode(self, pid):
    if pid in self.nodeSet: return
    self.nodeSet.append(pid)
    self.nodeSet.sort()

  def delNode(self, nodeID):                                                  #-
    assert nodeID in self.nodeSet, ''                                         #-
    del self.nodeSet[self.nodeSet.index(nodeID)]                              #-
    self.nodeSet.sort()                                                       #-
#-
  def finger(self, i):
    succ = (self.nodeID + pow(2, i-1)) % self.MAXPROC    # succ(p+2^(i-1))
    lwbi = self.nodeSet.index(self.nodeID)               # own index in nodeset
    upbi = (lwbi + 1) % len(self.nodeSet)                # index next neighbor
    for k in range(len(self.nodeSet)):                   # go through all segments
      if self.inbetween(succ, self.nodeSet[lwbi]+1, self.nodeSet[upbi]+1):
        return self.nodeSet[upbi]                        # found successor
      (lwbi,upbi) = (upbi, (upbi+1) % len(self.nodeSet)) # go to next segment
    return None                                                                #-

  def recomputeFingerTable(self):
    self.FT[0]  = self.nodeSet[self.nodeSet.index(self.nodeID)-1] # Predecessor
    self.FT[1:] = [self.finger(i) for i in range(1,self.nBits+1)] # Successors

  def localSuccNode(self, key): 
    if self.inbetween(key, self.FT[0]+1, self.nodeID+1):                      # key in (FT[0],self]
      return self.nodeID                                                      # node is responsible
    elif self.inbetween(key, self.nodeID+1, self.FT[1]):                      # key in (self,FT[1]]
      return self.FT[1]                                                       # successor responsible
    for i in range(1, self.nBits+1):                                          # go through rest of FT
      if self.inbetween(key, self.FT[i] + 1, self.FT[(i+1) % (self.nBits + 1)]):
        return self.FT[i]                                                     # key in [FT[i],FT[i+1])
    return self.FT[-1]

  def recomputeDaemon(self):
    while self.running:
      others = self.subgroup('node')
      if self.nodeID in others:
        others.remove(self.nodeID)
      #print(others)
      for i in others:  # -
        self.addNode(i)  # -
      self.recomputeFingerTable()  # -
      time.sleep(len(self.nodeSet) / 10)

  def run(self): #-
    self.nodeSet.append(self.nodeID) #-

    self.thread = threading.Thread(target=self.recomputeDaemon)
    self.thread.start()

    print(f'node #{self.nodeID}')
    print(f'address {self.nodeIP}')

    while True: #-
      msg = pickle.loads(self.listenSocket.recv())
      sender  = msg[0]              # Identify the sender #-
      command = msg[1]              # And the actual request #-
      message = msg[2]

      print(msg)

      if command == STOP: #-
        self.listenSocket.send(pickle.dumps((self.nodeID, DONE, '')))
        self.running = False
        break #-
      if command == LOOKUP_REQ:                       # A lookup request #-
        nextID = self.localSuccNode(message)          # look up next node #-
        print(f'sending LOOKUP_REP to {sender}: {nextID}')
        self.listenSocket.send(pickle.dumps((self.nodeID, LOOKUP_REP, nextID)))  # return to sender #-
      elif command == CONNECT: #-
        if not sender in self.nodeSet and sender in self.subgroup('node'):  # -
          self.addNode(sender)  #
        self.listenSocket.send(pickle.dumps((self.nodeID, DONE, '')))
      self.recomputeFingerTable() #-

    print('FT[','%04d'%self.nodeID,']: ',['%04d' % k for k in self.FT]) #- 
 #-


if __name__ == '__main__':
  serverHost, serverPort = sys.argv[1].split(':')
  serverPort = int(serverPort)

  nodeHost, nodePort = sys.argv[2].split(':')
  nodePort = int(nodePort)

  chordNode = ChordNode(serverHost, serverPort, nodeHost, nodePort)
  chordNode.run()