#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

import markovify
import traceback

class Plugin:

    def __init__(self, client):
        self.client = client

    @event.privmsg()
    def get_sentence(self, e):
        msg = e.values['msg'][1:].replace(': ', ' ').split()
        target = e.values['target']
        nick = e.values['nick']
        if self.client.nick_name == target or self.client.nick_name == nick:
            return
        target = target[1:].lower()
        try:
            if self.client.nick_name in msg:
                return
            if (len(msg) > 1):
                f = open('/tmp/markov-' + target + '.txt', 'a')
                f.write(' '.join(msg) + '\n')
                f.close()
        except Exception, e:
            print traceback.format_exc()
            pass

    @event.privmsg()
    def talk(self, e):
        nick = e.values['nick']
        target = e.values['target']
        msg = e.values['msg'][1:].replace(': ', ' ').split()
        if self.client.nick_name == target or self.client.nick_name == nick:
            return
        try:
            recipient = target
            target = target[1:].lower()

            if self.client.nick_name in msg:
                f = open('/tmp/markov-' + target + '.txt', 'r')
                text = f.read()
                f.close()
                text_model = markovify.NewlineText(text)
                sentence = text_model.make_short_sentence(2000)
                if sentence:
                    self.client.priv_msg(recipient, sentence)
        except Exception, e:
            print traceback.format_exc()
            pass


    def help(self, target):
        message = "Learning plugin based on Markov chains. "
        message += "Include " + self.client.nick_name
        message += " in your message to get a response"
        self.client.priv_msg(target, message)
