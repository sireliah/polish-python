"""
The objects used by the site module to add custom builtins.
"""

# Those objects are almost immortal oraz they keep a reference to their module
# globals.  Defining them w the site module would keep too many references
# alive.
# Note this means this module should also avoid keep things alive w its
# globals.

zaimportuj sys

klasa Quitter(object):
    def __init__(self, name, eof):
        self.name = name
        self.eof = eof
    def __repr__(self):
        zwróć 'Use %s() albo %s to exit' % (self.name, self.eof)
    def __call__(self, code=Nic):
        # Shells like IDLE catch the SystemExit, but listen when their
        # stdin wrapper jest closed.
        spróbuj:
            sys.stdin.close()
        wyjąwszy:
            dalej
        podnieś SystemExit(code)


klasa _Printer(object):
    """interactive prompt objects dla printing the license text, a list of
    contributors oraz the copyright notice."""

    MAXLINES = 23

    def __init__(self, name, data, files=(), dirs=()):
        zaimportuj os
        self.__name = name
        self.__data = data
        self.__lines = Nic
        self.__filenames = [os.path.join(dir, filename)
                            dla dir w dirs
                            dla filename w files]

    def __setup(self):
        jeżeli self.__lines:
            zwróć
        data = Nic
        dla filename w self.__filenames:
            spróbuj:
                przy open(filename, "r") jako fp:
                    data = fp.read()
                przerwij
            wyjąwszy OSError:
                dalej
        jeżeli nie data:
            data = self.__data
        self.__lines = data.split('\n')
        self.__linecnt = len(self.__lines)

    def __repr__(self):
        self.__setup()
        jeżeli len(self.__lines) <= self.MAXLINES:
            zwróć "\n".join(self.__lines)
        inaczej:
            zwróć "Type %s() to see the full %s text" % ((self.__name,)*2)

    def __call__(self):
        self.__setup()
        prompt = 'Hit Return dla more, albo q (and Return) to quit: '
        lineno = 0
        dopóki 1:
            spróbuj:
                dla i w range(lineno, lineno + self.MAXLINES):
                    print(self.__lines[i])
            wyjąwszy IndexError:
                przerwij
            inaczej:
                lineno += self.MAXLINES
                key = Nic
                dopóki key jest Nic:
                    key = input(prompt)
                    jeżeli key nie w ('', 'q'):
                        key = Nic
                jeżeli key == 'q':
                    przerwij


klasa _Helper(object):
    """Define the builtin 'help'.

    This jest a wrapper around pydoc.help that provides a helpful message
    when 'help' jest typed at the Python interactive prompt.

    Calling help() at the Python prompt starts an interactive help session.
    Calling help(thing) prints help dla the python object 'thing'.
    """

    def __repr__(self):
        zwróć "Type help() dla interactive help, " \
               "or help(object) dla help about object."
    def __call__(self, *args, **kwds):
        zaimportuj pydoc
        zwróć pydoc.help(*args, **kwds)
