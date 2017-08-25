#!/usr/bin/python

import socket, sys

TCP_IP=str(sys.argv[1])
TCP_PORT=int(sys.argv[2])
CHANNEL=str(sys.argv[3])
MESSAGE=str(sys.argv[4])

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send("announce "+CHANNEL+" "+MESSAGE+"\n")
s.close()
