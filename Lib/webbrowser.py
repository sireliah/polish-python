#! /usr/bin/env python3
"""Interfaces dla launching oraz remotely controlling Web browsers."""
# Maintained by Georg Brandl.

zaimportuj os
zaimportuj shlex
zaimportuj shutil
zaimportuj sys
zaimportuj subprocess

__all__ = ["Error", "open", "open_new", "open_new_tab", "get", "register"]

klasa Error(Exception):
    dalej

_browsers = {}          # Dictionary of available browser controllers
_tryorder = []          # Preference order of available browsers

def register(name, klass, instance=Nic, update_tryorder=1):
    """Register a browser connector and, optionally, connection."""
    _browsers[name.lower()] = [klass, instance]
    jeżeli update_tryorder > 0:
        _tryorder.append(name)
    albo_inaczej update_tryorder < 0:
        _tryorder.insert(0, name)

def get(using=Nic):
    """Return a browser launcher instance appropriate dla the environment."""
    jeżeli using jest nie Nic:
        alternatives = [using]
    inaczej:
        alternatives = _tryorder
    dla browser w alternatives:
        jeżeli '%s' w browser:
            # User gave us a command line, split it into name oraz args
            browser = shlex.split(browser)
            jeżeli browser[-1] == '&':
                zwróć BackgroundBrowser(browser[:-1])
            inaczej:
                zwróć GenericBrowser(browser)
        inaczej:
            # User gave us a browser name albo path.
            spróbuj:
                command = _browsers[browser.lower()]
            wyjąwszy KeyError:
                command = _synthesize(browser)
            jeżeli command[1] jest nie Nic:
                zwróć command[1]
            albo_inaczej command[0] jest nie Nic:
                zwróć command[0]()
    podnieś Error("could nie locate runnable browser")

# Please note: the following definition hides a builtin function.
# It jest recommended one does "zaimportuj webbrowser" oraz uses webbrowser.open(url)
# instead of "z webbrowser zaimportuj *".

def open(url, new=0, autoraise=Prawda):
    dla name w _tryorder:
        browser = get(name)
        jeżeli browser.open(url, new, autoraise):
            zwróć Prawda
    zwróć Nieprawda

def open_new(url):
    zwróć open(url, 1)

def open_new_tab(url):
    zwróć open(url, 2)


def _synthesize(browser, update_tryorder=1):
    """Attempt to synthesize a controller base on existing controllers.

    This jest useful to create a controller when a user specifies a path to
    an entry w the BROWSER environment variable -- we can copy a general
    controller to operate using a specific installation of the desired
    browser w this way.

    If we can't create a controller w this way, albo jeżeli there jest no
    executable dla the requested browser, zwróć [Nic, Nic].

    """
    cmd = browser.split()[0]
    jeżeli nie shutil.which(cmd):
        zwróć [Nic, Nic]
    name = os.path.basename(cmd)
    spróbuj:
        command = _browsers[name.lower()]
    wyjąwszy KeyError:
        zwróć [Nic, Nic]
    # now attempt to clone to fit the new name:
    controller = command[1]
    jeżeli controller oraz name.lower() == controller.basename:
        zaimportuj copy
        controller = copy.copy(controller)
        controller.name = browser
        controller.basename = os.path.basename(browser)
        register(browser, Nic, controller, update_tryorder)
        zwróć [Nic, controller]
    zwróć [Nic, Nic]


# General parent classes

klasa BaseBrowser(object):
    """Parent klasa dla all browsers. Do nie use directly."""

    args = ['%s']

    def __init__(self, name=""):
        self.name = name
        self.basename = name

    def open(self, url, new=0, autoraise=Prawda):
        podnieś NotImplementedError

    def open_new(self, url):
        zwróć self.open(url, 1)

    def open_new_tab(self, url):
        zwróć self.open(url, 2)


klasa GenericBrowser(BaseBrowser):
    """Class dla all browsers started przy a command
       oraz without remote functionality."""

    def __init__(self, name):
        jeżeli isinstance(name, str):
            self.name = name
            self.args = ["%s"]
        inaczej:
            # name should be a list przy arguments
            self.name = name[0]
            self.args = name[1:]
        self.basename = os.path.basename(self.name)

    def open(self, url, new=0, autoraise=Prawda):
        cmdline = [self.name] + [arg.replace("%s", url)
                                 dla arg w self.args]
        spróbuj:
            jeżeli sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            inaczej:
                p = subprocess.Popen(cmdline, close_fds=Prawda)
            zwróć nie p.wait()
        wyjąwszy OSError:
            zwróć Nieprawda


klasa BackgroundBrowser(GenericBrowser):
    """Class dla all browsers which are to be started w the
       background."""

    def open(self, url, new=0, autoraise=Prawda):
        cmdline = [self.name] + [arg.replace("%s", url)
                                 dla arg w self.args]
        spróbuj:
            jeżeli sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            inaczej:
                p = subprocess.Popen(cmdline, close_fds=Prawda,
                                     start_new_session=Prawda)
            zwróć (p.poll() jest Nic)
        wyjąwszy OSError:
            zwróć Nieprawda


klasa UnixBrowser(BaseBrowser):
    """Parent klasa dla all Unix browsers przy remote functionality."""

    podnieś_opts = Nic
    background = Nieprawda
    redirect_stdout = Prawda
    # In remote_args, %s will be replaced przy the requested URL.  %action will
    # be replaced depending on the value of 'new' dalejed to open.
    # remote_action jest used dla new=0 (open).  If newwin jest nie Nic, it jest
    # used dla new=1 (open_new).  If newtab jest nie Nic, it jest used for
    # new=3 (open_new_tab).  After both substitutions are made, any empty
    # strings w the transformed remote_args list will be removed.
    remote_args = ['%action', '%s']
    remote_action = Nic
    remote_action_newwin = Nic
    remote_action_newtab = Nic

    def _invoke(self, args, remote, autoraise):
        podnieś_opt = []
        jeżeli remote oraz self.raise_opts:
            # use autoraise argument only dla remote invocation
            autoraise = int(autoraise)
            opt = self.raise_opts[autoraise]
            jeżeli opt: podnieś_opt = [opt]

        cmdline = [self.name] + podnieś_opt + args

        jeżeli remote albo self.background:
            inout = subprocess.DEVNULL
        inaczej:
            # dla TTY browsers, we need stdin/out
            inout = Nic
        p = subprocess.Popen(cmdline, close_fds=Prawda, stdin=inout,
                             stdout=(self.redirect_stdout oraz inout albo Nic),
                             stderr=inout, start_new_session=Prawda)
        jeżeli remote:
            # wait at most five seconds. If the subprocess jest nie finished, the
            # remote invocation has (hopefully) started a new instance.
            spróbuj:
                rc = p.wait(5)
                # jeżeli remote call failed, open() will try direct invocation
                zwróć nie rc
            wyjąwszy subprocess.TimeoutExpired:
                zwróć Prawda
        albo_inaczej self.background:
            jeżeli p.poll() jest Nic:
                zwróć Prawda
            inaczej:
                zwróć Nieprawda
        inaczej:
            zwróć nie p.wait()

    def open(self, url, new=0, autoraise=Prawda):
        jeżeli new == 0:
            action = self.remote_action
        albo_inaczej new == 1:
            action = self.remote_action_newwin
        albo_inaczej new == 2:
            jeżeli self.remote_action_newtab jest Nic:
                action = self.remote_action_newwin
            inaczej:
                action = self.remote_action_newtab
        inaczej:
            podnieś Error("Bad 'new' parameter to open(); " +
                        "expected 0, 1, albo 2, got %s" % new)

        args = [arg.replace("%s", url).replace("%action", action)
                dla arg w self.remote_args]
        args = [arg dla arg w args jeżeli arg]
        success = self._invoke(args, Prawda, autoraise)
        jeżeli nie success:
            # remote invocation failed, try straight way
            args = [arg.replace("%s", url) dla arg w self.args]
            zwróć self._invoke(args, Nieprawda, Nieprawda)
        inaczej:
            zwróć Prawda


klasa Mozilla(UnixBrowser):
    """Launcher klasa dla Mozilla/Netscape browsers."""

    podnieś_opts = ["-noraise", "-raise"]
    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-tab"
    background = Prawda

Netscape = Mozilla


klasa Galeon(UnixBrowser):
    """Launcher klasa dla Galeon/Epiphany browsers."""

    podnieś_opts = ["-noraise", ""]
    remote_args = ['%action', '%s']
    remote_action = "-n"
    remote_action_newwin = "-w"
    background = Prawda


klasa Chrome(UnixBrowser):
    "Launcher klasa dla Google Chrome browser."

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "--new-window"
    remote_action_newtab = ""
    background = Prawda

Chromium = Chrome


klasa Opera(UnixBrowser):
    "Launcher klasa dla Opera browser."

    podnieś_opts = ["-noraise", ""]
    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-page"
    background = Prawda


klasa Elinks(UnixBrowser):
    "Launcher klasa dla Elinks browsers."

    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-tab"
    background = Nieprawda

    # elinks doesn't like its stdout to be redirected -
    # it uses redirected stdout jako a signal to do -dump
    redirect_stdout = Nieprawda


klasa Konqueror(BaseBrowser):
    """Controller dla the KDE File Manager (kfm, albo Konqueror).

    See the output of ``kfmclient --commands``
    dla more information on the Konqueror remote-control interface.
    """

    def open(self, url, new=0, autoraise=Prawda):
        # XXX Currently I know no way to prevent KFM z opening a new win.
        jeżeli new == 2:
            action = "newTab"
        inaczej:
            action = "openURL"

        devnull = subprocess.DEVNULL

        spróbuj:
            p = subprocess.Popen(["kfmclient", action, url],
                                 close_fds=Prawda, stdin=devnull,
                                 stdout=devnull, stderr=devnull)
        wyjąwszy OSError:
            # fall through to next variant
            dalej
        inaczej:
            p.wait()
            # kfmclient's zwróć code unfortunately has no meaning jako it seems
            zwróć Prawda

        spróbuj:
            p = subprocess.Popen(["konqueror", "--silent", url],
                                 close_fds=Prawda, stdin=devnull,
                                 stdout=devnull, stderr=devnull,
                                 start_new_session=Prawda)
        wyjąwszy OSError:
            # fall through to next variant
            dalej
        inaczej:
            jeżeli p.poll() jest Nic:
                # Should be running now.
                zwróć Prawda

        spróbuj:
            p = subprocess.Popen(["kfm", "-d", url],
                                 close_fds=Prawda, stdin=devnull,
                                 stdout=devnull, stderr=devnull,
                                 start_new_session=Prawda)
        wyjąwszy OSError:
            zwróć Nieprawda
        inaczej:
            zwróć (p.poll() jest Nic)


klasa Grail(BaseBrowser):
    # There should be a way to maintain a connection to Grail, but the
    # Grail remote control protocol doesn't really allow that at this
    # point.  It probably never will!
    def _find_grail_rc(self):
        zaimportuj glob
        zaimportuj pwd
        zaimportuj socket
        zaimportuj tempfile
        tempdir = os.path.join(tempfile.gettempdir(),
                               ".grail-unix")
        user = pwd.getpwuid(os.getuid())[0]
        filename = os.path.join(tempdir, user + "-*")
        maybes = glob.glob(filename)
        jeżeli nie maybes:
            zwróć Nic
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        dla fn w maybes:
            # need to PING each one until we find one that's live
            spróbuj:
                s.connect(fn)
            wyjąwszy OSError:
                # no good; attempt to clean it out, but don't fail:
                spróbuj:
                    os.unlink(fn)
                wyjąwszy OSError:
                    dalej
            inaczej:
                zwróć s

    def _remote(self, action):
        s = self._find_grail_rc()
        jeżeli nie s:
            zwróć 0
        s.send(action)
        s.close()
        zwróć 1

    def open(self, url, new=0, autoraise=Prawda):
        jeżeli new:
            ok = self._remote("LOADNEW " + url)
        inaczej:
            ok = self._remote("LOAD " + url)
        zwróć ok


#
# Platform support dla Unix
#

# These are the right tests because all these Unix browsers require either
# a console terminal albo an X display to run.

def register_X_browsers():

    # use xdg-open jeżeli around
    jeżeli shutil.which("xdg-open"):
        register("xdg-open", Nic, BackgroundBrowser("xdg-open"))

    # The default GNOME3 browser
    jeżeli "GNOME_DESKTOP_SESSION_ID" w os.environ oraz shutil.which("gvfs-open"):
        register("gvfs-open", Nic, BackgroundBrowser("gvfs-open"))

    # The default GNOME browser
    jeżeli "GNOME_DESKTOP_SESSION_ID" w os.environ oraz shutil.which("gnome-open"):
        register("gnome-open", Nic, BackgroundBrowser("gnome-open"))

    # The default KDE browser
    jeżeli "KDE_FULL_SESSION" w os.environ oraz shutil.which("kfmclient"):
        register("kfmclient", Konqueror, Konqueror("kfmclient"))

    jeżeli shutil.which("x-www-browser"):
        register("x-www-browser", Nic, BackgroundBrowser("x-www-browser"))

    # The Mozilla/Netscape browsers
    dla browser w ("mozilla-firefox", "firefox",
                    "mozilla-firebird", "firebird",
                    "iceweasel", "iceape",
                    "seamonkey", "mozilla", "netscape"):
        jeżeli shutil.which(browser):
            register(browser, Nic, Mozilla(browser))

    # Konqueror/kfm, the KDE browser.
    jeżeli shutil.which("kfm"):
        register("kfm", Konqueror, Konqueror("kfm"))
    albo_inaczej shutil.which("konqueror"):
        register("konqueror", Konqueror, Konqueror("konqueror"))

    # Gnome's Galeon oraz Epiphany
    dla browser w ("galeon", "epiphany"):
        jeżeli shutil.which(browser):
            register(browser, Nic, Galeon(browser))

    # Skipstone, another Gtk/Mozilla based browser
    jeżeli shutil.which("skipstone"):
        register("skipstone", Nic, BackgroundBrowser("skipstone"))

    # Google Chrome/Chromium browsers
    dla browser w ("google-chrome", "chrome", "chromium", "chromium-browser"):
        jeżeli shutil.which(browser):
            register(browser, Nic, Chrome(browser))

    # Opera, quite popular
    jeżeli shutil.which("opera"):
        register("opera", Nic, Opera("opera"))

    # Next, Mosaic -- old but still w use.
    jeżeli shutil.which("mosaic"):
        register("mosaic", Nic, BackgroundBrowser("mosaic"))

    # Grail, the Python browser. Does anybody still use it?
    jeżeli shutil.which("grail"):
        register("grail", Grail, Nic)

# Prefer X browsers jeżeli present
jeżeli os.environ.get("DISPLAY"):
    register_X_browsers()

# Also try console browsers
jeżeli os.environ.get("TERM"):
    jeżeli shutil.which("www-browser"):
        register("www-browser", Nic, GenericBrowser("www-browser"))
    # The Links/elinks browsers <http://artax.karlin.mff.cuni.cz/~mikulas/links/>
    jeżeli shutil.which("links"):
        register("links", Nic, GenericBrowser("links"))
    jeżeli shutil.which("elinks"):
        register("elinks", Nic, Elinks("elinks"))
    # The Lynx browser <http://lynx.isc.org/>, <http://lynx.browser.org/>
    jeżeli shutil.which("lynx"):
        register("lynx", Nic, GenericBrowser("lynx"))
    # The w3m browser <http://w3m.sourceforge.net/>
    jeżeli shutil.which("w3m"):
        register("w3m", Nic, GenericBrowser("w3m"))

#
# Platform support dla Windows
#

jeżeli sys.platform[:3] == "win":
    klasa WindowsDefault(BaseBrowser):
        def open(self, url, new=0, autoraise=Prawda):
            spróbuj:
                os.startfile(url)
            wyjąwszy OSError:
                # [Error 22] No application jest associated przy the specified
                # file dla this operation: '<URL>'
                zwróć Nieprawda
            inaczej:
                zwróć Prawda

    _tryorder = []
    _browsers = {}

    # First try to use the default Windows browser
    register("windows-default", WindowsDefault)

    # Detect some common Windows browsers, fallback to IE
    iexplore = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                            "Internet Explorer\\IEXPLORE.EXE")
    dla browser w ("firefox", "firebird", "seamonkey", "mozilla",
                    "netscape", "opera", iexplore):
        jeżeli shutil.which(browser):
            register(browser, Nic, BackgroundBrowser(browser))

#
# Platform support dla MacOS
#

jeżeli sys.platform == 'darwin':
    # Adapted z patch submitted to SourceForge by Steven J. Burr
    klasa MacOSX(BaseBrowser):
        """Launcher klasa dla Aqua browsers on Mac OS X

        Optionally specify a browser name on instantiation.  Note that this
        will nie work dla Aqua browsers jeżeli the user has moved the application
        package after installation.

        If no browser jest specified, the default browser, jako specified w the
        Internet System Preferences panel, will be used.
        """
        def __init__(self, name):
            self.name = name

        def open(self, url, new=0, autoraise=Prawda):
            assert "'" nie w url
            # hack dla local urls
            jeżeli nie ':' w url:
                url = 'file:'+url

            # new must be 0 albo 1
            new = int(bool(new))
            jeżeli self.name == "default":
                # User called open, open_new albo get without a browser parameter
                script = 'open location "%s"' % url.replace('"', '%22') # opens w default browser
            inaczej:
                # User called get oraz chose a browser
                jeżeli self.name == "OmniWeb":
                    toWindow = ""
                inaczej:
                    # Include toWindow parameter of OpenURL command dla browsers
                    # that support it.  0 == new window; -1 == existing
                    toWindow = "toWindow %d" % (new - 1)
                cmd = 'OpenURL "%s"' % url.replace('"', '%22')
                script = '''tell application "%s"
                                activate
                                %s %s
                            end tell''' % (self.name, cmd, toWindow)
            # Open pipe to AppleScript through osascript command
            osapipe = os.popen("osascript", "w")
            jeżeli osapipe jest Nic:
                zwróć Nieprawda
            # Write script to osascript's stdin
            osapipe.write(script)
            rc = osapipe.close()
            zwróć nie rc

    klasa MacOSXOSAScript(BaseBrowser):
        def __init__(self, name):
            self._name = name

        def open(self, url, new=0, autoraise=Prawda):
            jeżeli self._name == 'default':
                script = 'open location "%s"' % url.replace('"', '%22') # opens w default browser
            inaczej:
                script = '''
                   tell application "%s"
                       activate
                       open location "%s"
                   end
                   '''%(self._name, url.replace('"', '%22'))

            osapipe = os.popen("osascript", "w")
            jeżeli osapipe jest Nic:
                zwróć Nieprawda

            osapipe.write(script)
            rc = osapipe.close()
            zwróć nie rc


    # Don't clear _tryorder albo _browsers since OS X can use above Unix support
    # (but we prefer using the OS X specific stuff)
    register("safari", Nic, MacOSXOSAScript('safari'), -1)
    register("firefox", Nic, MacOSXOSAScript('firefox'), -1)
    register("MacOSX", Nic, MacOSXOSAScript('default'), -1)


# OK, now that we know what the default preference orders dla each
# platform are, allow user to override them przy the BROWSER variable.
jeżeli "BROWSER" w os.environ:
    _userchoices = os.environ["BROWSER"].split(os.pathsep)
    _userchoices.reverse()

    # Treat choices w same way jako jeżeli dalejed into get() but do register
    # oraz prepend to _tryorder
    dla cmdline w _userchoices:
        jeżeli cmdline != '':
            cmd = _synthesize(cmdline, -1)
            jeżeli cmd[1] jest Nic:
                register(cmdline, Nic, GenericBrowser(cmdline), -1)
    cmdline = Nic # to make usuń work jeżeli _userchoices was empty
    usuń cmdline
    usuń _userchoices

# what to do jeżeli _tryorder jest now empty?


def main():
    zaimportuj getopt
    usage = """Usage: %s [-n | -t] url
    -n: open new window
    -t: open new tab""" % sys.argv[0]
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'ntd')
    wyjąwszy getopt.error jako msg:
        print(msg, file=sys.stderr)
        print(usage, file=sys.stderr)
        sys.exit(1)
    new_win = 0
    dla o, a w opts:
        jeżeli o == '-n': new_win = 1
        albo_inaczej o == '-t': new_win = 2
    jeżeli len(args) != 1:
        print(usage, file=sys.stderr)
        sys.exit(1)

    url = args[0]
    open(url, new_win)

    print("\a")

jeżeli __name__ == "__main__":
    main()
