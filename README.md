irkotr0id - A modular IRC bot from the future
=======

irkotr0id is a modular and totally customizable IRC bot written in Python.

irkotr0id is based on a plugins system that makes it easy to add a new feature and load it while the bot is still running and connected to channels.

---


# Requirements
None !

irkotr0id have been written from the ground up. It only uses standard libraries that are shipped with the original python package.

Note, however, that some plugins may have extra requirements. Check your plugin requirements before loading it into irkotr0id.

# Installation
```bash
git clone https://github.com/nisay759/irkotr0id
cd irkotroid/
./start
```

# Usage
```bash
$ ./irkotroid -h
usage: irkotroid [-h] -H HOST -c CONFIG [-p PORT] [-P PASSWORD] [-n NICKSERV]
                 [-o OPER] [--use-ssl]

irkotr0id - A modular IRC bot from the future

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Hostname of the irc server
  -c CONFIG, --config CONFIG
                        Configuration json file
  -p PORT, --port PORT  The port the irc server is listening on
  -P PASSWORD, --password PASSWORD
                        Password of registered nickname
  -n NICKSERV, --nickserv NICKSERV
                        NickServ password
  -o OPER, --oper OPER  OP
  --use-ssl             Connect using a secure connection
```

# Plugins
Several plugins are provided in the ```src/plugins``` folder.

As of the time of writing, the following plugins are available:

```
notice: Stores messages and delivers them to a user when (s)he (re)joins the channel
weather: Gives info about weather. Data is from wttr.in
plus_one: Give or take away points to/from a user
rootme: Fetches user score from root-me.org
repeater: Useless and annoying. Kind of a parrot plugin
markov: A bot talking plugin. The bot learns from user messages on the connected chans
url_checker: Checks URLs title/content-type
```

However, if you decide to write your own plugin, here's how:

1. Drop ```your_plugin.py``` in the ```src/plugins``` folder. It should follow this skeleton:

```python
#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.my_event()
    def my_function(self, e):
        return

    def help(self, target)
        message = "This is the help message"
        self.client.priv_msg(target, message)
```

There are two rules that you should respect for your plugin to work:

  - It should contain a class named 'Plugin', in which you define your custom methods
  - The custom methods should be decorated with an ```event``` subclass.

In the example above, ```event.my_event()``` can be replaced with one of the following:

  - ```event.ping()```: When a PING is received from the remote server
  - ```event.privmsg()```: When a private message is sent, whether on a query or on a channel
  - ```event.join()```: When a user joins a channel
  - ```event.part()```: When a user parts a channel
  - ```event.quit()```: When a user quits
  - ```event.numeric()```: When the server sends a numeric message
  - ```event.kick()```: When a user gets kicked
  - ```event.mode()```: When a change in mode is performed
  - ```event.topic()```: When a channel's topic in changed
  - ```event.error()```: When an error occurs (e.g Ping timeout)
  - ```event.nick()```: When someone changes their nick

Once an event is raised, all the methods that have been decorated with that event are triggered.

Of course, you can decorate your methods with as many events as you like. Your method will be called for each event it has been decorated with.

2. Add ```your_plugin``` to the ```config.json``` file:

```json
    "plugins": ["notice", "your_plugin"],
````
Then fire up irkotr0id.

If the bot is already running, type ```:lp your_plugin``` in the console and that's it !

The ```help()``` method is optional, but highly recommended. It allows users to get help concerning your plugin by sending ```!man your_plugin``` in a channel where the bot is connected, or directly via a private message.

# Events
Events are defined in ```src/event.py```.

When the client receives a line from the server, an event instance is created, and the line is passed to the ```handle()``` method of that instance.

If the line matches the event, the associated instance updates its internal variables, and then gets passed to all plugin methods that have been decorated with that event class.

An event instance holds an internal ```dict()``` named ```values``` which, as its name suggests, contains the values parsed from the line that generated the event. The reason behind this is to simplify the process of plugin development by focusing on what the plugin will do instead of parsing the event line over and over again. Of course, if you wish to do some custom parsing, the line that generated the event is also available via the internal variable ```my_event.string```

The list below summarizes the information you can get access to per event:

```
event.ping    :   ping_value
event.join    :   nick, host, chan
event.part    :   nick, host, chan, reason
event.quit    :   nick, host, reason
event.privmsg :   nick, host, target, msg
event.numeric :   nick, host, num, msg
event.kick    :   nick, host, chan, target, reason
event.mode    :   nick, host, chan, target, mode
event.topic   :   nick, host, chan, topic
event.error   :   error, reason
event.nick    :   old_nick, new_nick, host
```

# Client
The client, defined in ```src/client.py```, represents the core logic of irkotr0id. It handles the connection to the remote server, joins channels, loads plugins, updates event-action mapping, etc.

The client provides some useful methods and structures that you will probably use during your plugin development:

```text
- client.channels
A dict() with all the channels that the client is connected to (or tried to connect to).
Keys are channel names, and values are instances of channel class.

- client.quit()
A method for terminating the connection to the server.

- client.priv_msg(target, message)
Send a private message to target, which is either a channel or a nickname
```

Other methods and structures not listed above are used locally by the client class. If you are interested in developing core plugins, it may be interesting to take a look at those in ```src/client.py```

# Console commands
You can interact with irkotr0id while it is running via the console.

Commands start with ```:```, and the following list summarizes the available commands:

```
- rp : Reload all loaded plugins
- dbg : Show debug information
- q : Quit
- lp plugin [, plugin, ...] : Load the plugins passed as arguments
- rmp plugin [, plugin, ...] : Remove the plugins passed as arguments
- j channel : Joins the channel passed as argument
```

# Contribution
Contributions are really appreciated. If you feel there is something useful that might be added to irkotr0id or if you notice a bug, don't hesitate to open an issue or submit a pull request :-)

# License
`irkotr0id` is available under the [Beerware](http://en.wikipedia.org/wiki/Beerware) license.

If we meet some day, and you think this stuff is worth it, you can buy me a beer in return.
