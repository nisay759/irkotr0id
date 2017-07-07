#/usr/bin/env python
# -*- coding: Utf8 -*-

import event
import requests

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def weather(self, e):
        target = e.values['target']
        nick = e.values['nick']
        msg = e.values['msg'][1:]
        if not msg[0:8] == '!weather':
            return
        if target == self.client.nick_name:
            recipient = nick
        else:
            recipient = target
        msg = msg.strip().split(' ', 1)
        if len(msg) == 1:
            location = ''
        else:
            args = msg[1].split()
            location = args[0]
        res = requests.get('http://wttr.in/'+location+'?0')
        message = res.text.encode('utf-8')
        if "ERROR" in message:
            message = "Unknown location"
        message = message.split('\n')
        for line in message:
            if line != '':
                self.client.priv_msg(recipient, line)

    def help(self, target):
        message = "!weather [location]"
        self.client.priv_msg(target, message)
