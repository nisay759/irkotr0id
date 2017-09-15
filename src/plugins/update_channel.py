#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.join()
    def channel_join(self, e):
        nick = e.values['nick']
        channel = e.values['chan'].lower()

        #self join is successful
        if (nick == self.client.nick_name):
            try:
                self.client.channels[channel].connected = 1
                self.client.channels[channel].name = channel
            except KeyError, e:
                self.client.logger.debug(e)
        else:
            self.client.channels[channel].update_user_list([nick])

    @event.numeric()
    def channel_users(self, e):
        if e.values['num'] == '353' :
            (chan, users) = e.values['msg'][1:].split(':', 1)
            chan = chan.strip().lower()
            self.client.channels[chan].update_user_list(users.strip().split(' '))

    @event.numeric()
    @event.topic()
    def update_topic(self, e):
        if e.values.has_key('num') and e.values['num'] == '332':
            (chan, topic) = e.values['msg'].split(':', 1)
            chan = chan.strip().lower()
        elif e.values.has_key('chan'):
            chan = e.values['chan'].lower()
            topic = e.values['topic']
        else:
            return

        self.client.channels[chan].topic = topic

    @event.part()
    def channel_part(self, e):
        nick = e.values['nick']
        channel = e.values['chan'].lower()

        self.client.channels[channel].remove_user(nick)
        if nick == self.client.nick_name:
            self.client.channels[channel].connected = 0

    @event.quit()
    def user_quit(self, e):
        nick = e.values['nick']
        for chan in self.client.channels:
            if self.client.channels[chan].connected == 1:
                self.client.channels[chan].remove_user(nick)

    @event.kick()
    def user_kick(self, e):
        chan = e.values['chan'].lower()
        target = e.values['target']
        if target == self.client.nick_name:
            self.client.channels[chan].connected = 0
        self.client.channels[chan].remove_user(target)

    def help(self, target):
        message = "This is a core plugin. You cannot interact with it in any way."
        self.client.priv_msg(target, message)
