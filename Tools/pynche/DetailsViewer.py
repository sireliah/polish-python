"""DetailsViewer class.

This klasa implements a pure input window which allows you to meticulously
edit the current color.  You have both mouse control of the color (via the
buttons along the bottom row), oraz there are keyboard bindings dla each of the
increment/decrement buttons.

The top three check buttons allow you to specify which of the three color
variations are tied together when incrementing oraz decrementing.  Red, green,
and blue are self evident.  By tying together red oraz green, you can modify
the yellow level of the color.  By tying together red oraz blue, you can modify
the magenta level of the color.  By tying together green oraz blue, you can
modify the cyan level, oraz by tying all three together, you can modify the
grey level.

The behavior at the boundaries (0 oraz 255) are defined by the `At boundary'
option menu:

    Stop
        When the increment albo decrement would send any of the tied variations
        out of bounds, the entire delta jest discarded.

    Wrap Around
        When the increment albo decrement would send any of the tied variations
        out of bounds, the out of bounds variation jest wrapped around to the
        other side.  Thus jeżeli red were at 238 oraz 25 were added to it, red
        would have the value 7.

    Preserve Distance
        When the increment albo decrement would send any of the tied variations
        out of bounds, all tied variations are wrapped jako one, so jako to
        preserve the distance between them.  Thus jeżeli green oraz blue were tied,
        oraz green was at 238 dopóki blue was at 223, oraz an increment of 25
        were applied, green would be at 15 oraz blue would be at 0.

    Squash
        When the increment albo decrement would send any of the tied variations
        out of bounds, the out of bounds variation jest set to the ceiling of
        255 albo floor of 0, jako appropriate.  In this way, all tied variations
        are squashed to one edge albo the other.

The following key bindings can be used jako accelerators.  Note that Pynche can
fall behind jeżeli you hold the key down jako a key repeat:

Left arrow == -1
Right arrow == +1

Control + Left == -10
Control + Right == 10

Shift + Left == -25
Shift + Right == +25
"""

z tkinter zaimportuj *

STOP = 'Stop'
WRAP = 'Wrap Around'
RATIO = 'Preserve Distance'
GRAV = 'Squash'

ADDTOVIEW = 'Details Window...'


klasa DetailsViewer:
    def __init__(self, switchboard, master=Nic):
        self.__sb = switchboard
        optiondb = switchboard.optiondb()
        self.__red, self.__green, self.__blue = switchboard.current_rgb()
        # GUI
        root = self.__root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.withdraw)
        root.title('Pynche Details Window')
        root.iconname('Pynche Details Window')
        root.bind('<Alt-q>', self.__quit)
        root.bind('<Alt-Q>', self.__quit)
        root.bind('<Alt-w>', self.withdraw)
        root.bind('<Alt-W>', self.withdraw)
        # accelerators
        root.bind('<KeyPress-Left>', self.__minus1)
        root.bind('<KeyPress-Right>', self.__plus1)
        root.bind('<Control-KeyPress-Left>', self.__minus10)
        root.bind('<Control-KeyPress-Right>', self.__plus10)
        root.bind('<Shift-KeyPress-Left>', self.__minus25)
        root.bind('<Shift-KeyPress-Right>', self.__plus25)
        #
        # color ties
        frame = self.__frame = Frame(root)
        frame.pack(expand=YES, fill=X)
        self.__l1 = Label(frame, text='Move Sliders:')
        self.__l1.grid(row=1, column=0, sticky=E)
        self.__rvar = IntVar()
        self.__rvar.set(optiondb.get('RSLIDER', 4))
        self.__radio1 = Checkbutton(frame, text='Red',
                                    variable=self.__rvar,
                                    command=self.__effect,
                                    onvalue=4, offvalue=0)
        self.__radio1.grid(row=1, column=1, sticky=W)
        self.__gvar = IntVar()
        self.__gvar.set(optiondb.get('GSLIDER', 2))
        self.__radio2 = Checkbutton(frame, text='Green',
                                    variable=self.__gvar,
                                    command=self.__effect,
                                    onvalue=2, offvalue=0)
        self.__radio2.grid(row=2, column=1, sticky=W)
        self.__bvar = IntVar()
        self.__bvar.set(optiondb.get('BSLIDER', 1))
        self.__radio3 = Checkbutton(frame, text='Blue',
                                    variable=self.__bvar,
                                    command=self.__effect,
                                    onvalue=1, offvalue=0)
        self.__radio3.grid(row=3, column=1, sticky=W)
        self.__l2 = Label(frame)
        self.__l2.grid(row=4, column=1, sticky=W)
        self.__effect()
        #
        # Boundary behavior
        self.__l3 = Label(frame, text='At boundary:')
        self.__l3.grid(row=5, column=0, sticky=E)
        self.__boundvar = StringVar()
        self.__boundvar.set(optiondb.get('ATBOUND', STOP))
        self.__omenu = OptionMenu(frame, self.__boundvar,
                                  STOP, WRAP, RATIO, GRAV)
        self.__omenu.grid(row=5, column=1, sticky=W)
        self.__omenu.configure(width=17)
        #
        # Buttons
        frame = self.__btnframe = Frame(frame)
        frame.grid(row=0, column=0, columnspan=2, sticky='EW')
        self.__down25 = Button(frame, text='-25',
                               command=self.__minus25)
        self.__down10 = Button(frame, text='-10',
                               command=self.__minus10)
        self.__down1 = Button(frame, text='-1',
                              command=self.__minus1)
        self.__up1 = Button(frame, text='+1',
                            command=self.__plus1)
        self.__up10 = Button(frame, text='+10',
                             command=self.__plus10)
        self.__up25 = Button(frame, text='+25',
                             command=self.__plus25)
        self.__down25.pack(expand=YES, fill=X, side=LEFT)
        self.__down10.pack(expand=YES, fill=X, side=LEFT)
        self.__down1.pack(expand=YES, fill=X, side=LEFT)
        self.__up1.pack(expand=YES, fill=X, side=LEFT)
        self.__up10.pack(expand=YES, fill=X, side=LEFT)
        self.__up25.pack(expand=YES, fill=X, side=LEFT)

    def __effect(self, event=Nic):
        tie = self.__rvar.get() + self.__gvar.get() + self.__bvar.get()
        jeżeli tie w (0, 1, 2, 4):
            text = ''
        inaczej:
            text = '(= %s Level)' % {3: 'Cyan',
                                     5: 'Magenta',
                                     6: 'Yellow',
                                     7: 'Grey'}[tie]
        self.__l2.configure(text=text)

    def __quit(self, event=Nic):
        self.__root.quit()

    def withdraw(self, event=Nic):
        self.__root.withdraw()

    def deiconify(self, event=Nic):
        self.__root.deiconify()

    def __minus25(self, event=Nic):
        self.__delta(-25)

    def __minus10(self, event=Nic):
        self.__delta(-10)

    def __minus1(self, event=Nic):
        self.__delta(-1)

    def __plus1(self, event=Nic):
        self.__delta(1)

    def __plus10(self, event=Nic):
        self.__delta(10)

    def __plus25(self, event=Nic):
        self.__delta(25)

    def __delta(self, delta):
        tie = []
        jeżeli self.__rvar.get():
            red = self.__red + delta
            tie.append(red)
        inaczej:
            red = self.__red
        jeżeli self.__gvar.get():
            green = self.__green + delta
            tie.append(green)
        inaczej:
            green = self.__green
        jeżeli self.__bvar.get():
            blue = self.__blue + delta
            tie.append(blue)
        inaczej:
            blue = self.__blue
        # now apply at boundary behavior
        atbound = self.__boundvar.get()
        jeżeli atbound == STOP:
            jeżeli red < 0 albo green < 0 albo blue < 0 albo \
               red > 255 albo green > 255 albo blue > 255:
                # then
                red, green, blue = self.__red, self.__green, self.__blue
        albo_inaczej atbound == WRAP albo (atbound == RATIO oraz len(tie) < 2):
            jeżeli red < 0:
                red += 256
            jeżeli green < 0:
                green += 256
            jeżeli blue < 0:
                blue += 256
            jeżeli red > 255:
                red -= 256
            jeżeli green > 255:
                green -= 256
            jeżeli blue > 255:
                blue -= 256
        albo_inaczej atbound == RATIO:
            # dla when 2 albo 3 colors are tied together
            dir = 0
            dla c w tie:
                jeżeli c < 0:
                    dir = -1
                albo_inaczej c > 255:
                    dir = 1
            jeżeli dir == -1:
                delta = max(tie)
                jeżeli self.__rvar.get():
                    red = red + 255 - delta
                jeżeli self.__gvar.get():
                    green = green + 255 - delta
                jeżeli self.__bvar.get():
                    blue = blue + 255 - delta
            albo_inaczej dir == 1:
                delta = min(tie)
                jeżeli self.__rvar.get():
                    red = red - delta
                jeżeli self.__gvar.get():
                    green = green - delta
                jeżeli self.__bvar.get():
                    blue = blue - delta
        albo_inaczej atbound == GRAV:
            jeżeli red < 0:
                red = 0
            jeżeli green < 0:
                green = 0
            jeżeli blue < 0:
                blue = 0
            jeżeli red > 255:
                red = 255
            jeżeli green > 255:
                green = 255
            jeżeli blue > 255:
                blue = 255
        self.__sb.update_views(red, green, blue)
        self.__root.update_idletasks()

    def update_yourself(self, red, green, blue):
        self.__red = red
        self.__green = green
        self.__blue = blue

    def save_options(self, optiondb):
        optiondb['RSLIDER'] = self.__rvar.get()
        optiondb['GSLIDER'] = self.__gvar.get()
        optiondb['BSLIDER'] = self.__bvar.get()
        optiondb['ATBOUND'] = self.__boundvar.get()
