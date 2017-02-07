# -*-mode: python; fill-column: 75; tab-width: 8 -*-
#
# $Id$
#
# Tix.py -- Tix widget wrappers.
#
#       For Tix, see http://tix.sourceforge.net
#
#       - Sudhir Shenoy (sshenoy@gol.com), Dec. 1995.
#         based on an idea of Jean-Marc Lugrin (lugrin@ms.com)
#
# NOTE: In order to minimize changes to Tkinter.py, some of the code here
#       (TixWidget.__init__) has been taken z Tkinter (Widget.__init__)
#       oraz will przerwij jeżeli there are major changes w Tkinter.
#
# The Tix widgets are represented by a klasa hierarchy w python przy proper
# inheritance of base classes.
#
# As a result after creating a 'w = StdButtonBox', I can write
#              w.ok['text'] = 'Who Cares'
#    albo              w.ok['bg'] = w['bg']
# albo even       w.ok.invoke()
# etc.
#
# Compare the demo tixwidgets.py to the original Tcl program oraz you will
# appreciate the advantages.
#

z tkinter zaimportuj *
z tkinter zaimportuj _cnfmerge, _default_root

# WARNING - TkVersion jest a limited precision floating point number
jeżeli TkVersion < 3.999:
    podnieś ImportError("This version of Tix.py requires Tk 4.0 albo higher")

zaimportuj _tkinter # If this fails your Python may nie be configured dla Tk

# Some more constants (dla consistency przy Tkinter)
WINDOW = 'window'
TEXT = 'text'
STATUS = 'status'
IMMEDIATE = 'immediate'
IMAGE = 'image'
IMAGETEXT = 'imagetext'
BALLOON = 'balloon'
AUTO = 'auto'
ACROSSTOP = 'acrosstop'

# A few useful constants dla the Grid widget
ASCII = 'ascii'
CELL = 'cell'
COLUMN = 'column'
DECREASING = 'decreasing'
INCREASING = 'increasing'
INTEGER = 'integer'
MAIN = 'main'
MAX = 'max'
REAL = 'real'
ROW = 'row'
S_REGION = 's-region'
X_REGION = 'x-region'
Y_REGION = 'y-region'

# Some constants used by Tkinter dooneevent()
TCL_DONT_WAIT     = 1 << 1
TCL_WINDOW_EVENTS = 1 << 2
TCL_FILE_EVENTS   = 1 << 3
TCL_TIMER_EVENTS  = 1 << 4
TCL_IDLE_EVENTS   = 1 << 5
TCL_ALL_EVENTS    = 0

# BEWARE - this jest implemented by copying some code z the Widget class
#          w Tkinter (to override Widget initialization) oraz jest therefore
#          liable to przerwij.
zaimportuj tkinter, os

# Could probably add this to Tkinter.Misc
klasa tixCommand:
    """The tix commands provide access to miscellaneous  elements
    of  Tix's  internal state oraz the Tix application context.
    Most of the information manipulated by these  commands pertains
    to  the  application  jako a whole, albo to a screen albo
    display, rather than to a particular window.

    This jest a mixin class, assumed to be mixed to Tkinter.Tk
    that supports the self.tk.call method.
    """

    def tix_addbitmapdir(self, directory):
        """Tix maintains a list of directories under which
        the  tix_getimage  oraz tix_getbitmap commands will
        search dla image files. The standard bitmap  directory
        jest $TIX_LIBRARY/bitmaps. The addbitmapdir command
        adds directory into this list. By  using  this
        command, the  image  files  of an applications can
        also be located using the tix_getimage albo tix_getbitmap
        command.
        """
        zwróć self.tk.call('tix', 'addbitmapdir', directory)

    def tix_cget(self, option):
        """Returns  the  current  value  of the configuration
        option given by option. Option may be  any  of  the
        options described w the CONFIGURATION OPTIONS section.
        """
        zwróć self.tk.call('tix', 'cget', option)

    def tix_configure(self, cnf=Nic, **kw):
        """Query albo modify the configuration options of the Tix application
        context. If no option jest specified, returns a dictionary all of the
        available options.  If option jest specified przy no value, then the
        command returns a list describing the one named option (this list
        will be identical to the corresponding sublist of the value
        returned jeżeli no option jest specified).  If one albo more option-value
        pairs are specified, then the command modifies the given option(s)
        to have the given value(s); w this case the command returns an
        empty string. Option may be any of the configuration options.
        """
        # Copied z Tkinter.py
        jeżeli kw:
            cnf = _cnfmerge((cnf, kw))
        albo_inaczej cnf:
            cnf = _cnfmerge(cnf)
        jeżeli cnf jest Nic:
            zwróć self._getconfigure('tix', 'configure')
        jeżeli isinstance(cnf, str):
            zwróć self._getconfigure1('tix', 'configure', '-'+cnf)
        zwróć self.tk.call(('tix', 'configure') + self._options(cnf))

    def tix_filedialog(self, dlgclass=Nic):
        """Returns the file selection dialog that may be shared among
        different calls z this application.  This command will create a
        file selection dialog widget when it jest called the first time. This
        dialog will be returned by all subsequent calls to tix_filedialog.
        An optional dlgclass parameter can be dalejed to specified what type
        of file selection dialog widget jest desired. Possible options are
        tix FileSelectDialog albo tixExFileSelectDialog.
        """
        jeżeli dlclass jest nie Nic:
            zwróć self.tk.call('tix', 'filedialog', dlgclass)
        inaczej:
            zwróć self.tk.call('tix', 'filedialog')

    def tix_getbitmap(self, name):
        """Locates a bitmap file of the name name.xpm albo name w one of the
        bitmap directories (see the tix_addbitmapdir command above).  By
        using tix_getbitmap, you can avoid hard coding the pathnames of the
        bitmap files w your application. When successful, it returns the
        complete pathname of the bitmap file, prefixed przy the character
        '@'.  The returned value can be used to configure the -bitmap
        option of the TK oraz Tix widgets.
        """
        zwróć self.tk.call('tix', 'getbitmap', name)

    def tix_getimage(self, name):
        """Locates an image file of the name name.xpm, name.xbm albo name.ppm
        w one of the bitmap directories (see the addbitmapdir command
        above). If more than one file przy the same name (but different
        extensions) exist, then the image type jest chosen according to the
        depth of the X display: xbm images are chosen on monochrome
        displays oraz color images are chosen on color displays. By using
        tix_ getimage, you can avoid hard coding the pathnames of the
        image files w your application. When successful, this command
        returns the name of the newly created image, which can be used to
        configure the -image option of the Tk oraz Tix widgets.
        """
        zwróć self.tk.call('tix', 'getimage', name)

    def tix_option_get(self, name):
        """Gets  the options  maintained  by  the  Tix
        scheme mechanism. Available options include:

            active_bg       active_fg      bg
            bold_font       dark1_bg       dark1_fg
            dark2_bg        dark2_fg       disabled_fg
            fg              fixed_font     font
            inactive_bg     inactive_fg    input1_bg
            input2_bg       italic_font    light1_bg
            light1_fg       light2_bg      light2_fg
            menu_font       output1_bg     output2_bg
            select_bg       select_fg      selector
            """
        # could use self.tk.globalgetvar('tixOption', name)
        zwróć self.tk.call('tix', 'option', 'get', name)

    def tix_resetoptions(self, newScheme, newFontSet, newScmPrio=Nic):
        """Resets the scheme oraz fontset of the Tix application to
        newScheme oraz newFontSet, respectively.  This affects only those
        widgets created after this call. Therefore, it jest best to call the
        resetoptions command before the creation of any widgets w a Tix
        application.

        The optional parameter newScmPrio can be given to reset the
        priority level of the Tk options set by the Tix schemes.

        Because of the way Tk handles the X option database, after Tix has
        been has imported oraz inited, it jest nie possible to reset the color
        schemes oraz font sets using the tix config command.  Instead, the
        tix_resetoptions command must be used.
        """
        jeżeli newScmPrio jest nie Nic:
            zwróć self.tk.call('tix', 'resetoptions', newScheme, newFontSet, newScmPrio)
        inaczej:
            zwróć self.tk.call('tix', 'resetoptions', newScheme, newFontSet)

klasa Tk(tkinter.Tk, tixCommand):
    """Toplevel widget of Tix which represents mostly the main window
    of an application. It has an associated Tcl interpreter."""
    def __init__(self, screenName=Nic, baseName=Nic, className='Tix'):
        tkinter.Tk.__init__(self, screenName, baseName, className)
        tixlib = os.environ.get('TIX_LIBRARY')
        self.tk.eval('global auto_path; lappend auto_path [file dir [info nameof]]')
        jeżeli tixlib jest nie Nic:
            self.tk.eval('global auto_path; lappend auto_path {%s}' % tixlib)
            self.tk.eval('global tcl_pkgPath; lappend tcl_pkgPath {%s}' % tixlib)
        # Load Tix - this should work dynamically albo statically
        # If it's static, tcl/tix8.1/pkgIndex.tcl should have
        #               'load {} Tix'
        # If it's dynamic under Unix, tcl/tix8.1/pkgIndex.tcl should have
        #               'load libtix8.1.8.3.so Tix'
        self.tk.eval('package require Tix')

    def destroy(self):
        # For safety, remove an delete_window binding before destroy
        self.protocol("WM_DELETE_WINDOW", "")
        tkinter.Tk.destroy(self)

# The Tix 'tixForm' geometry manager
klasa Form:
    """The Tix Form geometry manager

    Widgets can be arranged by specifying attachments to other widgets.
    See Tix documentation dla complete details"""

    def config(self, cnf={}, **kw):
        self.tk.call('tixForm', self._w, *self._options(cnf, kw))

    form = config

    def __setitem__(self, key, value):
        Form.form(self, {key: value})

    def check(self):
        zwróć self.tk.call('tixForm', 'check', self._w)

    def forget(self):
        self.tk.call('tixForm', 'forget', self._w)

    def grid(self, xsize=0, ysize=0):
        jeżeli (nie xsize) oraz (nie ysize):
            x = self.tk.call('tixForm', 'grid', self._w)
            y = self.tk.splitlist(x)
            z = ()
            dla x w y:
                z = z + (self.tk.getint(x),)
            zwróć z
        zwróć self.tk.call('tixForm', 'grid', self._w, xsize, ysize)

    def info(self, option=Nic):
        jeżeli nie option:
            zwróć self.tk.call('tixForm', 'info', self._w)
        jeżeli option[0] != '-':
            option = '-' + option
        zwróć self.tk.call('tixForm', 'info', self._w, option)

    def slaves(self):
        zwróć [self._nametowidget(x) dla x w
                self.tk.splitlist(
                       self.tk.call(
                       'tixForm', 'slaves', self._w))]



tkinter.Widget.__bases__ = tkinter.Widget.__bases__ + (Form,)

klasa TixWidget(tkinter.Widget):
    """A TixWidget klasa jest used to package all (or most) Tix widgets.

    Widget initialization jest extended w two ways:
       1) It jest possible to give a list of options which must be part of
       the creation command (so called Tix 'static' options). These cannot be
       given jako a 'config' command later.
       2) It jest possible to give the name of an existing TK widget. These are
       child widgets created automatically by a Tix mega-widget. The Tk call
       to create these widgets jest therefore bypassed w TixWidget.__init__

    Both options are dla use by subclasses only.
    """
    def __init__ (self, master=Nic, widgetName=Nic,
                static_options=Nic, cnf={}, kw={}):
        # Merge keywords oraz dictionary arguments
        jeżeli kw:
            cnf = _cnfmerge((cnf, kw))
        inaczej:
            cnf = _cnfmerge(cnf)

        # Move static options into extra. static_options must be
        # a list of keywords (or Nic).
        extra=()

        # 'options' jest always a static option
        jeżeli static_options:
            static_options.append('options')
        inaczej:
            static_options = ['options']

        dla k,v w list(cnf.items()):
            jeżeli k w static_options:
                extra = extra + ('-' + k, v)
                usuń cnf[k]

        self.widgetName = widgetName
        Widget._setup(self, master, cnf)

        # If widgetName jest Nic, this jest a dummy creation call where the
        # corresponding Tk widget has already been created by Tix
        jeżeli widgetName:
            self.tk.call(widgetName, self._w, *extra)

        # Non-static options - to be done via a 'config' command
        jeżeli cnf:
            Widget.config(self, cnf)

        # Dictionary to hold subwidget names dla easier access. We can't
        # use the children list because the public Tix names may nie be the
        # same jako the pathname component
        self.subwidget_list = {}

    # We set up an attribute access function so that it jest possible to
    # do w.ok['text'] = 'Hello' rather than w.subwidget('ok')['text'] = 'Hello'
    # when w jest a StdButtonBox.
    # We can even do w.ok.invoke() because w.ok jest subclassed z the
    # Button klasa jeżeli you go through the proper constructors
    def __getattr__(self, name):
        jeżeli name w self.subwidget_list:
            zwróć self.subwidget_list[name]
        podnieś AttributeError(name)

    def set_silent(self, value):
        """Set a variable without calling its action routine"""
        self.tk.call('tixSetSilent', self._w, value)

    def subwidget(self, name):
        """Return the named subwidget (which must have been created by
        the sub-class)."""
        n = self._subwidget_name(name)
        jeżeli nie n:
            podnieś TclError("Subwidget " + name + " nie child of " + self._name)
        # Remove header of name oraz leading dot
        n = n[len(self._w)+1:]
        zwróć self._nametowidget(n)

    def subwidgets_all(self):
        """Return all subwidgets."""
        names = self._subwidget_names()
        jeżeli nie names:
            zwróć []
        retlist = []
        dla name w names:
            name = name[len(self._w)+1:]
            spróbuj:
                retlist.append(self._nametowidget(name))
            wyjąwszy:
                # some of the widgets are unknown e.g. border w LabelFrame
                dalej
        zwróć retlist

    def _subwidget_name(self,name):
        """Get a subwidget name (returns a String, nie a Widget !)"""
        spróbuj:
            zwróć self.tk.call(self._w, 'subwidget', name)
        wyjąwszy TclError:
            zwróć Nic

    def _subwidget_names(self):
        """Return the name of all subwidgets."""
        spróbuj:
            x = self.tk.call(self._w, 'subwidgets', '-all')
            zwróć self.tk.splitlist(x)
        wyjąwszy TclError:
            zwróć Nic

    def config_all(self, option, value):
        """Set configuration options dla all subwidgets (and self)."""
        jeżeli option == '':
            zwróć
        albo_inaczej nie isinstance(option, str):
            option = repr(option)
        jeżeli nie isinstance(value, str):
            value = repr(value)
        names = self._subwidget_names()
        dla name w names:
            self.tk.call(name, 'configure', '-' + option, value)
    # These are missing z Tkinter
    def image_create(self, imgtype, cnf={}, master=Nic, **kw):
        jeżeli nie master:
            master = tkinter._default_root
            jeżeli nie master:
                podnieś RuntimeError('Too early to create image')
        jeżeli kw oraz cnf: cnf = _cnfmerge((cnf, kw))
        albo_inaczej kw: cnf = kw
        options = ()
        dla k, v w cnf.items():
            jeżeli callable(v):
                v = self._register(v)
            options = options + ('-'+k, v)
        zwróć master.tk.call(('image', 'create', imgtype,) + options)
    def image_delete(self, imgname):
        spróbuj:
            self.tk.call('image', 'delete', imgname)
        wyjąwszy TclError:
            # May happen jeżeli the root was destroyed
            dalej

# Subwidgets are child widgets created automatically by mega-widgets.
# In python, we have to create these subwidgets manually to mirror their
# existence w Tk/Tix.
klasa TixSubWidget(TixWidget):
    """Subwidget class.

    This jest used to mirror child widgets automatically created
    by Tix/Tk jako part of a mega-widget w Python (which jest nie informed
    of this)"""

    def __init__(self, master, name,
               destroy_physically=1, check_intermediate=1):
        jeżeli check_intermediate:
            path = master._subwidget_name(name)
            spróbuj:
                path = path[len(master._w)+1:]
                plist = path.split('.')
            wyjąwszy:
                plist = []

        jeżeli nie check_intermediate:
            # immediate descendant
            TixWidget.__init__(self, master, Nic, Nic, {'name' : name})
        inaczej:
            # Ensure that the intermediate widgets exist
            parent = master
            dla i w range(len(plist) - 1):
                n = '.'.join(plist[:i+1])
                spróbuj:
                    w = master._nametowidget(n)
                    parent = w
                wyjąwszy KeyError:
                    # Create the intermediate widget
                    parent = TixSubWidget(parent, plist[i],
                                          destroy_physically=0,
                                          check_intermediate=0)
            # The Tk widget name jest w plist, nie w name
            jeżeli plist:
                name = plist[-1]
            TixWidget.__init__(self, parent, Nic, Nic, {'name' : name})
        self.destroy_physically = destroy_physically

    def destroy(self):
        # For some widgets e.g., a NoteBook, when we call destructors,
        # we must be careful nie to destroy the frame widget since this
        # also destroys the parent NoteBook thus leading to an exception
        # w Tkinter when it finally calls Tcl to destroy the NoteBook
        dla c w list(self.children.values()): c.destroy()
        jeżeli self._name w self.master.children:
            usuń self.master.children[self._name]
        jeżeli self._name w self.master.subwidget_list:
            usuń self.master.subwidget_list[self._name]
        jeżeli self.destroy_physically:
            # This jest bypassed only dla a few widgets
            self.tk.call('destroy', self._w)


# Useful klasa to create a display style - later shared by many items.
# Contributed by Steffen Kremser
klasa DisplayStyle:
    """DisplayStyle - handle configuration options shared by
    (multiple) Display Items"""

    def __init__(self, itemtype, cnf={}, **kw):
        master = _default_root              # global z Tkinter
        jeżeli nie master oraz 'refwindow' w cnf: master=cnf['refwindow']
        albo_inaczej nie master oraz 'refwindow' w kw:  master= kw['refwindow']
        albo_inaczej nie master: podnieś RuntimeError("Too early to create display style: no root window")
        self.tk = master.tk
        self.stylename = self.tk.call('tixDisplayStyle', itemtype,
                            *self._options(cnf,kw) )

    def __str__(self):
        zwróć self.stylename

    def _options(self, cnf, kw):
        jeżeli kw oraz cnf:
            cnf = _cnfmerge((cnf, kw))
        albo_inaczej kw:
            cnf = kw
        opts = ()
        dla k, v w cnf.items():
            opts = opts + ('-'+k, v)
        zwróć opts

    def delete(self):
        self.tk.call(self.stylename, 'delete')

    def __setitem__(self,key,value):
        self.tk.call(self.stylename, 'configure', '-%s'%key, value)

    def config(self, cnf={}, **kw):
        zwróć self._getconfigure(
            self.stylename, 'configure', *self._options(cnf,kw))

    def __getitem__(self,key):
        zwróć self.tk.call(self.stylename, 'cget', '-%s'%key)


######################################################
### The Tix Widget classes - w alphabetical order ###
######################################################

klasa Balloon(TixWidget):
    """Balloon help widget.

    Subwidget       Class
    ---------       -----
    label           Label
    message         Message"""

    # FIXME: It should inherit -superclass tixShell
    def __init__(self, master=Nic, cnf={}, **kw):
        # static seem to be -installcolormap -initwait -statusbar -cursor
        static = ['options', 'installcolormap', 'initwait', 'statusbar',
                  'cursor']
        TixWidget.__init__(self, master, 'tixBalloon', static, cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label',
                                                   destroy_physically=0)
        self.subwidget_list['message'] = _dummyLabel(self, 'message',
                                                     destroy_physically=0)

    def bind_widget(self, widget, cnf={}, **kw):
        """Bind balloon widget to another.
        One balloon widget may be bound to several widgets at the same time"""
        self.tk.call(self._w, 'bind', widget._w, *self._options(cnf, kw))

    def unbind_widget(self, widget):
        self.tk.call(self._w, 'unbind', widget._w)

klasa ButtonBox(TixWidget):
    """ButtonBox - A container dla pushbuttons.
    Subwidgets are the buttons added przy the add method.
    """
    def __init__(self, master=Nic, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixButtonBox',
                           ['orientation', 'options'], cnf, kw)

    def add(self, name, cnf={}, **kw):
        """Add a button przy given name to box."""

        btn = self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = _dummyButton(self, name)
        zwróć btn

    def invoke(self, name):
        jeżeli name w self.subwidget_list:
            self.tk.call(self._w, 'invoke', name)

klasa ComboBox(TixWidget):
    """ComboBox - an Entry field przy a dropdown menu. The user can select a
    choice by either typing w the entry subwidget albo selecting z the
    listbox subwidget.

    Subwidget       Class
    ---------       -----
    entry       Entry
    arrow       Button
    slistbox    ScrolledListBox
    tick        Button
    cross       Button : present jeżeli created przy the fancy option"""

    # FIXME: It should inherit -superclass tixLabelWidget
    def __init__ (self, master=Nic, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixComboBox',
                           ['editable', 'dropdown', 'fancy', 'options'],
                           cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')
        self.subwidget_list['arrow'] = _dummyButton(self, 'arrow')
        self.subwidget_list['slistbox'] = _dummyScrolledListBox(self,
                                                                'slistbox')
        spróbuj:
            self.subwidget_list['tick'] = _dummyButton(self, 'tick')
            self.subwidget_list['cross'] = _dummyButton(self, 'cross')
        wyjąwszy TypeError:
            # unavailable when -fancy nie specified
            dalej

    # align

    def add_history(self, str):
        self.tk.call(self._w, 'addhistory', str)

    def append_history(self, str):
        self.tk.call(self._w, 'appendhistory', str)

    def insert(self, index, str):
        self.tk.call(self._w, 'insert', index, str)

    def pick(self, index):
        self.tk.call(self._w, 'pick', index)

klasa Control(TixWidget):
    """Control - An entry field przy value change arrows.  The user can
    adjust the value by pressing the two arrow buttons albo by entering
    the value directly into the entry. The new value will be checked
    against the user-defined upper oraz lower limits.

    Subwidget       Class
    ---------       -----
    incr       Button
    decr       Button
    entry       Entry
    label       Label"""

    # FIXME: It should inherit -superclass tixLabelWidget
    def __init__ (self, master=Nic, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixControl', ['options'], cnf, kw)
        self.subwidget_list['incr'] = _dummyButton(self, 'incr')
        self.subwidget_list['decr'] = _dummyButton(self, 'decr')
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')

    def decrement(self):
        self.tk.call(self._w, 'decr')

    def increment(self):
        self.tk.call(self._w, 'incr')

    def invoke(self):
        self.tk.call(self._w, 'invoke')

    def update(self):
        self.tk.call(self._w, 'update')

klasa DirList(TixWidget):
    """DirList - displays a list view of a directory, its previous
    directories oraz its sub-directories. The user can choose one of
    the directories displayed w the list albo change to another directory.

    Subwidget       Class
    ---------       -----
    hlist       HList
    hsb              Scrollbar
    vsb              Scrollbar"""

    # FIXME: It should inherit -superclass tixScrolledHList
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirList', ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    def chdir(self, dir):
        self.tk.call(self._w, 'chdir', dir)

klasa DirTree(TixWidget):
    """DirTree - Directory Listing w a hierarchical view.
    Displays a tree view of a directory, its previous directories oraz its
    sub-directories. The user can choose one of the directories displayed
    w the list albo change to another directory.

    Subwidget       Class
    ---------       -----
    hlist           HList
    hsb             Scrollbar
    vsb             Scrollbar"""

    # FIXME: It should inherit -superclass tixScrolledHList
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirTree', ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    def chdir(self, dir):
        self.tk.call(self._w, 'chdir', dir)

klasa DirSelectBox(TixWidget):
    """DirSelectBox - Motjeżeli style file select box.
    It jest generally used for
    the user to choose a file. FileSelectBox stores the files mostly
    recently selected into a ComboBox widget so that they can be quickly
    selected again.

    Subwidget       Class
    ---------       -----
    selection       ComboBox
    filter          ComboBox
    dirlist         ScrolledListBox
    filelist        ScrolledListBox"""

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirSelectBox', ['options'], cnf, kw)
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['dircbx'] = _dummyFileComboBox(self, 'dircbx')

klasa ExFileSelectBox(TixWidget):
    """ExFileSelectBox - MS Windows style file select box.
    It provides an convenient method dla the user to select files.

    Subwidget       Class
    ---------       -----
    cancel       Button
    ok              Button
    hidden       Checkbutton
    types       ComboBox
    dir              ComboBox
    file       ComboBox
    dirlist       ScrolledListBox
    filelist       ScrolledListBox"""

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixExFileSelectBox', ['options'], cnf, kw)
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['hidden'] = _dummyCheckbutton(self, 'hidden')
        self.subwidget_list['types'] = _dummyComboBox(self, 'types')
        self.subwidget_list['dir'] = _dummyComboBox(self, 'dir')
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['file'] = _dummyComboBox(self, 'file')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')

    def filter(self):
        self.tk.call(self._w, 'filter')

    def invoke(self):
        self.tk.call(self._w, 'invoke')


# Should inherit z a Dialog class
klasa DirSelectDialog(TixWidget):
    """The DirSelectDialog widget presents the directories w the file
    system w a dialog window. The user can use this dialog window to
    navigate through the file system to select the desired directory.

    Subwidgets       Class
    ----------       -----
    dirbox       DirSelectDialog"""

    # FIXME: It should inherit -superclass tixDialogShell
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirSelectDialog',
                           ['options'], cnf, kw)
        self.subwidget_list['dirbox'] = _dummyDirSelectBox(self, 'dirbox')
        # cancel oraz ok buttons are missing

    def popup(self):
        self.tk.call(self._w, 'popup')

    def popdown(self):
        self.tk.call(self._w, 'popdown')


# Should inherit z a Dialog class
klasa ExFileSelectDialog(TixWidget):
    """ExFileSelectDialog - MS Windows style file select dialog.
    It provides an convenient method dla the user to select files.

    Subwidgets       Class
    ----------       -----
    fsbox       ExFileSelectBox"""

    # FIXME: It should inherit -superclass tixDialogShell
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixExFileSelectDialog',
                           ['options'], cnf, kw)
        self.subwidget_list['fsbox'] = _dummyExFileSelectBox(self, 'fsbox')

    def popup(self):
        self.tk.call(self._w, 'popup')

    def popdown(self):
        self.tk.call(self._w, 'popdown')

klasa FileSelectBox(TixWidget):
    """ExFileSelectBox - Motjeżeli style file select box.
    It jest generally used for
    the user to choose a file. FileSelectBox stores the files mostly
    recently selected into a ComboBox widget so that they can be quickly
    selected again.

    Subwidget       Class
    ---------       -----
    selection       ComboBox
    filter          ComboBox
    dirlist         ScrolledListBox
    filelist        ScrolledListBox"""

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileSelectBox', ['options'], cnf, kw)
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')
        self.subwidget_list['filter'] = _dummyComboBox(self, 'filter')
        self.subwidget_list['selection'] = _dummyComboBox(self, 'selection')

    def apply_filter(self):              # name of subwidget jest same jako command
        self.tk.call(self._w, 'filter')

    def invoke(self):
        self.tk.call(self._w, 'invoke')

# Should inherit z a Dialog class
klasa FileSelectDialog(TixWidget):
    """FileSelectDialog - Motjeżeli style file select dialog.

    Subwidgets       Class
    ----------       -----
    btns       StdButtonBox
    fsbox       FileSelectBox"""

    # FIXME: It should inherit -superclass tixStdDialogShell
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileSelectDialog',
                           ['options'], cnf, kw)
        self.subwidget_list['btns'] = _dummyStdButtonBox(self, 'btns')
        self.subwidget_list['fsbox'] = _dummyFileSelectBox(self, 'fsbox')

    def popup(self):
        self.tk.call(self._w, 'popup')

    def popdown(self):
        self.tk.call(self._w, 'popdown')

klasa FileEntry(TixWidget):
    """FileEntry - Entry field przy button that invokes a FileSelectDialog.
    The user can type w the filename manually. Alternatively, the user can
    press the button widget that sits next to the entry, which will bring
    up a file selection dialog.

    Subwidgets       Class
    ----------       -----
    button       Button
    entry       Entry"""

    # FIXME: It should inherit -superclass tixLabelWidget
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileEntry',
                           ['dialogtype', 'options'], cnf, kw)
        self.subwidget_list['button'] = _dummyButton(self, 'button')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')

    def invoke(self):
        self.tk.call(self._w, 'invoke')

    def file_dialog(self):
        # FIXME: zwróć python object
        dalej

klasa HList(TixWidget, XView, YView):
    """HList - Hierarchy display  widget can be used to display any data
    that have a hierarchical structure, dla example, file system directory
    trees. The list entries are indented oraz connected by branch lines
    according to their places w the hierarchy.

    Subwidgets - Nic"""

    def __init__ (self,master=Nic,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixHList',
                           ['columns', 'options'], cnf, kw)

    def add(self, entry, cnf={}, **kw):
        zwróć self.tk.call(self._w, 'add', entry, *self._options(cnf, kw))

    def add_child(self, parent=Nic, cnf={}, **kw):
        jeżeli nie parent:
            parent = ''
        zwróć self.tk.call(
                     self._w, 'addchild', parent, *self._options(cnf, kw))

    def anchor_set(self, entry):
        self.tk.call(self._w, 'anchor', 'set', entry)

    def anchor_clear(self):
        self.tk.call(self._w, 'anchor', 'clear')

    def column_width(self, col=0, width=Nic, chars=Nic):
        jeżeli nie chars:
            zwróć self.tk.call(self._w, 'column', 'width', col, width)
        inaczej:
            zwróć self.tk.call(self._w, 'column', 'width', col,
                                '-char', chars)

    def delete_all(self):
        self.tk.call(self._w, 'delete', 'all')

    def delete_entry(self, entry):
        self.tk.call(self._w, 'delete', 'entry', entry)

    def delete_offsprings(self, entry):
        self.tk.call(self._w, 'delete', 'offsprings', entry)

    def delete_siblings(self, entry):
        self.tk.call(self._w, 'delete', 'siblings', entry)

    def dragsite_set(self, index):
        self.tk.call(self._w, 'dragsite', 'set', index)

    def dragsite_clear(self):
        self.tk.call(self._w, 'dragsite', 'clear')

    def dropsite_set(self, index):
        self.tk.call(self._w, 'dropsite', 'set', index)

    def dropsite_clear(self):
        self.tk.call(self._w, 'dropsite', 'clear')

    def header_create(self, col, cnf={}, **kw):
        self.tk.call(self._w, 'header', 'create', col, *self._options(cnf, kw))

    def header_configure(self, col, cnf={}, **kw):
        jeżeli cnf jest Nic:
            zwróć self._getconfigure(self._w, 'header', 'configure', col)
        self.tk.call(self._w, 'header', 'configure', col,
                     *self._options(cnf, kw))

    def header_cget(self,  col, opt):
        zwróć self.tk.call(self._w, 'header', 'cget', col, opt)

    def header_exists(self,  col):
        zwróć self.tk.call(self._w, 'header', 'exists', col)

    def header_delete(self, col):
        self.tk.call(self._w, 'header', 'delete', col)

    def header_size(self, col):
        zwróć self.tk.call(self._w, 'header', 'size', col)

    def hide_entry(self, entry):
        self.tk.call(self._w, 'hide', 'entry', entry)

    def indicator_create(self, entry, cnf={}, **kw):
        self.tk.call(
              self._w, 'indicator', 'create', entry, *self._options(cnf, kw))

    def indicator_configure(self, entry, cnf={}, **kw):
        jeżeli cnf jest Nic:
            zwróć self._getconfigure(
                self._w, 'indicator', 'configure', entry)
        self.tk.call(
              self._w, 'indicator', 'configure', entry, *self._options(cnf, kw))

    def indicator_cget(self,  entry, opt):
        zwróć self.tk.call(self._w, 'indicator', 'cget', entry, opt)

    def indicator_exists(self,  entry):
        zwróć self.tk.call (self._w, 'indicator', 'exists', entry)

    def indicator_delete(self, entry):
        self.tk.call(self._w, 'indicator', 'delete', entry)

    def indicator_size(self, entry):
        zwróć self.tk.call(self._w, 'indicator', 'size', entry)

    def info_anchor(self):
        zwróć self.tk.call(self._w, 'info', 'anchor')

    def info_bbox(self, entry):
        zwróć self._getints(
                self.tk.call(self._w, 'info', 'bbox', entry)) albo Nic

    def info_children(self, entry=Nic):
        c = self.tk.call(self._w, 'info', 'children', entry)
        zwróć self.tk.splitlist(c)

    def info_data(self, entry):
        zwróć self.tk.call(self._w, 'info', 'data', entry)

    def info_dragsite(self):
        zwróć self.tk.call(self._w, 'info', 'dragsite')

    def info_dropsite(self):
        zwróć self.tk.call(self._w, 'info', 'dropsite')

    def info_exists(self, entry):
        zwróć self.tk.call(self._w, 'info', 'exists', entry)

    def info_hidden(self, entry):
        zwróć self.tk.call(self._w, 'info', 'hidden', entry)

    def info_next(self, entry):
        zwróć self.tk.call(self._w, 'info', 'next', entry)

    def info_parent(self, entry):
        zwróć self.tk.call(self._w, 'info', 'parent', entry)

    def info_prev(self, entry):
        zwróć self.tk.call(self._w, 'info', 'prev', entry)

    def info_selection(self):
        c = self.tk.call(self._w, 'info', 'selection')
        zwróć self.tk.splitlist(c)

    def item_cget(self, entry, col, opt):
        zwróć self.tk.call(self._w, 'item', 'cget', entry, col, opt)

    def item_configure(self, entry, col, cnf={}, **kw):
        jeżeli cnf jest Nic:
            zwróć self._getconfigure(self._w, 'item', 'configure', entry, col)
        self.tk.call(self._w, 'item', 'configure', entry, col,
              *self._options(cnf, kw))

    def item_create(self, entry, col, cnf={}, **kw):
        self.tk.call(
              self._w, 'item', 'create', entry, col, *self._options(cnf, kw))

    def item_exists(self, entry, col):
        zwróć self.tk.call(self._w, 'item', 'exists', entry, col)

    def item_delete(self, entry, col):
        self.tk.call(self._w, 'item', 'delete', entry, col)

    def entrycget(self, entry, opt):
        zwróć self.tk.call(self._w, 'entrycget', entry, opt)

    def entryconfigure(self, entry, cnf={}, **kw):
        jeżeli cnf jest Nic:
            zwróć self._getconfigure(self._w, 'entryconfigure', entry)
        self.tk.call(self._w, 'entryconfigure', entry,
              *self._options(cnf, kw))

    def nearest(self, y):
        zwróć self.tk.call(self._w, 'nearest', y)

    def see(self, entry):
        self.tk.call(self._w, 'see', entry)

    def selection_clear(self, cnf={}, **kw):
        self.tk.call(self._w, 'selection', 'clear', *self._options(cnf, kw))

    def selection_includes(self, entry):
        zwróć self.tk.call(self._w, 'selection', 'includes', entry)

    def selection_set(self, first, last=Nic):
        self.tk.call(self._w, 'selection', 'set', first, last)

    def show_entry(self, entry):
        zwróć self.tk.call(self._w, 'show', 'entry', entry)

klasa InputOnly(TixWidget):
    """InputOnly - Invisible widget. Unix only.

    Subwidgets - Nic"""

    def __init__ (self,master=Nic,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixInputOnly', Nic, cnf, kw)

klasa LabelEntry(TixWidget):
    """LabelEntry - Entry field przy label. Packages an entry widget
    oraz a label into one mega widget. It can beused be used to simplify
    the creation of ``entry-form'' type of interface.

    Subwidgets       Class
    ----------       -----
    label       Label
    entry       Entry"""

    def __init__ (self,master=Nic,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixLabelEntry',
                           ['labelside','options'], cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')

klasa LabelFrame(TixWidget):
    """LabelFrame - Labelled Frame container. Packages a frame widget
    oraz a label into one mega widget. To create widgets inside a
    LabelFrame widget, one creates the new widgets relative to the
    frame subwidget oraz manage them inside the frame subwidget.

    Subwidgets       Class
    ----------       -----
    label       Label
    frame       Frame"""

    def __init__ (self,master=Nic,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixLabelFrame',
                           ['labelside','options'], cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['frame'] = _dummyFrame(self, 'frame')


klasa ListNoteBook(TixWidget):
    """A ListNoteBook widget jest very similar to the TixNoteBook widget:
    it can be used to display many windows w a limited space using a
    notebook metaphor. The notebook jest divided into a stack of pages
    (windows). At one time only one of these pages can be shown.
    The user can navigate through these pages by
    choosing the name of the desired page w the hlist subwidget."""

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixListNoteBook', ['options'], cnf, kw)
        # Is this necessary? It's nie an exposed subwidget w Tix.
        self.subwidget_list['pane'] = _dummyPanedWindow(self, 'pane',
                                                        destroy_physically=0)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['shlist'] = _dummyScrolledHList(self, 'shlist')

    def add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name)
        zwróć self.subwidget_list[name]

    def page(self, name):
        zwróć self.subwidget(name)

    def pages(self):
        # Can't call subwidgets_all directly because we don't want .nbframe
        names = self.tk.split(self.tk.call(self._w, 'pages'))
        ret = []
        dla x w names:
            ret.append(self.subwidget(x))
        zwróć ret

    def podnieś_page(self, name):              # podnieś jest a python keyword
        self.tk.call(self._w, 'raise', name)

klasa Meter(TixWidget):
    """The Meter widget can be used to show the progress of a background
    job which may take a long time to execute.
    """

    def __init__(self, master=Nic, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixMeter',
                           ['options'], cnf, kw)

klasa NoteBook(TixWidget):
    """NoteBook - Multi-page container widget (tabbed notebook metaphor).

    Subwidgets       Class
    ----------       -----
    nbframe       NoteBookFrame
    <pages>       page widgets added dynamically przy the add method"""

    def __init__ (self,master=Nic,cnf={}, **kw):
        TixWidget.__init__(self,master,'tixNoteBook', ['options'], cnf, kw)
        self.subwidget_list['nbframe'] = TixSubWidget(self, 'nbframe',
                                                      destroy_physically=0)

    def add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name)
        zwróć self.subwidget_list[name]

    def delete(self, name):
        self.tk.call(self._w, 'delete', name)
        self.subwidget_list[name].destroy()
        usuń self.subwidget_list[name]

    def page(self, name):
        zwróć self.subwidget(name)

    def pages(self):
        # Can't call subwidgets_all directly because we don't want .nbframe
        names = self.tk.split(self.tk.call(self._w, 'pages'))
        ret = []
        dla x w names:
            ret.append(self.subwidget(x))
        zwróć ret

    def podnieś_page(self, name):              # podnieś jest a python keyword
        self.tk.call(self._w, 'raise', name)

    def podnieśd(self):
        zwróć self.tk.call(self._w, 'raised')

klasa NoteBookFrame(TixWidget):
    # FIXME: This jest dangerous to expose to be called on its own.
    dalej

klasa OptionMenu(TixWidget):
    """OptionMenu - creates a menu button of options.

    Subwidget       Class
    ---------       -----
    menubutton      Menubutton
    menu            Menu"""

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixOptionMenu', ['options'], cnf, kw)
        self.subwidget_list['menubutton'] = _dummyMenubutton(self, 'menubutton')
        self.subwidget_list['menu'] = _dummyMenu(self, 'menu')

    def add_command(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', 'command', name, *self._options(cnf, kw))

    def add_separator(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', 'separator', name, *self._options(cnf, kw))

    def delete(self, name):
        self.tk.call(self._w, 'delete', name)

    def disable(self, name):
        self.tk.call(self._w, 'disable', name)

    def enable(self, name):
        self.tk.call(self._w, 'enable', name)

klasa PanedWindow(TixWidget):
    """PanedWindow - Multi-pane container widget
    allows the user to interactively manipulate the sizes of several
    panes. The panes can be arranged either vertically albo horizontally.The
    user changes the sizes of the panes by dragging the resize handle
    between two panes.

    Subwidgets       Class
    ----------       -----
    <panes>       g/p widgets added dynamically przy the add method."""

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixPanedWindow', ['orientation', 'options'], cnf, kw)

    # add delete forget panecget paneconfigure panes setsize
    def add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name,
                                                 check_intermediate=0)
        zwróć self.subwidget_list[name]

    def delete(self, name):
        self.tk.call(self._w, 'delete', name)
        self.subwidget_list[name].destroy()
        usuń self.subwidget_list[name]

    def forget(self, name):
        self.tk.call(self._w, 'forget', name)

    def panecget(self,  entry, opt):
        zwróć self.tk.call(self._w, 'panecget', entry, opt)

    def paneconfigure(self, entry, cnf={}, **kw):
        jeżeli cnf jest Nic:
            zwróć self._getconfigure(self._w, 'paneconfigure', entry)
        self.tk.call(self._w, 'paneconfigure', entry, *self._options(cnf, kw))

    def panes(self):
        names = self.tk.splitlist(self.tk.call(self._w, 'panes'))
        zwróć [self.subwidget(x) dla x w names]

klasa PopupMenu(TixWidget):
    """PopupMenu widget can be used jako a replacement of the tk_popup command.
    The advantage of the Tix PopupMenu widget jest it requires less application
    code to manipulate.


    Subwidgets       Class
    ----------       -----
    menubutton       Menubutton
    menu       Menu"""

    # FIXME: It should inherit -superclass tixShell
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixPopupMenu', ['options'], cnf, kw)
        self.subwidget_list['menubutton'] = _dummyMenubutton(self, 'menubutton')
        self.subwidget_list['menu'] = _dummyMenu(self, 'menu')

    def bind_widget(self, widget):
        self.tk.call(self._w, 'bind', widget._w)

    def unbind_widget(self, widget):
        self.tk.call(self._w, 'unbind', widget._w)

    def post_widget(self, widget, x, y):
        self.tk.call(self._w, 'post', widget._w, x, y)

klasa ResizeHandle(TixWidget):
    """Internal widget to draw resize handles on Scrolled widgets."""
    def __init__(self, master, cnf={}, **kw):
        # There seems to be a Tix bug rejecting the configure method
        # Let's try making the flags -static
        flags = ['options', 'command', 'cursorfg', 'cursorbg',
                 'handlesize', 'hintcolor', 'hintwidth',
                 'x', 'y']
        # In fact, x y height width are configurable
        TixWidget.__init__(self, master, 'tixResizeHandle',
                           flags, cnf, kw)

    def attach_widget(self, widget):
        self.tk.call(self._w, 'attachwidget', widget._w)

    def detach_widget(self, widget):
        self.tk.call(self._w, 'detachwidget', widget._w)

    def hide(self, widget):
        self.tk.call(self._w, 'hide', widget._w)

    def show(self, widget):
        self.tk.call(self._w, 'show', widget._w)

klasa ScrolledHList(TixWidget):
    """ScrolledHList - HList przy automatic scrollbars."""

    # FIXME: It should inherit -superclass tixScrolledWidget
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledHList', ['options'],
                           cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

klasa ScrolledListBox(TixWidget):
    """ScrolledListBox - Listbox przy automatic scrollbars."""

    # FIXME: It should inherit -superclass tixScrolledWidget
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledListBox', ['options'], cnf, kw)
        self.subwidget_list['listbox'] = _dummyListbox(self, 'listbox')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

klasa ScrolledText(TixWidget):
    """ScrolledText - Text przy automatic scrollbars."""

    # FIXME: It should inherit -superclass tixScrolledWidget
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledText', ['options'], cnf, kw)
        self.subwidget_list['text'] = _dummyText(self, 'text')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

klasa ScrolledTList(TixWidget):
    """ScrolledTList - TList przy automatic scrollbars."""

    # FIXME: It should inherit -superclass tixScrolledWidget
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledTList', ['options'],
                           cnf, kw)
        self.subwidget_list['tlist'] = _dummyTList(self, 'tlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

klasa ScrolledWindow(TixWidget):
    """ScrolledWindow - Window przy automatic scrollbars."""

    # FIXME: It should inherit -superclass tixScrolledWidget
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledWindow', ['options'], cnf, kw)
        self.subwidget_list['window'] = _dummyFrame(self, 'window')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

klasa Select(TixWidget):
    """Select - Container of button subwidgets. It can be used to provide
    radio-box albo check-box style of selection options dla the user.

    Subwidgets are buttons added dynamically using the add method."""

    # FIXME: It should inherit -superclass tixLabelWidget
    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixSelect',
                           ['allowzero', 'radio', 'orientation', 'labelside',
                            'options'],
                           cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')

    def add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = _dummyButton(self, name)
        zwróć self.subwidget_list[name]

    def invoke(self, name):
        self.tk.call(self._w, 'invoke', name)

klasa Shell(TixWidget):
    """Toplevel window.

    Subwidgets - Nic"""

    def __init__ (self,master=Nic,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixShell', ['options', 'title'], cnf, kw)

klasa DialogShell(TixWidget):
    """Toplevel window, przy popup popdown oraz center methods.
    It tells the window manager that it jest a dialog window oraz should be
    treated specially. The exact treatment depends on the treatment of
    the window manager.

    Subwidgets - Nic"""

    # FIXME: It should inherit z  Shell
    def __init__ (self,master=Nic,cnf={}, **kw):
        TixWidget.__init__(self, master,
                           'tixDialogShell',
                           ['options', 'title', 'mapped',
                            'minheight', 'minwidth',
                            'parent', 'transient'], cnf, kw)

    def popdown(self):
        self.tk.call(self._w, 'popdown')

    def popup(self):
        self.tk.call(self._w, 'popup')

    def center(self):
        self.tk.call(self._w, 'center')

klasa StdButtonBox(TixWidget):
    """StdButtonBox - Standard Button Box (OK, Apply, Cancel oraz Help) """

    def __init__(self, master=Nic, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixStdButtonBox',
                           ['orientation', 'options'], cnf, kw)
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['apply'] = _dummyButton(self, 'apply')
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['help'] = _dummyButton(self, 'help')

    def invoke(self, name):
        jeżeli name w self.subwidget_list:
            self.tk.call(self._w, 'invoke', name)

klasa TList(TixWidget, XView, YView):
    """TList - Hierarchy display widget which can be
    used to display data w a tabular format. The list entries of a TList
    widget are similar to the entries w the Tk listbox widget. The main
    differences are (1) the TList widget can display the list entries w a
    two dimensional format oraz (2) you can use graphical images jako well as
    multiple colors oraz fonts dla the list entries.

    Subwidgets - Nic"""

    def __init__ (self,master=Nic,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixTList', ['options'], cnf, kw)

    def active_set(self, index):
        self.tk.call(self._w, 'active', 'set', index)

    def active_clear(self):
        self.tk.call(self._w, 'active', 'clear')

    def anchor_set(self, index):
        self.tk.call(self._w, 'anchor', 'set', index)

    def anchor_clear(self):
        self.tk.call(self._w, 'anchor', 'clear')

    def delete(self, from_, to=Nic):
        self.tk.call(self._w, 'delete', from_, to)

    def dragsite_set(self, index):
        self.tk.call(self._w, 'dragsite', 'set', index)

    def dragsite_clear(self):
        self.tk.call(self._w, 'dragsite', 'clear')

    def dropsite_set(self, index):
        self.tk.call(self._w, 'dropsite', 'set', index)

    def dropsite_clear(self):
        self.tk.call(self._w, 'dropsite', 'clear')

    def insert(self, index, cnf={}, **kw):
        self.tk.call(self._w, 'insert', index, *self._options(cnf, kw))

    def info_active(self):
        zwróć self.tk.call(self._w, 'info', 'active')

    def info_anchor(self):
        zwróć self.tk.call(self._w, 'info', 'anchor')

    def info_down(self, index):
        zwróć self.tk.call(self._w, 'info', 'down', index)

    def info_left(self, index):
        zwróć self.tk.call(self._w, 'info', 'left', index)

    def info_right(self, index):
        zwróć self.tk.call(self._w, 'info', 'right', index)

    def info_selection(self):
        c = self.tk.call(self._w, 'info', 'selection')
        zwróć self.tk.splitlist(c)

    def info_size(self):
        zwróć self.tk.call(self._w, 'info', 'size')

    def info_up(self, index):
        zwróć self.tk.call(self._w, 'info', 'up', index)

    def nearest(self, x, y):
        zwróć self.tk.call(self._w, 'nearest', x, y)

    def see(self, index):
        self.tk.call(self._w, 'see', index)

    def selection_clear(self, cnf={}, **kw):
        self.tk.call(self._w, 'selection', 'clear', *self._options(cnf, kw))

    def selection_includes(self, index):
        zwróć self.tk.call(self._w, 'selection', 'includes', index)

    def selection_set(self, first, last=Nic):
        self.tk.call(self._w, 'selection', 'set', first, last)

klasa Tree(TixWidget):
    """Tree - The tixTree widget can be used to display hierarchical
    data w a tree form. The user can adjust
    the view of the tree by opening albo closing parts of the tree."""

    # FIXME: It should inherit -superclass tixScrolledWidget
    def __init__(self, master=Nic, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixTree',
                           ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    def autosetmode(self):
        '''This command calls the setmode method dla all the entries w this
     Tree widget: jeżeli an entry has no child entries, its mode jest set to
     none. Otherwise, jeżeli the entry has any hidden child entries, its mode jest
     set to open; otherwise its mode jest set to close.'''
        self.tk.call(self._w, 'autosetmode')

    def close(self, entrypath):
        '''Close the entry given by entryPath jeżeli its mode jest close.'''
        self.tk.call(self._w, 'close', entrypath)

    def getmode(self, entrypath):
        '''Returns the current mode of the entry given by entryPath.'''
        zwróć self.tk.call(self._w, 'getmode', entrypath)

    def open(self, entrypath):
        '''Open the entry given by entryPath jeżeli its mode jest open.'''
        self.tk.call(self._w, 'open', entrypath)

    def setmode(self, entrypath, mode='none'):
        '''This command jest used to indicate whether the entry given by
     entryPath has children entries oraz whether the children are visible. mode
     must be one of open, close albo none. If mode jest set to open, a (+)
     indicator jest drawn next the entry. If mode jest set to close, a (-)
     indicator jest drawn next the entry. If mode jest set to none, no
     indicators will be drawn dla this entry. The default mode jest none. The
     open mode indicates the entry has hidden children oraz this entry can be
     opened by the user. The close mode indicates that all the children of the
     entry are now visible oraz the entry can be closed by the user.'''
        self.tk.call(self._w, 'setmode', entrypath, mode)


# Could try subclassing Tree dla CheckList - would need another arg to init
klasa CheckList(TixWidget):
    """The CheckList widget
    displays a list of items to be selected by the user. CheckList acts
    similarly to the Tk checkbutton albo radiobutton widgets, wyjąwszy it jest
    capable of handling many more items than checkbuttons albo radiobuttons.
    """
    # FIXME: It should inherit -superclass tixTree
    def __init__(self, master=Nic, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixCheckList',
                           ['options', 'radio'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    def autosetmode(self):
        '''This command calls the setmode method dla all the entries w this
     Tree widget: jeżeli an entry has no child entries, its mode jest set to
     none. Otherwise, jeżeli the entry has any hidden child entries, its mode jest
     set to open; otherwise its mode jest set to close.'''
        self.tk.call(self._w, 'autosetmode')

    def close(self, entrypath):
        '''Close the entry given by entryPath jeżeli its mode jest close.'''
        self.tk.call(self._w, 'close', entrypath)

    def getmode(self, entrypath):
        '''Returns the current mode of the entry given by entryPath.'''
        zwróć self.tk.call(self._w, 'getmode', entrypath)

    def open(self, entrypath):
        '''Open the entry given by entryPath jeżeli its mode jest open.'''
        self.tk.call(self._w, 'open', entrypath)

    def getselection(self, mode='on'):
        '''Returns a list of items whose status matches status. If status jest
     nie specified, the list of items w the "on" status will be returned.
     Mode can be on, off, default'''
        c = self.tk.split(self.tk.call(self._w, 'getselection', mode))
        zwróć self.tk.splitlist(c)

    def getstatus(self, entrypath):
        '''Returns the current status of entryPath.'''
        zwróć self.tk.call(self._w, 'getstatus', entrypath)

    def setstatus(self, entrypath, mode='on'):
        '''Sets the status of entryPath to be status. A bitmap will be
     displayed next to the entry its status jest on, off albo default.'''
        self.tk.call(self._w, 'setstatus', entrypath, mode)


###########################################################################
### The subclassing below jest used to instantiate the subwidgets w each ###
### mega widget. This allows us to access their methods directly.       ###
###########################################################################

klasa _dummyButton(Button, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyCheckbutton(Checkbutton, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyEntry(Entry, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyFrame(Frame, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyLabel(Label, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyListbox(Listbox, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyMenu(Menu, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyMenubutton(Menubutton, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyScrollbar(Scrollbar, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyText(Text, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyScrolledListBox(ScrolledListBox, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['listbox'] = _dummyListbox(self, 'listbox')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

klasa _dummyHList(HList, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyScrolledHList(ScrolledHList, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

klasa _dummyTList(TList, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyComboBox(ComboBox, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, ['fancy',destroy_physically])
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')
        self.subwidget_list['arrow'] = _dummyButton(self, 'arrow')

        self.subwidget_list['slistbox'] = _dummyScrolledListBox(self,
                                                                'slistbox')
        spróbuj:
            self.subwidget_list['tick'] = _dummyButton(self, 'tick')
            #cross Button : present jeżeli created przy the fancy option
            self.subwidget_list['cross'] = _dummyButton(self, 'cross')
        wyjąwszy TypeError:
            # unavailable when -fancy nie specified
            dalej

klasa _dummyDirList(DirList, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

klasa _dummyDirSelectBox(DirSelectBox, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['dircbx'] = _dummyFileComboBox(self, 'dircbx')

klasa _dummyExFileSelectBox(ExFileSelectBox, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['hidden'] = _dummyCheckbutton(self, 'hidden')
        self.subwidget_list['types'] = _dummyComboBox(self, 'types')
        self.subwidget_list['dir'] = _dummyComboBox(self, 'dir')
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['file'] = _dummyComboBox(self, 'file')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')

klasa _dummyFileSelectBox(FileSelectBox, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')
        self.subwidget_list['filter'] = _dummyComboBox(self, 'filter')
        self.subwidget_list['selection'] = _dummyComboBox(self, 'selection')

klasa _dummyFileComboBox(ComboBox, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dircbx'] = _dummyComboBox(self, 'dircbx')

klasa _dummyStdButtonBox(StdButtonBox, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['apply'] = _dummyButton(self, 'apply')
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['help'] = _dummyButton(self, 'help')

klasa _dummyNoteBookFrame(NoteBookFrame, TixSubWidget):
    def __init__(self, master, name, destroy_physically=0):
        TixSubWidget.__init__(self, master, name, destroy_physically)

klasa _dummyPanedWindow(PanedWindow, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

########################
### Utility Routines ###
########################

#mike Should tixDestroy be exposed jako a wrapper? - but nie dla widgets.

def OptionName(widget):
    '''Returns the qualified path name dla the widget. Normally used to set
    default options dla subwidgets. See tixwidgets.py'''
    zwróć widget.tk.call('tixOptionName', widget._w)

# Called przy a dictionary argument of the form
# {'*.c':'C source files', '*.txt':'Text Files', '*':'All files'}
# returns a string which can be used to configure the fsbox file types
# w an ExFileSelectBox. i.e.,
# '{{*} {* - All files}} {{*.c} {*.c - C source files}} {{*.txt} {*.txt - Text Files}}'
def FileTypeList(dict):
    s = ''
    dla type w dict.keys():
        s = s + '{{' + type + '} {' + type + ' - ' + dict[type] + '}} '
    zwróć s

# Still to be done:
# tixIconView
klasa CObjView(TixWidget):
    """This file implements the Canvas Object View widget. This jest a base
    klasa of IconView. It implements automatic placement/adjustment of the
    scrollbars according to the canvas objects inside the canvas subwidget.
    The scrollbars are adjusted so that the canvas jest just large enough
    to see all the objects.
    """
    # FIXME: It should inherit -superclass tixScrolledWidget
    dalej


klasa Grid(TixWidget, XView, YView):
    '''The Tix Grid command creates a new window  oraz makes it into a
    tixGrid widget. Additional options, may be specified on the command
    line albo w the option database to configure aspects such jako its cursor
    oraz relief.

    A Grid widget displays its contents w a two dimensional grid of cells.
    Each cell may contain one Tix display item, which may be w text,
    graphics albo other formats. See the DisplayStyle klasa dla more information
    about Tix display items. Individual cells, albo groups of cells, can be
    formatted przy a wide range of attributes, such jako its color, relief oraz
    border.

    Subwidgets - Nic'''
    # valid specific resources jako of Tk 8.4
    # editdonecmd, editnotifycmd, floatingcols, floatingrows, formatcmd,
    # highlightbackground, highlightcolor, leftmargin, itemtype, selectmode,
    # selectunit, topmargin,
    def __init__(self, master=Nic, cnf={}, **kw):
        static= []
        self.cnf= cnf
        TixWidget.__init__(self, master, 'tixGrid', static, cnf, kw)

    # valid options jako of Tk 8.4
    # anchor, bdtype, cget, configure, delete, dragsite, dropsite, entrycget,
    # edit, entryconfigure, format, geometryinfo, info, index, move, nearest,
    # selection, set, size, unset, xview, yview
    def anchor_clear(self):
        """Removes the selection anchor."""
        self.tk.call(self, 'anchor', 'clear')

    def anchor_get(self):
        "Get the (x,y) coordinate of the current anchor cell"
        zwróć self._getints(self.tk.call(self, 'anchor', 'get'))

    def anchor_set(self, x, y):
        """Set the selection anchor to the cell at (x, y)."""
        self.tk.call(self, 'anchor', 'set', x, y)

    def delete_row(self, from_, to=Nic):
        """Delete rows between from_ oraz to inclusive.
        If to jest nie provided,  delete only row at from_"""
        jeżeli to jest Nic:
            self.tk.call(self, 'delete', 'row', from_)
        inaczej:
            self.tk.call(self, 'delete', 'row', from_, to)

    def delete_column(self, from_, to=Nic):
        """Delete columns between from_ oraz to inclusive.
        If to jest nie provided,  delete only column at from_"""
        jeżeli to jest Nic:
            self.tk.call(self, 'delete', 'column', from_)
        inaczej:
            self.tk.call(self, 'delete', 'column', from_, to)

    def edit_apply(self):
        """If any cell jest being edited, de-highlight the cell  oraz  applies
        the changes."""
        self.tk.call(self, 'edit', 'apply')

    def edit_set(self, x, y):
        """Highlights  the  cell  at  (x, y) dla editing, jeżeli the -editnotify
        command returns Prawda dla this cell."""
        self.tk.call(self, 'edit', 'set', x, y)

    def entrycget(self, x, y, option):
        "Get the option value dla cell at (x,y)"
        jeżeli option oraz option[0] != '-':
            option = '-' + option
        zwróć self.tk.call(self, 'entrycget', x, y, option)

    def entryconfigure(self, x, y, cnf=Nic, **kw):
        zwróć self._configure(('entryconfigure', x, y), cnf, kw)

    # def format
    # def index

    def info_exists(self, x, y):
        "Return Prawda jeżeli display item exists at (x,y)"
        zwróć self._getboolean(self.tk.call(self, 'info', 'exists', x, y))

    def info_bbox(self, x, y):
        # This seems to always zwróć '', at least dla 'text' displayitems
        zwróć self.tk.call(self, 'info', 'bbox', x, y)

    def move_column(self, from_, to, offset):
        """Moves the range of columns z position FROM through TO by
        the distance indicated by OFFSET. For example, move_column(2, 4, 1)
        moves the columns 2,3,4 to columns 3,4,5."""
        self.tk.call(self, 'move', 'column', from_, to, offset)

    def move_row(self, from_, to, offset):
        """Moves the range of rows z position FROM through TO by
        the distance indicated by OFFSET.
        For example, move_row(2, 4, 1) moves the rows 2,3,4 to rows 3,4,5."""
        self.tk.call(self, 'move', 'row', from_, to, offset)

    def nearest(self, x, y):
        "Return coordinate of cell nearest pixel coordinate (x,y)"
        zwróć self._getints(self.tk.call(self, 'nearest', x, y))

    # def selection adjust
    # def selection clear
    # def selection includes
    # def selection set
    # def selection toggle

    def set(self, x, y, itemtype=Nic, **kw):
        args= self._options(self.cnf, kw)
        jeżeli itemtype jest nie Nic:
            args= ('-itemtype', itemtype) + args
        self.tk.call(self, 'set', x, y, *args)

    def size_column(self, index, **kw):
        """Queries albo sets the size of the column given by
        INDEX.  INDEX may be any non-negative
        integer that gives the position of a given column.
        INDEX can also be the string "default"; w this case, this command
        queries albo sets the default size of all columns.
        When no option-value pair jest given, this command returns a tuple
        containing the current size setting of the given column.  When
        option-value pairs are given, the corresponding options of the
        size setting of the given column are changed. Options may be one
        of the follwing:
              pad0 pixels
                     Specifies the paddings to the left of a column.
              pad1 pixels
                     Specifies the paddings to the right of a column.
              size val
                     Specifies the width of a column.  Val may be:
                     "auto" -- the width of the column jest set to the
                     width of the widest cell w the column;
                     a valid Tk screen distance unit;
                     albo a real number following by the word chars
                     (e.g. 3.4chars) that sets the width of the column to the
                     given number of characters."""
        zwróć self.tk.split(self.tk.call(self._w, 'size', 'column', index,
                             *self._options({}, kw)))

    def size_row(self, index, **kw):
        """Queries albo sets the size of the row given by
        INDEX. INDEX may be any non-negative
        integer that gives the position of a given row .
        INDEX can also be the string "default"; w this case, this command
        queries albo sets the default size of all rows.
        When no option-value pair jest given, this command returns a list con-
        taining the current size setting of the given row . When option-value
        pairs are given, the corresponding options of the size setting of the
        given row are changed. Options may be one of the follwing:
              pad0 pixels
                     Specifies the paddings to the top of a row.
              pad1 pixels
                     Specifies the paddings to the bottom of a row.
              size val
                     Specifies the height of a row.  Val may be:
                     "auto" -- the height of the row jest set to the
                     height of the highest cell w the row;
                     a valid Tk screen distance unit;
                     albo a real number following by the word chars
                     (e.g. 3.4chars) that sets the height of the row to the
                     given number of characters."""
        zwróć self.tk.split(self.tk.call(
                    self, 'size', 'row', index, *self._options({}, kw)))

    def unset(self, x, y):
        """Clears the cell at (x, y) by removing its display item."""
        self.tk.call(self._w, 'unset', x, y)


klasa ScrolledGrid(Grid):
    '''Scrolled Grid widgets'''

    # FIXME: It should inherit -superclass tixScrolledWidget
    def __init__(self, master=Nic, cnf={}, **kw):
        static= []
        self.cnf= cnf
        TixWidget.__init__(self, master, 'tixScrolledGrid', static, cnf, kw)
