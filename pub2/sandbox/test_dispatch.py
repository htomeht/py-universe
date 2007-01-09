import dispatch

class Askable:
    """"""
    def __init__(self):
        self.answer = {'ha':'ho'}

    def __call__(self, parent):
        
        @parent.ask.when('cmd')
        def ask(self, cmd, c=self):
            if c.answer[cmd]: print (c.answer[cmd])
            print parent.x

        @parent.ask.before('parent.x == 5')
        def ask(self, cmd, c=self):
            print 'I evaluate first'

        @parent.ask.after('parent.x == 5')
        def ask(self, cmd, c=self):
            print 'I evaluate last'
          

class a:
    def __init__(self):
        """"""
        self.x = 5

    @dispatch.generic()
    def ask(self,cmd):
        """"""

def run_it():
    component = Askable()
    object = a()

    #This actually makes the dispatch.
    component(object)
    object.ask('ha')

run_it()
