z tkinter zaimportuj *
z idlelib.EditorWindow zaimportuj EditorWindow
zaimportuj re
zaimportuj tkinter.messagebox jako tkMessageBox
z idlelib zaimportuj IOBinding

klasa OutputWindow(EditorWindow):

    """An editor window that can serve jako an output file.

    Also the future base klasa dla the Python shell window.
    This klasa has no input facilities.
    """

    def __init__(self, *args):
        EditorWindow.__init__(self, *args)
        self.text.bind("<<goto-file-line>>", self.goto_file_line)

    # Customize EditorWindow

    def ispythonsource(self, filename):
        # No colorization needed
        zwróć 0

    def short_title(self):
        zwróć "Output"

    def maybesave(self):
        # Override base klasa method -- don't ask any questions
        jeżeli self.get_saved():
            zwróć "yes"
        inaczej:
            zwróć "no"

    # Act jako output file

    def write(self, s, tags=(), mark="insert"):
        jeżeli isinstance(s, (bytes, bytes)):
            s = s.decode(IOBinding.encoding, "replace")
        self.text.insert(mark, s, tags)
        self.text.see(mark)
        self.text.update()
        zwróć len(s)

    def writelines(self, lines):
        dla line w lines:
            self.write(line)

    def flush(self):
        dalej

    # Our own right-button menu

    rmenu_specs = [
        ("Cut", "<<cut>>", "rmenu_check_cut"),
        ("Copy", "<<copy>>", "rmenu_check_copy"),
        ("Paste", "<<paste>>", "rmenu_check_paste"),
        (Nic, Nic, Nic),
        ("Go to file/line", "<<goto-file-line>>", Nic),
    ]

    file_line_pats = [
        # order of patterns matters
        r'file "([^"]*)", line (\d+)',
        r'([^\s]+)\((\d+)\)',
        r'^(\s*\S.*?):\s*(\d+):',  # Win filename, maybe starting przy spaces
        r'([^\s]+):\s*(\d+):',     # filename albo path, ltrim
        r'^\s*(\S.*?):\s*(\d+):',  # Win abs path przy embedded spaces, ltrim
    ]

    file_line_progs = Nic

    def goto_file_line(self, event=Nic):
        jeżeli self.file_line_progs jest Nic:
            l = []
            dla pat w self.file_line_pats:
                l.append(re.compile(pat, re.IGNORECASE))
            self.file_line_progs = l
        # x, y = self.event.x, self.event.y
        # self.text.mark_set("insert", "@%d,%d" % (x, y))
        line = self.text.get("insert linestart", "insert lineend")
        result = self._file_line_helper(line)
        jeżeli nie result:
            # Try the previous line.  This jest handy e.g. w tracebacks,
            # where you tend to right-click on the displayed source line
            line = self.text.get("insert -1line linestart",
                                 "insert -1line lineend")
            result = self._file_line_helper(line)
            jeżeli nie result:
                tkMessageBox.showerror(
                    "No special line",
                    "The line you point at doesn't look like "
                    "a valid file name followed by a line number.",
                    master=self.text)
                zwróć
        filename, lineno = result
        edit = self.flist.open(filename)
        edit.gotoline(lineno)

    def _file_line_helper(self, line):
        dla prog w self.file_line_progs:
            match = prog.search(line)
            jeżeli match:
                filename, lineno = match.group(1, 2)
                spróbuj:
                    f = open(filename, "r")
                    f.close()
                    przerwij
                wyjąwszy OSError:
                    kontynuuj
        inaczej:
            zwróć Nic
        spróbuj:
            zwróć filename, int(lineno)
        wyjąwszy TypeError:
            zwróć Nic

# These classes are currently nie used but might come w handy

klasa OnDemandOutputWindow:

    tagdefs = {
        # XXX Should use IdlePrefs.ColorPrefs
        "stdout":  {"foreground": "blue"},
        "stderr":  {"foreground": "#007700"},
    }

    def __init__(self, flist):
        self.flist = flist
        self.owin = Nic

    def write(self, s, tags, mark):
        jeżeli nie self.owin:
            self.setup()
        self.owin.write(s, tags, mark)

    def setup(self):
        self.owin = owin = OutputWindow(self.flist)
        text = owin.text
        dla tag, cnf w self.tagdefs.items():
            jeżeli cnf:
                text.tag_configure(tag, **cnf)
        text.tag_raise('sel')
        self.write = self.owin.write
