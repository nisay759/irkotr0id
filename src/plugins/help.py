#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def help_request(self, e):
        target = e.values['target']
        msg = e.values['msg'][1:]
        nick = e.values['nick']
        if nick == self.client.nick_name:
            return
        if target == self.client.nick_name:
            target = nick
        if msg in ('!help', '!man', '!usage'):
            self.help(target)
        elif msg[0:4] == '!man':
            plugins = msg[4:].strip().split(' ')
            for p in plugins:
                if p == '' or not (p in self.client.plugins):
                    continue
                if p == 'help':
                    continue
                if self.client.plugins[p].__class__.__dict__.has_key('help'):
                    self.client.plugins[p].help(target)
                else:
                    message = p + " plugin has no manual yet :("
                    self.client.priv_msg(target, message)


    def help(self, target):
        message = "irkotr0id. A modular irc bot from the future"
        self.client.priv_msg(target, message)
        plugins = []
        for p in self.client.plugins:
            plugins.append(p)
        self.client.priv_msg(target, 'Loaded plugins: ' + ', '.join(plugins))
        message = "\'!man plugin\' to get usage of specific plugin"
        self.client.priv_msg(target, message)
