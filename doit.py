#!/usr/bin/env python
import sys,os,time
import server
import chordNode, chordClient, random, threading

m = int(sys.argv[1]) # 5
n = int(sys.argv[2]) # 8

serverHost = '0.0.0.0'
serverPort = 8080
server = server.Server(nBits=m, portNo=serverPort)

thread = threading.Thread(target=server.run)
thread.start()


ports = [i for i in range(1000, 5000)]
#port = random.choice(ports)
#node = chordNode.ChordNode(serverHost, serverPort, 'localhost', port)
#node.run()

nodes = []
for i in range(n):
	port1 = random.choice(ports)
	ports.remove(port1)
	port2 = random.choice(ports)
	ports.remove(port2)
	nodes.append(chordNode.ChordNode((serverHost, serverPort), port1, port2))
time.sleep(0.5)


for i in range(n):
	thread = threading.Thread(target=nodes[i].run)
	thread.start()
time.sleep(1)

port1 = random.choice(ports)
ports.remove(port1)
port2 = random.choice(ports)
ports.remove(port2)
client = chordClient.ChordClient((serverHost, serverPort), port1, port2)
client.run()

os._exit(0)
