#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
import ssl
import sys
import time
import os
import logging

import event
import channel

import traceback

def blue(string):
    return '\033[94m' + string + '\033[0m'

##########################
####### LOGGING ##########
##########################
home = os.getenv("HOME")
config_dir = home + '/.irkotroid'
if not os.path.exists(config_dir):
    os.mkdir(config_dir)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(config_dir + '/logs')
stdout_handler = logging.StreamHandler()

file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stdout_formatter = logging.Formatter(blue('%(levelname)s') + ' - ' + '%(message)s')

file_handler.setFormatter(file_formatter)
stdout_handler.setFormatter(stdout_formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

class client:

    MSG_MAXLEN = 512

    def __init__(self, host, port=6667, use_ssl=False, password=None,
                 oper=None, nickserv=None, config=None):
        self.socket = None
        self.channels = {}
        self.plugins = {}
        self.map = {}
        self.modules = {}

        self.host      = host
        self.port      = port
        self.use_ssl   = use_ssl
        self.password  = password
        self.connected = 0
        self.oper      = oper
        self.nickserv  = nickserv
        self.config    = config

        self.user_name    = self.config['user']['USERNAME']
        self.host_name    = self.config['user']['HOSTNAME']
        self.server_name  = self.config['user']['SERVERNAME']
        self.real_name    = self.config['user']['REALNAME']
        self.nick_name    = self.config['user']['NICKNAME']

        self.logger = logger

        #load events
        self.load_events()

        #Load plugins
        self.plugin_list = self.config['core_plugins'] + \
                self.config['plugins']
        self.plugins_path = "plugins/"
        sys.path.insert(0, self.plugins_path)
        self.load_all_plugins()

        self.terminated = False

    #########################
    ### Mapping functions ###
    #########################
    def update_mapping(self, plugin):
        p = self.plugins[plugin]
        plugin_actions = [a.__name__ for a in [p.__class__.__dict__.get(f) for f in
            dir(p.__class__)] if hasattr(a, 'triggers')]
        for pa in plugin_actions:
            for t in getattr(p, pa).triggers:
                if not self.map.has_key(t):
                    self.map[t] = []
                self.map[t].append(getattr(p, pa))

    def reset_mapping(self):
        self.map = {}
        for plugin in self.plugins:
            self.update_mapping(plugin)


    ###############################
    ### Event loading functions ###
    ###############################
    def load_events(self):
        reload(event)
        self.events = {e.__name__:e for e in [event.__dict__.get(a) for a in dir(event)] if
                isinstance(e, type) and len(e.__abstractmethods__) == 0}


    ################################
    ### Plugin loading functions ###
    ################################
    def load_all_plugins(self):
        for f in os.listdir(self.plugins_path):
            fname, ext = os.path.splitext(f)
            if ext == '.py' and fname in self.plugin_list \
                and fname not in self.plugins:
                self.load_plugin(fname)

    def reload_plugin(self, plugin):
        if plugin in self.plugins:
            #reload events
            self.load_events()
            try:
                self.modules[plugin] = reload(self.modules[plugin])
            except Exception, e:
                self.logger.debug(str(e))
                return
            self.plugins[plugin] = self.modules[plugin].Plugin(self)
            self.reset_mapping()

    def reload_plugins(self):
        print "[!] Reloading all plugins"
        #reload events
        self.load_events()
        #reload already loaded module
        for mod in self.modules:
            self.modules[mod] = reload(self.modules[mod])
            self.plugins[mod] = self.modules[mod].Plugin(self)
        self.reset_mapping()
        #load new plugins
        self.load_all_plugins()

    def load_plugin(self, plugin):
        if self.plugins.has_key(plugin):
            return
        try:
            mod = __import__(plugin)
        except ImportError, e:
            self.logger.debug("[!] Import error in plugin: " + plugin)
            self.logger.debug(str(e))
            return
        if not mod.__dict__.has_key('Plugin'):
            print "[!] Class Plugin not found in: " + plugin
            return
        print "[+] Loading plugin: " + plugin
        self.modules[plugin] = mod
        self.plugins[plugin] = mod.Plugin(self)
        self.update_mapping(plugin)

    def remove_plugin(self, plugin):
        if plugin in self.plugins:
            print "[-] Removing plugin: " + plugin
            del self.plugins[plugin]
            del self.modules[plugin]
            self.reset_mapping()


    ############################
    ### Connection functions ###
    ############################
    def run(self):
        self.connect()

        input_thread = threading.Thread(target=self.input_handle)
        input_thread.daemon = False
        input_thread.start()

        self.irc_login()
        for chan in self.config['channels']['JOINCHAN']:
            self.join_chan(chan)

        kb_thread = threading.Thread(target=self.kb_handle)
        kb_thread.daemon = False
        kb_thread.start()

        input_thread.join()
        kb_thread.join()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, \
                                        socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            if(self.use_ssl):
                try:
                    self.socket = ssl.wrap_socket(self.socket)
                except ssl.SSLError, e:
                    self.logger.debug('SSL error [' + str(e[0]) + ']: '+e[1])
                    sys.exit(1)

        except socket.error, e:
            self.logger.debug('Socket error [' + str(e[0]) + ']: '+e[1])
            sys.exit(1)

    def join_chan(self, chan):
        self.channels[chan.lower()] = channel.channel(self, chan)
        self.channels[chan.lower()].join()

    def disconnect(self):
        self.send_server('QUIT :be back soon')

    def quit(self):
        self.terminated = True
        self.disconnect()
        self.socket.close()

    def send_server(self, string):
        try:
            if (len(string) > client.MSG_MAXLEN - 2):
                string = string[:client.MSG_MAXLEN-3]
            self.logger.info('>> ' + string)
            self.socket.send(string+'\r\n')
        except Exception, e:
            self.logger.debug('An exception occured while trying to'\
                 +' send data to server: ' +str(e))

            self.terminated = True
            self.socket.close()
            sys.exit(1)


    def priv_msg(self, target, message):
        msg = message.split('\n', 1)[0]
        self.send_server('PRIVMSG '+ target + ' :' + msg)


    def irc_login(self):

        attempt_count = 1
        while (not self.connected) and (attempt_count < self.config['connection']['MAX_RETRY']):
            if(self.password != None):
                self.send_server('PASS '+self.password)

            self.send_server('USER '+self.user_name+' '
                                    +self.host_name+' '
                                    +self.server_name+' :'
                                    +self.real_name)

            self.send_server('NICK '+self.nick_name)
            #time.sleep(self.config['connection']['SLEEP'])
            if(self.oper != None):
                self.send_server('OPER '+self.user_name+' '+self.oper)

            if(self.nickserv != None):
                self.priv_msg('NickServ', 'IDENTIFY '+self.nickserv)
            time.sleep(self.config['connection']['SLEEP'])
            attempt_count += 1

    def input_handle(self):
        buf = ''
        try:
            while not self.terminated:
                s = self.socket.recv(512)
                lines = s.split('\r\n')
                lines[0] = buf + lines[0]
                buf = ''
                if not ('' in lines):
                    buf = lines[-1]
                    del lines[-1]
                for l in lines:
                    if (len(l.strip()) >0):
                        self.logger.info('<< ' + l)
                        for e in self.events:
                            #break if current line
                            #matches an existing event
                            if(self.map.has_key(e)):
                                tmp = self.events[e]()
                                if tmp.handle(l):
                                    for pa in self.map[e]:
                                        pa(tmp)
                                    del tmp
                                    break
        except Exception, e:
            self.logger.debug('Exception in thread input_handle: '+str(e))
            self.logger.debug(traceback.format_exc())

    def kb_handle(self):
        s = ''
        while s == '' or s[0] != ':' :
            s = raw_input()
            if s == ':q':
                self.send_server('quit')
                continue
            elif s[0:3] == ':rp' :
                if s == ':rp':
                    self.reload_plugins()
                else:
                    s = s.split()
                    if len(s) == 1:
                        s = ''
                        continue
                    for p in s[1:]:
                        self.reload_plugin(p)
            elif s == ':dbg':
                #print self.map
                for chan in self.channels:
                    self.channels[chan].channel_summary()
                    print '=' * 30
            elif s[0:5] == ':rmp ':
                try:
                    plugins = s[5:].strip()
                    for p in plugins.split(' '):
                        self.remove_plugin(p)
                except:
                    s = ''
            elif s[0:4] == ':lp ':
                try:
                    plugins = s[4:].strip()
                    for p in plugins.split(' '):
                        self.load_plugin(p)
                except:
                    s = ''
            elif s[0:3] == ':j ':
                try:
                    channel = s.split(' ')[1]
                    if channel[0] != '#':
                        channel = '#' + channel
                    self.join_chan(channel)
                except:
                    s = ''
            elif s[0:3] == ':p ':
                try:
                    chan = s.split(' ')[1]
                    if chan[0] != '#':
                        chan = '#' + chan
                    self.channels[chan.lower()].part()
                except:
                    s = ''
            s = ''

        self.quit()
