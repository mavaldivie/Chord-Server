import server #-
import random, math #-
from constChord import * #-
from constServer import *
import pickle, socket, zmq, sys, argparse


class ChordClient: #-
  def __init__(self, serverIP, serverPort=8080, nodePort=8081):                #-
    self.hostName = socket.gethostname()

    self.serverIP = serverIP
    self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    self.socket.bind((self.hostName, serverPort))
    self.socket.connect(self.serverIP)

    self.socket.send(pickle.dumps((JOIN, 'client')))
    self.nodeID = pickle.loads(self.socket.recv(BUFFERSIZE))  # Find out who you are         #-
    print(f'Node assigned id: {self.nodeID}')

    self.socket.send(pickle.dumps((NBITS, ' ')))
    self.nBits = pickle.loads(self.socket.recv(BUFFERSIZE))  # Num of bits for the ID space #-
    self.MAXPROC = pow(2, self.nBits)

    self.context = zmq.Context()
    self.talkSocket = self.context.socket(zmq.REQ)
    self.talkSocket.bind(f'tcp://0.0.0.0:{nodePort}')

    self.addresses = {}


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

  def stop(self):
    self.socket.send(pickle.dumps((DISCONNECT, '')))
    self.socket.close()
    self.talkSocket.close()
 #-
  def run(self): #-
    self.socket.send(pickle.dumps((SUBGROUP, 'node')))
    procs = pickle.loads(self.socket.recv(BUFFERSIZE))

    print(['%04d' % k for k in procs]) #-
    p = procs[random.randint(0,len(procs)-1)] #-
    key = random.randint(0,self.MAXPROC-1) #-

    while True:
      add = self.address(p)
      print(self.nodeID, "Client #", self.nodeID,"sending LOOKUP request for", key, "to", p, add) #-

      self.talkSocket.connect(add)
      self.talkSocket.send(pickle.dumps((self.nodeID ,LOOKUP_REQ, key))) #-
      msg = pickle.loads(self.talkSocket.recv())
      self.talkSocket.disconnect(add)

      sender = msg[0]  # Identify the sender #-
      command = msg[1]  # And the actual request #-
      message = msg[2]

      print(f'Client #{self.nodeID} received answer from {p}: {message}')
      if p == message: break
      p = message

    print( 'Client #',self.nodeID, "received final answer from", p) #-
    for i in procs:
      add = self.address(i)
      print(f'Client #{self.nodeID} sending STOP to node {i} at {add}')
      self.talkSocket.connect(add)
      self.talkSocket.send(pickle.dumps((self.nodeID, STOP, ' ')))
      msg = pickle.loads(self.talkSocket.recv())
      self.talkSocket.disconnect(add)

    self.stop()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--server', required=True, type=str, help='Server Address')
  parser.add_argument('--port1', default=8080, required=False, type=int, help='Node outgoing server communications port')
  parser.add_argument('--port2', default=8081, required=False, type=int, help='Node outgoing nodes communications port')
  args = parser.parse_args()

  serverHost, serverPort = args.server.split(':')
  serverPort = int(serverPort)
  port1, port2 = args.port1, args.port2

  client = ChordClient((serverHost, serverPort), port1, port2)
  client.run()
