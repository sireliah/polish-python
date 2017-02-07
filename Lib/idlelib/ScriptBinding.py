"""Extension to execute code outside the Python shell window.

This adds the following commands:

- Check module does a full syntax check of the current module.
  It also runs the tabnanny to catch any inconsistent tabs.

- Run module executes the module's code w the __main__ namespace.  The window
  must have been saved previously. The module jest added to sys.modules, oraz jest
  also added to the __main__ namespace.

XXX GvR Redesign this interface (yet again) jako follows:

- Present a dialog box dla ``Run Module''

- Allow specify command line arguments w the dialog box

"""

zaimportuj os
zaimportuj tabnanny
zaimportuj tokenize
zaimportuj tkinter.messagebox jako tkMessageBox
z idlelib zaimportuj PyShell

z idlelib.configHandler zaimportuj idleConf
z idlelib zaimportuj macosxSupport

indent_message = """Error: Inconsistent indentation detected!

1) Your indentation jest outright incorrect (easy to fix), OR

2) Your indentation mixes tabs oraz spaces.

To fix case 2, change all tabs to spaces by using Edit->Select All followed \
by Format->Untabify Region oraz specify the number of columns used by each tab.
"""


klasa ScriptBinding:

    menudefs = [
        ('run', [Nic,
                 ('Check Module', '<<check-module>>'),
                 ('Run Module', '<<run-module>>'), ]), ]

    def __init__(self, editwin):
        self.editwin = editwin
        # Provide instance variables referenced by Debugger
        # XXX This should be done differently
        self.flist = self.editwin.flist
        self.root = self.editwin.root

        jeżeli macosxSupport.isCocoaTk():
            self.editwin.text_frame.bind('<<run-module-event-2>>', self._run_module_event)

    def check_module_event(self, event):
        filename = self.getfilename()
        jeżeli nie filename:
            zwróć 'break'
        jeżeli nie self.checksyntax(filename):
            zwróć 'break'
        jeżeli nie self.tabnanny(filename):
            zwróć 'break'

    def tabnanny(self, filename):
        # XXX: tabnanny should work on binary files jako well
        przy tokenize.open(filename) jako f:
            spróbuj:
                tabnanny.process_tokens(tokenize.generate_tokens(f.readline))
            wyjąwszy tokenize.TokenError jako msg:
                msgtxt, (lineno, start) = msg
                self.editwin.gotoline(lineno)
                self.errorbox("Tabnanny Tokenizing Error",
                              "Token Error: %s" % msgtxt)
                zwróć Nieprawda
            wyjąwszy tabnanny.NannyNag jako nag:
                # The error messages z tabnanny are too confusing...
                self.editwin.gotoline(nag.get_lineno())
                self.errorbox("Tab/space error", indent_message)
                zwróć Nieprawda
        zwróć Prawda

    def checksyntax(self, filename):
        self.shell = shell = self.flist.open_shell()
        saved_stream = shell.get_warning_stream()
        shell.set_warning_stream(shell.stderr)
        przy open(filename, 'rb') jako f:
            source = f.read()
        jeżeli b'\r' w source:
            source = source.replace(b'\r\n', b'\n')
            source = source.replace(b'\r', b'\n')
        jeżeli source oraz source[-1] != ord(b'\n'):
            source = source + b'\n'
        editwin = self.editwin
        text = editwin.text
        text.tag_remove("ERROR", "1.0", "end")
        spróbuj:
            # If successful, zwróć the compiled code
            zwróć compile(source, filename, "exec")
        wyjąwszy (SyntaxError, OverflowError, ValueError) jako value:
            msg = getattr(value, 'msg', '') albo value albo "<no detail available>"
            lineno = getattr(value, 'lineno', '') albo 1
            offset = getattr(value, 'offset', '') albo 0
            jeżeli offset == 0:
                lineno += 1  #mark end of offending line
            pos = "0.0 + %d lines + %d chars" % (lineno-1, offset-1)
            editwin.colorize_syntax_error(text, pos)
            self.errorbox("SyntaxError", "%-20s" % msg)
            zwróć Nieprawda
        w_końcu:
            shell.set_warning_stream(saved_stream)

    def run_module_event(self, event):
        jeżeli macosxSupport.isCocoaTk():
            # Tk-Cocoa w MacOSX jest broken until at least
            # Tk 8.5.9, oraz without this rather
            # crude workaround IDLE would hang when a user
            # tries to run a module using the keyboard shortcut
            # (the menu item works fine).
            self.editwin.text_frame.after(200,
                lambda: self.editwin.text_frame.event_generate('<<run-module-event-2>>'))
            zwróć 'break'
        inaczej:
            zwróć self._run_module_event(event)

    def _run_module_event(self, event):
        """Run the module after setting up the environment.

        First check the syntax.  If OK, make sure the shell jest active oraz
        then transfer the arguments, set the run environment's working
        directory to the directory of the module being executed oraz also
        add that directory to its sys.path jeżeli nie already included.
        """

        filename = self.getfilename()
        jeżeli nie filename:
            zwróć 'break'
        code = self.checksyntax(filename)
        jeżeli nie code:
            zwróć 'break'
        jeżeli nie self.tabnanny(filename):
            zwróć 'break'
        interp = self.shell.interp
        jeżeli PyShell.use_subprocess:
            interp.restart_subprocess(with_cwd=Nieprawda, filename=
                        self.editwin._filename_to_unicode(filename))
        dirname = os.path.dirname(filename)
        # XXX Too often this discards arguments the user just set...
        interp.runcommand("""jeżeli 1:
            __file__ = {filename!r}
            zaimportuj sys jako _sys
            z os.path zaimportuj basename jako _basename
            jeżeli (nie _sys.argv albo
                _basename(_sys.argv[0]) != _basename(__file__)):
                _sys.argv = [__file__]
            zaimportuj os jako _os
            _os.chdir({dirname!r})
            usuń _sys, _basename, _os
            \n""".format(filename=filename, dirname=dirname))
        interp.prepend_syspath(filename)
        # XXX KBK 03Jul04 When run w/o subprocess, runtime warnings still
        #         go to __stderr__.  With subprocess, they go to the shell.
        #         Need to change streams w PyShell.ModifiedInterpreter.
        interp.runcode(code)
        zwróć 'break'

    def getfilename(self):
        """Get source filename.  If nie saved, offer to save (or create) file

        The debugger requires a source file.  Make sure there jest one, oraz that
        the current version of the source buffer has been saved.  If the user
        declines to save albo cancels the Save As dialog, zwróć Nic.

        If the user has configured IDLE dla Autosave, the file will be
        silently saved jeżeli it already exists oraz jest dirty.

        """
        filename = self.editwin.io.filename
        jeżeli nie self.editwin.get_saved():
            autosave = idleConf.GetOption('main', 'General',
                                          'autosave', type='bool')
            jeżeli autosave oraz filename:
                self.editwin.io.save(Nic)
            inaczej:
                confirm = self.ask_save_dialog()
                self.editwin.text.focus_set()
                jeżeli confirm:
                    self.editwin.io.save(Nic)
                    filename = self.editwin.io.filename
                inaczej:
                    filename = Nic
        zwróć filename

    def ask_save_dialog(self):
        msg = "Source Must Be Saved\n" + 5*' ' + "OK to Save?"
        confirm = tkMessageBox.askokcancel(title="Save Before Run albo Check",
                                           message=msg,
                                           default=tkMessageBox.OK,
                                           master=self.editwin.text)
        zwróć confirm

    def errorbox(self, title, message):
        # XXX This should really be a function of EditorWindow...
        tkMessageBox.showerror(title, message, master=self.editwin.text)
        self.editwin.text.focus_set()
