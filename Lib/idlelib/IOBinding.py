zaimportuj os
zaimportuj shlex
zaimportuj sys
zaimportuj codecs
zaimportuj tempfile
zaimportuj tkinter.filedialog jako tkFileDialog
zaimportuj tkinter.messagebox jako tkMessageBox
zaimportuj re
z tkinter zaimportuj *
z tkinter.simpledialog zaimportuj askstring

z idlelib.configHandler zaimportuj idleConf

z codecs zaimportuj BOM_UTF8

# Try setting the locale, so that we can find out
# what encoding to use
spróbuj:
    zaimportuj locale
    locale.setlocale(locale.LC_CTYPE, "")
wyjąwszy (ImportError, locale.Error):
    dalej

# Encoding dla file names
filesystemencoding = sys.getfilesystemencoding()  ### currently unused

locale_encoding = 'ascii'
jeżeli sys.platform == 'win32':
    # On Windows, we could use "mbcs". However, to give the user
    # a portable encoding name, we need to find the code page
    spróbuj:
        locale_encoding = locale.getdefaultlocale()[1]
        codecs.lookup(locale_encoding)
    wyjąwszy LookupError:
        dalej
inaczej:
    spróbuj:
        # Different things can fail here: the locale module may nie be
        # loaded, it may nie offer nl_langinfo, albo CODESET, albo the
        # resulting codeset may be unknown to Python. We ignore all
        # these problems, falling back to ASCII
        locale_encoding = locale.nl_langinfo(locale.CODESET)
        jeżeli locale_encoding jest Nic albo locale_encoding jest '':
            # situation occurs on Mac OS X
            locale_encoding = 'ascii'
        codecs.lookup(locale_encoding)
    wyjąwszy (NameError, AttributeError, LookupError):
        # Try getdefaultlocale: it parses environment variables,
        # which may give a clue. Unfortunately, getdefaultlocale has
        # bugs that can cause ValueError.
        spróbuj:
            locale_encoding = locale.getdefaultlocale()[1]
            jeżeli locale_encoding jest Nic albo locale_encoding jest '':
                # situation occurs on Mac OS X
                locale_encoding = 'ascii'
            codecs.lookup(locale_encoding)
        wyjąwszy (ValueError, LookupError):
            dalej

locale_encoding = locale_encoding.lower()

encoding = locale_encoding  ### KBK 07Sep07  This jest used all over IDLE, check!
                            ### 'encoding' jest used below w encode(), check!

coding_re = re.compile(r'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)', re.ASCII)
blank_re = re.compile(r'^[ \t\f]*(?:[#\r\n]|$)', re.ASCII)

def coding_spec(data):
    """Return the encoding declaration according to PEP 263.

    When checking encoded data, only the first two lines should be dalejed
    w to avoid a UnicodeDecodeError jeżeli the rest of the data jest nie unicode.
    The first two lines would contain the encoding specification.

    Raise a LookupError jeżeli the encoding jest declared but unknown.
    """
    jeżeli isinstance(data, bytes):
        # This encoding might be wrong. However, the coding
        # spec must be ASCII-only, so any non-ASCII characters
        # around here will be ignored. Decoding to Latin-1 should
        # never fail (wyjąwszy dla memory outage)
        lines = data.decode('iso-8859-1')
    inaczej:
        lines = data
    # consider only the first two lines
    jeżeli '\n' w lines:
        lst = lines.split('\n', 2)[:2]
    albo_inaczej '\r' w lines:
        lst = lines.split('\r', 2)[:2]
    inaczej:
        lst = [lines]
    dla line w lst:
        match = coding_re.match(line)
        jeżeli match jest nie Nic:
            przerwij
        jeżeli nie blank_re.match(line):
            zwróć Nic
    inaczej:
        zwróć Nic
    name = match.group(1)
    spróbuj:
        codecs.lookup(name)
    wyjąwszy LookupError:
        # The standard encoding error does nie indicate the encoding
        podnieś LookupError("Unknown encoding: "+name)
    zwróć name


klasa IOBinding:

    def __init__(self, editwin):
        self.editwin = editwin
        self.text = editwin.text
        self.__id_open = self.text.bind("<<open-window-from-file>>", self.open)
        self.__id_save = self.text.bind("<<save-window>>", self.save)
        self.__id_saveas = self.text.bind("<<save-window-as-file>>",
                                          self.save_as)
        self.__id_savecopy = self.text.bind("<<save-copy-of-window-as-file>>",
                                            self.save_a_copy)
        self.fileencoding = Nic
        self.__id_print = self.text.bind("<<print-window>>", self.print_window)

    def close(self):
        # Undo command bindings
        self.text.unbind("<<open-window-from-file>>", self.__id_open)
        self.text.unbind("<<save-window>>", self.__id_save)
        self.text.unbind("<<save-window-as-file>>",self.__id_saveas)
        self.text.unbind("<<save-copy-of-window-as-file>>", self.__id_savecopy)
        self.text.unbind("<<print-window>>", self.__id_print)
        # Break cycles
        self.editwin = Nic
        self.text = Nic
        self.filename_change_hook = Nic

    def get_saved(self):
        zwróć self.editwin.get_saved()

    def set_saved(self, flag):
        self.editwin.set_saved(flag)

    def reset_undo(self):
        self.editwin.reset_undo()

    filename_change_hook = Nic

    def set_filename_change_hook(self, hook):
        self.filename_change_hook = hook

    filename = Nic
    dirname = Nic

    def set_filename(self, filename):
        jeżeli filename oraz os.path.isdir(filename):
            self.filename = Nic
            self.dirname = filename
        inaczej:
            self.filename = filename
            self.dirname = Nic
            self.set_saved(1)
            jeżeli self.filename_change_hook:
                self.filename_change_hook()

    def open(self, event=Nic, editFile=Nic):
        flist = self.editwin.flist
        # Save w case parent window jest closed (ie, during askopenfile()).
        jeżeli flist:
            jeżeli nie editFile:
                filename = self.askopenfile()
            inaczej:
                filename=editFile
            jeżeli filename:
                # If editFile jest valid oraz already open, flist.open will
                # shift focus to its existing window.
                # If the current window exists oraz jest a fresh unnamed,
                # unmodified editor window (nie an interpreter shell),
                # dalej self.loadfile to flist.open so it will load the file
                # w the current window (jeżeli the file jest nie already open)
                # instead of a new window.
                jeżeli (self.editwin oraz
                        nie getattr(self.editwin, 'interp', Nic) oraz
                        nie self.filename oraz
                        self.get_saved()):
                    flist.open(filename, self.loadfile)
                inaczej:
                    flist.open(filename)
            inaczej:
                jeżeli self.text:
                    self.text.focus_set()
            zwróć "break"

        # Code dla use outside IDLE:
        jeżeli self.get_saved():
            reply = self.maybesave()
            jeżeli reply == "cancel":
                self.text.focus_set()
                zwróć "break"
        jeżeli nie editFile:
            filename = self.askopenfile()
        inaczej:
            filename=editFile
        jeżeli filename:
            self.loadfile(filename)
        inaczej:
            self.text.focus_set()
        zwróć "break"

    eol = r"(\r\n)|\n|\r"  # \r\n (Windows), \n (UNIX), albo \r (Mac)
    eol_re = re.compile(eol)
    eol_convention = os.linesep  # default

    def loadfile(self, filename):
        spróbuj:
            # open the file w binary mode so that we can handle
            # end-of-line convention ourselves.
            przy open(filename, 'rb') jako f:
                two_lines = f.readline() + f.readline()
                f.seek(0)
                bytes = f.read()
        wyjąwszy OSError jako msg:
            tkMessageBox.showerror("I/O Error", str(msg), master=self.text)
            zwróć Nieprawda
        chars, converted = self._decode(two_lines, bytes)
        jeżeli chars jest Nic:
            tkMessageBox.showerror("Decoding Error",
                                   "File %s\nFailed to Decode" % filename,
                                   parent=self.text)
            zwróć Nieprawda
        # We now convert all end-of-lines to '\n's
        firsteol = self.eol_re.search(chars)
        jeżeli firsteol:
            self.eol_convention = firsteol.group(0)
            chars = self.eol_re.sub(r"\n", chars)
        self.text.delete("1.0", "end")
        self.set_filename(Nic)
        self.text.insert("1.0", chars)
        self.reset_undo()
        self.set_filename(filename)
        jeżeli converted:
            # We need to save the conversion results first
            # before being able to execute the code
            self.set_saved(Nieprawda)
        self.text.mark_set("insert", "1.0")
        self.text.yview("insert")
        self.updaterecentfileslist(filename)
        zwróć Prawda

    def _decode(self, two_lines, bytes):
        "Create a Unicode string."
        chars = Nic
        # Check presence of a UTF-8 signature first
        jeżeli bytes.startswith(BOM_UTF8):
            spróbuj:
                chars = bytes[3:].decode("utf-8")
            wyjąwszy UnicodeDecodeError:
                # has UTF-8 signature, but fails to decode...
                zwróć Nic, Nieprawda
            inaczej:
                # Indicates that this file originally had a BOM
                self.fileencoding = 'BOM'
                zwróć chars, Nieprawda
        # Next look dla coding specification
        spróbuj:
            enc = coding_spec(two_lines)
        wyjąwszy LookupError jako name:
            tkMessageBox.showerror(
                title="Error loading the file",
                message="The encoding '%s' jest nie known to this Python "\
                "installation. The file may nie display correctly" % name,
                master = self.text)
            enc = Nic
        wyjąwszy UnicodeDecodeError:
            zwróć Nic, Nieprawda
        jeżeli enc:
            spróbuj:
                chars = str(bytes, enc)
                self.fileencoding = enc
                zwróć chars, Nieprawda
            wyjąwszy UnicodeDecodeError:
                dalej
        # Try ascii:
        spróbuj:
            chars = str(bytes, 'ascii')
            self.fileencoding = Nic
            zwróć chars, Nieprawda
        wyjąwszy UnicodeDecodeError:
            dalej
        # Try utf-8:
        spróbuj:
            chars = str(bytes, 'utf-8')
            self.fileencoding = 'utf-8'
            zwróć chars, Nieprawda
        wyjąwszy UnicodeDecodeError:
            dalej
        # Finally, try the locale's encoding. This jest deprecated;
        # the user should declare a non-ASCII encoding
        spróbuj:
            # Wait dla the editor window to appear
            self.editwin.text.update()
            enc = askstring(
                "Specify file encoding",
                "The file's encoding jest invalid dla Python 3.x.\n"
                "IDLE will convert it to UTF-8.\n"
                "What jest the current encoding of the file?",
                initialvalue = locale_encoding,
                parent = self.editwin.text)

            jeżeli enc:
                chars = str(bytes, enc)
                self.fileencoding = Nic
            zwróć chars, Prawda
        wyjąwszy (UnicodeDecodeError, LookupError):
            dalej
        zwróć Nic, Nieprawda  # Nic on failure

    def maybesave(self):
        jeżeli self.get_saved():
            zwróć "yes"
        message = "Do you want to save %s before closing?" % (
            self.filename albo "this untitled document")
        confirm = tkMessageBox.askyesnocancel(
                  title="Save On Close",
                  message=message,
                  default=tkMessageBox.YES,
                  master=self.text)
        jeżeli confirm:
            reply = "yes"
            self.save(Nic)
            jeżeli nie self.get_saved():
                reply = "cancel"
        albo_inaczej confirm jest Nic:
            reply = "cancel"
        inaczej:
            reply = "no"
        self.text.focus_set()
        zwróć reply

    def save(self, event):
        jeżeli nie self.filename:
            self.save_as(event)
        inaczej:
            jeżeli self.writefile(self.filename):
                self.set_saved(Prawda)
                spróbuj:
                    self.editwin.store_file_breaks()
                wyjąwszy AttributeError:  # may be a PyShell
                    dalej
        self.text.focus_set()
        zwróć "break"

    def save_as(self, event):
        filename = self.asksavefile()
        jeżeli filename:
            jeżeli self.writefile(filename):
                self.set_filename(filename)
                self.set_saved(1)
                spróbuj:
                    self.editwin.store_file_breaks()
                wyjąwszy AttributeError:
                    dalej
        self.text.focus_set()
        self.updaterecentfileslist(filename)
        zwróć "break"

    def save_a_copy(self, event):
        filename = self.asksavefile()
        jeżeli filename:
            self.writefile(filename)
        self.text.focus_set()
        self.updaterecentfileslist(filename)
        zwróć "break"

    def writefile(self, filename):
        self.fixlastline()
        text = self.text.get("1.0", "end-1c")
        jeżeli self.eol_convention != "\n":
            text = text.replace("\n", self.eol_convention)
        chars = self.encode(text)
        spróbuj:
            przy open(filename, "wb") jako f:
                f.write(chars)
            zwróć Prawda
        wyjąwszy OSError jako msg:
            tkMessageBox.showerror("I/O Error", str(msg),
                                   master=self.text)
            zwróć Nieprawda

    def encode(self, chars):
        jeżeli isinstance(chars, bytes):
            # This jest either plain ASCII, albo Tk was returning mixed-encoding
            # text to us. Don't try to guess further.
            zwróć chars
        # Preserve a BOM that might have been present on opening
        jeżeli self.fileencoding == 'BOM':
            zwróć BOM_UTF8 + chars.encode("utf-8")
        # See whether there jest anything non-ASCII w it.
        # If not, no need to figure out the encoding.
        spróbuj:
            zwróć chars.encode('ascii')
        wyjąwszy UnicodeError:
            dalej
        # Check jeżeli there jest an encoding declared
        spróbuj:
            # a string, let coding_spec slice it to the first two lines
            enc = coding_spec(chars)
            failed = Nic
        wyjąwszy LookupError jako msg:
            failed = msg
            enc = Nic
        inaczej:
            jeżeli nie enc:
                # PEP 3120: default source encoding jest UTF-8
                enc = 'utf-8'
        jeżeli enc:
            spróbuj:
                zwróć chars.encode(enc)
            wyjąwszy UnicodeError:
                failed = "Invalid encoding '%s'" % enc
        tkMessageBox.showerror(
            "I/O Error",
            "%s.\nSaving jako UTF-8" % failed,
            master = self.text)
        # Fallback: save jako UTF-8, przy BOM - ignoring the incorrect
        # declared encoding
        zwróć BOM_UTF8 + chars.encode("utf-8")

    def fixlastline(self):
        c = self.text.get("end-2c")
        jeżeli c != '\n':
            self.text.insert("end-1c", "\n")

    def print_window(self, event):
        confirm = tkMessageBox.askokcancel(
                  title="Print",
                  message="Print to Default Printer",
                  default=tkMessageBox.OK,
                  master=self.text)
        jeżeli nie confirm:
            self.text.focus_set()
            zwróć "break"
        tempfilename = Nic
        saved = self.get_saved()
        jeżeli saved:
            filename = self.filename
        # shell undo jest reset after every prompt, looks saved, probably isn't
        jeżeli nie saved albo filename jest Nic:
            (tfd, tempfilename) = tempfile.mkstemp(prefix='IDLE_tmp_')
            filename = tempfilename
            os.close(tfd)
            jeżeli nie self.writefile(tempfilename):
                os.unlink(tempfilename)
                zwróć "break"
        platform = os.name
        printPlatform = Prawda
        jeżeli platform == 'posix': #posix platform
            command = idleConf.GetOption('main','General',
                                         'print-command-posix')
            command = command + " 2>&1"
        albo_inaczej platform == 'nt': #win32 platform
            command = idleConf.GetOption('main','General','print-command-win')
        inaczej: #no printing dla this platform
            printPlatform = Nieprawda
        jeżeli printPlatform:  #we can try to print dla this platform
            command = command % shlex.quote(filename)
            pipe = os.popen(command, "r")
            # things can get ugly on NT jeżeli there jest no printer available.
            output = pipe.read().strip()
            status = pipe.close()
            jeżeli status:
                output = "Printing failed (exit status 0x%x)\n" % \
                         status + output
            jeżeli output:
                output = "Printing command: %s\n" % repr(command) + output
                tkMessageBox.showerror("Print status", output, master=self.text)
        inaczej:  #no printing dla this platform
            message = "Printing jest nie enabled dla this platform: %s" % platform
            tkMessageBox.showinfo("Print status", message, master=self.text)
        jeżeli tempfilename:
            os.unlink(tempfilename)
        zwróć "break"

    opendialog = Nic
    savedialog = Nic

    filetypes = [
        ("Python files", "*.py *.pyw", "TEXT"),
        ("Text files", "*.txt", "TEXT"),
        ("All files", "*"),
        ]

    defaultextension = '.py' jeżeli sys.platform == 'darwin' inaczej ''

    def askopenfile(self):
        dir, base = self.defaultfilename("open")
        jeżeli nie self.opendialog:
            self.opendialog = tkFileDialog.Open(master=self.text,
                                                filetypes=self.filetypes)
        filename = self.opendialog.show(initialdir=dir, initialfile=base)
        zwróć filename

    def defaultfilename(self, mode="open"):
        jeżeli self.filename:
            zwróć os.path.split(self.filename)
        albo_inaczej self.dirname:
            zwróć self.dirname, ""
        inaczej:
            spróbuj:
                pwd = os.getcwd()
            wyjąwszy OSError:
                pwd = ""
            zwróć pwd, ""

    def asksavefile(self):
        dir, base = self.defaultfilename("save")
        jeżeli nie self.savedialog:
            self.savedialog = tkFileDialog.SaveAs(
                    master=self.text,
                    filetypes=self.filetypes,
                    defaultextension=self.defaultextension)
        filename = self.savedialog.show(initialdir=dir, initialfile=base)
        zwróć filename

    def updaterecentfileslist(self,filename):
        "Update recent file list on all editor windows"
        jeżeli self.editwin.flist:
            self.editwin.update_recent_files_list(filename)

def _io_binding(parent):  # htest #
    root = Tk()
    root.title("Test IOBinding")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    klasa MyEditWin:
        def __init__(self, text):
            self.text = text
            self.flist = Nic
            self.text.bind("<Control-o>", self.open)
            self.text.bind("<Control-s>", self.save)
        def get_saved(self): zwróć 0
        def set_saved(self, flag): dalej
        def reset_undo(self): dalej
        def open(self, event):
            self.text.event_generate("<<open-window-from-file>>")
        def save(self, event):
            self.text.event_generate("<<save-window>>")

    text = Text(root)
    text.pack()
    text.focus_set()
    editwin = MyEditWin(text)
    IOBinding(editwin)

jeżeli __name__ == "__main__":
    z idlelib.idle_test.htest zaimportuj run
    run(_io_binding)
