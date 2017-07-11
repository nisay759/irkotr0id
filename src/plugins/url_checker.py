#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

import re
import requests
from bs4 import BeautifulSoup

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def url_checker(self, e):
        target = e.values['target']
        nick = e.values['nick']
        msg = e.values['msg'][1:]
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)
        if target == self.client.nick_name:
            recipient = nick
        else:
            recipient = target

        for url in urls:
            try:
                res = requests.get(url, timeout=3, allow_redirects=True)
                if 'text/html' in res.headers['content-type']:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    title = str(soup.title.text.encode('utf-8'))
                    self.client.priv_msg(recipient, title)
                else:
                    message = res.headers['content-type']
                    self.client.priv_msg(recipient, message)
            except:
                pass

    def help(self, target):
        message = "Checks URL for you"
        self.client.priv_msg(target, message)
