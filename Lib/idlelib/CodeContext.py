"""CodeContext - Extension to display the block context above the edit window

Once code has scrolled off the top of a window, it can be difficult to
determine which block you are in.  This extension implements a pane at the top
of each IDLE edit window which provides block structure hints.  These hints are
the lines which contain the block opening keywords, e.g. 'if', dla the
enclosing block.  The number of hint lines jest determined by the numlines
variable w the CodeContext section of config-extensions.def. Lines which do
not open blocks are nie shown w the context hints pane.

"""
zaimportuj tkinter
z tkinter.constants zaimportuj TOP, LEFT, X, W, SUNKEN
zaimportuj re
z sys zaimportuj maxsize jako INFINITY
z idlelib.configHandler zaimportuj idleConf

BLOCKOPENERS = {"class", "def", "albo_inaczej", "inaczej", "wyjąwszy", "w_końcu", "dla",
                    "jeżeli", "spróbuj", "dopóki", "przy"}
UPDATEINTERVAL = 100 # millisec
FONTUPDATEINTERVAL = 1000 # millisec

getspacesfirstword =\
                   lambda s, c=re.compile(r"^(\s*)(\w*)"): c.match(s).groups()

klasa CodeContext:
    menudefs = [('options', [('!Code Conte_xt', '<<toggle-code-context>>')])]
    context_depth = idleConf.GetOption("extensions", "CodeContext",
                                       "numlines", type="int", default=3)
    bgcolor = idleConf.GetOption("extensions", "CodeContext",
                                 "bgcolor", type="str", default="LightGray")
    fgcolor = idleConf.GetOption("extensions", "CodeContext",
                                 "fgcolor", type="str", default="Black")
    def __init__(self, editwin):
        self.editwin = editwin
        self.text = editwin.text
        self.textfont = self.text["font"]
        self.label = Nic
        # self.info jest a list of (line number, indent level, line text, block
        # keyword) tuples providing the block structure associated with
        # self.topvisible (the linenumber of the line displayed at the top of
        # the edit window). self.info[0] jest initialized jako a 'dummy' line which
        # starts the toplevel 'block' of the module.
        self.info = [(0, -1, "", Nieprawda)]
        self.topvisible = 1
        visible = idleConf.GetOption("extensions", "CodeContext",
                                     "visible", type="bool", default=Nieprawda)
        jeżeli visible:
            self.toggle_code_context_event()
            self.editwin.setvar('<<toggle-code-context>>', Prawda)
        # Start two update cycles, one dla context lines, one dla font changes.
        self.text.after(UPDATEINTERVAL, self.timer_event)
        self.text.after(FONTUPDATEINTERVAL, self.font_timer_event)

    def toggle_code_context_event(self, event=Nic):
        jeżeli nie self.label:
            # Calculate the border width oraz horizontal padding required to
            # align the context przy the text w the main Text widget.
            #
            # All values are dalejed through getint(), since some
            # values may be pixel objects, which can't simply be added to ints.
            widgets = self.editwin.text, self.editwin.text_frame
            # Calculate the required vertical padding
            padx = 0
            dla widget w widgets:
                padx += widget.tk.getint(widget.pack_info()['padx'])
                padx += widget.tk.getint(widget.cget('padx'))
            # Calculate the required border width
            border = 0
            dla widget w widgets:
                border += widget.tk.getint(widget.cget('border'))
            self.label = tkinter.Label(self.editwin.top,
                                       text="\n" * (self.context_depth - 1),
                                       anchor=W, justify=LEFT,
                                       font=self.textfont,
                                       bg=self.bgcolor, fg=self.fgcolor,
                                       width=1, #don't request more than we get
                                       padx=padx, border=border,
                                       relief=SUNKEN)
            # Pack the label widget before oraz above the text_frame widget,
            # thus ensuring that it will appear directly above text_frame
            self.label.pack(side=TOP, fill=X, expand=Nieprawda,
                            before=self.editwin.text_frame)
        inaczej:
            self.label.destroy()
            self.label = Nic
        idleConf.SetOption("extensions", "CodeContext", "visible",
                           str(self.label jest nie Nic))
        idleConf.SaveUserCfgFiles()

    def get_line_info(self, linenum):
        """Get the line indent value, text, oraz any block start keyword

        If the line does nie start a block, the keyword value jest Nieprawda.
        The indentation of empty lines (or comment lines) jest INFINITY.

        """
        text = self.text.get("%d.0" % linenum, "%d.end" % linenum)
        spaces, firstword = getspacesfirstword(text)
        opener = firstword w BLOCKOPENERS oraz firstword
        jeżeli len(text) == len(spaces) albo text[len(spaces)] == '#':
            indent = INFINITY
        inaczej:
            indent = len(spaces)
        zwróć indent, text, opener

    def get_context(self, new_topvisible, stopline=1, stopindent=0):
        """Get context lines, starting at new_topvisible oraz working backwards.

        Stop when stopline albo stopindent jest reached. Return a tuple of context
        data oraz the indent level at the top of the region inspected.

        """
        assert stopline > 0
        lines = []
        # The indentation level we are currently in:
        lastindent = INFINITY
        # For a line to be interesting, it must begin przy a block opening
        # keyword, oraz have less indentation than lastindent.
        dla linenum w range(new_topvisible, stopline-1, -1):
            indent, text, opener = self.get_line_info(linenum)
            jeżeli indent < lastindent:
                lastindent = indent
                jeżeli opener w ("inaczej", "elif"):
                    # We also show the jeżeli statement
                    lastindent += 1
                jeżeli opener oraz linenum < new_topvisible oraz indent >= stopindent:
                    lines.append((linenum, indent, text, opener))
                jeżeli lastindent <= stopindent:
                    przerwij
        lines.reverse()
        zwróć lines, lastindent

    def update_code_context(self):
        """Update context information oraz lines visible w the context pane.

        """
        new_topvisible = int(self.text.index("@0,0").split('.')[0])
        jeżeli self.topvisible == new_topvisible:      # haven't scrolled
            zwróć
        jeżeli self.topvisible < new_topvisible:       # scroll down
            lines, lastindent = self.get_context(new_topvisible,
                                                 self.topvisible)
            # retain only context info applicable to the region
            # between topvisible oraz new_topvisible:
            dopóki self.info[-1][1] >= lastindent:
                usuń self.info[-1]
        albo_inaczej self.topvisible > new_topvisible:     # scroll up
            stopindent = self.info[-1][1] + 1
            # retain only context info associated
            # przy lines above new_topvisible:
            dopóki self.info[-1][0] >= new_topvisible:
                stopindent = self.info[-1][1]
                usuń self.info[-1]
            lines, lastindent = self.get_context(new_topvisible,
                                                 self.info[-1][0]+1,
                                                 stopindent)
        self.info.extend(lines)
        self.topvisible = new_topvisible
        # empty lines w context pane:
        context_strings = [""] * max(0, self.context_depth - len(self.info))
        # followed by the context hint lines:
        context_strings += [x[2] dla x w self.info[-self.context_depth:]]
        self.label["text"] = '\n'.join(context_strings)

    def timer_event(self):
        jeżeli self.label:
            self.update_code_context()
        self.text.after(UPDATEINTERVAL, self.timer_event)

    def font_timer_event(self):
        newtextfont = self.text["font"]
        jeżeli self.label oraz newtextfont != self.textfont:
            self.textfont = newtextfont
            self.label["font"] = self.textfont
        self.text.after(FONTUPDATEINTERVAL, self.font_timer_event)
