#    pubcgi.py                                             5/21/04 CSM
#
#    This module enables a PUB session to occur using CGI.
#    demonstation: http://csm.freeshell.org/if/gargoyle/gredgar.cgi
#
#    Use this module with:
#       1) import pubcgi
#       2) setup the player using the CGIPlayer
#       3) call handle_request() with the relevant arguments. 
#          see games/gredgar.cgi for example usage 
#
#    2004-5/21:
#    Clint S. McCulloch (CSM) 
#       Baseline.
#
#----------------------------------------------------------------------

import cgitb; cgitb.enable()
import cgi, Cookie, random, pickle, os, sys, time, string
from cStringIO import StringIO


from md5 import md5
from cPickle import load, dump
from os.path import isdir, isfile
from os import remove

# PUB modules
import pub
from pubcore import *
import pubobjs

# settings
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# cookie name
id = 'gid'
# cookie
cookie = None
# session id
sid = None
# save directory, set in handle_request()
storagedir = None
# set to true upon valid restoration with CGIPlayer.Restore
restored = FALSE
# erase requested saves after 1 week by default
max_saved_game_age = 60 * 60 * 24 * 7
# erase temporary saves after 1 day
max_tmp_game_age = 60 * 60 * 24

# functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def cleanupsaves(filelist, maxage = 86400):
    """
    Delete saved games beyond a certain age.
    """
    import stat

    maxtime = int(time.time() - maxage)

    for f in filelist:
        mtime = os.stat(f)[stat.ST_MTIME]
        if mtime < maxtime:
            try:
                os.unlink(f)
            except:
                pass


# classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CGIPlayer(pubobjs.Actor):

    def __init__(self,pNames):
        pubobjs.Actor.__init__(self,pNames)
        self.inbuf = []
        self.outbuf = []

    def Tell(self, pWhat):
        self.outbuf.append( "<p>" + pWhat + "</p>" + "\n" )

    def Act(self):
        if pub.scheduler.HasEventFor( self ): 
            return
        # no scheduled events, so check for a command in the buffer
        if len(self.inbuf):
            cmdstr = self.inbuf[0].lower()
            self.inbuf = self.inbuf[1:]
            words = cmdstr.split()
            words[0] = words[0].lower()
            if   words[0]=='quit': self.Quit()
            elif words[0]=='save': self.Save()
            elif words[0]=='restore': self.Restore(words)
            else: self.DoCommandString(cmdstr)
        else: pub.scheduler.AddEvent( 1, Event(self, 'object.Act()') )

    def HandleMsg(self,msg):
        # place the message in the inbuf, for later use
        self.inbuf.append(msg)

    def Quit(self):
        """
        Quit game without asking.
        """
        self.Tell('Thanks for playing....')        
        pub.gameStatus = QUIT

    def Save(self):
        """
        Provide restoration instructions.
        """
        global sid
        
        # preface saved game with a g to save it specially
        gsid = 'g' + sid
        savegame(storagedir + gsid, TRUE)        
        self.Tell('Thanks for playing.')
        self.Tell("You can resume your game using the command below. " +
            "<ul>restore " + gsid + "</ul>")
        self.Tell("From time to time games may have be deleted to " +
            "conserve disk space.") 

    def Restore(self, words):
        """
        Restore game from provided code.
        """
        global sid, isfile, storagedir, restored
        
        code = None
        if len(words) == 2: code = words[1]
        if not code or len(code) < 2 or code[0] != 'g':
            self.Tell('Please enter a valid game code to restore.')
            return CANCEL
        for letter in code[1:]:
            if letter not in "0123456789abcdef":
                self.Tell('Please enter a valid game code to restore.')
                return CANCEL
        if not isfile(storagedir + code):                 
            self.Tell('Sorry, that game code could not be found.')
            return CANCEL

        if isfile(storagedir + sid):
            remove(storagedir + sid)
            
        sid = code
        
        # set global restored flag
        restored = TRUE
        
# processing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def handle_request(savedir, title='PUB', 
    header='', midder='', footer='', updates=3):
    """
    Handle the CGI request.
    """

    global id, sid, storagedir, restored, max_saved_game_age, max_tmp_game_age
    
    # buffer stdout to catch print/debug/warnings w/in pub b4 CGI header
    stdout = sys.stdout
    sys.stdout = StringIO()

    # find script name to be used in the html form action attribute
    scriptname = os.environ.get('SCRIPT_NAME', '.')
    
    # check savedir
    if not isdir(savedir):
        raise "Invalid savedir passed to pubcgi.handle_request"
    if not savedir[-1] in ['/', '\\']: savedir = savedir + os.path.sep
    storagedir = savedir
    
    # get session id from cookie if available
    cookie = Cookie.SimpleCookie()
    cookie.load(os.environ.get('HTTP_COOKIE',''))
    if cookie.has_key(id): sid = cookie[id].value 

    if sid and isfile(storagedir + str(sid)):
        restoregame(storagedir + sid, TRUE)
    else:
        sid = md5(str(time.time() * random.randint(0, 1000000))).hexdigest()
        pub.player.Tell(pub.player.container.GetDesc(pub.player))
    
    # get command
    form = cgi.FieldStorage()
    command = form.getvalue('command','')
    if command: pub.player.HandleMsg(command)         
        
    pub.scheduler.AddEvent( 0, pub.Event(pub.player, 'object.Act()') ) 

    # there is probably a better way to handle this
    # once I learn more about the scheduler?
    for i in xrange(updates): pub.scheduler.Update()
    
    # there is probably a better way to do this, too
    if restored:
        restoregame(storagedir + sid, TRUE)
        pub.player.Tell('Game restored....')
        pub.player.Tell(pub.player.container.GetDesc(pub.player))
        sid = sid[1:]   
        
    # get text
    text = string.join(pub.player.outbuf)
    pub.player.outbuf = []

    if pub.gameStatus != RUNNING:
        if isfile(storagedir + sid): 
            remove(storagedir + sid)
    else:
        savegame(storagedir + sid, TRUE)
        #os.chmod(storagedir + sid, 0664)
    
    # reassign stdout
    printed = sys.stdout.getvalue()
    if printed:
        # possible log, but for now we'll just ...
        pass
    sys.stdout = stdout
    
    # return output
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # return header
    
    # set cookie
    cookie[id]=sid
    
    print cookie
    print 'Content-type: text/html\n\n'

    if not header: header = """
        <html>
          <head>
            <title>%s</title>
          </head>
          <body onLoad="document.forms[0].command.focus()">
          <center>
          <h3>%s</h3>
          <table border="0" width="75%%"><tr><td>
          <hr>
    """ % (title, title)
    if not midder: midder = "<br><center>"
    if not footer: footer = """
            <div class="commands">
              <a href="gredgar.cgi?command=look">Look</a> &bull; 
              <a href="gredgar.cgi?command=inventory">Inventory</a> &bull; 
              <a href="gredgar.cgi?command=help">Help</a> &bull; 
              <a href="gredgar.cgi?command=save">Save</a> &bull; 
              <a href="gredgar.cgi?command=quit">Quit</a>
            </div>
          </center>
          <br>
          <hr>
          </td></tr></table>
          </center>
          </body>
        </html>
    """

    # return page 
    print header
    print """
       <form action="%s" method="post">
       %s
       %s
       <input type="text" id="command" name="command" size="40" maxlength="80">
       <input id="submit" type="submit" value="Submit">
       </form>
    """ % (scriptname, text, midder)
    print footer 
    
    # periodically, delete old games
    if (time.localtime()[5] + 1) % 60 == 0:
        import glob
        cleanupsaves(glob.glob(storagedir + '[0-9a-f]*'), max_tmp_game_age)
        cleanupsaves(glob.glob(storagedir + 'g[0-9a-f]*'), max_saved_game_age)
        