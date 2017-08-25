#!/usr/bin/python
#
# This file provides the needed classes for the connections

# importing some classes
import socket, os, thread, time, logging

# This class represents a fanout channel.
# Such a channel has a specific name and action.
class Fanout_Channel:
	# the constructor
	def __init__(self, name, action):
		self.name=name
		self.action=action

	# the function that runs the action with the given data from the server
	def do_action(self, data):
		# data example: "jail=sshd, ip=::1"

		# ignore the data if "!" is not in it or if it's for debug purpose
		if "!" not in data or "debug!" in data:
			logging.warning("Either 'debug!' or not '!' in recieved data: "+data)
			return

		# split the data by the "!" to get channel name and message
		local_action=self.action
		channel=data.split("!")[0]
		message=data.split("!")[1]

		# if "=" is in the message, get the key and value
		if "=" in message:
			messageSplit=message.split(",")
			array=[]
			# iterating throught the message and store key and value in a 2-dimensional array
			for i in range(len(messageSplit)):
				array.append([])
				array[i].append(messageSplit[i].split("=")[0].strip())
				array[i].append(messageSplit[i].split("=")[1].strip())

			# iterating through the array and replace key with value in the action
			for i in array:
        	                if "%"+i[0]+"%" in self.action:
                	                local_action=local_action.replace("%"+i[0]+"%", i[1])

		# replace %_msg% with the whole message
		if "%_msg%" in self.action:
			local_action=local_action.replace("%_msg%", message)

		# replace %_channel% with the channel name
		if "%_channel%" in self.action:
                        local_action=local_action.replace("%_channel%", message)

		# replace every key that has no value
		dont_care_count=0
		while local_action.count("%")-dont_care_count >= 2:
		        start=local_action.index("%")
		        substr=local_action[start+1:]
		        end=substr.index("%")
		        substr=substr[:end]
		        if " " not in substr:
		                local_action=local_action.replace(local_action[start:start+end+2],"")
		        else:
		                dont_care_count+=2

		# sending the action to the os and execute it as command
		os.system(local_action)

# This class represents a fanout connection.
# A connection has a host address/IP, port, timeout and a list of channels
class Fanout_Connection:
	# the constructor
	def __init__(self, host, port, timeout, channel_list):
		self.host=host
		self.port=port
		self.timeout=timeout
		self.channels=channel_list
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.buffer=2048
		self.shouldRun=True # thread stop flag, terminates all threads when false
		self.is_recieveing=False # syncing the threads

	# the function to establish the connection and subscribe to channels
	def establish(self, buffer=2048):
		logging.info("Establish connection "+self.host+":"+str(self.port))
		self.buffer_size=buffer # default buffer size is 2048

		# initialize a new socket and connect to the socket with the given parameter
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((str(self.host), int(self.port)))

		# iterating through all channels
		for channel in self.channels:
			self.sock.send("subscribe "+channel.name+"\n") # subscribe to the channel
		logging.info("Successfully established connection "+self.host+":"+str(self.port))

	# the function that pings in a given intervall to see if the connection is still running
	def ping(self):
		# run loop until the thread should stop due to the close function
		while self.shouldRun is True:
			# thread syncing
			while (self.is_recieveing is True):
				pass
			self.is_recieveing=True
			logging.info("Started pinging to Server "+self.host+":"+str(self.port))
			self.sock.send("ping\n") # send ping
			data = self.sock.recv(32) # the first value returns "debug!connected" and will be ingnored
			data = self.sock.recv(32) # the actual ping return value
			logging.info("Ping Data: "+str(data).strip())

			try:
				value = int(data.strip()) # ping should be an integer, if not connection will be reestablished
				logging.info("Success on pinging to Server "+self.host+":"+str(self.port))
			except ValueError:
				for channel in self.channels:
	                                thread.start_new_thread(channel.do_action, (str(data).strip(),))
				logging.error("Pinging failed on  Server "+self.host+":"+str(self.port))
				self.establish()
			self.is_recieveing=False
			time.sleep(self.timeout)

	# the connection the recieve data from the connection
	def recieve(self):
		logging.info("Started recieving on connection "+self.host+":"+str(self.port))
		# run loop until the thread should stop due to the close function
		while self.shouldRun is True:
			if self.is_recieveing is False:
				self.is_recieveing=True
				data = None
				data = self.sock.recv(self.buffer_size) # recieves data
				if str(data) is not None:
					logging.info("Data recived on connection "+self.host+":"+str(self.port)+". Data: "+str(data).strip())
					# iterates through the channels and starts a new thread to run the action
					for channel in self.channels:
						thread.start_new_thread(channel.do_action, (str(data).strip(),)) # runs the action in a new thread
						#channel.do_action(str(data).strip())
				self.is_recieveing=False
			time.sleep(0.01)

	# the function starts the ping and recieve function in a new thread
	def run(self):
		self.shouldRun=True
		thread.start_new_thread(self.recieve, ())
		thread.start_new_thread(self.ping, ())

	# the function sets the thread stop flag and closes the connection
	def close(self):
		self.shouldRun=False
		self.sock.close()
