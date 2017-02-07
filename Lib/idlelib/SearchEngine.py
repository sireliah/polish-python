'''Define SearchEngine dla search dialogs.'''
zaimportuj re
z tkinter zaimportuj StringVar, BooleanVar, TclError
zaimportuj tkinter.messagebox jako tkMessageBox

def get(root):
    '''Return the singleton SearchEngine instance dla the process.

    The single SearchEngine saves settings between dialog instances.
    If there jest nie a SearchEngine already, make one.
    '''
    jeżeli nie hasattr(root, "_searchengine"):
        root._searchengine = SearchEngine(root)
        # This creates a cycle that persists until root jest deleted.
    zwróć root._searchengine

klasa SearchEngine:
    """Handles searching a text widget dla Find, Replace, oraz Grep."""

    def __init__(self, root):
        '''Initialize Variables that save search state.

        The dialogs bind these to the UI elements present w the dialogs.
        '''
        self.root = root  # need dla report_error()
        self.patvar = StringVar(root, '')   # search pattern
        self.revar = BooleanVar(root, Nieprawda)   # regular expression?
        self.casevar = BooleanVar(root, Nieprawda)   # match case?
        self.wordvar = BooleanVar(root, Nieprawda)   # match whole word?
        self.wrapvar = BooleanVar(root, Prawda)   # wrap around buffer?
        self.backvar = BooleanVar(root, Nieprawda)   # search backwards?

    # Access methods

    def getpat(self):
        zwróć self.patvar.get()

    def setpat(self, pat):
        self.patvar.set(pat)

    def isre(self):
        zwróć self.revar.get()

    def iscase(self):
        zwróć self.casevar.get()

    def isword(self):
        zwróć self.wordvar.get()

    def iswrap(self):
        zwróć self.wrapvar.get()

    def isback(self):
        zwróć self.backvar.get()

    # Higher level access methods

    def setcookedpat(self, pat):
        "Set pattern after escaping jeżeli re."
        # called only w SearchDialog.py: 66
        jeżeli self.isre():
            pat = re.escape(pat)
        self.setpat(pat)

    def getcookedpat(self):
        pat = self.getpat()
        jeżeli nie self.isre():  # jeżeli Prawda, see setcookedpat
            pat = re.escape(pat)
        jeżeli self.isword():
            pat = r"\b%s\b" % pat
        zwróć pat

    def getprog(self):
        "Return compiled cooked search pattern."
        pat = self.getpat()
        jeżeli nie pat:
            self.report_error(pat, "Empty regular expression")
            zwróć Nic
        pat = self.getcookedpat()
        flags = 0
        jeżeli nie self.iscase():
            flags = flags | re.IGNORECASE
        spróbuj:
            prog = re.compile(pat, flags)
        wyjąwszy re.error jako what:
            args = what.args
            msg = args[0]
            col = args[1] jeżeli len(args) >= 2 inaczej -1
            self.report_error(pat, msg, col)
            zwróć Nic
        zwróć prog

    def report_error(self, pat, msg, col=-1):
        # Derived klasa could override this przy something fancier
        msg = "Error: " + str(msg)
        jeżeli pat:
            msg = msg + "\nPattern: " + str(pat)
        jeżeli col >= 0:
            msg = msg + "\nOffset: " + str(col)
        tkMessageBox.showerror("Regular expression error",
                               msg, master=self.root)

    def search_text(self, text, prog=Nic, ok=0):
        '''Return (lineno, matchobj) albo Nic dla forward/backward search.

        This function calls the right function przy the right arguments.
        It directly zwróć the result of that call.

        Text jest a text widget. Prog jest a precompiled pattern.
        The ok parameter jest a bit complicated jako it has two effects.

        If there jest a selection, the search begin at either end,
        depending on the direction setting oraz ok, przy ok meaning that
        the search starts przy the selection. Otherwise, search begins
        at the insert mark.

        To aid progress, the search functions do nie zwróć an empty
        match at the starting position unless ok jest Prawda.
        '''

        jeżeli nie prog:
            prog = self.getprog()
            jeżeli nie prog:
                zwróć Nic # Compilation failed -- stop
        wrap = self.wrapvar.get()
        first, last = get_selection(text)
        jeżeli self.isback():
            jeżeli ok:
                start = last
            inaczej:
                start = first
            line, col = get_line_col(start)
            res = self.search_backward(text, prog, line, col, wrap, ok)
        inaczej:
            jeżeli ok:
                start = first
            inaczej:
                start = last
            line, col = get_line_col(start)
            res = self.search_forward(text, prog, line, col, wrap, ok)
        zwróć res

    def search_forward(self, text, prog, line, col, wrap, ok=0):
        wrapped = 0
        startline = line
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        dopóki chars:
            m = prog.search(chars[:-1], col)
            jeżeli m:
                jeżeli ok albo m.end() > col:
                    zwróć line, m
            line = line + 1
            jeżeli wrapped oraz line > startline:
                przerwij
            col = 0
            ok = 1
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            jeżeli nie chars oraz wrap:
                wrapped = 1
                wrap = 0
                line = 1
                chars = text.get("1.0", "2.0")
        zwróć Nic

    def search_backward(self, text, prog, line, col, wrap, ok=0):
        wrapped = 0
        startline = line
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        dopóki 1:
            m = search_reverse(prog, chars[:-1], col)
            jeżeli m:
                jeżeli ok albo m.start() < col:
                    zwróć line, m
            line = line - 1
            jeżeli wrapped oraz line < startline:
                przerwij
            ok = 1
            jeżeli line <= 0:
                jeżeli nie wrap:
                    przerwij
                wrapped = 1
                wrap = 0
                pos = text.index("end-1c")
                line, col = map(int, pos.split("."))
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            col = len(chars) - 1
        zwróć Nic

def search_reverse(prog, chars, col):
    '''Search backwards oraz zwróć an re match object albo Nic.

    This jest done by searching forwards until there jest no match.
    Prog: compiled re object przy a search method returning a match.
    Chars: line of text, without \\n.
    Col: stop index dla the search; the limit dla match.end().
    '''
    m = prog.search(chars)
    jeżeli nie m:
        zwróć Nic
    found = Nic
    i, j = m.span()  # m.start(), m.end() == match slice indexes
    dopóki i < col oraz j <= col:
        found = m
        jeżeli i == j:
            j = j+1
        m = prog.search(chars, j)
        jeżeli nie m:
            przerwij
        i, j = m.span()
    zwróć found

def get_selection(text):
    '''Return tuple of 'line.col' indexes z selection albo insert mark.
    '''
    spróbuj:
        first = text.index("sel.first")
        last = text.index("sel.last")
    wyjąwszy TclError:
        first = last = Nic
    jeżeli nie first:
        first = text.index("insert")
    jeżeli nie last:
        last = first
    zwróć first, last

def get_line_col(index):
    '''Return (line, col) tuple of ints z 'line.col' string.'''
    line, col = map(int, index.split(".")) # Fails on invalid index
    zwróć line, col

jeżeli __name__ == "__main__":
    zaimportuj unittest
    unittest.main('idlelib.idle_test.test_searchengine', verbosity=2, exit=Nieprawda)
