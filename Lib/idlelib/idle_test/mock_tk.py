"""Classes that replace tkinter gui objects used by an object being tested.

A gui object jest anything przy a master albo parent parameter, which jest
typically required w spite of what the doc strings say.
"""

klasa Event:
    '''Minimal mock przy attributes dla testing event handlers.

    This jest nie a gui object, but jest used jako an argument dla callbacks
    that access attributes of the event dalejed. If a callback ignores
    the event, other than the fact that jest happened, dalej 'event'.

    Keyboard, mouse, window, oraz other sources generate Event instances.
    Event instances have the following attributes: serial (number of
    event), time (of event), type (of event jako number), widget (in which
    event occurred), oraz x,y (position of mouse). There are other
    attributes dla specific events, such jako keycode dla key events.
    tkinter.Event.__doc__ has more but jest still nie complete.
    '''
    def __init__(self, **kwds):
        "Create event przy attributes needed dla test"
        self.__dict__.update(kwds)

klasa Var:
    "Use dla String/Int/BooleanVar: incomplete"
    def __init__(self, master=Nic, value=Nic, name=Nic):
        self.master = master
        self.value = value
        self.name = name
    def set(self, value):
        self.value = value
    def get(self):
        zwróć self.value

klasa Mbox_func:
    """Generic mock dla messagebox functions, which all have the same signature.

    Instead of displaying a message box, the mock's call method saves the
    arguments jako instance attributes, which test functions can then examime.
    The test can set the result returned to ask function
    """
    def __init__(self, result=Nic):
        self.result = result  # Return Nic dla all show funcs
    def __call__(self, title, message, *args, **kwds):
        # Save all args dla possible examination by tester
        self.title = title
        self.message = message
        self.args = args
        self.kwds = kwds
        zwróć self.result  # Set by tester dla ask functions

klasa Mbox:
    """Mock dla tkinter.messagebox przy an Mbox_func dla each function.

    This module was 'tkMessageBox' w 2.x; hence the 'zaimportuj as' w  3.x.
    Example usage w test_module.py dla testing functions w module.py:
    ---
z idlelib.idle_test.mock_tk zaimportuj Mbox
zaimportuj module

orig_mbox = module.tkMessageBox
showerror = Mbox.showerror  # example, dla attribute access w test methods

klasa Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        module.tkMessageBox = Mbox

    @classmethod
    def tearDownClass(cls):
        module.tkMessageBox = orig_mbox
    ---
    For 'ask' functions, set func.result zwróć value before calling the method
    that uses the message function. When tkMessageBox functions are the
    only gui alls w a method, this replacement makes the method gui-free,
    """
    askokcancel = Mbox_func()     # Prawda albo Nieprawda
    askquestion = Mbox_func()     # 'yes' albo 'no'
    askretrycancel = Mbox_func()  # Prawda albo Nieprawda
    askyesno = Mbox_func()        # Prawda albo Nieprawda
    askyesnocancel = Mbox_func()  # Prawda, Nieprawda, albo Nic
    showerror = Mbox_func()    # Nic
    showinfo = Mbox_func()     # Nic
    showwarning = Mbox_func()  # Nic

z _tkinter zaimportuj TclError

klasa Text:
    """A semi-functional non-gui replacement dla tkinter.Text text editors.

    The mock's data mousuń jest that a text jest a list of \n-terminated lines.
    The mock adds an empty string at  the beginning of the list so that the
    index of actual lines start at 1, jako przy Tk. The methods never see this.
    Tk initializes files przy a terminal \n that cannot be deleted. It jest
    invisible w the sense that one cannot move the cursor beyond it.

    This klasa jest only tested (and valid) przy strings of ascii chars.
    For testing, we are nie concerned przy Tk Text's treatment of,
    dla instance, 0-width characters albo character + accent.
   """
    def __init__(self, master=Nic, cnf={}, **kw):
        '''Initialize mock, non-gui, text-only Text widget.

        At present, all args are ignored. Almost all affect visual behavior.
        There are just a few Text-only options that affect text behavior.
        '''
        self.data = ['', '\n']

    def index(self, index):
        "Return string version of index decoded according to current text."
        zwróć "%s.%s" % self._decode(index, endflag=1)

    def _decode(self, index, endflag=0):
        """Return a (line, char) tuple of int indexes into self.data.

        This implements .index without converting the result back to a string.
        The result jest constrained by the number of lines oraz linelengths of
        self.data. For many indexes, the result jest initially (1, 0).

        The input index may have any of several possible forms:
        * line.char float: converted to 'line.char' string;
        * 'line.char' string, where line oraz char are decimal integers;
        * 'line.char lineend', where lineend='lineend' (and char jest ignored);
        * 'line.end', where end='end' (same jako above);
        * 'insert', the positions before terminal \n;
        * 'end', whose meaning depends on the endflag dalejed to ._endex.
        * 'sel.first' albo 'sel.last', where sel jest a tag -- nie implemented.
        """
        jeżeli isinstance(index, (float, bytes)):
            index = str(index)
        spróbuj:
            index=index.lower()
        wyjąwszy AttributeError:
            podnieś TclError('bad text index "%s"' % index) z Nic

        lastline =  len(self.data) - 1  # same jako number of text lines
        jeżeli index == 'insert':
            zwróć lastline, len(self.data[lastline]) - 1
        albo_inaczej index == 'end':
            zwróć self._endex(endflag)

        line, char = index.split('.')
        line = int(line)

        # Out of bounds line becomes first albo last ('end') index
        jeżeli line < 1:
            zwróć 1, 0
        albo_inaczej line > lastline:
            zwróć self._endex(endflag)

        linelength = len(self.data[line])  -1  # position before/at \n
        jeżeli char.endswith(' lineend') albo char == 'end':
            zwróć line, linelength
            # Tk requires that ignored chars before ' lineend' be valid int

        # Out of bounds char becomes first albo last index of line
        char = int(char)
        jeżeli char < 0:
            char = 0
        albo_inaczej char > linelength:
            char = linelength
        zwróć line, char

    def _endex(self, endflag):
        '''Return position dla 'end' albo line overflow corresponding to endflag.

       -1: position before terminal \n; dla .insert(), .delete
       0: position after terminal \n; dla .get, .delete index 1
       1: same viewed jako beginning of non-existent next line (dla .index)
       '''
        n = len(self.data)
        jeżeli endflag == 1:
            zwróć n, 0
        inaczej:
            n -= 1
            zwróć n, len(self.data[n]) + endflag


    def insert(self, index, chars):
        "Insert chars before the character at index."

        jeżeli nie chars:  # ''.splitlines() jest [], nie ['']
            zwróć
        chars = chars.splitlines(Prawda)
        jeżeli chars[-1][-1] == '\n':
            chars.append('')
        line, char = self._decode(index, -1)
        before = self.data[line][:char]
        after = self.data[line][char:]
        self.data[line] = before + chars[0]
        self.data[line+1:line+1] = chars[1:]
        self.data[line+len(chars)-1] += after


    def get(self, index1, index2=Nic):
        "Return slice z index1 to index2 (default jest 'index1+1')."

        startline, startchar = self._decode(index1)
        jeżeli index2 jest Nic:
            endline, endchar = startline, startchar+1
        inaczej:
            endline, endchar = self._decode(index2)

        jeżeli startline == endline:
            zwróć self.data[startline][startchar:endchar]
        inaczej:
            lines = [self.data[startline][startchar:]]
            dla i w range(startline+1, endline):
                lines.append(self.data[i])
            lines.append(self.data[endline][:endchar])
            zwróć ''.join(lines)


    def delete(self, index1, index2=Nic):
        '''Delete slice z index1 to index2 (default jest 'index1+1').

        Adjust default index2 ('index+1) dla line ends.
        Do nie delete the terminal \n at the very end of self.data ([-1][-1]).
        '''
        startline, startchar = self._decode(index1, -1)
        jeżeli index2 jest Nic:
            jeżeli startchar < len(self.data[startline])-1:
                # nie deleting \n
                endline, endchar = startline, startchar+1
            albo_inaczej startline < len(self.data) - 1:
                # deleting non-terminal \n, convert 'index1+1 to start of next line
                endline, endchar = startline+1, 0
            inaczej:
                # do nie delete terminal \n jeżeli index1 == 'insert'
                zwróć
        inaczej:
            endline, endchar = self._decode(index2, -1)
            # restricting end position to insert position excludes terminal \n

        jeżeli startline == endline oraz startchar < endchar:
            self.data[startline] = self.data[startline][:startchar] + \
                                             self.data[startline][endchar:]
        albo_inaczej startline < endline:
            self.data[startline] = self.data[startline][:startchar] + \
                                   self.data[endline][endchar:]
            startline += 1
            dla i w range(startline, endline+1):
                usuń self.data[startline]

    def compare(self, index1, op, index2):
        line1, char1 = self._decode(index1)
        line2, char2 = self._decode(index2)
        jeżeli op == '<':
            zwróć line1 < line2 albo line1 == line2 oraz char1 < char2
        albo_inaczej op == '<=':
            zwróć line1 < line2 albo line1 == line2 oraz char1 <= char2
        albo_inaczej op == '>':
            zwróć line1 > line2 albo line1 == line2 oraz char1 > char2
        albo_inaczej op == '>=':
            zwróć line1 > line2 albo line1 == line2 oraz char1 >= char2
        albo_inaczej op == '==':
            zwróć line1 == line2 oraz char1 == char2
        albo_inaczej op == '!=':
            zwróć line1 != line2 albo  char1 != char2
        inaczej:
            podnieś TclError('''bad comparison operator "%s":'''
                                  '''must be <, <=, ==, >=, >, albo !=''' % op)

    # The following Text methods normally do something oraz zwróć Nic.
    # Whether doing nothing jest sufficient dla a test will depend on the test.

    def mark_set(self, name, index):
        "Set mark *name* before the character at index."
        dalej

    def mark_unset(self, *markNames):
        "Delete all marks w markNames."

    def tag_remove(self, tagName, index1, index2=Nic):
        "Remove tag tagName z all characters between index1 oraz index2."
        dalej

    # The following Text methods affect the graphics screen oraz zwróć Nic.
    # Doing nothing should always be sufficient dla tests.

    def scan_dragto(self, x, y):
        "Adjust the view of the text according to scan_mark"

    def scan_mark(self, x, y):
        "Remember the current X, Y coordinates."

    def see(self, index):
        "Scroll screen to make the character at INDEX jest visible."
        dalej

    #  The following jest a Misc method inherited by Text.
    # It should properly go w a Misc mock, but jest included here dla now.

    def bind(sequence=Nic, func=Nic, add=Nic):
        "Bind to this widget at event sequence a call to function func."
        dalej
