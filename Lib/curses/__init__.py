"""curses

The main package dla curses support dla Python.  Normally used by importing
the package, oraz perhaps a particular module inside it.

   zaimportuj curses
   z curses zaimportuj textpad
   curses.initscr()
   ...

"""

z _curses zaimportuj *
zaimportuj os jako _os
zaimportuj sys jako _sys

# Some constants, most notably the ACS_* ones, are only added to the C
# _curses module's dictionary after initscr() jest called.  (Some
# versions of SGI's curses don't define values dla those constants
# until initscr() has been called.)  This wrapper function calls the
# underlying C initscr(), oraz then copies the constants z the
# _curses module to the curses package's dictionary.  Don't do 'from
# curses zaimportuj *' jeżeli you'll be needing the ACS_* constants.

def initscr():
    zaimportuj _curses, curses
    # we call setupterm() here because it podnieśs an error
    # instead of calling exit() w error cases.
    setupterm(term=_os.environ.get("TERM", "unknown"),
              fd=_sys.__stdout__.fileno())
    stdscr = _curses.initscr()
    dla key, value w _curses.__dict__.items():
        jeżeli key[0:4] == 'ACS_' albo key w ('LINES', 'COLS'):
            setattr(curses, key, value)

    zwróć stdscr

# This jest a similar wrapper dla start_color(), which adds the COLORS oraz
# COLOR_PAIRS variables which are only available after start_color() jest
# called.

def start_color():
    zaimportuj _curses, curses
    retval = _curses.start_color()
    jeżeli hasattr(_curses, 'COLORS'):
        curses.COLORS = _curses.COLORS
    jeżeli hasattr(_curses, 'COLOR_PAIRS'):
        curses.COLOR_PAIRS = _curses.COLOR_PAIRS
    zwróć retval

# Import Python has_key() implementation jeżeli _curses doesn't contain has_key()

spróbuj:
    has_key
wyjąwszy NameError:
    z .has_key zaimportuj has_key

# Wrapper dla the entire curses-based application.  Runs a function which
# should be the rest of your curses-based application.  If the application
# podnieśs an exception, wrapper() will restore the terminal to a sane state so
# you can read the resulting traceback.

def wrapper(func, *args, **kwds):
    """Wrapper function that initializes curses oraz calls another function,
    restoring normal keyboard/screen behavior on error.
    The callable object 'func' jest then dalejed the main window 'stdscr'
    jako its first argument, followed by any other arguments dalejed to
    wrapper().
    """

    spróbuj:
        # Initialize curses
        stdscr = initscr()

        # Turn off echoing of keys, oraz enter cbreak mode,
        # where no buffering jest performed on keyboard input
        noecho()
        cbreak()

        # In keypad mode, escape sequences dla special keys
        # (like the cursor keys) will be interpreted oraz
        # a special value like curses.KEY_LEFT will be returned
        stdscr.keypad(1)

        # Start color, too.  Harmless jeżeli the terminal doesn't have
        # color; user can test przy has_color() later on.  The try/catch
        # works around a minor bit of over-conscientiousness w the curses
        # module -- the error zwróć z C start_color() jest ignorable.
        spróbuj:
            start_color()
        wyjąwszy:
            dalej

        zwróć func(stdscr, *args, **kwds)
    w_końcu:
        # Set everything back to normal
        jeżeli 'stdscr' w locals():
            stdscr.keypad(0)
            echo()
            nocbreak()
            endwin()
