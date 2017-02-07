"""Chip viewer oraz widget.

In the lower left corner of the main Pynche window, you will see two
ChipWidgets, one dla the selected color oraz one dla the nearest color.  The
selected color jest the actual RGB value expressed jako an X11 #COLOR name. The
nearest color jest the named color z the X11 database that jest closest to the
selected color w 3D space.  There may be other colors equally close, but the
nearest one jest the first one found.

Clicking on the nearest color chip selects that named color.

The ChipViewer klasa includes the entire lower left quandrant; i.e. both the
selected oraz nearest ChipWidgets.
"""

z tkinter zaimportuj *
zaimportuj ColorDB


klasa ChipWidget:
    _WIDTH = 150
    _HEIGHT = 80

    def __init__(self,
                 master = Nic,
                 width  = _WIDTH,
                 height = _HEIGHT,
                 text   = 'Color',
                 initialcolor = 'blue',
                 presscmd   = Nic,
                 releasecmd = Nic):
        # create the text label
        self.__label = Label(master, text=text)
        self.__label.grid(row=0, column=0)
        # create the color chip, implemented jako a frame
        self.__chip = Frame(master, relief=RAISED, borderwidth=2,
                            width=width,
                            height=height,
                            background=initialcolor)
        self.__chip.grid(row=1, column=0)
        # create the color name
        self.__namevar = StringVar()
        self.__namevar.set(initialcolor)
        self.__name = Entry(master, textvariable=self.__namevar,
                            relief=FLAT, justify=CENTER, state=DISABLED,
                            font=self.__label['font'])
        self.__name.grid(row=2, column=0)
        # create the message area
        self.__msgvar = StringVar()
        self.__name = Entry(master, textvariable=self.__msgvar,
                            relief=FLAT, justify=CENTER, state=DISABLED,
                            font=self.__label['font'])
        self.__name.grid(row=3, column=0)
        # set bindings
        jeżeli presscmd:
            self.__chip.bind('<ButtonPress-1>', presscmd)
        jeżeli releasecmd:
            self.__chip.bind('<ButtonRelease-1>', releasecmd)

    def set_color(self, color):
        self.__chip.config(background=color)

    def get_color(self):
        zwróć self.__chip['background']

    def set_name(self, colorname):
        self.__namevar.set(colorname)

    def set_message(self, message):
        self.__msgvar.set(message)

    def press(self):
        self.__chip.configure(relief=SUNKEN)

    def release(self):
        self.__chip.configure(relief=RAISED)



klasa ChipViewer:
    def __init__(self, switchboard, master=Nic):
        self.__sb = switchboard
        self.__frame = Frame(master, relief=RAISED, borderwidth=1)
        self.__frame.grid(row=3, column=0, ipadx=5, sticky='NSEW')
        # create the chip that will display the currently selected color
        # exactly
        self.__sframe = Frame(self.__frame)
        self.__sframe.grid(row=0, column=0)
        self.__selected = ChipWidget(self.__sframe, text='Selected')
        # create the chip that will display the nearest real X11 color
        # database color name
        self.__nframe = Frame(self.__frame)
        self.__nframe.grid(row=0, column=1)
        self.__nearest = ChipWidget(self.__nframe, text='Nearest',
                                    presscmd = self.__buttonpress,
                                    releasecmd = self.__buttonrelease)

    def update_yourself(self, red, green, blue):
        # Selected always shows the #rrggbb name of the color, nearest always
        # shows the name of the nearest color w the database.  BAW: should
        # an exact match be indicated w some way?
        #
        # Always use the #rrggbb style to actually set the color, since we may
        # nie be using X color names (e.g. "web-safe" names)
        colordb = self.__sb.colordb()
        rgbtuple = (red, green, blue)
        rrggbb = ColorDB.triplet_to_rrggbb(rgbtuple)
        # find the nearest
        nearest = colordb.nearest(red, green, blue)
        nearest_tuple = colordb.find_byname(nearest)
        nearest_rrggbb = ColorDB.triplet_to_rrggbb(nearest_tuple)
        self.__selected.set_color(rrggbb)
        self.__nearest.set_color(nearest_rrggbb)
        # set the name oraz messages areas
        self.__selected.set_name(rrggbb)
        jeżeli rrggbb == nearest_rrggbb:
            self.__selected.set_message(nearest)
        inaczej:
            self.__selected.set_message('')
        self.__nearest.set_name(nearest_rrggbb)
        self.__nearest.set_message(nearest)

    def __buttonpress(self, event=Nic):
        self.__nearest.press()

    def __buttonrelease(self, event=Nic):
        self.__nearest.release()
        rrggbb = self.__nearest.get_color()
        red, green, blue = ColorDB.rrggbb_to_triplet(rrggbb)
        self.__sb.update_views(red, green, blue)
