#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

import re
import requests
from bs4 import BeautifulSoup
import pafy

import traceback

# Color codes
colors = {
        'red' : '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        }

def colorize(string, color):
    global colors
    if not color in colors:
        return string
    else:
        return colors[color] + str(string) + '\033[0m'

def process_youtube(url):
    video = pafy.new(url)
    likes = colorize(video.likes, 'green')
    dislikes = colorize(video.dislikes, 'red')
    duration = colorize(video.duration, 'blue')
    title = video.title.encode('utf-8')

    return title + " | " + likes + ":" + dislikes + " | " + duration


class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def url_checker(self, e):
        target = e.values['target']
        nick = e.values['nick']
        msg = e.values['msg'][1:]
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)

        if nick == self.client.nick_name:
            return

        if target == self.client.nick_name:
            recipient = nick
        else:
            recipient = target

        for url in urls:
            try:
                print url
                res = requests.get(url, timeout=3, allow_redirects=True)
                if 'text/html' in res.headers['content-type']:
                    if res.headers['Server'] == 'YouTube Frontend Proxy':
                        message = process_youtube(url)
                    else:
                        soup = BeautifulSoup(res.text, 'html.parser')
                        message = str(soup.title.text.encode('utf-8'))
                else:
                    message = res.headers['content-type']

                message = ''.join(c for c in message if c not in ('\n', '\b', '\r', '\a', '\f', '\v', '\t'))
                self.client.priv_msg(recipient, message)
            except:
                print traceback.format_exc()
                pass

    def help(self, target):
        message = "Checks URL for you"
        self.client.priv_msg(target, message)
