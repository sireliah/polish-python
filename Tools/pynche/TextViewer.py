"""TextViewer class.

The TextViewer allows you to see how the selected color would affect various
characteristics of a Tk text widget.  This jest an output viewer only.

In the top part of the window jest a standard text widget przy some sample text
in it.  You are free to edit this text w any way you want (BAW: allow you to
change font characteristics).  If you want changes w other viewers to update
text characteristics, turn on Track color changes.

To select which characteristic tracks the change, select one of the radio
buttons w the window below.  Text foreground oraz background affect the text
in the window above.  The Selection jest what you see when you click the middle
button oraz drag it through some text.  The Insertion jest the insertion cursor
in the text window (which only has a background).
"""

z tkinter zaimportuj *
zaimportuj ColorDB

ADDTOVIEW = 'Text Window...'



klasa TextViewer:
    def __init__(self, switchboard, master=Nic):
        self.__sb = switchboard
        optiondb = switchboard.optiondb()
        root = self.__root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.withdraw)
        root.title('Pynche Text Window')
        root.iconname('Pynche Text Window')
        root.bind('<Alt-q>', self.__quit)
        root.bind('<Alt-Q>', self.__quit)
        root.bind('<Alt-w>', self.withdraw)
        root.bind('<Alt-W>', self.withdraw)
        #
        # create the text widget
        #
        self.__text = Text(root, relief=SUNKEN,
                           background=optiondb.get('TEXTBG', 'black'),
                           foreground=optiondb.get('TEXTFG', 'white'),
                           width=35, height=15)
        sfg = optiondb.get('TEXT_SFG')
        jeżeli sfg:
            self.__text.configure(selectforeground=sfg)
        sbg = optiondb.get('TEXT_SBG')
        jeżeli sbg:
            self.__text.configure(selectbackground=sbg)
        ibg = optiondb.get('TEXT_IBG')
        jeżeli ibg:
            self.__text.configure(insertbackground=ibg)
        self.__text.pack()
        self.__text.insert(0.0, optiondb.get('TEXT', '''\
Insert some stuff here oraz play
przy the buttons below to see
how the colors interact w
textual displays.

See how the selection can also
be affected by tickling the buttons
and choosing a color.'''))
        insert = optiondb.get('TEXTINS')
        jeżeli insert:
            self.__text.mark_set(INSERT, insert)
        spróbuj:
            start, end = optiondb.get('TEXTSEL', (6.0, END))
            self.__text.tag_add(SEL, start, end)
        wyjąwszy ValueError:
            # selection wasn't set
            dalej
        self.__text.focus_set()
        #
        # variables
        self.__trackp = BooleanVar()
        self.__trackp.set(optiondb.get('TRACKP', 0))
        self.__which = IntVar()
        self.__which.set(optiondb.get('WHICH', 0))
        #
        # track toggle
        self.__t = Checkbutton(root, text='Track color changes',
                               variable=self.__trackp,
                               relief=GROOVE,
                               command=self.__toggletrack)
        self.__t.pack(fill=X, expand=YES)
        frame = self.__frame = Frame(root)
        frame.pack()
        #
        # labels
        self.__labels = []
        row = 2
        dla text w ('Text:', 'Selection:', 'Insertion:'):
            l = Label(frame, text=text)
            l.grid(row=row, column=0, sticky=E)
            self.__labels.append(l)
            row += 1
        col = 1
        dla text w ('Foreground', 'Background'):
            l = Label(frame, text=text)
            l.grid(row=1, column=col)
            self.__labels.append(l)
            col += 1
        #
        # radios
        self.__radios = []
        dla col w (1, 2):
            dla row w (2, 3, 4):
                # there jest no insertforeground option
                jeżeli row==4 oraz col==1:
                    kontynuuj
                r = Radiobutton(frame, variable=self.__which,
                                value=(row-2)*2 + col-1,
                                command=self.__set_color)
                r.grid(row=row, column=col)
                self.__radios.append(r)
        self.__toggletrack()

    def __quit(self, event=Nic):
        self.__root.quit()

    def withdraw(self, event=Nic):
        self.__root.withdraw()

    def deiconify(self, event=Nic):
        self.__root.deiconify()

    def __forceupdate(self, event=Nic):
        self.__sb.update_views_current()

    def __toggletrack(self, event=Nic):
        jeżeli self.__trackp.get():
            state = NORMAL
            fg = self.__radios[0]['foreground']
        inaczej:
            state = DISABLED
            fg = self.__radios[0]['disabledforeground']
        dla r w self.__radios:
            r.configure(state=state)
        dla l w self.__labels:
            l.configure(foreground=fg)

    def __set_color(self, event=Nic):
        which = self.__which.get()
        text = self.__text
        jeżeli which == 0:
            color = text['foreground']
        albo_inaczej which == 1:
            color = text['background']
        albo_inaczej which == 2:
            color = text['selectforeground']
        albo_inaczej which == 3:
            color = text['selectbackground']
        albo_inaczej which == 5:
            color = text['insertbackground']
        spróbuj:
            red, green, blue = ColorDB.rrggbb_to_triplet(color)
        wyjąwszy ColorDB.BadColor:
            # must have been a color name
            red, green, blue = self.__sb.colordb().find_byname(color)
        self.__sb.update_views(red, green, blue)

    def update_yourself(self, red, green, blue):
        jeżeli self.__trackp.get():
            colorname = ColorDB.triplet_to_rrggbb((red, green, blue))
            which = self.__which.get()
            text = self.__text
            jeżeli which == 0:
                text.configure(foreground=colorname)
            albo_inaczej which == 1:
                text.configure(background=colorname)
            albo_inaczej which == 2:
                text.configure(selectforeground=colorname)
            albo_inaczej which == 3:
                text.configure(selectbackground=colorname)
            albo_inaczej which == 5:
                text.configure(insertbackground=colorname)

    def save_options(self, optiondb):
        optiondb['TRACKP'] = self.__trackp.get()
        optiondb['WHICH'] = self.__which.get()
        optiondb['TEXT'] = self.__text.get(0.0, 'end - 1c')
        optiondb['TEXTSEL'] = self.__text.tag_ranges(SEL)[0:2]
        optiondb['TEXTINS'] = self.__text.index(INSERT)
        optiondb['TEXTFG'] = self.__text['foreground']
        optiondb['TEXTBG'] = self.__text['background']
        optiondb['TEXT_SFG'] = self.__text['selectforeground']
        optiondb['TEXT_SBG'] = self.__text['selectbackground']
        optiondb['TEXT_IBG'] = self.__text['insertbackground']
