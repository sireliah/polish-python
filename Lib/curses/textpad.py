"""Simple textbox editing widget przy Emacs-like keybindings."""

zaimportuj curses
zaimportuj curses.ascii

def rectangle(win, uly, ulx, lry, lrx):
    """Draw a rectangle przy corners at the provided upper-left
    oraz lower-right coordinates.
    """
    win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
    win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
    win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
    win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
    win.addch(uly, ulx, curses.ACS_ULCORNER)
    win.addch(uly, lrx, curses.ACS_URCORNER)
    win.addch(lry, lrx, curses.ACS_LRCORNER)
    win.addch(lry, ulx, curses.ACS_LLCORNER)

klasa Textbox:
    """Editing widget using the interior of a window object.
     Supports the following Emacs-like key bindings:

    Ctrl-A      Go to left edge of window.
    Ctrl-B      Cursor left, wrapping to previous line jeżeli appropriate.
    Ctrl-D      Delete character under cursor.
    Ctrl-E      Go to right edge (stripspaces off) albo end of line (stripspaces on).
    Ctrl-F      Cursor right, wrapping to next line when appropriate.
    Ctrl-G      Terminate, returning the window contents.
    Ctrl-H      Delete character backward.
    Ctrl-J      Terminate jeżeli the window jest 1 line, otherwise insert newline.
    Ctrl-K      If line jest blank, delete it, otherwise clear to end of line.
    Ctrl-L      Refresh screen.
    Ctrl-N      Cursor down; move down one line.
    Ctrl-O      Insert a blank line at cursor location.
    Ctrl-P      Cursor up; move up one line.

    Move operations do nothing jeżeli the cursor jest at an edge where the movement
    jest nie possible.  The following synonyms are supported where possible:

    KEY_LEFT = Ctrl-B, KEY_RIGHT = Ctrl-F, KEY_UP = Ctrl-P, KEY_DOWN = Ctrl-N
    KEY_BACKSPACE = Ctrl-h
    """
    def __init__(self, win, insert_mode=Nieprawda):
        self.win = win
        self.insert_mode = insert_mode
        (self.maxy, self.maxx) = win.getmaxyx()
        self.maxy = self.maxy - 1
        self.maxx = self.maxx - 1
        self.stripspaces = 1
        self.lastcmd = Nic
        win.keypad(1)

    def _end_of_line(self, y):
        """Go to the location of the first blank on the given line,
        returning the index of the last non-blank character."""
        last = self.maxx
        dopóki Prawda:
            jeżeli curses.ascii.ascii(self.win.inch(y, last)) != curses.ascii.SP:
                last = min(self.maxx, last+1)
                przerwij
            albo_inaczej last == 0:
                przerwij
            last = last - 1
        zwróć last

    def _insert_printable_char(self, ch):
        (y, x) = self.win.getyx()
        jeżeli y < self.maxy albo x < self.maxx:
            jeżeli self.insert_mode:
                oldch = self.win.inch()
            # The try-catch ignores the error we trigger z some curses
            # versions by trying to write into the lowest-rightmost spot
            # w the window.
            spróbuj:
                self.win.addch(ch)
            wyjąwszy curses.error:
                dalej
            jeżeli self.insert_mode:
                (backy, backx) = self.win.getyx()
                jeżeli curses.ascii.isprint(oldch):
                    self._insert_printable_char(oldch)
                    self.win.move(backy, backx)

    def do_command(self, ch):
        "Process a single editing command."
        (y, x) = self.win.getyx()
        self.lastcmd = ch
        jeżeli curses.ascii.isprint(ch):
            jeżeli y < self.maxy albo x < self.maxx:
                self._insert_printable_char(ch)
        albo_inaczej ch == curses.ascii.SOH:                           # ^a
            self.win.move(y, 0)
        albo_inaczej ch w (curses.ascii.STX,curses.KEY_LEFT, curses.ascii.BS,curses.KEY_BACKSPACE):
            jeżeli x > 0:
                self.win.move(y, x-1)
            albo_inaczej y == 0:
                dalej
            albo_inaczej self.stripspaces:
                self.win.move(y-1, self._end_of_line(y-1))
            inaczej:
                self.win.move(y-1, self.maxx)
            jeżeli ch w (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
        albo_inaczej ch == curses.ascii.EOT:                           # ^d
            self.win.delch()
        albo_inaczej ch == curses.ascii.ENQ:                           # ^e
            jeżeli self.stripspaces:
                self.win.move(y, self._end_of_line(y))
            inaczej:
                self.win.move(y, self.maxx)
        albo_inaczej ch w (curses.ascii.ACK, curses.KEY_RIGHT):       # ^f
            jeżeli x < self.maxx:
                self.win.move(y, x+1)
            albo_inaczej y == self.maxy:
                dalej
            inaczej:
                self.win.move(y+1, 0)
        albo_inaczej ch == curses.ascii.BEL:                           # ^g
            zwróć 0
        albo_inaczej ch == curses.ascii.NL:                            # ^j
            jeżeli self.maxy == 0:
                zwróć 0
            albo_inaczej y < self.maxy:
                self.win.move(y+1, 0)
        albo_inaczej ch == curses.ascii.VT:                            # ^k
            jeżeli x == 0 oraz self._end_of_line(y) == 0:
                self.win.deleteln()
            inaczej:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
        albo_inaczej ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        albo_inaczej ch w (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            jeżeli y < self.maxy:
                self.win.move(y+1, x)
                jeżeli x > self._end_of_line(y+1):
                    self.win.move(y+1, self._end_of_line(y+1))
        albo_inaczej ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
        albo_inaczej ch w (curses.ascii.DLE, curses.KEY_UP):          # ^p
            jeżeli y > 0:
                self.win.move(y-1, x)
                jeżeli x > self._end_of_line(y-1):
                    self.win.move(y-1, self._end_of_line(y-1))
        zwróć 1

    def gather(self):
        "Collect oraz zwróć the contents of the window."
        result = ""
        dla y w range(self.maxy+1):
            self.win.move(y, 0)
            stop = self._end_of_line(y)
            jeżeli stop == 0 oraz self.stripspaces:
                kontynuuj
            dla x w range(self.maxx+1):
                jeżeli self.stripspaces oraz x > stop:
                    przerwij
                result = result + chr(curses.ascii.ascii(self.win.inch(y, x)))
            jeżeli self.maxy > 0:
                result = result + "\n"
        zwróć result

    def edit(self, validate=Nic):
        "Edit w the widget window oraz collect the results."
        dopóki 1:
            ch = self.win.getch()
            jeżeli validate:
                ch = validate(ch)
            jeżeli nie ch:
                kontynuuj
            jeżeli nie self.do_command(ch):
                przerwij
            self.win.refresh()
        zwróć self.gather()

jeżeli __name__ == '__main__':
    def test_editbox(stdscr):
        ncols, nlines = 9, 4
        uly, ulx = 15, 20
        stdscr.addstr(uly-2, ulx, "Use Ctrl-G to end editing.")
        win = curses.newwin(nlines, ncols, uly, ulx)
        rectangle(stdscr, uly-1, ulx-1, uly + nlines, ulx + ncols)
        stdscr.refresh()
        zwróć Textbox(win).edit()

    str = curses.wrapper(test_editbox)
    print('Contents of text box:', repr(str))
