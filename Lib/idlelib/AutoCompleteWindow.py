"""
An auto-completion window dla IDLE, used by the AutoComplete extension
"""
z tkinter zaimportuj *
z idlelib.MultiCall zaimportuj MC_SHIFT
z idlelib.AutoComplete zaimportuj COMPLETE_FILES, COMPLETE_ATTRIBUTES

HIDE_VIRTUAL_EVENT_NAME = "<<autocompletewindow-hide>>"
HIDE_SEQUENCES = ("<FocusOut>", "<ButtonPress>")
KEYPRESS_VIRTUAL_EVENT_NAME = "<<autocompletewindow-keypress>>"
# We need to bind event beyond <Key> so that the function will be called
# before the default specific IDLE function
KEYPRESS_SEQUENCES = ("<Key>", "<Key-BackSpace>", "<Key-Return>", "<Key-Tab>",
                      "<Key-Up>", "<Key-Down>", "<Key-Home>", "<Key-End>",
                      "<Key-Prior>", "<Key-Next>")
KEYRELEASE_VIRTUAL_EVENT_NAME = "<<autocompletewindow-keyrelease>>"
KEYRELEASE_SEQUENCE = "<KeyRelease>"
LISTUPDATE_SEQUENCE = "<B1-ButtonRelease>"
WINCONFIG_SEQUENCE = "<Configure>"
DOUBLECLICK_SEQUENCE = "<B1-Double-ButtonRelease>"

klasa AutoCompleteWindow:

    def __init__(self, widget):
        # The widget (Text) on which we place the AutoCompleteWindow
        self.widget = widget
        # The widgets we create
        self.autocompletewindow = self.listbox = self.scrollbar = Nic
        # The default foreground oraz background of a selection. Saved because
        # they are changed to the regular colors of list items when the
        # completion start jest nie a prefix of the selected completion
        self.origselforeground = self.origselbackground = Nic
        # The list of completions
        self.completions = Nic
        # A list przy more completions, albo Nic
        self.morecompletions = Nic
        # The completion mode. Either AutoComplete.COMPLETE_ATTRIBUTES albo
        # AutoComplete.COMPLETE_FILES
        self.mode = Nic
        # The current completion start, on the text box (a string)
        self.start = Nic
        # The index of the start of the completion
        self.startindex = Nic
        # The last typed start, used so that when the selection changes,
        # the new start will be jako close jako possible to the last typed one.
        self.lasttypedstart = Nic
        # Do we have an indication that the user wants the completion window
        # (dla example, he clicked the list)
        self.userwantswindow = Nic
        # event ids
        self.hideid = self.keypressid = self.listupdateid = self.winconfigid \
        = self.keyreleaseid = self.doubleclickid                         = Nic
        # Flag set jeżeli last keypress was a tab
        self.lastkey_was_tab = Nieprawda

    def _change_start(self, newstart):
        min_len = min(len(self.start), len(newstart))
        i = 0
        dopóki i < min_len oraz self.start[i] == newstart[i]:
            i += 1
        jeżeli i < len(self.start):
            self.widget.delete("%s+%dc" % (self.startindex, i),
                               "%s+%dc" % (self.startindex, len(self.start)))
        jeżeli i < len(newstart):
            self.widget.insert("%s+%dc" % (self.startindex, i),
                               newstart[i:])
        self.start = newstart

    def _binary_search(self, s):
        """Find the first index w self.completions where completions[i] jest
        greater albo equal to s, albo the last index jeżeli there jest no such
        one."""
        i = 0; j = len(self.completions)
        dopóki j > i:
            m = (i + j) // 2
            jeżeli self.completions[m] >= s:
                j = m
            inaczej:
                i = m + 1
        zwróć min(i, len(self.completions)-1)

    def _complete_string(self, s):
        """Assuming that s jest the prefix of a string w self.completions,
        zwróć the longest string which jest a prefix of all the strings which
        s jest a prefix of them. If s jest nie a prefix of a string, zwróć s."""
        first = self._binary_search(s)
        jeżeli self.completions[first][:len(s)] != s:
            # There jest nie even one completion which s jest a prefix of.
            zwróć s
        # Find the end of the range of completions where s jest a prefix of.
        i = first + 1
        j = len(self.completions)
        dopóki j > i:
            m = (i + j) // 2
            jeżeli self.completions[m][:len(s)] != s:
                j = m
            inaczej:
                i = m + 1
        last = i-1

        jeżeli first == last: # only one possible completion
            zwróć self.completions[first]

        # We should zwróć the maximum prefix of first oraz last
        first_comp = self.completions[first]
        last_comp = self.completions[last]
        min_len = min(len(first_comp), len(last_comp))
        i = len(s)
        dopóki i < min_len oraz first_comp[i] == last_comp[i]:
            i += 1
        zwróć first_comp[:i]

    def _selection_changed(self):
        """Should be called when the selection of the Listbox has changed.
        Updates the Listbox display oraz calls _change_start."""
        cursel = int(self.listbox.curselection()[0])

        self.listbox.see(cursel)

        lts = self.lasttypedstart
        selstart = self.completions[cursel]
        jeżeli self._binary_search(lts) == cursel:
            newstart = lts
        inaczej:
            min_len = min(len(lts), len(selstart))
            i = 0
            dopóki i < min_len oraz lts[i] == selstart[i]:
                i += 1
            newstart = selstart[:i]
        self._change_start(newstart)

        jeżeli self.completions[cursel][:len(self.start)] == self.start:
            # start jest a prefix of the selected completion
            self.listbox.configure(selectbackground=self.origselbackground,
                                   selectforeground=self.origselforeground)
        inaczej:
            self.listbox.configure(selectbackground=self.listbox.cget("bg"),
                                   selectforeground=self.listbox.cget("fg"))
            # If there are more completions, show them, oraz call me again.
            jeżeli self.morecompletions:
                self.completions = self.morecompletions
                self.morecompletions = Nic
                self.listbox.delete(0, END)
                dla item w self.completions:
                    self.listbox.insert(END, item)
                self.listbox.select_set(self._binary_search(self.start))
                self._selection_changed()

    def show_window(self, comp_lists, index, complete, mode, userWantsWin):
        """Show the autocomplete list, bind events.
        If complete jest Prawda, complete the text, oraz jeżeli there jest exactly one
        matching completion, don't open a list."""
        # Handle the start we already have
        self.completions, self.morecompletions = comp_lists
        self.mode = mode
        self.startindex = self.widget.index(index)
        self.start = self.widget.get(self.startindex, "insert")
        jeżeli complete:
            completed = self._complete_string(self.start)
            start = self.start
            self._change_start(completed)
            i = self._binary_search(completed)
            jeżeli self.completions[i] == completed oraz \
               (i == len(self.completions)-1 albo
                self.completions[i+1][:len(completed)] != completed):
                # There jest exactly one matching completion
                zwróć completed == start
        self.userwantswindow = userWantsWin
        self.lasttypedstart = self.start

        # Put widgets w place
        self.autocompletewindow = acw = Toplevel(self.widget)
        # Put it w a position so that it jest nie seen.
        acw.wm_geometry("+10000+10000")
        # Make it float
        acw.wm_overrideredirect(1)
        spróbuj:
            # This command jest only needed oraz available on Tk >= 8.4.0 dla OSX
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            acw.tk.call("::tk::unsupported::MacWindowStyle", "style", acw._w,
                        "help", "noActivates")
        wyjąwszy TclError:
            dalej
        self.scrollbar = scrollbar = Scrollbar(acw, orient=VERTICAL)
        self.listbox = listbox = Listbox(acw, yscrollcommand=scrollbar.set,
                                         exportselection=Nieprawda, bg="white")
        dla item w self.completions:
            listbox.insert(END, item)
        self.origselforeground = listbox.cget("selectforeground")
        self.origselbackground = listbox.cget("selectbackground")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=BOTH, expand=Prawda)

        # Initialize the listbox selection
        self.listbox.select_set(self._binary_search(self.start))
        self._selection_changed()

        # bind events
        self.hideid = self.widget.bind(HIDE_VIRTUAL_EVENT_NAME,
                                       self.hide_event)
        dla seq w HIDE_SEQUENCES:
            self.widget.event_add(HIDE_VIRTUAL_EVENT_NAME, seq)
        self.keypressid = self.widget.bind(KEYPRESS_VIRTUAL_EVENT_NAME,
                                           self.keypress_event)
        dla seq w KEYPRESS_SEQUENCES:
            self.widget.event_add(KEYPRESS_VIRTUAL_EVENT_NAME, seq)
        self.keyreleaseid = self.widget.bind(KEYRELEASE_VIRTUAL_EVENT_NAME,
                                             self.keyrelease_event)
        self.widget.event_add(KEYRELEASE_VIRTUAL_EVENT_NAME,KEYRELEASE_SEQUENCE)
        self.listupdateid = listbox.bind(LISTUPDATE_SEQUENCE,
                                         self.listselect_event)
        self.winconfigid = acw.bind(WINCONFIG_SEQUENCE, self.winconfig_event)
        self.doubleclickid = listbox.bind(DOUBLECLICK_SEQUENCE,
                                          self.doubleclick_event)

    def winconfig_event(self, event):
        jeżeli nie self.is_active():
            zwróć
        # Position the completion list window
        text = self.widget
        text.see(self.startindex)
        x, y, cx, cy = text.bbox(self.startindex)
        acw = self.autocompletewindow
        acw_width, acw_height = acw.winfo_width(), acw.winfo_height()
        text_width, text_height = text.winfo_width(), text.winfo_height()
        new_x = text.winfo_rootx() + min(x, max(0, text_width - acw_width))
        new_y = text.winfo_rooty() + y
        jeżeli (text_height - (y + cy) >= acw_height # enough height below
            albo y < acw_height): # nie enough height above
            # place acw below current line
            new_y += cy
        inaczej:
            # place acw above current line
            new_y -= acw_height
        acw.wm_geometry("+%d+%d" % (new_x, new_y))

    def hide_event(self, event):
        jeżeli nie self.is_active():
            zwróć
        self.hide_window()

    def listselect_event(self, event):
        jeżeli nie self.is_active():
            zwróć
        self.userwantswindow = Prawda
        cursel = int(self.listbox.curselection()[0])
        self._change_start(self.completions[cursel])

    def doubleclick_event(self, event):
        # Put the selected completion w the text, oraz close the list
        cursel = int(self.listbox.curselection()[0])
        self._change_start(self.completions[cursel])
        self.hide_window()

    def keypress_event(self, event):
        jeżeli nie self.is_active():
            zwróć
        keysym = event.keysym
        jeżeli hasattr(event, "mc_state"):
            state = event.mc_state
        inaczej:
            state = 0
        jeżeli keysym != "Tab":
            self.lastkey_was_tab = Nieprawda
        jeżeli (len(keysym) == 1 albo keysym w ("underscore", "BackSpace")
            albo (self.mode == COMPLETE_FILES oraz keysym w
                ("period", "minus"))) \
           oraz nie (state & ~MC_SHIFT):
            # Normal editing of text
            jeżeli len(keysym) == 1:
                self._change_start(self.start + keysym)
            albo_inaczej keysym == "underscore":
                self._change_start(self.start + '_')
            albo_inaczej keysym == "period":
                self._change_start(self.start + '.')
            albo_inaczej keysym == "minus":
                self._change_start(self.start + '-')
            inaczej:
                # keysym == "BackSpace"
                jeżeli len(self.start) == 0:
                    self.hide_window()
                    zwróć
                self._change_start(self.start[:-1])
            self.lasttypedstart = self.start
            self.listbox.select_clear(0, int(self.listbox.curselection()[0]))
            self.listbox.select_set(self._binary_search(self.start))
            self._selection_changed()
            zwróć "break"

        albo_inaczej keysym == "Return":
            self.hide_window()
            zwróć

        albo_inaczej (self.mode == COMPLETE_ATTRIBUTES oraz keysym w
              ("period", "space", "parenleft", "parenright", "bracketleft",
               "bracketright")) albo \
             (self.mode == COMPLETE_FILES oraz keysym w
              ("slash", "backslash", "quotedbl", "apostrophe")) \
             oraz nie (state & ~MC_SHIFT):
            # If start jest a prefix of the selection, but jest nie '' when
            # completing file names, put the whole
            # selected completion. Anyway, close the list.
            cursel = int(self.listbox.curselection()[0])
            jeżeli self.completions[cursel][:len(self.start)] == self.start \
               oraz (self.mode == COMPLETE_ATTRIBUTES albo self.start):
                self._change_start(self.completions[cursel])
            self.hide_window()
            zwróć

        albo_inaczej keysym w ("Home", "End", "Prior", "Next", "Up", "Down") oraz \
             nie state:
            # Move the selection w the listbox
            self.userwantswindow = Prawda
            cursel = int(self.listbox.curselection()[0])
            jeżeli keysym == "Home":
                newsel = 0
            albo_inaczej keysym == "End":
                newsel = len(self.completions)-1
            albo_inaczej keysym w ("Prior", "Next"):
                jump = self.listbox.nearest(self.listbox.winfo_height()) - \
                       self.listbox.nearest(0)
                jeżeli keysym == "Prior":
                    newsel = max(0, cursel-jump)
                inaczej:
                    assert keysym == "Next"
                    newsel = min(len(self.completions)-1, cursel+jump)
            albo_inaczej keysym == "Up":
                newsel = max(0, cursel-1)
            inaczej:
                assert keysym == "Down"
                newsel = min(len(self.completions)-1, cursel+1)
            self.listbox.select_clear(cursel)
            self.listbox.select_set(newsel)
            self._selection_changed()
            self._change_start(self.completions[newsel])
            zwróć "break"

        albo_inaczej (keysym == "Tab" oraz nie state):
            jeżeli self.lastkey_was_tab:
                # two tabs w a row; insert current selection oraz close acw
                cursel = int(self.listbox.curselection()[0])
                self._change_start(self.completions[cursel])
                self.hide_window()
                zwróć "break"
            inaczej:
                # first tab; let AutoComplete handle the completion
                self.userwantswindow = Prawda
                self.lastkey_was_tab = Prawda
                zwróć

        albo_inaczej any(s w keysym dla s w ("Shift", "Control", "Alt",
                                       "Meta", "Command", "Option")):
            # A modifier key, so ignore
            zwróć

        albo_inaczej event.char oraz event.char >= ' ':
            # Regular character przy a non-length-1 keycode
            self._change_start(self.start + event.char)
            self.lasttypedstart = self.start
            self.listbox.select_clear(0, int(self.listbox.curselection()[0]))
            self.listbox.select_set(self._binary_search(self.start))
            self._selection_changed()
            zwróć "break"

        inaczej:
            # Unknown event, close the window oraz let it through.
            self.hide_window()
            zwróć

    def keyrelease_event(self, event):
        jeżeli nie self.is_active():
            zwróć
        jeżeli self.widget.index("insert") != \
           self.widget.index("%s+%dc" % (self.startindex, len(self.start))):
            # If we didn't catch an event which moved the insert, close window
            self.hide_window()

    def is_active(self):
        zwróć self.autocompletewindow jest nie Nic

    def complete(self):
        self._change_start(self._complete_string(self.start))
        # The selection doesn't change.

    def hide_window(self):
        jeżeli nie self.is_active():
            zwróć

        # unbind events
        dla seq w HIDE_SEQUENCES:
            self.widget.event_delete(HIDE_VIRTUAL_EVENT_NAME, seq)
        self.widget.unbind(HIDE_VIRTUAL_EVENT_NAME, self.hideid)
        self.hideid = Nic
        dla seq w KEYPRESS_SEQUENCES:
            self.widget.event_delete(KEYPRESS_VIRTUAL_EVENT_NAME, seq)
        self.widget.unbind(KEYPRESS_VIRTUAL_EVENT_NAME, self.keypressid)
        self.keypressid = Nic
        self.widget.event_delete(KEYRELEASE_VIRTUAL_EVENT_NAME,
                                 KEYRELEASE_SEQUENCE)
        self.widget.unbind(KEYRELEASE_VIRTUAL_EVENT_NAME, self.keyreleaseid)
        self.keyreleaseid = Nic
        self.listbox.unbind(LISTUPDATE_SEQUENCE, self.listupdateid)
        self.listupdateid = Nic
        self.autocompletewindow.unbind(WINCONFIG_SEQUENCE, self.winconfigid)
        self.winconfigid = Nic

        # destroy widgets
        self.scrollbar.destroy()
        self.scrollbar = Nic
        self.listbox.destroy()
        self.listbox = Nic
        self.autocompletewindow.destroy()
        self.autocompletewindow = Nic
