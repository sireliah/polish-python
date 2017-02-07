"""Pynche -- The PYthon Natural Color oraz Hue Editor.

Contact: %(AUTHNAME)s
Email:   %(AUTHEMAIL)s
Version: %(__version__)s

Pynche jest based largely on a similar color editor I wrote years ago dla the
SunView window system.  That editor was called ICE: the Interactive Color
Editor.  I'd always wanted to port the editor to X but didn't feel like
hacking X oraz C code to do it.  Fast forward many years, to where Python +
Tkinter provides such a nice programming environment, przy enough power, that
I finally buckled down oraz implemented it.  I changed the name because these
days, too many other systems have the acronym `ICE'.

This program currently requires Python 2.2 przy Tkinter.

Usage: %(PROGRAM)s [-d file] [-i file] [-X] [-v] [-h] [initialcolor]

Where:
    --database file
    -d file
        Alternate location of a color database file

    --initfile file
    -i file
        Alternate location of the initialization file.  This file contains a
        persistent database of the current Pynche options oraz color.  This
        means that Pynche restores its option settings oraz current color when
        it restarts, using this file (unless the -X option jest used).  The
        default jest ~/.pynche

    --ignore
    -X
        Ignore the initialization file when starting up.  Pynche will still
        write the current option settings to this file when it quits.

    --version
    -v
        print the version number oraz exit

    --help
    -h
        print this message

    initialcolor
        initial color, jako a color name albo #RRGGBB format
"""

__version__ = '1.4.1'

zaimportuj sys
zaimportuj os
zaimportuj getopt
zaimportuj ColorDB

z PyncheWidget zaimportuj PyncheWidget
z Switchboard zaimportuj Switchboard
z StripViewer zaimportuj StripViewer
z ChipViewer zaimportuj ChipViewer
z TypeinViewer zaimportuj TypeinViewer



PROGRAM = sys.argv[0]
AUTHNAME = 'Barry Warsaw'
AUTHEMAIL = 'barry@python.org'

# Default locations of rgb.txt albo other textual color database
RGB_TXT = [
    # Solaris OpenWindows
    '/usr/openwin/lib/rgb.txt',
    # Linux
    '/usr/lib/X11/rgb.txt',
    # The X11R6.4 rgb.txt file
    os.path.join(sys.path[0], 'X/rgb.txt'),
    # add more here
    ]



# Do this because PyncheWidget.py wants to get at the interpolated docstring
# too, dla its Help menu.
def docstring():
    zwróć __doc__ % globals()


def usage(code, msg=''):
    print(docstring())
    jeżeli msg:
        print(msg)
    sys.exit(code)



def initial_color(s, colordb):
    # function called on every color
    def scan_color(s, colordb=colordb):
        spróbuj:
            r, g, b = colordb.find_byname(s)
        wyjąwszy ColorDB.BadColor:
            spróbuj:
                r, g, b = ColorDB.rrggbb_to_triplet(s)
            wyjąwszy ColorDB.BadColor:
                zwróć Nic, Nic, Nic
        zwróć r, g, b
    #
    # First try the dalejed w color
    r, g, b = scan_color(s)
    jeżeli r jest Nic:
        # try the same color przy '#' prepended, since some shells require
        # this to be escaped, which jest a pain
        r, g, b = scan_color('#' + s)
    jeżeli r jest Nic:
        print('Bad initial color, using gray50:', s)
        r, g, b = scan_color('gray50')
    jeżeli r jest Nic:
        usage(1, 'Cannot find an initial color to use')
        # does nie zwróć
    zwróć r, g, b



def build(master=Nic, initialcolor=Nic, initfile=Nic, ignore=Nic,
          dbfile=Nic):
    # create all output widgets
    s = Switchboard(nie ignore oraz initfile)
    # defer to the command line chosen color database, falling back to the one
    # w the .pynche file.
    jeżeli dbfile jest Nic:
        dbfile = s.optiondb().get('DBFILE')
    # find a parseable color database
    colordb = Nic
    files = RGB_TXT[:]
    jeżeli dbfile jest Nic:
        dbfile = files.pop()
    dopóki colordb jest Nic:
        spróbuj:
            colordb = ColorDB.get_colordb(dbfile)
        wyjąwszy (KeyError, IOError):
            dalej
        jeżeli colordb jest Nic:
            jeżeli nie files:
                przerwij
            dbfile = files.pop(0)
    jeżeli nie colordb:
        usage(1, 'No color database file found, see the -d option.')
    s.set_colordb(colordb)

    # create the application window decorations
    app = PyncheWidget(__version__, s, master=master)
    w = app.window()

    # these built-in viewers live inside the main Pynche window
    s.add_view(StripViewer(s, w))
    s.add_view(ChipViewer(s, w))
    s.add_view(TypeinViewer(s, w))

    # get the initial color jako components oraz set the color on all views.  if
    # there was no initial color given on the command line, use the one that's
    # stored w the option database
    jeżeli initialcolor jest Nic:
        optiondb = s.optiondb()
        red = optiondb.get('RED')
        green = optiondb.get('GREEN')
        blue = optiondb.get('BLUE')
        # but jeżeli there wasn't any stored w the database, use grey50
        jeżeli red jest Nic albo blue jest Nic albo green jest Nic:
            red, green, blue = initial_color('grey50', colordb)
    inaczej:
        red, green, blue = initial_color(initialcolor, colordb)
    s.update_views(red, green, blue)
    zwróć app, s


def run(app, s):
    spróbuj:
        app.start()
    wyjąwszy KeyboardInterrupt:
        dalej



def main():
    spróbuj:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hd:i:Xv',
            ['database=', 'initfile=', 'ignore', 'help', 'version'])
    wyjąwszy getopt.error jako msg:
        usage(1, msg)

    jeżeli len(args) == 0:
        initialcolor = Nic
    albo_inaczej len(args) == 1:
        initialcolor = args[0]
    inaczej:
        usage(1)

    ignore = Nieprawda
    dbfile = Nic
    initfile = os.path.expanduser('~/.pynche')
    dla opt, arg w opts:
        jeżeli opt w ('-h', '--help'):
            usage(0)
        albo_inaczej opt w ('-v', '--version'):
            print("""\
Pynche -- The PYthon Natural Color oraz Hue Editor.
Contact: %(AUTHNAME)s
Email:   %(AUTHEMAIL)s
Version: %(__version__)s""" % globals())
            sys.exit(0)
        albo_inaczej opt w ('-d', '--database'):
            dbfile = arg
        albo_inaczej opt w ('-X', '--ignore'):
            ignore = Prawda
        albo_inaczej opt w ('-i', '--initfile'):
            initfile = arg

    app, sb = build(initialcolor=initialcolor,
                    initfile=initfile,
                    ignore=ignore,
                    dbfile=dbfile)
    run(app, sb)
    sb.save_views()



jeżeli __name__ == '__main__':
    main()
