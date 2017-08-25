#!/usr/bin/python
#
# This script can be used to send a message to the specified channels
#
# usage: python fail2ban-cluster-client.py <channel_name> <message>
# Example: python fail2ban-cluster-client.py Channel1 "jail=ssh, ip=1.2.3.4, source=host.example.com"

# importing some classes
import socket, sys, yaml, logging

# loads the yaml config file
stream = open("/etc/fail2ban-cluster.yml", "r")
yml = yaml.load(stream)

# initialize logging with the log file
logging.basicConfig(filename=str(yml['log_file']),
	filemode='a',
	format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
	datefmt='%H:%M:%S',
	level=logging.DEBUG)
logging.info("Client started and successfully read yml file")
log_file=yml['log_file']

# iterates through all servers from the yaml file
for server in yml['servers']:
	logging.info("Loading config for server "+server['host']+" from yml file")
	# iterates through all channels for this server
	for channel in server['channels']:
		if channel['name'] is sys.argv[1]: # if the specified channel name is the name of the channel, send the message
			logging.info("For server "+server['host']+":"+str(server['port'])+" was a channel found with the name "+channel['name']))
			# set the variables requiered for sending
			TCP_IP=str(server['host'])
			TCP_PORT=int(server['port'])
			CHANNEL=str(channel['name'])
			MESSAGE=str(sys.argv[2])

			try:
				logging.info("Started announcing")
				s=socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialize socket
				s.connect((TCP_IP, TCP_PORT)) # connect to the server
				s.send("announce "+CHANNEL+" "+MESSAGE+"\n") # send the message
				logging.info("Successfully announced")
			except:
				logging.error("Could not announce message to server "+server['host']+":"+str(server['port'])
			finally:
				s.close() # close the socket
