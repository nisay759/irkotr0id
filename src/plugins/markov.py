#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

import markovify
import os
import traceback

home = os.getenv("HOME")
config_dir = home + '/.irkotroid'
if not os.path.exists(config_dir):
    os.mkdir(config_dir)

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def get_sentence(self, e):
        global home
        msg = e.values['msg'][1:].replace(': ', ' ').split()
        target = e.values['target']
        nick = e.values['nick']
        if self.client.nick_name == target or self.client.nick_name == nick:
            return
        target = target[1:].lower()
        try:
            if self.client.nick_name in msg:
                return
            path = config_dir + '/markov-' + target + '.txt'
            f = open(path, 'a')
            f.write(' '.join(msg) + '\n')
            f.close()
        except Exception, e:
            self.client.logger.debug(traceback.format_exc())
            pass

    @event.privmsg()
    def talk(self, e):
        global home
        nick = e.values['nick']
        target = e.values['target']
        msg = e.values['msg'][1:].replace(': ', ' ').split()
        if self.client.nick_name == target or self.client.nick_name == nick:
            return
        try:
            recipient = target
            target = target[1:].lower()

            if self.client.nick_name in msg:
                path = config_dir + '/markov-' + target + '.txt'
                if os.path.exists(path):
                    f = open(path, 'r')
                    text = f.read()
                    f.close()
                    text_model = markovify.NewlineText(text)
                    sentence = text_model.make_short_sentence(2000)
                    if sentence:
                        self.client.priv_msg(recipient, sentence)
        except Exception, e:
            self.client.logger.debug(traceback.format_exc())
            pass


    def help(self, target):
        message = "Learning plugin based on Markov chains. "
        message += "Include " + self.client.nick_name
        message += " in your message to get a response"
        self.client.priv_msg(target, message)
