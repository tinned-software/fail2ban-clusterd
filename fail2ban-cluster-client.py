#!/usr/bin/python
#
# This script can be used to send a message to the specified channels
#
# usage #1: python fail2ban-cluster-client.py -c <channel_name> -m <message>
# usage #2: python fail2ban-cluster-client.py --host-address <host_address> -p <port> -c <channel_name> -m <message>
# usage #3: python fail2ban-cluster-client.py --config=</path/to/config.yml> -c <channel_name> -m <message>
#
# Example: python fail2ban-cluster-client.py -c Channel1 -m "jail=ssh, ip=1.2.3.4, source=host.example.com"

# importing some classes
from optparse import OptionParser
import socket, sys, yaml, logging

# define command line options
opts = OptionParser(usage=" 1.: python fail2ban-cluster-client.py -c <channel_name> -m <message>\n        2.: python fail2ban-cluster-client.py -h <host_address> -p <port> -c <channel_name> -m <message>\n        3.: python fail2ban-cluster-client.py --config=</path/to/config.yml> -c <channel_name> -m <message>")
opts.add_option(      "--config",       action="store", type="string", dest="configfile",   help="Load an alternative config file. Default is /etc/fail2ban-cluster.yml")
opts.add_option("-c", "--channel",      action="store", type="string", dest="channel_name", help="Set the name of the channel to where the messages should be sent to.")
opts.add_option(      "--host",         action="store", type="string", dest="host_address", help="Set the host address or IP address of the server on which the channel is")
opts.add_option("-p", "--port",         action="store", type="int",    dest="port",         help="Set the port on which the server runnns")
opts.add_option("-m", "--message",      action="store", type="string", dest="message",      help="Set the message")
(options, args) = opts.parse_args()

# check if message is set in the command line
if options.message is None:
	print "Error: Message not set"
	sys.exit(2)

# check if the channel name is set in the command line
if options.channel_name is None:
	print "Error: Channel name not set"
	sys.exit(2)

# check if host and port are set in the command line
if options.host_address is not None and options.port is not None:
	try:
		s=socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialize socket
		s.connect((options.host_address, options.port)) # connect to the server
		s.send("announce "+options.channel_name+" "+options.message+"\n") # send the message
	except:
		print "Could not announce message to server "+options.host_address+":"+str(options.port)
	finally:
		s.close() # close the socket
		sys.exit(0)

# check if an alternative config file is set in the command line
if options.configfile is not None:
	stream = open(options.configfile, "r") # loads the alternative yaml config file
else:
	stream = open("/etc/fail2ban-cluster.yml", "r") # loads the default config file
yml = yaml.load(stream)

# get log level from config
if int(yml['log_level']) == 0:
	lvl=40
elif int(yml['log_level']) == 1:
	lvl=30
elif int(yml['log_level']) == 2:
	lvl=20
elif int(yml['log_level']) > 2:
	lvl=10

# initialize logging with the log file
logging.basicConfig(filename=str(yml['log_file']),
	filemode='a',
	format='[%(asctime)s,%(msecs)d] [%(name)s] [client] %(levelname)s %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S',
	level=lvl)
logging.info("Client started and successfully read yml file")

# iterates through all servers from the yaml file
for server in yml['servers']:
	logging.info("Loading config for server "+server['host']+" from yml file")
	# iterates through all channels for this server
	for channel in server['channels']:
		if channel['name'] == options.channel_name: # if the specified channel name is the name of the channel, send the message
			logging.info("For server "+server['host']+":"+str(server['port'])+" was a channel found with the name "+channel['name'])
			# set the variables requiered for sending
			TCP_IP=str(server['host'])
			TCP_PORT=int(server['port'])
			CHANNEL=str(options.channel_name)
			MESSAGE=str(options.message)
			try:
				logging.info("Started announcing message '"+MESSAGE+"'")
				s=socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialize socket
				s.connect((TCP_IP, TCP_PORT)) # connect to the server
				s.send("announce "+CHANNEL+" "+MESSAGE+"\n") # send the message
				logging.info("Successfully announced")
			except:
				logging.error("Could not announce message to server "+server['host']+":"+str(server['port']))
			finally:
				s.close() # close the socket
				sys.exit(0)
