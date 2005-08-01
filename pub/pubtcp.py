#    pubtcp.py                                            8/05/96 JJS
#
#   Copyright (C) 1996 Joe Strout
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# CHANGELOG
# 
#   2002-5/10:
#     Terry Hancock
#       I'm not going to support this, because:
#       1) It's probably been superceded by JJS's MUD project
#       2) I'm not planning on using it, since I'm more interested
#       in adding AI players.
#
#   2004-22/10: Gabriel Jagenstedt
#       Cleaned up and inserted a copyright notice
#--------------------------------------------------------------------
"""
This module defines an Actor which connects to the
game via TCP/IP -- in effect, turning PUB into MUD.
"""


#----------------------------------------------------------------------

# standard imports
import random
import string
import types
import re
import copy
from socket import *


# PUB imports

import pub
from pubcore import *
import pubverbs
from pubobjs import Actor

# protocols imports

#----------------------------------------------------------------------
# global (module) vars
#
HOST = ''       # null string means local host (this machine)
PORT = 4000     # port to use
MAXCONS = 3     # maximum connections to allow
endl = "\r\n"   # string to end lines (for standard Telnet)
connlist = []   # list of connected players
running = 0     # 0=starting up, 1=running, -1=shutting down
sock = None     # socket used to receive connections
NPlist = []     # list of all NetPlayers
LoginList = []  # list of people trying to log in

#----------------------------------------------------------------------
# function to start the server
#
def StartServer():
    global HOST, PORT, running, sock

    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(HOST, PORT)
    sock.setblocking(0) 
    sock.listen(1)
    print "Server open on port",PORT
    running = 1

#----------------------------------------------------------------------
# function to disconnect a NetPlayer
#
def Disconnect(player, msg=''):
    global endl,connlist

    if player.conn:
        if msg: player.send( msg+endl );
        player.conn.close()
    player.conn = None
    player.connected = 0
    if player in connlist: connlist.remove(player)

#----------------------------------------------------------------------
# function to shut the server down
#
def ShutDown():
    global connlist, running, endl, sock

    if running < -1: return
    print "Shutting server down."
    for p in connlist: Disconnect(p, "Server shutting down.")
    sock.close()
    running = -2

#----------------------------------------------------------------------
# handle a new connection
#
def NewConn( conn, addr ):
    global connlist, MAXCONS, endl

    print "Got connection from",addr
    if running < 1:
        conn.send("Server is not running.")
        conn.close()
    if len(connlist)+len(LoginList) >= MAXCONS:
        conn.send("Sorry, only " + str(MAXCONS) + \
            " connections are allowed.  Please try again later." \
            + endl )
        conn.close()
        return
    # looks good -- log 'em in...
    conn.setblocking(0)
    LoginConn(conn)

#----------------------------------------------------------------------
# network update -- call this function periodically
#
def NetUpdate():
    global connlist, running, sock

    if not running: return StartServer()
    if running < 0: return ShutDown()
    
    # check for incoming connections
    try:
        conn, addr = sock.accept()
        NewConn( conn, addr )
    except: pass

    # handle incoming messages
    for u in connlist + LoginList:
        u.Act()
        try:
            data = u.conn.recv(1024)
        except: data = None
        if data:
            data = filter(lambda x: x>=' ' and x<='z', data)
            data = string.strip(data)
            if data:
#               print "From",u.name,':', data
                u.HandleMsg(data)
                if data == "shutdown": running=-1


#----------------------------------------------------------------------
#
# class of the network player -- i.e., the Actor interfaced to a socket
#
class NetPlayer(Actor):

    def __init__(self,pNames):
        global NPlist
        Actor.__init__(self,pNames)
        self.linebreak = 80
        self.connected = 0
        self.conn = None
        self.inbuf = []
        self.password = ''
        NPlist.append(self)     

    def send(self, pWhat):
        if not self.conn: return
        try: self.conn.send(pWhat)
        except: pass

    def Tell(self, pWhat):
        if not self.connected or not self.conn:
            return
               
        pWhat = string.join(string.split(pWhat,'\n'),endl)
        if self.linebreak:
            # break lines every <linebreak> characters:
            while len(pWhat) >= self.linebreak:
                pos = string.rfind(pWhat[:self.linebreak],' ')
                pos2 = string.rfind(pWhat[:self.linebreak],'\n')
                if pos2 < pos and pos2 > -1: pos = pos2
                self.send( pWhat[:pos] + endl )
                pWhat = pWhat[pos+1:]
        self.send( pWhat + endl )

    def Act(self):
        if pub.scheduler.HasEventFor( self ): 
            return
        # no scheduled events, so check for a command in the buffer
        if len(self.inbuf):
            cmdstr = self.inbuf[0]
            self.inbuf = self.inbuf[1:]
#           print self.name,"doing command:",cmdstr
            if cmdstr=='quit': self.Quit()
            else: self.DoCommandString(cmdstr)
        else: pub.scheduler.AddEvent( 1, Event(self, 'object.Act()') )

    def HandleMsg(self,msg):
        # place the message in the inbuf, for later use
        self.inbuf.append(msg)

    def Quit(self):
        # leave the game (without killing th server!)
        Disconnect(self,"Goodbye!")

# end of class NetPlayer

#----------------------------------------------------------------------


#----------------------------------------------------------------------
#
# class LoginConn -- a connection still in the process of logging in
#
class LoginConn(NetPlayer):

    def __init__(self,conn,pNames='<login>'):
        global LoginList, NPlist
        NetPlayer.__init__(self,pNames)
        self.conn = conn
        conn.send('Name: ')
        NPlist.remove(self)
        LoginList.append(self)

    def HandleMsg(self,msg):
        global NPlist, endl
        if self.name == '<login>':  # first msg should be name
            if len(msg)<2: return
            self.name = msg
            if msg == 'guest':
                self.password = 'guest'
            else:
                self.send('Password: ')
            return
        elif self.password == '':
            self.password = msg
            # check to see if this matches some player
            mtch = filter(self.Matches, NPlist)
            if not mtch:
                return self.Abort('Invalid login.');
            mtch = mtch[0]  # shouldn't be more than one!
            if mtch.connected:
                return self.Abort('Already logged in!');
            # looks good -- let 'em in
            self.EnterGame(mtch)
            return
        else:
            print "Unexpected message after login:",msg

    def Act(self):
        return      # no actions to take yet

    def Abort(self,msg='You are kicked off:'):
        global endl, LoginList
        if msg: self.send(msg+endl)
        self.conn.close()
        if self in LoginList: LoginList.remove(self)

    def Matches(self,player):   # return 1 if matches this NetPlayer
        return (self.password == player.password and \
            self.name == player.name)

    def EnterGame(self,match):
        global LoginList, connlist, endl
        match.conn = self.conn
        match.connected = 1
        LoginList.remove(self)
        self.send('Welcome, '+match.name+'!'+endl)
        match.inbuf = ["look"]
        connlist.append(match)
