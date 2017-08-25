#!/usr/bin/python

import socket, os, thread, time, logging

class Fanout_Channel:
	def __init__(self, name, action):
		self.name=name
		self.action=action

	def do_action(self, data):
		# e.g.: "jail=sshd, ip=::1"
		if "!" not in data or "debug!" in data:
			logging.warning("Either 'debug!' or not '!' in recieved data: "+data)
			return

		local_action=self.action
		channel=data.split("!")[0]
		message=data.split("!")[1]
		if "=" in message:
			messageSplit=message.split(",")
			array=[]
			for i in range(len(messageSplit)):
				array.append([])
				array[i].append(messageSplit[i].split("=")[0].strip())
				array[i].append(messageSplit[i].split("=")[1].strip())

			for i in array:
        	                if "%"+i[0]+"%" in self.action:
                	                local_action=local_action.replace("%"+i[0]+"%", i[1])

		if "%_msg%" in self.action:
			local_action=local_action.replace("%_msg%", message)

		if "%_channel%" in self.action:
                        local_action=local_action.replace("%_channel%", message)

#		while local_action.count("%") >= 2:
#			start=local_action.index("%")
#			substr=local_action[start+1:]
#			end=substr.index("%")
#			substr=substr[0:end]
#			logging.info("substr:"+substr)
#			if " " not in substr:
#				logging.info("delstr:"+local_action[start-1:local_action.index("%")+end+2])
#				local_action.replace(local_action[start-1:local_action.index("%")+end+2], "")
		os.system(local_action)

class Fanout_Connection:
	def __init__(self, host, port, timeout, channel_list):
		self.host=host
		self.port=port
		self.timeout=timeout
		self.channels=channel_list
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.buffer=2048
		self.shouldRun=True
		self.is_recieveing=False

	def establish(self, buffer=2048):
		logging.info("Establish connection "+self.host+":"+str(self.port))
		self.buffer_size=buffer

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((str(self.host), int(self.port)))

		for channel in self.channels:
			self.sock.send("subscribe "+channel.name+"\n")
		logging.info("Successfully established connection "+self.host+":"+str(self.port))

	def ping(self):
		while self.shouldRun is True:
			while (self.is_recieveing is True):
				pass
				#time.sleep(0.1)
			self.is_recieveing=True
			logging.info("Started pinging to Server "+self.host+":"+str(self.port))
			self.sock.send("ping\n")
			data = self.sock.recv(32)
			data = self.sock.recv(32)
			logging.info("Ping Data: "+str(data).strip())
			#for channel in self.channels:
				#thread.start_new_thread(channel.do_action, (str(data).strip(),))
				#channel.do_action(str(data).strip())
			try:
				value = int(data.strip())
				logging.info("Success on pinging to Server "+self.host+":"+str(self.port))
			except ValueError:
				for channel in self.channels:
	                                thread.start_new_thread(channel.do_action, (str(data).strip(),))
				logging.error("Pinging failed on  Server "+self.host+":"+str(self.port))
				self.establish()
			self.is_recieveing=False
			time.sleep(self.timeout)

	def recieve(self):
		logging.info("Started recieving on connection "+self.host+":"+str(self.port))
		while self.shouldRun is True:
			if self.is_recieveing is False:
				self.is_recieveing=True
				data = None
				data = self.sock.recv(self.buffer_size)
				if str(data) is not None:
					logging.info("Data recived on connection "+self.host+":"+str(self.port)+". Data: "+str(data).strip())
					for channel in self.channels:
						thread.start_new_thread(channel.do_action, (str(data).strip(),))
						#channel.do_action(str(data).strip())
				self.is_recieveing=False
			time.sleep(0.01)

	def run(self):
		self.shouldRun=True
		thread.start_new_thread(self.recieve, ())
		thread.start_new_thread(self.ping, ())
		time.sleep(0.1)
#		thread.start_new_thread(self.recieve, ())

	def close(self):
		self.shouldRun=False
		self.sock.close()
