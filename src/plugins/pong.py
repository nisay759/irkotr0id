#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.ping()
    def pong(self, e):
        value = e.values['ping_value']
        self.client.send_server('PONG :'+ value)

    def help(self, target):
        message = "This is a core plugin. You cannot interact with it in any way."
        self.client.priv_msg(target, message)
