#!/usr/bin/env python
# -*- coding: Utf8 -*-
#[{:}{prefix}{SP}]{COMMANDE}[{SP}{PARAMETRES}]{CRLF}
import abc

class event(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.values = dict()

    def __call__(self, function):
        if not hasattr(function, 'triggers'):
            function.triggers = []
        function.triggers.append(type(self).__name__)
        return function

    @abc.abstractmethod
    def handle(self, string):
        return

class ping(event):
    def __init__(self):
        super(ping, self).__init__()

    def handle(self, string):
        s = string.split(':')
        if (len(s) == 2 and s[0].strip() == 'PING'):
            self.string = string
            self.values['ping_value'] = s[1].strip()
            return True
        return False

##:debsqueeze!debsqueeze@mre-FD71C744 JOIN :#betruger
##:debsqueeze!debsqueeze@mre-FD71C744 JOIN #betruger
class join(event):

    def __init__(self):
        super(join, self).__init__()

    def handle(self, string):
        if(string[0] == ':'):
            try:
                #string[1:] -> skip initial ':'
                (prefix, command, channel) = string[1:].split(' ', 2)
                (nick, host) = prefix.strip().split('!', 1)
            except ValueError, e:
                return False
            if(command.strip() == 'JOIN'):
                self.string = string
                if channel[0] == ':' :
                    channel = channel[1:]
                self.values['chan'] = channel.strip()
                self.values['nick'] = nick
                self.values['host'] = host
                return True
        return False

#:debsqueeze!debsqueeze@mre-FD71C744 PART #betruger :Quitte
class part(event):

    def __init__(self):
        super(part, self).__init__()

    def handle(self, string):
        if(string[0] == ':'):
            try:
                #string[1:] -> skip initial ':'
                (prefix, command, params) = string[1:].split(' ', 2)
                (nick, host) = prefix.split('!', 1)
                if ':' in params :
                    (channel, reason) = params.split(':', 1)
                else:
                    channel = params
                    reason = ''
            except ValueError, e:
                return False
            if(command == 'PART'):
                self.string = string
                self.values['nick'] = nick
                self.values['host'] = host
                self.values['chan'] = channel.strip()
                self.values['reason'] = reason.strip()

                return True
        return False

#:debsqueeze!debsqueeze@mre-FD71C744 QUIT :Quit: voilà ma raison
class quit(event):
    def __init__(self):
        super(quit, self).__init__()

    def handle(self, string):
        if(string[0] == ':'):
            try:
                #string[1:] -> skip initial ':'
                (prefix, command, reason) = string[1:].split(' ', 2)
                (nick, host) = prefix.split('!', 1)
                reason = reason[1:]
            except ValueError, e:
                return False
            if(command.strip() == 'QUIT'):
                self.string = string
                self.values['nick'] = nick
                self.values['host'] = host
                self.values['reason'] = reason.strip()
                return True

        return False

# :debsqueeze!debsqueeze@mre-FD71C744 PRIVMSG pulsifer :yop
class privmsg(event):
    def __init__(self):
        super(privmsg, self).__init__()

    def handle(self, string):
        if(string[0] == ':'):
            try:
                #string[1:] -> skip initial ':'
                (prefix, command, target, msg) = string[1:].split(' ', 3)
                (nick, host) = prefix.split('!', 1)
            except ValueError, e:
                return False

            if(command.strip() == 'PRIVMSG'):
                self.string = string
                self.values['nick']     = nick.strip()
                self.values['host']     = host.strip()
                self.values['target']   = target.strip()
                self.values['msg']      = msg.strip()
                return True

        return False

#use numeric 001 to be sure the connection is successful
#no subscribers for the moment, I only use specific numerics
class numeric(event):
    def __init__(self):
        super(numeric, self).__init__()

    def handle(self, string):
        if(string[0] == ':'):
            try:
                #string[1:] -> skip initial ':'
                (host, num, nick, msg) = string[1:].split(' ', 3)
            except ValueError, e:
                return False

            #make sure this is a numeric message
            if num.isdigit():
                self.string = string
                self.values['host'] = host
                self.values['num'] = num
                self.values['nick'] = nick
                self.values['msg'] = msg
                return True

        return False

#:nisay!~nisay@53.ip-192-99-70.net KICK #testbobot nisay_bot :reason
class kick(event):
    def __init__(self):
        super(kick, self).__init__()

    def handle(self, string):
        if(string[0] == ':'):
            try:
                (prefix, cmd, chan, target, reason) = string[1:].split(' ', 4)
                reason = reason[1:]
                (nick, host) = prefix.strip().split('!', 1)
            except ValueError, e:
                return False

            if (cmd == 'KICK'):
                self.string = string
                self.values['chan'] = chan
                self.values['target'] = target
                self.values['reason'] = reason
                self.values['nick'] = nick
                self.values['host'] = host
                return True

        return False

#:nisay!~nisay@53.ip-192-99-70.net MODE #testbobot +o nisay_bot
class mode(event):
    def __init__(self):
        super(mode, self).__init__()

    def handle(self, string):
        if(string[0] == ':'):
            try:
                (prefix, cmd, chan, mode, target) = string[1:].split(' ', 4)
                (nick, host) = prefix.split('!', 1)
            except ValueError, e:
                return False

            if (cmd == 'MODE'):
                self.string = string
                self.values['chan'] = chan
                self.values['mode'] = mode
                self.values['target'] = target
                self.values['nick'] = nick
                self.values['host'] = host
                return True

        return False

#:nisay!~nisay@53.ip-192-99-70.net TOPIC #testbobot :This is a topic
class topic(event):
    def __init__(self):
        super(topic, self).__init__()

    def handle(self, string):
        if(string[0] == ':'):
            try:
                (prefix, cmd, chan, topic) = string[1:].split(' ', 3)
                (nick, host) = prefix.split('!', 1)
            except ValueError, e:
                return False

            if (cmd == 'TOPIC'):
                self.string = string
                self.values['nick'] = nick
                self.values['host'] = host
                self.values['chan'] = chan
                self.values['topic'] = topic[1:]
                return True
        return False

#ERROR :Closing link: (irk0bot@53.ip-192-99-70.net) [Ping timeout: 121 seconds]
class error(event):
    def __init__(self):
        super(error, self).__init__()

    def handle(self, string):
        try:
            (text, error, reason) = string.split(':', 2)
            if text.strip() == 'ERROR':
                self.string = string
                self.values['text'] = text
                self.values['error'] = error
                self.values['reason'] = reason.strip()
                return True
        except:
            return False
        return False

class nick(event):
    def __init__(self):
        super(nick, self).__init__()

    def handle(self, string):
        if string[0] == ':':
            try:
                (prefix, cmd, new_nick) = string[1:].split(' ', 2)
                (old_nick, host) = prefix.split('!', 1)
            except ValueError, e:
                return False

            if (cmd == 'NICK'):
                self.string = string
                self.values['old_nick'] = old_nick
                #Some IRCd add ':' before new_nick
                if (new_nick[0] == ':'):
                    new_nick = new_nick[1:]
                self.values['new_nick'] = new_nick
                self.values['host']     = host
                return True
        return False
