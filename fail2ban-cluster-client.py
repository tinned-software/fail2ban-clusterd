#!/usr/bin/python

import socket, sys, yaml, logging

stream = open("/etc/fail2ban-cluster.yml", "r")
yml = yaml.load(stream)
logging.basicConfig(filename=str(yml['log_file']),
	filemode='a',
	format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
	datefmt='%H:%M:%S',
	level=logging.DEBUG)
logging.info("Client started and successfully read yml file")
log_file=yml['log_file']
for server in yml['servers']:
	logging.info("Loading config for server "+server['host']+" from yml file")
	for channel in server['channels']:
		if channel['name'] is sys.argv[1]:
			logging.info("For server "+server['host']+":"+str(server['port'])+" was a channel found with the name "+channel['name']))
			TCP_IP=str(server['host'])
			TCP_PORT=int(server['port'])
			CHANNEL=str(channel['name'])
			MESSAGE=str(sys.argv[2])

			try:
				logging.info("Started announcing")
				s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((TCP_IP, TCP_PORT))
				s.send("announce "+CHANNEL+" "+MESSAGE+"\n")
				logging.info("Successfully announced")
			except:
				logging.error("Could not announce message to server "+server['host']+":"+str(server['port'])
			finally:
				s.close()
