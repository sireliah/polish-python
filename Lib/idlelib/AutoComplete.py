"""AutoComplete.py - An IDLE extension dla automatically completing names.

This extension can complete either attribute names of file names. It can pop
a window przy all available names, dla the user to select from.
"""
zaimportuj os
zaimportuj sys
zaimportuj string

z idlelib.configHandler zaimportuj idleConf

# This string includes all chars that may be w an identifier
ID_CHARS = string.ascii_letters + string.digits + "_"

# These constants represent the two different types of completions
COMPLETE_ATTRIBUTES, COMPLETE_FILES = range(1, 2+1)

z idlelib zaimportuj AutoCompleteWindow
z idlelib.HyperParser zaimportuj HyperParser

zaimportuj __main__

SEPS = os.sep
jeżeli os.altsep:  # e.g. '/' on Windows...
    SEPS += os.altsep

klasa AutoComplete:

    menudefs = [
        ('edit', [
            ("Show Completions", "<<force-open-completions>>"),
        ])
    ]

    popupwait = idleConf.GetOption("extensions", "AutoComplete",
                                   "popupwait", type="int", default=0)

    def __init__(self, editwin=Nic):
        self.editwin = editwin
        jeżeli editwin jest Nic:  # subprocess oraz test
            zwróć
        self.text = editwin.text
        self.autocompletewindow = Nic

        # id of delayed call, oraz the index of the text insert when the delayed
        # call was issued. If _delayed_completion_id jest Nic, there jest no
        # delayed call.
        self._delayed_completion_id = Nic
        self._delayed_completion_index = Nic

    def _make_autocomplete_window(self):
        zwróć AutoCompleteWindow.AutoCompleteWindow(self.text)

    def _remove_autocomplete_window(self, event=Nic):
        jeżeli self.autocompletewindow:
            self.autocompletewindow.hide_window()
            self.autocompletewindow = Nic

    def force_open_completions_event(self, event):
        """Happens when the user really wants to open a completion list, even
        jeżeli a function call jest needed.
        """
        self.open_completions(Prawda, Nieprawda, Prawda)

    def try_open_completions_event(self, event):
        """Happens when it would be nice to open a completion list, but nie
        really necessary, dla example after an dot, so function
        calls won't be made.
        """
        lastchar = self.text.get("insert-1c")
        jeżeli lastchar == ".":
            self._open_completions_later(Nieprawda, Nieprawda, Nieprawda,
                                         COMPLETE_ATTRIBUTES)
        albo_inaczej lastchar w SEPS:
            self._open_completions_later(Nieprawda, Nieprawda, Nieprawda,
                                         COMPLETE_FILES)

    def autocomplete_event(self, event):
        """Happens when the user wants to complete his word, oraz jeżeli necessary,
        open a completion list after that (jeżeli there jest more than one
        completion)
        """
        jeżeli hasattr(event, "mc_state") oraz event.mc_state:
            # A modifier was pressed along przy the tab, continue jako usual.
            zwróć
        jeżeli self.autocompletewindow oraz self.autocompletewindow.is_active():
            self.autocompletewindow.complete()
            zwróć "break"
        inaczej:
            opened = self.open_completions(Nieprawda, Prawda, Prawda)
            jeżeli opened:
                zwróć "break"

    def _open_completions_later(self, *args):
        self._delayed_completion_index = self.text.index("insert")
        jeżeli self._delayed_completion_id jest nie Nic:
            self.text.after_cancel(self._delayed_completion_id)
        self._delayed_completion_id = \
            self.text.after(self.popupwait, self._delayed_open_completions,
                            *args)

    def _delayed_open_completions(self, *args):
        self._delayed_completion_id = Nic
        jeżeli self.text.index("insert") != self._delayed_completion_index:
            zwróć
        self.open_completions(*args)

    def open_completions(self, evalfuncs, complete, userWantsWin, mode=Nic):
        """Find the completions oraz create the AutoCompleteWindow.
        Return Prawda jeżeli successful (no syntax error albo so found).
        jeżeli complete jest Prawda, then jeżeli there's nothing to complete oraz no
        start of completion, won't open completions oraz zwróć Nieprawda.
        If mode jest given, will open a completion list only w this mode.
        """
        # Cancel another delayed call, jeżeli it exists.
        jeżeli self._delayed_completion_id jest nie Nic:
            self.text.after_cancel(self._delayed_completion_id)
            self._delayed_completion_id = Nic

        hp = HyperParser(self.editwin, "insert")
        curline = self.text.get("insert linestart", "insert")
        i = j = len(curline)
        jeżeli hp.is_in_string() oraz (nie mode albo mode==COMPLETE_FILES):
            # Find the beginning of the string
            # fetch_completions will look at the file system to determine whether the
            # string value constitutes an actual file name
            # XXX could consider raw strings here oraz unescape the string value jeżeli it's
            # nie raw.
            self._remove_autocomplete_window()
            mode = COMPLETE_FILES
            # Find last separator albo string start
            dopóki i oraz curline[i-1] nie w "'\"" + SEPS:
                i -= 1
            comp_start = curline[i:j]
            j = i
            # Find string start
            dopóki i oraz curline[i-1] nie w "'\"":
                i -= 1
            comp_what = curline[i:j]
        albo_inaczej hp.is_in_code() oraz (nie mode albo mode==COMPLETE_ATTRIBUTES):
            self._remove_autocomplete_window()
            mode = COMPLETE_ATTRIBUTES
            dopóki i oraz (curline[i-1] w ID_CHARS albo ord(curline[i-1]) > 127):
                i -= 1
            comp_start = curline[i:j]
            jeżeli i oraz curline[i-1] == '.':
                hp.set_index("insert-%dc" % (len(curline)-(i-1)))
                comp_what = hp.get_expression()
                jeżeli nie comp_what albo \
                   (nie evalfuncs oraz comp_what.find('(') != -1):
                    zwróć
            inaczej:
                comp_what = ""
        inaczej:
            zwróć

        jeżeli complete oraz nie comp_what oraz nie comp_start:
            zwróć
        comp_lists = self.fetch_completions(comp_what, mode)
        jeżeli nie comp_lists[0]:
            zwróć
        self.autocompletewindow = self._make_autocomplete_window()
        zwróć nie self.autocompletewindow.show_window(
                comp_lists, "insert-%dc" % len(comp_start),
                complete, mode, userWantsWin)

    def fetch_completions(self, what, mode):
        """Return a pair of lists of completions dla something. The first list
        jest a sublist of the second. Both are sorted.

        If there jest a Python subprocess, get the comp. list there.  Otherwise,
        either fetch_completions() jest running w the subprocess itself albo it
        was called w an IDLE EditorWindow before any script had been run.

        The subprocess environment jest that of the most recently run script.  If
        two unrelated modules are being edited some calltips w the current
        module may be inoperative jeżeli the module was nie the last to run.
        """
        spróbuj:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        wyjąwszy:
            rpcclt = Nic
        jeżeli rpcclt:
            zwróć rpcclt.remotecall("exec", "get_the_completion_list",
                                     (what, mode), {})
        inaczej:
            jeżeli mode == COMPLETE_ATTRIBUTES:
                jeżeli what == "":
                    namespace = __main__.__dict__.copy()
                    namespace.update(__main__.__builtins__.__dict__)
                    bigl = eval("dir()", namespace)
                    bigl.sort()
                    jeżeli "__all__" w bigl:
                        smalll = sorted(eval("__all__", namespace))
                    inaczej:
                        smalll = [s dla s w bigl jeżeli s[:1] != '_']
                inaczej:
                    spróbuj:
                        entity = self.get_entity(what)
                        bigl = dir(entity)
                        bigl.sort()
                        jeżeli "__all__" w bigl:
                            smalll = sorted(entity.__all__)
                        inaczej:
                            smalll = [s dla s w bigl jeżeli s[:1] != '_']
                    wyjąwszy:
                        zwróć [], []

            albo_inaczej mode == COMPLETE_FILES:
                jeżeli what == "":
                    what = "."
                spróbuj:
                    expandedpath = os.path.expanduser(what)
                    bigl = os.listdir(expandedpath)
                    bigl.sort()
                    smalll = [s dla s w bigl jeżeli s[:1] != '.']
                wyjąwszy OSError:
                    zwróć [], []

            jeżeli nie smalll:
                smalll = bigl
            zwróć smalll, bigl

    def get_entity(self, name):
        """Lookup name w a namespace spanning sys.modules oraz __main.dict__"""
        namespace = sys.modules.copy()
        namespace.update(__main__.__dict__)
        zwróć eval(name, namespace)


jeżeli __name__ == '__main__':
    z unittest zaimportuj main
    main('idlelib.idle_test.test_autocomplete', verbosity=2)
