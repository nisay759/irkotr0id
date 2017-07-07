#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.numeric()
    def connect_success(self, e):
        if e.values['num'] == '001':
            self.client.connected = 1

    def help(self, target):
        message = "This is a core plugin. You cannot interact with it in any way."
        self.client.priv_msg(target, message)
