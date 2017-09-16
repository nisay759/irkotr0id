#/usr/bin/env python
# -*- coding: Utf8 -*-

import event
import signal
import subprocess
import os

home = os.getenv("HOME")
config_dir = home + '/.irkotroid'
kahoot_dir = config_dir + '/src/plugins/kahoot-hack'
kahoot_nicks_file = kahoot_dir + '/nicknames.txt'

kahoot_process = dict()

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def kahoot(self, e):
        target = e.values['target']
        nick = e.values['nick']
        msg = e.values['msg'][1:]

        msg = msg.strip().split(' ', 1)
        if not msg[0] == '!kahoot':
            return

        if len(msg) > 1:
            kahoot_args = msg[1].split()
            kahoot_code = kahoot_args[0]
        else:
            self.help(target)
            return

        process = subprocess.Popen(['go run '+ kahoot_dir +'/main.go '+ kahoot_code +' '+kahoot_nicks_file], stdout=subprocess.PIPE, shell=True)

        if nick in kahoot_process:
            try:
                kahoot_process[nick].send_signal(signal.SIGINT)
            except Exception:
                None
            finally:
                kahoot_process.pop(nick, None)
        kahoot_process[nick] = process

        for line in iter(process.stdout.readline, b''):
            if line !='':
                self.client.priv_msg(nick, line.rstrip())

    @event.privmsg()
    def kahootstop(self, e):
        msg = e.values['msg'][1:]
        msg = msg.strip().split(' ', 1)
        nick = e.values['nick']
        target = e.values['target']

        if msg[0] == '!kahootstop':
            try:
                kahoot_process[nick].send_signal(signal.SIGINT)
                kahoot_process.pop(nick, None)
                self.client.priv_msg(target, "!kahoot started by "+ nick + " has been stopped.")
            except Exception:
                self.client.priv_msg(target, "It seems there is no !kahoot associated to "+ nick + ".")

    def help(self, target):
        self.client.priv_msg(target, "!kahoot <kahoot code>")
        self.client.priv_msg(target, "The invoker must use !kahootstop to stop his !kahoot after the game has finished.")