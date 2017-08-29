#!/usr/bin/env python
#
# This python script is responsible to start, stop and restart the daemon.
#
# usage: python fail2ban-clusterd.py start|stop|restart

# importing classes that are needed
import sys, time, os, socket, yaml, logging
from daemon import Daemon
from optparse import OptionParser
from classes import Fanout_Channel, Fanout_Connection

VERSION="0.1.0"
# the MyDaemon class implements all functionality of the Daemon class and runs the code as daemon
class MyDaemon(Daemon):
	def run(self):
		# initialize the log with some parameter
		logging.basicConfig(filename=str(yml['log_file']),
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
		logging.info("Daemon started and successfully read yml file")

		# iterating through all the servers in yml file
		for server in yml['servers']:
			logging.info("Loading config for server "+server['host']+" from yml file")
			channel_list=[]
			# iterating through all the servers in yml file
			for channel in server['channels']:
				logging.info("Loading config for channel "+channel['name']+" from yml file")
				if "!" in str(channel['action']) or "\n" in str(channel['action']) or "^" in str(channel['action']): # check if any invalid characters are in the action
					logging.error("Unvalid charakter in action of channel "+channel['name']+" in server "+server['host']+":"+server['port'])
					sys.exit(1)
				channel_list.append(Fanout_Channel(str(channel['name']), str(channel['action']))) # adding the channel to the channel_list
			self.connection_list.append(Fanout_Connection(str(server['host']), int(server['port']), int(server['ping_timeout']), channel_list)) # adding the server to the list of servers/connections
			logging.info("Successfully loaded config for channel "+channel['name']+" from yml file")
		logging.info("Successfully loaded config for server "+server['host']+" from yml file")

		# iterating through the server/connection list
		for con in self.connection_list:
			con.establish() # establish the connection and subscribe
			con.run() # recieve messages

		# endless loop
		while True:
			time.sleep(1)

if __name__ == "__main__":
	opts = OptionParser(usage="python fail2ban-clusterd.py start|stop|restart|[options]")
	opts.add_option("-c", "--config", action="store", type="string", dest="configfile", help="Load an alternative config file. Default is /etc/fail2ben-cluster.yml")
	opts.add_option("-V", "--version", action='store_true', dest='isVer', help="Show the version of the daemon")
	(options, args) = opts.parse_args()

	if options.isVer:
		print VERSION
		sys.exit(0)

	if options.configfile is not None:
		stream = open(options.configfile, "r")
	else:
		stream = open("/etc/fail2ban-cluster.yml", "r") # get the pid file location from the config
        yml = yaml.load(stream)
	daemon = MyDaemon(str(yml['pid_file'])) # the pid file for the daemon
	# start, stop or restart the daemon
#	if len(sys.argv) == 2:
	if 'start' in sys.argv[1:]:
		daemon.start()
	elif 'stop' in sys.argv[1:]:
		for con in daemon.connection_list:
			con.close()
		daemon.stop()
	elif 'restart' in sys.argv[1:]:
		daemon.restart()
	else:
		print "Unknown command"
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
	sys.exit(0)
#	else:
#		print "usage: %s start|stop|restart" % sys.argv[0]
#		sys.exit(2)
