#    pubverbs.py            8/27/96 JJS
#
#    This module defines the standard PUB verbs.
#
#    Use this module with:  import pubverbs
#
#----------------------------------------------------------------------
"""
Defines the basic classes of verbs understood by the game. More
verbs are interpreted via synonyms to these.
"""

import code, sys
import string

import pub
from pubcore import *

#----------------------------------------------------------------------
# Transitive verbs -- require a direct object

class Transitive(Verb):
    """
    Transitive verbs -- require direct objects.
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        x = self.synonyms[0]
        self.succ = 'You '+x+' <the dirobj>.'
        self.osucc = '<The actor> '+x+'s <a dirobj>.'
        self.fail = cap(x)+' what?!?'
        self.seefail = "You can't see that here."
        self.seesucc = "It takes a bit of groping, but you manage it..."

    def Begin(self,cmd):
        if not cmd.dirobj or not isInstance(cmd.dirobj):
            cmd.actor.Tell(self.fail)
            return CANCEL
        if not cmd.actor.CanSee(cmd.dirobj):
            if cmd.dirobj.container == cmd.actor:
                cmd.Tell(self.seesucc)
            else:
                cmd.Tell(self.seefail)
                return CANCEL
        return Verb.Begin(self,cmd)

    def Finish(self,cmd): return Verb.Finish(self,cmd)

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Social verb class: verbs which do very little, and may either
# have no objects, or one object (which we'll call dirobj).

class Social(Verb):
    """
    Social verb class -- little effect on topology
        verbs which do very little, and may either
        have no objects, or one object (which we'll
        call dirobj).

        Note that Social verbs may take on a whole new
        meaning with emotive characters. These may become
        every bit as meaningful as action verbs. The
        distinction then will be that social verbs affect
        the agent state of other characters while action
        verbs affect the topological world.

        (But since agents emit action verbs based on
        emotive state, social verbs may indirectly affect
        the topo world. This makes for a new dimension in
        game play involving complex persuasion tasks).
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        x = self.synonyms[0]
        self.succ = 'You ' + x + '.'
        self.osucc = '<The actor> ' + x + 's.'
        self.atsucc = 'You ' + x + ' at <the dirobj>.'
        self.atosucc = '<The actor> ' + x + 's at <the dirobj>.'
        self.atobjsucc = '<The actor> ' + x + 's at you.'

    def Finish(self,cmd):        # execute and output the event
        atwhom = cmd.dirobj
        if not atwhom: atwhom = cmd.atobj
        if not atwhom: atwhom = cmd.withobj
        if not atwhom: atwhom = cmd.toobj
        if not atwhom:
            cmd.Tell( self.succ, self.osucc )
        else:
            cmd.dirobj = atwhom        # necessary for correct substitution
            cmd.Tell( self.atsucc, self.atosucc, self.atobjsucc, atwhom )

#----------------------------------------------------------------------
# Default Social Verbs:
#

laugh = Social('laugh,giggle,chuckle')

nod = Social('nod')
nod.succ = 'You nod solemnly.'
nod.osucc = '<The actor> nods solemnly.'
nod.atsucc = 'You nod to <the dirobj>.'
nod.atosucc = '<The actor> nods to <the dirobj>.'
nod.atobjsucc = '<The actor> nods to you.'

grin = Social('grin,smile')
grin.succ = 'You smile charmingly.'
grin.osucc = '<The actor> grins like an idiot.'
grin.atsucc = 'You smile at <the dirobj>.'


#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Use verbs: call the Use(byWhom) method of the object
#
class Use(Transitive):
    """
    Call the Use(byWhom) method of the object

        This is a heavily used concept for PUB objects,
        as you might expect.
    """

    def Finish(self,cmd):
        # update the objects
        if cmd.dirobj and isInstance(cmd.dirobj):
            if hasattr(cmd.dirobj,'Use'):
                if cmd.dirobj.Use(cmd.actor) == CANCEL:
                    return CANCEL
            else:
                cmd.Tell( '<The dirobj> appears useless.')
                return CANCEL

        # allow superclass to handle postchecks and output
        Transitive.Finish(self,cmd)

#----------------------------------------------------------------------
# Default Use verbs:
#
use = Use('use')
push = Use('push,poke,prod')
push.osucc = '<The actor> pushes <the dirobj>.'
go = Use('go,move,mv,walk,wander')
go.fail = 'Go where?!?'

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# DefVerb: this transitive verb class calls the verb specified by
#      the defcmd property of the direct object

class DefVerb(Transitive):
    """
    Call verb defined by defcmd of an object --
        this transitive verb class calls the verb specified
        by the defcmd property of the direct object
    """

    def Begin(self,cmd):
        if not isInstance(cmd.dirobj):
            cmd.actor.Tell('Huh?!?')
            return CANCEL
        if not hasattr(cmd.dirobj,'defverb') or not cmd.dirobj.defverb:
            cmd.Tell('What do you want to do with <the dirobj>?')
            return CANCEL
        theVerb = cmd.dirobj.defverb
        if isString(theVerb): theVerb = pub.verbdict[theVerb]
        cmd.verb = theVerb
        return theVerb.Begin(cmd)

defverb = DefVerb('defverb')        # instantiate it

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Inventory verb (a class unto itself)
#
class Inventory(Verb):
    """
    Get the inventory (of the player) --
        (a class unto itself)
        Obviously this is the verb for the inventory command
        the player uses to find out what they're carrying.
        
        An interesting thought -- should NPC's be able to do
        this, and why?  An agent might act on or be affected
        emotionally or intellectually by what they are
        carrying. Of course, they can directly query their
        contents, I would think.
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        self.succ = 'You are carrying:'
        self.fail = 'You are empty-handed.'

    def Finish(self,cmd):

        # perform post-checks
        if self.DoPostchecks(cmd) == CANCEL: return OK

        # give output
        if cmd.actor.contents:
            cmd.Tell(self.succ)
            for item in cmd.actor.contents:
                if cmd.actor.CanSee(item): cmd.Tell(item.GetListLine())
        else:
            cmd.Tell(self.fail)
        return OK

#----------------------------------------------------------------------
# Inventory verb: can't imagine why you'd need more than one, but...
#
inventory = Inventory('inv,inventory,i')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Get verb -- get an object into your grubby little hands
#
class Get(Transitive):
    """
    Get an object into your grubby little hands.
    """

    def Finish(self,cmd):
        # update the database
        cmd.dirobj.MoveTo(cmd.actor)

        # let superclass handle postchecks and output
        return Transitive.Finish(self,cmd)

#----------------------------------------------------------------------
# Get verb instantiation

get = Get('get,take,grab,obtain,procure')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Drop verb -- place on object into the actor's container
#
class Drop(Transitive):
    """
    Place on object into the Actor's Container.
    """

    def Finish(self,cmd):
        # update the database
        cmd.dirobj.MoveTo(cmd.actor.container)

        # let superclass handle postchecks and output
        return Transitive.Finish(self,cmd)

#----------------------------------------------------------------------
# Drop verb instantiation

drop = Drop('drop')        # couldn't think of any 1-word synonyms!

#----------------------------------------------------------------------
# Follow verb -- follow another Actor
#
class Follow(Transitive):
    """
    Follow another Actor --
        Follow another Actor  (adds the actor to the list
        of followers for another actor (technically anything
        that implements the followers attribute).  When that
        actor moves, this actor will automatically get a
        command to move with it.

        See also Actor class in the pubobjs.py module.
    """

    def __init__(self,pNames=''):
        Transitive.__init__(self,pNames)
        self.selfsucc = 'You stop following <the dirobj>.'
        self.oselfsucc = '<The actor> stops following <the dirobj>.'
        
    def Begin(self,cmd):
        if not hasattr(cmd.dirobj,'followers'):
            cmd.Tell("You can't follow <a dirobj>.")
            return CANCEL
        if not Transitive.Begin(self,cmd): return CANCEL
        return OK
    
    def Finish(self,cmd):
        # update the database
        if cmd.actor.following:
            cmd.actor.following.followers.remove(cmd.actor)
        if cmd.dirobj != cmd.actor:
            cmd.actor.following = cmd.dirobj
            cmd.dirobj.followers.append(cmd.actor)
            if cmd.dirobj.following == cmd.actor:
                # uh-oh!  following loop!  Have dirobj follow self
                cmd.dirobj.following = None
                cmd.actor.followers.remove(cmd.dirobj)
        else:
            cmd.dirobj = cmd.actor.following
            cmd.actor.following = None
            cmd.Tell( self.selfsucc, self.oselfsucc)
            return OK

        # let superclass handle postchecks and output
        return Transitive.Finish(self,cmd)


follow = Follow('follow,fol')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# On verb -- activate an object
#
class On(Transitive):
    """
    Turn ON --
        activate an object  (see also Off, Toggle, this
        module, and Switch in pubobjs).
    """

    def Begin(self,cmd):
        if not isInstance(cmd.dirobj) or not hasattr(cmd.dirobj,'Activate'):
            cmd.Tell('You can see no way to do that.')
            return CANCEL
        return Transitive.Begin(self,cmd)
        
    def Finish(self,cmd):
        # update the database
        if (cmd.dirobj.Activate(cmd.actor)) == CANCEL: return CANCEL

        # let superclass handle postchecks and output
        return Transitive.Finish(self,cmd)

on = On('activate,on,switch on,turn on,wear,don,light,start')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Off verb -- deactivate an object
#
class Off(Transitive):
    """
    Turn OFF --
        deactivate an object
        See also On, Toggle in this module and
        Switch in pubobjs.
    """

    def Begin(self,cmd):
        if not isInstance(cmd.dirobj) or not hasattr(cmd.dirobj,'Deactivate'):
            cmd.Tell('You can see no way to do that.')
            return CANCEL
        return Transitive.Begin(self,cmd)
        
    def Finish(self,cmd):
        # update the database
        cmd.dirobj.Deactivate(cmd.actor)

        # let superclass handle postchecks and output
        return Transitive.Finish(self,cmd)

off = Off('deactivate,off,turn off,switch off,shut off,remove,doff,extinguish,stop')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Toggle verb -- activate or deactivate an object
#
class Toggle(Transitive):
    """
    Toggle ON/OFF --
        activate or deactivate an object

        See also On, Off in this module and
        Switch in pubobjs.

        This is why Switch doesn't need a toggle method, this
        verb handles it.
    """

    def Begin(self,cmd):
        if not isInstance(cmd.dirobj) or not hasattr(cmd.dirobj,'Deactivate') \
        or not hasattr(cmd.dirobj,'Activate') or not hasattr(cmd.dirobj,'isActive'):
            cmd.Tell('You can see no way to do that.')
            return CANCEL
        if cmd.dirobj.isActive: cmd.verb = off
        else: cmd.verb = on
        return Transitive.Begin(self,cmd)
        
    def Finish(self,cmd):
        # update the database
        if cmd.dirobj.isActive: cmd.dirobj.Deactivate(cmd.actor)
        else: cmd.dirobj.Activate(cmd.actor)

        # let superclass handle postchecks and output
        return Transitive.Finish(self,cmd)

toggle = Toggle('toggle,switch,turn,change,invert')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Look
#
class Look(Verb):
    """
    Look (get description from an object) --
        Returns a description of the direct object to the 
        subject.

        While in text adventure games, this may be a very
        simple text string, in a graphical extension, this
        might contain more complex topological or even
        absolute spatial information which could be interpreted
        by an agent or presented graphically to the player.

        Thus, this is a potential AutoManga hook (also see
        what a "Description" is -- is it a string, or a
        general object?
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        x = self.synonyms[0]
        self.osucc = '<The actor> '+x+'s around.'
        self.atsucc = 'You ' + x + ' at <the dirobj>.'
        self.atosucc = '<The actor> ' + x + 's at <the dirobj>.'
        self.atobjsucc = '<The actor> ' + x + 's at you.'
        self.fail = cap(x)+' at what?!?'

    def Finish(self,cmd):
        if cmd.atobj: cmd.dirobj = cmd.atobj
        if cmd.dirobj:
            if not isInstance(cmd.dirobj) or not cmd.actor.CanSee(cmd.dirobj):
                cmd.Tell(self.fail)
                return CANCEL
            cmd.Tell(cmd.dirobj.GetDesc(), self.atosucc, self.atobjsucc, cmd.dirobj)
        elif cmd.inobj:
            if not isInstance(cmd.inobj) or not cmd.actor.CanSee(cmd.inobj):
                cmd.Tell(self.fail)
                return CANCEL
            try: str = cmd.inobj.GetContentsDesc(cmd.actor)
            except AttributeError:
	        cmd.Tell("You can't look in <the inobj>")
		return CANCEL
	    if str:
                cmd.Tell('It looks like <the inobj> contains:' + str)
            else:
                cmd.Tell('<The inobj> appears to be empty.')
        else:    # no objects specified? describe the room
            cmd.Tell(cmd.actor.container.GetDesc(cmd.actor), self.osucc)
        return OK

#----------------------------------------------------------------------
look = Look('look,l,examine,ex,x,inspect,read')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Put -- put something into something else
#
class Put(Transitive):
    """
    Put something into something else.

        Note that this topological universe doesn't distinguish
        'in' 'on' 'within', etc. (I don't think).  This is
        pretty typical of IF game behavior in general.
    """

    def __init__(self, pNames=''):
        Transitive.__init__(self,pNames)
        self.succ = "You put <the dirobj> into <the inobj>."
        self.osucc= "<The actor> puts <a dirobj> into <a inobj>."
        self.inobjsucc= "<The actor> puts <a dirobj> into you."

    def Begin(self,cmd):
        if not isInstance(cmd.inobj):        # must have inobj
            if isInstance(cmd.dirobj):
                cmd.Tell('Put <the dirobj> where?!?')
            else:
                cmd.Tell('Put what where?!?')
            return CANCEL
        else:
            if not isInstance(cmd.dirobj):
                cmd.Tell('Put *what* into <the inobj>?!?')
                return CANCEL
            if not cmd.inobj.CanContain(cmd.dirobj):
                cmd.Tell("You can't put <the dirobj> into <the inobj>.")
                return CANCEL
        return Transitive.Begin(self,cmd)

    def Finish(self,cmd):
        # update the database
        cmd.dirobj.MoveTo(cmd.inobj)

        if self.DoPostchecks(cmd) == OK:
            cmd.Tell( self.succ, self.osucc, self.inobjsucc, cmd.inobj )
        return OK
        
# instantiate Put
put = Put('put,stuff,stick')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Give -- give something to someone else
#
class Give(Transitive):
    """
    Give something to someone else

        Its not clear to me if the recipient can refuse it,
        I suspect that would be done via the recipient's
        PreObj method, which looks like it might get called
        by this code. (?)
    """

    def __init__(self, pNames=''):
        Transitive.__init__(self,pNames)
        self.succ = "You give <the dirobj> to <the inobj>."
        self.osucc= "<The actor> gives <the inobj> <a dirobj>."
        self.inobjsucc = "<The actor> gives you <a dirobj>."
        self.infail = "Give <the dirobj> to whom?!?"
        
    def Begin(self,cmd):
        if cmd.toobj: cmd.inobj = cmd.toobj
        if not isInstance(cmd.inobj):        # must have inobj
            cmd.Tell(self.infail)
            return CANCEL
        return Transitive.Begin(self,cmd)

    def Finish(self,cmd):
        # update the database
        cmd.dirobj.MoveTo(cmd.inobj)

        if self.DoPostchecks(cmd) == OK:
            cmd.Tell( self.succ, self.osucc, self.inobjsucc, cmd.inobj )
        return OK
        
# instantiate Give
give = Give('give,hand')

#----------------------------------------------------------------------
# Quit the game

class Quit(Verb):
    """
    Quit the game --
        Really a game command.
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        x = self.synonyms[0]
        self.succ = 'Quitting game.'
        self.osucc = '<The actor> '+x+'s the game.'
        self.ask = '  Are you sure you want to quit? Y/y/N/n (Default No): '
	
    def Finish(self,cmd):
        # to quit the game, set pub.gameStatus...
        answer = raw_input(self.ask)
        if not answer or answer not in ['Y', 'y', 'Yes', 'yes']:
            print '  Returning to game'
            return CANCEL
        else: pub.gameStatus = QUIT

        # let superclass handle postchecks and output
        return Verb.Finish(self,cmd)
        
# instantiate Quit
quit = Quit("quit,q")

#----------------------------------------------------------------------
# Wait (by default, 5 minutes)

class Wait(Verb):
    """
    Wait (by default, 5 minutes)
        Again, this looks like real time behavior, I haven't
        found anything turn-based yet (could be turns are
        implemented through the scheduler as virtual time
        passage?).
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        self.succ = 'Time passes...'
        self.osucc = '<The actor> waits.'
        self.duration = 5                # wait 5 minutes

    def GetDuration(self,cmd):
        # duration may be specified as a direct object
        if isInt(cmd.dirobj): return toInt(cmd.dirobj)
        return self.duration

    def Finish(self,cmd):
        return OK

# instantiate Wait
wait = Wait("wait,z")
zz = Wait("zz")
zz.duration = 10
zzz = Wait("zzz")
zzz.duration = 15

#----------------------------------------------------------------------
# Say

class Say(Verb):
    """
    Say -- send information to Tell methods --
        This is not a do-nothing verb with PUB -- objects may
        be listening.
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        self.succ = 'You say'
        self.osucc = '<The actor> says,'
        self.fail = 'Say what?!?'
        self.duration = 0

    def Begin(self,cmd):
        if not cmd.dirobj:
            cmd.actor.Tell(self.fail)
            return CANCEL
        return Verb.Begin(self,cmd)
    
    def Finish(self,cmd):
        # perform post-checks
        if self.DoPostchecks(cmd) == CANCEL: return OK

        # give output
        # (remember to strip the quote which might be the first character)
        text = str(cmd.dirobj)
        if text[0]=='"': text = text[1:]
        cmd.Tell( self.succ + ' "' + text + '"', \
                  self.osucc+ ' "' + text + '"')

        return OK
        
say = Say('say,speak,talk')        # instantiate it

#----------------------------------------------------------------------
# eat -- used to... well eat stuff =)
#

class Eat(Verb):

    """
    Used to eat things. It is possible to make hunger and food have an effect
    on a game even though at this time it's only a matter of numbers.

    It should be up to the author what happens. 
    You can essentially be poisoned by food but haven't added the code for it.
    """
    
    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        self.fail = "You can't eat <a dirobj>."
	self.succ = "You eat <the dirobj>."
        self.seefail = "What should I eat?."
	
    def Begin(self,cmd):
	if not cmd.dirobj or not isInstance(cmd.dirobj):
	    cmd.actor.Tell(self.seefail)
	    return CANCEL
	if not hasattr(cmd.dirobj, 'edible'): 
	    cmd.Tell(self.fail)
	    return CANCEL
        if not cmd.dirobj.edible:
	    cmd.Tell(self.fail)
	    return CANCEL
        if cmd.dirobj.container == cmd.actor: cmd.Tell(self.succ)
        return Verb.Begin(self,cmd)
    
    def Finish(self,cmd):
	cmd.dirobj.MoveTo('TRASH') # delete the object
        return Verb.Finish(self,cmd)
    
eat = Eat('eat')

#---------------------------------------------------------------------
# drink -- verb for drinking. No! Really!
#

class Drink(Verb):
    """
    Drink -- Checks if an object can be drunk and then executes.
    Quenching thirst at this time does nothing. 
    The actor doesn't get thirstier even right now.

    This is up to the author to play with for now.
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
	self.fail = "You can't drink <a dirobj>."
	self.succ = "You drink <the dirobj>."
        self.seefail = "You can't see any <dirobj> here."

    def Begin(self,cmd):
        if not cmd.dirobj or not isInstance(cmd.dirobj):
            cmd.actor.Tell(self.seefail)
            return CANCEL
        if not hasattr(cmd.dirobj, 'drinkable'):
            cmd.Tell(self.fail)
	    return CANCEL
        if not cmd.dirobj.drinkable:
            cmd.Tell(self.fail)
            return CANCEL
        if cmd.dirobj.container == cmd.actor: cmd.Tell(self.succ)
        return Verb.Begin(self,cmd)

    def Finish(self,cmd):
	cmd.dirobj.MoveTo('TRASH') # delete the object
        return Verb.Finish(self,cmd)
	
drink = Drink('drink')
#----------------------------------------------------------------------
# @break -- sets line breaks, or turns them off
#

class SetBreak(Verb):
    """
    @break:    sets line breaks, or turns them off.
    (for debugging)
    It appears that the '@' prefix is used for
    verbs the player isn't really supposed to use.
    """

    def Finish(self,cmd):
        try: num = string.atoi(cmd.dirobj)
        except: num = 0
        cmd.actor.linebreak = num
                
        return OK
        
setBreak = SetBreak('@break')    # instantiate it


#----------------------------------------------------------------------
# @Examine -- a debugging verb which prints all attributes of an object
#

class DbgExamine(Transitive):
    """
    @Examine: Print all attributes of an object.
    (for debugging)
    """

    def Finish(self,cmd):
        print '\n', cmd.dirobj,'\n'
        for att in dir(cmd.dirobj):
            print '%20s' % att, ':', getattr(cmd.dirobj,att)
        print
                
        return OK
        
dbgEx = DbgExamine('@ex,@examine')    # instantiate it

#----------------------------------------------------------------------
# @contents -- a debugging verb which prints all contents of an object
#
class DbgContents(Transitive):
    """
    @contents: Print all contents of an object.
    (for debugging)
    """
    def Finish(self,cmd):
        print '\nContents of', cmd.dirobj,'\n'
        for item in cmd.dirobj.contents:
            print item
        print
        
        return OK

dbgContents = DbgContents('@contents,@con')

#----------------------------------------------------------------------
# verbs -- print all known verbs
#
class VerbsVerb(Verb):
    """
    verbs:    print all known verbs

        Probably useful for debugging and for help.
    """

    def Finish(self,cmd):
        print '\nKnown verbs:\n'
        for word in verbs:
            print (word+"               ")[:15],
        print '\n\n'
        return OK

verbsVerb = VerbsVerb('verbs,help')



#----------------------------------------------------------------------
#----------------------------------------------------------------------
# save -- save the game
#
class Save(Verb):
    """
    Save the game to disk.
    """

    def Finish(self,cmd):
	file = raw_input('  Enter a name for this game, default is pub.dat.')
        cmd.actor.Tell('  Saving game to disk...')
        if file == '': savegame()
	else: savegame(file)
        return OK

save = Save('save')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# restore -- restore the game
#
class Restore(Verb):
    """
    Restore the game from disk.

        Looks like maybe we only get one saved-game.  Probably
        ought to use the direct object as a filename instead. (?)
    """

    def Finish(self,cmd):
        file = raw_input('  Enter a save game to load, default is pub.dat.')
	cmd.actor.Tell('  Restoring game from disk...')
        if file == '': restoregame()
        else: restoregame(file)
	cmd.actor = pub.player
        cmd.actor.DoCommandString("look")
        raise pub.BailOutError, "Resetting stack to restore game"

restore = Restore('restore')


class Script(Verb):

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)

    def Finish(self,cmd):
        if self.DoPostchecks(cmd) == CANCEL: return OK
	code.interact(banner='', local=sys.modules['__main__'].__dict__)
	return OK

script = Script('@script,@code')
