#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

class Plugin:

    def __init__(self, client):
        self.client = client
        self.notices = {}

    #:nisay!~nisay@53.ip-192-99-70.net PRIVMSG #testbobot :!notice user message
    @event.privmsg()
    def get_notice(self, e):
        target = e.values['target']
        msg = e.values['msg'][1:]
        nick = e.values['nick']

        if nick == self.client.nick_name:
            return

        if msg == '!notice':
            self.help(target)

            if target == self.client.nick_name:
                message = "You can only send a notice on a channel !"
                self.client.priv_msg(nick, message)
                return

        elif msg[0:7] == '!notice':
            try:
                (cmd, user, message) = msg.split(' ', 2)
            except ValueError, e:
                self.help(target)
                return
            if user in self.client.channels[target.lower()].users:
                message = nick + ": Can\'t you really do that by yourself ? ._."
                self.client.priv_msg(target, message)
            else:
                message = message.strip()
                notice = 'From ' + nick + ': ' + message
                if not self.notices.has_key(target):
                    self.notices[target] = {}
                if not self.notices[target].has_key(user):
                    self.notices[target][user] = []
                self.notices[target][user].append(notice)

    @event.join()
    def send_notice(self, e):
        nick = e.values['nick']
        if nick[0] in ('&', '~', '+', '@'):
            nick = nick[1:]
        chan = e.values['chan']
        if nick == self.client.nick_name:
            return
        if self.notices.has_key(chan):
            if self.notices[chan].has_key(nick):
                message = nick + ": While you were away"
                self.client.priv_msg(chan, message)
                for notice in self.notices[chan][nick]:
                    self.client.priv_msg(chan, notice)
                self.notices[chan].pop(nick)

    def help(self, target):
        message = "Notify a user with a message when (s)he reconnects."
        self.client.priv_msg(target, message)
        message = "!notice user message"
        self.client.priv_msg(target, message)
