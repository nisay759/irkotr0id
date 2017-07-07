#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def repeat(self, e):
        target = e.values['target']
        nick   = e.values['nick']
        message= e.values['msg'][1:]
        if target[0] == '#':
            self.client.priv_msg(target, message)
        if target == self.client.nick_name:
            self.client.priv_msg(nick, message*2)
