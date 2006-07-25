import dispatch

class Askable:
    """"""
    def __init__(self):
        self.answer = {'ha':'ho'}

    def __call__(self, parent):
        
        @parent.ask.when('cmd')
        def ask(self, cmd, c=self):
            if c.answer[cmd]: print (c.answer[cmd])


class a:
    def __init__(self):
        """"""
    @dispatch.generic()
    def ask(self,cmd):
        """"""

def run_it():
    component = Askable()
    object = a()

    #This actually makes the dispatch.
    component(object)
    object.ask('ha')
