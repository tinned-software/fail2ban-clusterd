# fail2ban-clusterd

With fail2ban-clusterd you can send a message over a message broker like "fanout" to other systems.
The systems that recieve the messages will run a specified command with specified values.

## The daemon

fail2ban-clusterd.py is a daemon written in python.
It is responsible for recieving messages from fanout and runs the action with the given values.

## The client

fail2ban-cluster-client.py is a python script that sends messages to the specified channel on a server.
You can start it and give certain parameters via the command line.

## The yaml config file

In the config file you can specify multiple servers, multiple channels and an action for each channel.
It is also possible to set the pid file, log file and log level in the config.
