#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

import requests
from bs4 import BeautifulSoup

class User:
    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.url = 'https://www.root-me.org/' + pseudo
        self.score = 0
        self.rank = 'n/a'
    def update(self):
        res = requests.get(self.url + '?inc=score&lang=en', allow_redirects=True)
        if res.status_code == 404: return self
        if "This author does not participate to challenges" in res.text: return self
        self.htmlcontent = BeautifulSoup(res.text, 'html.parser')
        self.score = int(self.get_score())
        self.rank = int(self.get_rank())
        return self
    def get_score(self):
        return self.htmlcontent.findAll("span", {"class": "color1 tl"})[0].text.encode('utf-8').split('\n')[1].split('\xc2')[0]
    def get_rank(self):
        return self.htmlcontent.findAll("span", {"class": "color1 tl"})[1].encode('utf-8').split('\n')[1].split('<')[0]

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def score(self, e):
        try:
            if e.values['nick'] == self.client.nick_name:
                return
            if e.values['msg'][1:8] == '!rootme' :
                target = e.values['target']
                nicks = e.values['msg'].split(' ', 1)[1:]
                if len(nicks) == 0 or nicks[0].strip() == '':
                    nicks = [e.values['nick']]
                else:
                    nicks = nicks[0].split(' ')
                for nick in nicks:
                    # Avoid URL traversal
                    nick = nick.split('/')[-1]
                    if nick == '': continue
                    if nick[0] in ('~', '#', '@', '+'):
                        nick = nick[1:].strip()
                    if len(nick) > 1:
                        user = User(nick).update()
                        string = '{}: points: {} | rank: {}'.format(user.pseudo, user.score, user.rank)
                        if target[0] == '#':
                            self.client.priv_msg(target, string)
                        elif target == self.client.nick_name :
                            self.client.priv_msg(e.values['nick'], string)
        except:
            pass

    def help(self, target):
        self.client.priv_msg(target, '!rootme [nick1 [, nick2 ...]]')
