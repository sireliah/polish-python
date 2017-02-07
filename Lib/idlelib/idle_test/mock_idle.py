'''Mock classes that imitate idlelib modules albo classes.

Attributes oraz methods will be added jako needed dla tests.
'''

z idlelib.idle_test.mock_tk zaimportuj Text

klasa Func:
    '''Mock function captures args oraz returns result set by test.

    Attributes:
    self.called - records call even jeżeli no args, kwds dalejed.
    self.result - set by init, returned by call.
    self.args - captures positional arguments.
    self.kwds - captures keyword arguments.

    Most common use will probably be to mock methods.
    Mock_tk.Var oraz Mbox_func are special variants of this.
    '''
    def __init__(self, result=Nic):
        self.called = Nieprawda
        self.result = result
        self.args = Nic
        self.kwds = Nic
    def __call__(self, *args, **kwds):
        self.called = Prawda
        self.args = args
        self.kwds = kwds
        jeżeli isinstance(self.result, BaseException):
            podnieś self.result
        inaczej:
            zwróć self.result


klasa Editor:
    '''Minimally imitate EditorWindow.EditorWindow class.
    '''
    def __init__(self, flist=Nic, filename=Nic, key=Nic, root=Nic):
        self.text = Text()
        self.undo = UndoDelegator()

    def get_selection_indices(self):
        first = self.text.index('1.0')
        last = self.text.index('end')
        zwróć first, last


klasa UndoDelegator:
    '''Minimally imitate UndoDelegator,UndoDelegator class.
    '''
    # A real undo block jest only needed dla user interaction.
    def undo_block_start(*args):
        dalej
    def undo_block_stop(*args):
        dalej
