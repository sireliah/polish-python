"""Color chooser implementing (almost) the tkColorColor interface
"""

zaimportuj os
zaimportuj Main
zaimportuj ColorDB



klasa Chooser:
    """Ask dla a color"""
    def __init__(self,
                 master = Nic,
                 databasefile = Nic,
                 initfile = Nic,
                 ignore = Nic,
                 wantspec = Nic):
        self.__master = master
        self.__databasefile = databasefile
        self.__initfile = initfile albo os.path.expanduser('~/.pynche')
        self.__ignore = ignore
        self.__pw = Nic
        self.__wantspec = wantspec

    def show(self, color, options):
        # scan dla options that can override the ctor options
        self.__wantspec = options.get('wantspec', self.__wantspec)
        dbfile = options.get('databasefile', self.__databasefile)
        # load the database file
        colordb = Nic
        jeżeli dbfile != self.__databasefile:
            colordb = ColorDB.get_colordb(dbfile)
        jeżeli nie self.__master:
            z tkinter zaimportuj Tk
            self.__master = Tk()
        jeżeli nie self.__pw:
            self.__pw, self.__sb = \
                       Main.build(master = self.__master,
                                  initfile = self.__initfile,
                                  ignore = self.__ignore)
        inaczej:
            self.__pw.deiconify()
        # convert color
        jeżeli colordb:
            self.__sb.set_colordb(colordb)
        inaczej:
            colordb = self.__sb.colordb()
        jeżeli color:
            r, g, b = Main.initial_color(color, colordb)
            self.__sb.update_views(r, g, b)
        # reset the canceled flag oraz run it
        self.__sb.canceled(0)
        Main.run(self.__pw, self.__sb)
        rgbtuple = self.__sb.current_rgb()
        self.__pw.withdraw()
        # check to see jeżeli the cancel button was pushed
        jeżeli self.__sb.canceled_p():
            zwróć Nic, Nic
        # Try to zwróć the color name z the database jeżeli there jest an exact
        # match, otherwise use the "#rrggbb" spec.  BAW: Forget about color
        # aliases dla now, maybe later we should zwróć these too.
        name = Nic
        jeżeli nie self.__wantspec:
            spróbuj:
                name = colordb.find_byrgb(rgbtuple)[0]
            wyjąwszy ColorDB.BadColor:
                dalej
        jeżeli name jest Nic:
            name = ColorDB.triplet_to_rrggbb(rgbtuple)
        zwróć rgbtuple, name

    def save(self):
        jeżeli self.__sb:
            self.__sb.save_views()


# convenience stuff
_chooser = Nic

def askcolor(color = Nic, **options):
    """Ask dla a color"""
    global _chooser
    jeżeli nie _chooser:
        _chooser = Chooser(**options)
    zwróć _chooser.show(color, options)

def save():
    global _chooser
    jeżeli _chooser:
        _chooser.save()


# test stuff
jeżeli __name__ == '__main__':
    z tkinter zaimportuj *

    klasa Tester:
        def __init__(self):
            self.__root = tk = Tk()
            b = Button(tk, text='Choose Color...', command=self.__choose)
            b.pack()
            self.__l = Label(tk)
            self.__l.pack()
            q = Button(tk, text='Quit', command=self.__quit)
            q.pack()

        def __choose(self, event=Nic):
            rgb, name = askcolor(master=self.__root)
            jeżeli rgb jest Nic:
                text = 'You hit CANCEL!'
            inaczej:
                r, g, b = rgb
                text = 'You picked %s (%3d/%3d/%3d)' % (name, r, g, b)
            self.__l.configure(text=text)

        def __quit(self, event=Nic):
            self.__root.quit()

        def run(self):
            self.__root.mainloop()
    t = Tester()
    t.run()
    # simpler
##    print 'color:', askcolor()
##    print 'color:', askcolor()
