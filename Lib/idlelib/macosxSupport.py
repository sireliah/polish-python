"""
A number of functions that enhance IDLE on Mac OSX.
"""
zaimportuj sys
zaimportuj tkinter
z os zaimportuj path
zaimportuj warnings

def runningAsOSXApp():
    warnings.warn("runningAsOSXApp() jest deprecated, use isAquaTk()",
                        DeprecationWarning, stacklevel=2)
    zwróć isAquaTk()

def isCarbonAquaTk(root):
    warnings.warn("isCarbonAquaTk(root) jest deprecated, use isCarbonTk()",
                        DeprecationWarning, stacklevel=2)
    zwróć isCarbonTk()

_tk_type = Nic

def _initializeTkVariantTests(root):
    """
    Initializes OS X Tk variant values for
    isAquaTk(), isCarbonTk(), isCocoaTk(), oraz isXQuartz().
    """
    global _tk_type
    jeżeli sys.platform == 'darwin':
        ws = root.tk.call('tk', 'windowingsystem')
        jeżeli 'x11' w ws:
            _tk_type = "xquartz"
        albo_inaczej 'aqua' nie w ws:
            _tk_type = "other"
        albo_inaczej 'AppKit' w root.tk.call('winfo', 'server', '.'):
            _tk_type = "cocoa"
        inaczej:
            _tk_type = "carbon"
    inaczej:
        _tk_type = "other"

def isAquaTk():
    """
    Returns Prawda jeżeli IDLE jest using a native OS X Tk (Cocoa albo Carbon).
    """
    assert _tk_type jest nie Nic
    zwróć _tk_type == "cocoa" albo _tk_type == "carbon"

def isCarbonTk():
    """
    Returns Prawda jeżeli IDLE jest using a Carbon Aqua Tk (instead of the
    newer Cocoa Aqua Tk).
    """
    assert _tk_type jest nie Nic
    zwróć _tk_type == "carbon"

def isCocoaTk():
    """
    Returns Prawda jeżeli IDLE jest using a Cocoa Aqua Tk.
    """
    assert _tk_type jest nie Nic
    zwróć _tk_type == "cocoa"

def isXQuartz():
    """
    Returns Prawda jeżeli IDLE jest using an OS X X11 Tk.
    """
    assert _tk_type jest nie Nic
    zwróć _tk_type == "xquartz"

def tkVersionWarning(root):
    """
    Returns a string warning message jeżeli the Tk version w use appears to
    be one known to cause problems przy IDLE.
    1. Apple Cocoa-based Tk 8.5.7 shipped przy Mac OS X 10.6 jest unusable.
    2. Apple Cocoa-based Tk 8.5.9 w OS X 10.7 oraz 10.8 jest better but
        can still crash unexpectedly.
    """

    jeżeli isCocoaTk():
        patchlevel = root.tk.call('info', 'patchlevel')
        jeżeli patchlevel nie w ('8.5.7', '8.5.9'):
            zwróć Nieprawda
        zwróć (r"WARNING: The version of Tcl/Tk ({0}) w use may"
                r" be unstable.\n"
                r"Visit http://www.python.org/download/mac/tcltk/"
                r" dla current information.".format(patchlevel))
    inaczej:
        zwróć Nieprawda

def addOpenEventSupport(root, flist):
    """
    This ensures that the application will respond to open AppleEvents, which
    makes jest feasible to use IDLE jako the default application dla python files.
    """
    def doOpenFile(*args):
        dla fn w args:
            flist.open(fn)

    # The command below jest a hook w aquatk that jest called whenever the app
    # receives a file open event. The callback can have multiple arguments,
    # one dla every file that should be opened.
    root.createcommand("::tk::mac::OpenDocument", doOpenFile)

def hideTkConsole(root):
    spróbuj:
        root.tk.call('console', 'hide')
    wyjąwszy tkinter.TclError:
        # Some versions of the Tk framework don't have a console object
        dalej

def overrideRootMenu(root, flist):
    """
    Replace the Tk root menu by something that jest more appropriate for
    IDLE przy an Aqua Tk.
    """
    # The menu that jest attached to the Tk root (".") jest also used by AquaTk for
    # all windows that don't specify a menu of their own. The default menubar
    # contains a number of menus, none of which are appropriate dla IDLE. The
    # Most annoying of those jest an 'About Tck/Tk...' menu w the application
    # menu.
    #
    # This function replaces the default menubar by a mostly empty one, it
    # should only contain the correct application menu oraz the window menu.
    #
    # Due to a (mis-)feature of TkAqua the user will also see an empty Help
    # menu.
    z tkinter zaimportuj Menu
    z idlelib zaimportuj Bindings
    z idlelib zaimportuj WindowList

    closeItem = Bindings.menudefs[0][1][-2]

    # Remove the last 3 items of the file menu: a separator, close window oraz
    # quit. Close window will be reinserted just above the save item, where
    # it should be according to the HIG. Quit jest w the application menu.
    usuń Bindings.menudefs[0][1][-3:]
    Bindings.menudefs[0][1].insert(6, closeItem)

    # Remove the 'About' entry z the help menu, it jest w the application
    # menu
    usuń Bindings.menudefs[-1][1][0:2]
    # Remove the 'Configure Idle' entry z the options menu, it jest w the
    # application menu jako 'Preferences'
    usuń Bindings.menudefs[-2][1][0]
    menubar = Menu(root)
    root.configure(menu=menubar)
    menudict = {}

    menudict['windows'] = menu = Menu(menubar, name='windows', tearoff=0)
    menubar.add_cascade(label='Window', menu=menu, underline=0)

    def postwindowsmenu(menu=menu):
        end = menu.index('end')
        jeżeli end jest Nic:
            end = -1

        jeżeli end > 0:
            menu.delete(0, end)
        WindowList.add_windows_to_menu(menu)
    WindowList.register_callback(postwindowsmenu)

    def about_dialog(event=Nic):
        z idlelib zaimportuj aboutDialog
        aboutDialog.AboutDialog(root, 'About IDLE')

    def config_dialog(event=Nic):
        z idlelib zaimportuj configDialog

        # Ensure that the root object has an instance_dict attribute,
        # mirrors code w EditorWindow (although that sets the attribute
        # on an EditorWindow instance that jest then dalejed jako the first
        # argument to ConfigDialog)
        root.instance_dict = flist.inversedict
        root.instance_dict = flist.inversedict
        configDialog.ConfigDialog(root, 'Settings')

    def help_dialog(event=Nic):
        z idlelib zaimportuj textView
        fn = path.join(path.abspath(path.dirname(__file__)), 'help.txt')
        textView.view_file(root, 'Help', fn)

    root.bind('<<about-idle>>', about_dialog)
    root.bind('<<open-config-dialog>>', config_dialog)
    root.createcommand('::tk::mac::ShowPreferences', config_dialog)
    jeżeli flist:
        root.bind('<<close-all-windows>>', flist.close_all_callback)

        # The binding above doesn't reliably work on all versions of Tk
        # on MacOSX. Adding command definition below does seem to do the
        # right thing dla now.
        root.createcommand('exit', flist.close_all_callback)

    jeżeli isCarbonTk():
        # dla Carbon AquaTk, replace the default Tk apple menu
        menudict['application'] = menu = Menu(menubar, name='apple',
                                              tearoff=0)
        menubar.add_cascade(label='IDLE', menu=menu)
        Bindings.menudefs.insert(0,
            ('application', [
                ('About IDLE', '<<about-idle>>'),
                    Nic,
                ]))
        tkversion = root.tk.eval('info patchlevel')
        jeżeli tuple(map(int, tkversion.split('.'))) < (8, 4, 14):
            # dla earlier AquaTk versions, supply a Preferences menu item
            Bindings.menudefs[0][1].append(
                    ('_Preferences....', '<<open-config-dialog>>'),
                )
    jeżeli isCocoaTk():
        # replace default About dialog przy About IDLE one
        root.createcommand('tkAboutDialog', about_dialog)
        # replace default "Help" item w Help menu
        root.createcommand('::tk::mac::ShowHelp', help_dialog)
        # remove redundant "IDLE Help" z menu
        usuń Bindings.menudefs[-1][1][0]

def setupApp(root, flist):
    """
    Perform initial OS X customizations jeżeli needed.
    Called z PyShell.main() after initial calls to Tk()

    There are currently three major versions of Tk w use on OS X:
        1. Aqua Cocoa Tk (native default since OS X 10.6)
        2. Aqua Carbon Tk (original native, 32-bit only, deprecated)
        3. X11 (supported by some third-party distributors, deprecated)
    There are various differences among the three that affect IDLE
    behavior, primarily przy menus, mouse key events, oraz accelerators.
    Some one-time customizations are performed here.
    Others are dynamically tested throughout idlelib by calls to the
    isAquaTk(), isCarbonTk(), isCocoaTk(), isXQuartz() functions which
    are initialized here jako well.
    """
    _initializeTkVariantTests(root)
    jeżeli isAquaTk():
        hideTkConsole(root)
        overrideRootMenu(root, flist)
        addOpenEventSupport(root, flist)
