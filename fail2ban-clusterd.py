#!/usr/bin/env python

import sys, time, os, socket, yaml, logging
from daemon import Daemon
from classes import Fanout_Channel, Fanout_Connection

class MyDaemon(Daemon):
	def run(self):
		stream = open("/etc/fail2ban-clusterd.yml", "r")
		yml = yaml.load(stream)
		#logging.basicConfig(filename=str(yml['log_level']),level=logging.DEBUG)
		logging.basicConfig(filename=str(yml['log_file']),
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
		logging.info("Daemon started and successfully read yml file")
		log_file=yml['log_file']
		#log_level=yml['log_level']

#		self.connection_list=[]
		for server in yml['servers']:
			logging.info("Loading config for server "+server['host']+" from yml file")
			channel_list=[]
			for channel in server['channels']:
				logging.info("Loading config for channel "+channel['name']+" from yml file")
				if "!" in str(channel['action']) or "\n" in str(channel['action']) or "^" in str(channel['action']):
					logging.error("Unvalid charakter in action of channel "+channel['name']+" in server "+server['host']+":"+server['port'])
					sys.exit(1)
				channel_list.append(Fanout_Channel(str(channel['name']), str(channel['action'])))
			self.connection_list.append(Fanout_Connection(str(server['host']), int(server['port']), int(server['ping_timeout']), channel_list))
			logging.info("Successfully loaded config for channel "+channel['name']+" from yml file")
		logging.info("Successfully loaded config for server "+server['host']+" from yml file")

		for con in self.connection_list:
			con.establish()
			con.run()

		while True:
			time.sleep(1)

if __name__ == "__main__":
	daemon = MyDaemon('/tmp/fanout.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			for con in daemon.connection_list:
				con.close()
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
