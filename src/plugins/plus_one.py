#/usr/bin/env python
# -*- coding: Utf8 -*-

import event

class Plugin:

    def __init__(self, client):
        self.client = client
        self.points = dict()

    @event.privmsg()
    def give_point(self, e):
        msg = e.values['msg'][1:]
        nick = e.values['nick']
        if msg[0:3] == '+1 'or msg[0:3] == '-1 ':
            target = e.values['target']
            if target == self.client.nick_name:
                message = "Points can only be given on a channel"
                self.client.priv_msg(nick, message)
                return
            target = target.lower()
            recipient = msg.split(' ', 1)
            if len(recipient) != 2:
                return
            recipient = recipient[1].strip()
            if recipient == '' or ' ' in recipient:
                message = "You can give points to one (and only one) user"
                self.client.priv_msg(target, message)
                return
            if recipient == nick:
                message = "I see what you did here"
                self.client.priv_msg(target, message)
                return
            if not self.points.has_key(target):
                self.points[target] = dict()
            if not recipient in self.client.channels[target].users:
                message = recipient + " is not connected to this chan"
                self.client.priv_msg(target, message)
                return
            if not self.points[target].has_key(recipient):
                self.points[target][recipient] = 0
            self.points[target][recipient] += int(msg[0:3])

            message = nick + ' gave ' + recipient + ' ' + msg[0:3].strip() + '. '
            message += "Total points: " + str(self.points[target][recipient])
            self.client.priv_msg(target, message)

    @event.privmsg()
    def get_points(self, e):
        target = e.values['target']
        nick = e.values['nick']
        msg = e.values['msg'][1:].strip()
        if target == self.client.nick_name:
            message = "You can request your points only in a channel"
        target = target.lower()
        if msg == '!points':
            if not self.points.has_key(target):
                message = "No points have been attributed in this channel"
                self.client.priv_msg(target, message)
                return
            elif not self.points[target].has_key('nick'):
                message = "You have not been attributed any points"
                self.client.priv_msg(target, message)
                return
            else:
                message = nick + " : " + str(self.points[target][nick]) + " points"
                self.client.priv_msg(target, message)

    @event.privmsg()
    def get_ranking(self, e):
        if len(self.points) == 0:
            return
        target = e.values['target']
        nick = e.values['nick']
        msg = e.values['msg'][1:].strip()
        if target == self.client.nick_name:
            message = "You can request your points only in a channel"
        target = target.lower()
        if msg == '!rank':
            try:
                scoreboard = sorted(self.points[target], key=lambda user: self.points[target][user], reverse=True)
                message = ""
                for user in scoreboard:
                    message += user + ': ' + str(self.points[target][user]) + ' | '
                #Remove last "| "
                message = message[:-2]
                self.client.priv_msg(target, message)
            except:
                pass


    def help(self, target):
        message = "[+/-]1 user : Give or take 1 point from a user"
        self.client.priv_msg(target, message)
        message = "!points : Get your own points count"
        self.client.priv_msg(target, message)
        message = "!rank : Get chan scoreboard"
        self.client.priv_msg(target, message)



