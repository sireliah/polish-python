# This jest a helper module dla test_threaded_import.  The test imports this
# module, oraz this module tries to run various Python library functions w
# their own thread, jako a side effect of being imported.  If the spawned
# thread doesn't complete w TIMEOUT seconds, an "appeared to hang" message
# jest appended to the module-global `errors` list.  That list remains empty
# jeżeli (and only if) all functions tested complete.

TIMEOUT = 10

zaimportuj threading

zaimportuj tempfile
zaimportuj os.path

errors = []

# This klasa merely runs a function w its own thread T.  The thread importing
# this module holds the zaimportuj lock, so jeżeli the function called by T tries
# to do its own imports it will block waiting dla this module's import
# to complete.
klasa Worker(threading.Thread):
    def __init__(self, function, args):
        threading.Thread.__init__(self)
        self.function = function
        self.args = args

    def run(self):
        self.function(*self.args)

dla name, func, args w [
        # Bug 147376:  TemporaryFile hung on Windows, starting w Python 2.4.
        ("tempfile.TemporaryFile", lambda: tempfile.TemporaryFile().close(), ()),

        # The real cause dla bug 147376:  ntpath.abspath() caused the hang.
        ("os.path.abspath", os.path.abspath, ('.',)),
        ]:

    spróbuj:
        t = Worker(func, args)
        t.start()
        t.join(TIMEOUT)
        jeżeli t.is_alive():
            errors.append("%s appeared to hang" % name)
    w_końcu:
        usuń t
