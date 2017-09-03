# fail2ban-clusterd

With fail2ban-clusterd you can send a message over a message broker like "fanout" to other systems.
The systems that recieve the messages will run a specified command with specified values.

## Installation

Fail2ban-clusterd is written in python and requires the following python libraries. To install them use "pip".

    pip install pyYAML


## The daemon

fail2ban-clusterd.py is a daemon written in python.
It is responsible for recieving messages from fanout and runs the action with the given values.

## The client

fail2ban-cluster-client.py is a python script that sends messages to the specified channel on a server.
You can start it and give certain parameters via the command line.

## The yaml config file

In the config file you can specify multiple servers, multiple channels and an action for each channel.
It is also possible to set the pid file, log file and log level in the config.

The default config location is `/etc/fail2ban-cluster.yml`.

| Log Level | Meaning                  |
|:---------:|:------------------------ |
| 0         | only errors and critical |
| 1         | warnings and above       |
| 2         | infos and above          |
| 3         | debug infos and above    |

## Example of the script

### Config

```yaml
servers:
  - host: host.example.com
    port: 1234
    ping_timeout: 60
    channels:
      - name: Fail2ban
        action: "fail2ban-client set %jail% %action% %ip%"
    filter:
      - key: action
        values:
          - banip
          - unbanip
      - key: jail
        values:
          - sshd
log_level: 3
log_file: /var/log/fail2ban-clusterd.log
pid_file: /var/run/fail2ban-clusterd.pid
```

There is only one server called host.example.com and for this server only one channel called Fail2ban.
The channel has the action to ban an IP with fail2ban when it gets a message. 

We also set two filters. The key "action" can only have the value "banip" or "unbanip" and the key "jail" can only have the values "sshd".
You can imagine it like this in logic like this: `(%action% == "banip" || %action% == "unbanip") && %jail% == "sshd"`
If this is not true for the incomming values, the action won't be executed.

### Daemon

You can now start the daemon with:
```
python fail2ban-clusterd.py start
```
in the terminal to load from the default configuration. Or with:
```
python fail2ban-clusterd.py --config=/some/other/config.yml
```
to load an alternative config file.

### Client

You can start the client with the following:
```
python fail2ban-cluster-client.py -c Fail2ban -m "jail=sshd, action=banip, ip=192.168.0.1"
```
This sends the message to every server that has a channel called Fail2ban.
You can also specify this even further:
```
python fail2ban-cluster-client.py --host=host.example.com -p 1234 -c Fail2ban -m "jail=sshd, action=banip, ip=192.168.0.1"
```
This sends only to the channel to the specified host.

To use with fail2ban, you have to execute the client with the parameters after someone gets banned.

### The process

The daemon recieves data from the client.
Data: `Fail2ban!jail=sshd, action=banip, ip=192.168.0.1`

This message will be split up into channel and message. The message will also again split up into key and value (e.g. key=jail and value=sshd).
Then keys and values go through the filter. In our example the result is true, so the action will be executed at the end.

There are also predefined special keys:

| Key        | Meaning                   |
|:----------:|:------------------------- |
| %_msg%     | inserts the whole message |
| %_channel% | inserts channel name      |

After this the daemon inserts the value for the keys into the specified action:
```fail2ban-client set %jail% %action% %ip%` -> `fail2ban-client set sshd banip 192.168.0.1```
and will be executed with the same rights the daemon has.
