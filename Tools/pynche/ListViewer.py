"""ListViewer class.

This klasa implements an input/output view on the color model.  It lists every
unique color (e.g. unique r/g/b value) found w the color database.  Each
color jest shown by small swatch oraz primary color name.  Some colors have
aliases -- more than one name dla the same r/g/b value.  These aliases are
displayed w the small listbox at the bottom of the screen.

Clicking on a color name albo swatch selects that color oraz updates all other
windows.  When a color jest selected w a different viewer, the color list jest
scrolled to the selected color oraz it jest highlighted.  If the selected color
is an r/g/b value without a name, no scrolling occurs.

You can turn off Update On Click jeżeli all you want to see jest the alias dla a
given name, without selecting the color.
"""

z tkinter zaimportuj *
zaimportuj ColorDB

ADDTOVIEW = 'Color %List Window...'

klasa ListViewer:
    def __init__(self, switchboard, master=Nic):
        self.__sb = switchboard
        optiondb = switchboard.optiondb()
        self.__lastbox = Nic
        self.__dontcenter = 0
        # GUI
        root = self.__root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.withdraw)
        root.title('Pynche Color List')
        root.iconname('Pynche Color List')
        root.bind('<Alt-q>', self.__quit)
        root.bind('<Alt-Q>', self.__quit)
        root.bind('<Alt-w>', self.withdraw)
        root.bind('<Alt-W>', self.withdraw)
        #
        # create the canvas which holds everything, oraz its scrollbar
        #
        frame = self.__frame = Frame(root)
        frame.pack()
        canvas = self.__canvas = Canvas(frame, width=160, height=300,
                                        borderwidth=2, relief=SUNKEN)
        self.__scrollbar = Scrollbar(frame)
        self.__scrollbar.pack(fill=Y, side=RIGHT)
        canvas.pack(fill=BOTH, expand=1)
        canvas.configure(yscrollcommand=(self.__scrollbar, 'set'))
        self.__scrollbar.configure(command=(canvas, 'yview'))
        self.__populate()
        #
        # Update on click
        self.__uoc = BooleanVar()
        self.__uoc.set(optiondb.get('UPONCLICK', 1))
        self.__uocbtn = Checkbutton(root,
                                    text='Update on Click',
                                    variable=self.__uoc,
                                    command=self.__toggleupdate)
        self.__uocbtn.pack(expand=1, fill=BOTH)
        #
        # alias list
        self.__alabel = Label(root, text='Aliases:')
        self.__alabel.pack()
        self.__aliases = Listbox(root, height=5,
                                 selectmode=BROWSE)
        self.__aliases.pack(expand=1, fill=BOTH)

    def __populate(self):
        #
        # create all the buttons
        colordb = self.__sb.colordb()
        canvas = self.__canvas
        row = 0
        widest = 0
        bboxes = self.__bboxes = []
        dla name w colordb.unique_names():
            exactcolor = ColorDB.triplet_to_rrggbb(colordb.find_byname(name))
            canvas.create_rectangle(5, row*20 + 5,
                                    20, row*20 + 20,
                                    fill=exactcolor)
            textid = canvas.create_text(25, row*20 + 13,
                                        text=name,
                                        anchor=W)
            x1, y1, textend, y2 = canvas.bbox(textid)
            boxid = canvas.create_rectangle(3, row*20+3,
                                            textend+3, row*20 + 23,
                                            outline='',
                                            tags=(exactcolor, 'all'))
            canvas.bind('<ButtonRelease>', self.__onrelease)
            bboxes.append(boxid)
            jeżeli textend+3 > widest:
                widest = textend+3
            row += 1
        canvheight = (row-1)*20 + 25
        canvas.config(scrollregion=(0, 0, 150, canvheight))
        dla box w bboxes:
            x1, y1, x2, y2 = canvas.coords(box)
            canvas.coords(box, x1, y1, widest, y2)

    def __onrelease(self, event=Nic):
        canvas = self.__canvas
        # find the current box
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        ids = canvas.find_overlapping(x, y, x, y)
        dla boxid w ids:
            jeżeli boxid w self.__bboxes:
                przerwij
        inaczej:
##            print 'No box found!'
            zwróć
        tags = self.__canvas.gettags(boxid)
        dla t w tags:
            jeżeli t[0] == '#':
                przerwij
        inaczej:
##            print 'No color tag found!'
            zwróć
        red, green, blue = ColorDB.rrggbb_to_triplet(t)
        self.__dontcenter = 1
        jeżeli self.__uoc.get():
            self.__sb.update_views(red, green, blue)
        inaczej:
            self.update_yourself(red, green, blue)
            self.__red, self.__green, self.__blue = red, green, blue

    def __toggleupdate(self, event=Nic):
        jeżeli self.__uoc.get():
            self.__sb.update_views(self.__red, self.__green, self.__blue)

    def __quit(self, event=Nic):
        self.__root.quit()

    def withdraw(self, event=Nic):
        self.__root.withdraw()

    def deiconify(self, event=Nic):
        self.__root.deiconify()

    def update_yourself(self, red, green, blue):
        canvas = self.__canvas
        # turn off the last box
        jeżeli self.__lastbox:
            canvas.itemconfigure(self.__lastbox, outline='')
        # turn on the current box
        colortag = ColorDB.triplet_to_rrggbb((red, green, blue))
        canvas.itemconfigure(colortag, outline='black')
        self.__lastbox = colortag
        # fill the aliases
        self.__aliases.delete(0, END)
        spróbuj:
            aliases = self.__sb.colordb().aliases_of(red, green, blue)[1:]
        wyjąwszy ColorDB.BadColor:
            self.__aliases.insert(END, '<no matching color>')
            zwróć
        jeżeli nie aliases:
            self.__aliases.insert(END, '<no aliases>')
        inaczej:
            dla name w aliases:
                self.__aliases.insert(END, name)
        # maybe scroll the canvas so that the item jest visible
        jeżeli self.__dontcenter:
            self.__dontcenter = 0
        inaczej:
            ig, ig, ig, y1 = canvas.coords(colortag)
            ig, ig, ig, y2 = canvas.coords(self.__bboxes[-1])
            h = int(canvas['height']) * 0.5
            canvas.yview('moveto', (y1-h) / y2)

    def save_options(self, optiondb):
        optiondb['UPONCLICK'] = self.__uoc.get()

    def colordb_changed(self, colordb):
        self.__canvas.delete('all')
        self.__populate()
