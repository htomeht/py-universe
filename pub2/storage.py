# (C) 2007 Terry Hancock
#----
# storage
"""
Store game session data in a Durus-based storage file.
"""
# GPLv2+

# FIXME: might want to get name of storage file from game instance .cfg file?

from durus.file_storage import FileStorage
from durus.connection import Connection
from durus.persistent import Persistent
from durus.persistent_dict import PersistentDict
from durus.persistent_list import PersistentList

from symbol import sym

class Session(object):
    """
    Representation of the game state.
    """    
    _persistent_attributes = (
        'scheduler',
        'started',
        'lastroom',
        'universe',
        'characters',
        'player',
        'debugging')
    # default values
    scheduler   = None      # Scheduler instance
    started     = False     # Is game started yet? (I.e. have player turns/actions begun)
    lastroom    = None      # Used to determine auto-placement of items
    universe    = None      # Top level container object (provides storage for entire game state)
    characters  = ()        # List of character agents (references into universe)
    player      = ()        # List of player character agents (normally only 1 in PUB)
    debugging   = False     # Debugging mode is for use during game development
    
    def __init__(self, storagefile="default.sav"):
        self.storage = Connection(FileStorage(storagefile))
        self.root    = self.storage.get_root()

        self.running = False

    def __setattr__(self, name, value):
        if name in self._persistent_attributes:
            self.root[name] = value
        else:
            object.__setattr__(self, name, value)

    def __getattribute__(self, name):
        persistent_attributes = object.__getattribute__(self, '_persistent_attributes')
        if name in persistent_attributes:
            try:
                return self.root[name]
            except KeyError:
                return getattr(self.__class__, name)
        else:
            return object.__getattribute__(self, name)

    def new_game(self):
        """
        Start up a new game (clear the storage instance).
        """
        self.scheduler  = None
        self.started    = True
        self.lastroom   = None
        self.universe   = None
        self.characters = None
        self.player     = None
        self.debugging  = False
        self.commit()
        self.pack()
        
    def commit(self):
        self.storage.commit()

    def abort(self):
        self.storage.abort()

    def pack(self):
        self.storage.pack()


    # FIXME: need 'rollback', 'savepoint', etc



# 1) locale info is not stored in the persistent storage. You can change language in the middle of game.
#
# 2) verbs are not stored in the persistent storage, they must be imported.
#    names of verbs are mapped from the locale (as are names of Nouns)
#
# 3) symbol table is generated on each startup (it's part of the code)
#
# 4) all noun instances are stored in the persistent cache, including their relationships to each other
#    this is in the "universe" key. All topological relationships are modeled as object database
#    relationships and all universe changes are therefore object database transactions

