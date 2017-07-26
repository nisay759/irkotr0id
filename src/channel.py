#!/usr/bin/env python
# -*- coding: Utf8 -*-

class channel:
    def __init__(self, client, name):
        self.name      = name
        self.client    = client
        self.connected = 0
        self.users     = list()

    def join(self):
        self.client.send_server('JOIN ' + self.name)

    def part(self):
        self.client.send_server('PART ' + self.name)

    def update_user_list(self, ulist):
        for u in ulist:
            #remove user status: not useful
            if (u[0] in ('&', '~', '+', '@')):
                u = u[1:]
            if u not in self.users:
                self.users.append(u)

    def remove_user(self, nick):
        if nick in self.users:
            self.users.remove(nick)
            #try:
            #	self.users.remove(nick)
            #except ValueError, e:
            #	print e

    def list_user(self):
        for u in self.users:
            print '****'+u
