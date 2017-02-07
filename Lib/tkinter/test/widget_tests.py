# Common tests dla test_tkinter/test_widgets.py oraz test_ttk/test_widgets.py

zaimportuj unittest
zaimportuj sys
zaimportuj tkinter
z tkinter.ttk zaimportuj Scale
z tkinter.test.support zaimportuj (AbstractTkTest, tcl_version, requires_tcl,
                                  get_tk_patchlevel, pixels_conv, tcl_obj_eq)
zaimportuj test.support


noconv = Nieprawda
jeżeli get_tk_patchlevel() < (8, 5, 11):
    noconv = str

pixels_round = round
jeżeli get_tk_patchlevel()[:3] == (8, 5, 11):
    # Issue #19085: Workaround a bug w Tk
    # http://core.tcl.tk/tk/info/3497848
    pixels_round = int


_sentinel = object()

klasa AbstractWidgetTest(AbstractTkTest):
    _conv_pixels = staticmethod(pixels_round)
    _conv_pad_pixels = Nic
    _stringify = Nieprawda

    @property
    def scaling(self):
        spróbuj:
            zwróć self._scaling
        wyjąwszy AttributeError:
            self._scaling = float(self.root.call('tk', 'scaling'))
            zwróć self._scaling

    def _str(self, value):
        jeżeli nie self._stringify oraz self.wantobjects oraz tcl_version >= (8, 6):
            zwróć value
        jeżeli isinstance(value, tuple):
            zwróć ' '.join(map(self._str, value))
        zwróć str(value)

    def assertEqual2(self, actual, expected, msg=Nic, eq=object.__eq__):
        jeżeli eq(actual, expected):
            zwróć
        self.assertEqual(actual, expected, msg)

    def checkParam(self, widget, name, value, *, expected=_sentinel,
                   conv=Nieprawda, eq=Nic):
        widget[name] = value
        jeżeli expected jest _sentinel:
            expected = value
        jeżeli conv:
            expected = conv(expected)
        jeżeli self._stringify albo nie self.wantobjects:
            jeżeli isinstance(expected, tuple):
                expected = tkinter._join(expected)
            inaczej:
                expected = str(expected)
        jeżeli eq jest Nic:
            eq = tcl_obj_eq
        self.assertEqual2(widget[name], expected, eq=eq)
        self.assertEqual2(widget.cget(name), expected, eq=eq)
        # XXX
        jeżeli nie isinstance(widget, Scale):
            t = widget.configure(name)
            self.assertEqual(len(t), 5)
            self.assertEqual2(t[4], expected, eq=eq)

    def checkInvalidParam(self, widget, name, value, errmsg=Nic, *,
                          keep_orig=Prawda):
        orig = widget[name]
        jeżeli errmsg jest nie Nic:
            errmsg = errmsg.format(value)
        przy self.assertRaises(tkinter.TclError) jako cm:
            widget[name] = value
        jeżeli errmsg jest nie Nic:
            self.assertEqual(str(cm.exception), errmsg)
        jeżeli keep_orig:
            self.assertEqual(widget[name], orig)
        inaczej:
            widget[name] = orig
        przy self.assertRaises(tkinter.TclError) jako cm:
            widget.configure({name: value})
        jeżeli errmsg jest nie Nic:
            self.assertEqual(str(cm.exception), errmsg)
        jeżeli keep_orig:
            self.assertEqual(widget[name], orig)
        inaczej:
            widget[name] = orig

    def checkParams(self, widget, name, *values, **kwargs):
        dla value w values:
            self.checkParam(widget, name, value, **kwargs)

    def checkIntegerParam(self, widget, name, *values, **kwargs):
        self.checkParams(widget, name, *values, **kwargs)
        self.checkInvalidParam(widget, name, '',
                errmsg='expected integer but got ""')
        self.checkInvalidParam(widget, name, '10p',
                errmsg='expected integer but got "10p"')
        self.checkInvalidParam(widget, name, 3.2,
                errmsg='expected integer but got "3.2"')

    def checkFloatParam(self, widget, name, *values, conv=float, **kwargs):
        dla value w values:
            self.checkParam(widget, name, value, conv=conv, **kwargs)
        self.checkInvalidParam(widget, name, '',
                errmsg='expected floating-point number but got ""')
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='expected floating-point number but got "spam"')

    def checkBooleanParam(self, widget, name):
        dla value w (Nieprawda, 0, 'false', 'no', 'off'):
            self.checkParam(widget, name, value, expected=0)
        dla value w (Prawda, 1, 'true', 'yes', 'on'):
            self.checkParam(widget, name, value, expected=1)
        self.checkInvalidParam(widget, name, '',
                errmsg='expected boolean value but got ""')
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='expected boolean value but got "spam"')

    def checkColorParam(self, widget, name, *, allow_empty=Nic, **kwargs):
        self.checkParams(widget, name,
                         '#ff0000', '#00ff00', '#0000ff', '#123456',
                         'red', 'green', 'blue', 'white', 'black', 'grey',
                         **kwargs)
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='unknown color name "spam"')

    def checkCursorParam(self, widget, name, **kwargs):
        self.checkParams(widget, name, 'arrow', 'watch', 'cross', '',**kwargs)
        jeżeli tcl_version >= (8, 5):
            self.checkParam(widget, name, 'none')
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='bad cursor spec "spam"')

    def checkCommandParam(self, widget, name):
        def command(*args):
            dalej
        widget[name] = command
        self.assertPrawda(widget[name])
        self.checkParams(widget, name, '')

    def checkEnumParam(self, widget, name, *values, errmsg=Nic, **kwargs):
        self.checkParams(widget, name, *values, **kwargs)
        jeżeli errmsg jest Nic:
            errmsg2 = ' %s "{}": must be %s%s albo %s' % (
                    name,
                    ', '.join(values[:-1]),
                    ',' jeżeli len(values) > 2 inaczej '',
                    values[-1])
            self.checkInvalidParam(widget, name, '',
                                   errmsg='ambiguous' + errmsg2)
            errmsg = 'bad' + errmsg2
        self.checkInvalidParam(widget, name, 'spam', errmsg=errmsg)

    def checkPixelsParam(self, widget, name, *values,
                         conv=Nic, keep_orig=Prawda, **kwargs):
        jeżeli conv jest Nic:
            conv = self._conv_pixels
        dla value w values:
            expected = _sentinel
            conv1 = conv
            jeżeli isinstance(value, str):
                jeżeli conv1 oraz conv1 jest nie str:
                    expected = pixels_conv(value) * self.scaling
                    conv1 = round
            self.checkParam(widget, name, value, expected=expected,
                            conv=conv1, **kwargs)
        self.checkInvalidParam(widget, name, '6x',
                errmsg='bad screen distance "6x"', keep_orig=keep_orig)
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='bad screen distance "spam"', keep_orig=keep_orig)

    def checkReliefParam(self, widget, name):
        self.checkParams(widget, name,
                         'flat', 'groove', 'raised', 'ridge', 'solid', 'sunken')
        errmsg='bad relief "spam": must be '\
               'flat, groove, podnieśd, ridge, solid, albo sunken'
        jeżeli tcl_version < (8, 6):
            errmsg = Nic
        self.checkInvalidParam(widget, name, 'spam',
                errmsg=errmsg)

    def checkImageParam(self, widget, name):
        image = tkinter.PhotoImage(master=self.root, name='image1')
        self.checkParam(widget, name, image, conv=str)
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='image "spam" doesn\'t exist')
        widget[name] = ''

    def checkVariableParam(self, widget, name, var):
        self.checkParam(widget, name, var, conv=str)

    def assertIsBoundingBox(self, bbox):
        self.assertIsNotNic(bbox)
        self.assertIsInstance(bbox, tuple)
        jeżeli len(bbox) != 4:
            self.fail('Invalid bounding box: %r' % (bbox,))
        dla item w bbox:
            jeżeli nie isinstance(item, int):
                self.fail('Invalid bounding box: %r' % (bbox,))
                przerwij


klasa StandardOptionsTests:
    STANDARD_OPTIONS = (
        'activebackground', 'activeborderwidth', 'activeforeground', 'anchor',
        'background', 'bitmap', 'borderwidth', 'compound', 'cursor',
        'disabledforeground', 'exportselection', 'font', 'foreground',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'image', 'insertbackground', 'insertborderwidth',
        'insertofftime', 'insertontime', 'insertwidth',
        'jump', 'justify', 'orient', 'padx', 'pady', 'relief',
        'repeatdelay', 'repeatinterval',
        'selectbackground', 'selectborderwidth', 'selectforeground',
        'setgrid', 'takefocus', 'text', 'textvariable', 'troughcolor',
        'underline', 'wraplength', 'xscrollcommand', 'yscrollcommand',
    )

    def test_activebackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'activebackground')

    def test_activeborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'activeborderwidth',
                              0, 1.3, 2.9, 6, -2, '10p')

    def test_activeforeground(self):
        widget = self.create()
        self.checkColorParam(widget, 'activeforeground')

    def test_anchor(self):
        widget = self.create()
        self.checkEnumParam(widget, 'anchor',
                'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center')

    def test_background(self):
        widget = self.create()
        self.checkColorParam(widget, 'background')
        jeżeli 'bg' w self.OPTIONS:
            self.checkColorParam(widget, 'bg')

    def test_bitmap(self):
        widget = self.create()
        self.checkParam(widget, 'bitmap', 'questhead')
        self.checkParam(widget, 'bitmap', 'gray50')
        filename = test.support.findfile('python.xbm', subdir='imghdrdata')
        self.checkParam(widget, 'bitmap', '@' + filename)
        # Cocoa Tk widgets don't detect invalid -bitmap values
        # See https://core.tcl.tk/tk/info/31cd33dbf0
        jeżeli nie ('aqua' w self.root.tk.call('tk', 'windowingsystem') oraz
                'AppKit' w self.root.winfo_server()):
            self.checkInvalidParam(widget, 'bitmap', 'spam',
                    errmsg='bitmap "spam" nie defined')

    def test_borderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'borderwidth',
                              0, 1.3, 2.6, 6, -2, '10p')
        jeżeli 'bd' w self.OPTIONS:
            self.checkPixelsParam(widget, 'bd', 0, 1.3, 2.6, 6, -2, '10p')

    def test_compound(self):
        widget = self.create()
        self.checkEnumParam(widget, 'compound',
                'bottom', 'center', 'left', 'none', 'right', 'top')

    def test_cursor(self):
        widget = self.create()
        self.checkCursorParam(widget, 'cursor')

    def test_disabledforeground(self):
        widget = self.create()
        self.checkColorParam(widget, 'disabledforeground')

    def test_exportselection(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'exportselection')

    def test_font(self):
        widget = self.create()
        self.checkParam(widget, 'font',
                        '-Adobe-Helvetica-Medium-R-Normal--*-120-*-*-*-*-*-*')
        self.checkInvalidParam(widget, 'font', '',
                               errmsg='font "" doesn\'t exist')

    def test_foreground(self):
        widget = self.create()
        self.checkColorParam(widget, 'foreground')
        jeżeli 'fg' w self.OPTIONS:
            self.checkColorParam(widget, 'fg')

    def test_highlightbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'highlightbackground')

    def test_highlightcolor(self):
        widget = self.create()
        self.checkColorParam(widget, 'highlightcolor')

    def test_highlightthickness(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'highlightthickness',
                              0, 1.3, 2.6, 6, '10p')
        self.checkParam(widget, 'highlightthickness', -2, expected=0,
                        conv=self._conv_pixels)

    @unittest.skipIf(sys.platform == 'darwin',
                     'crashes przy Cocoa Tk (issue19733)')
    def test_image(self):
        widget = self.create()
        self.checkImageParam(widget, 'image')

    def test_insertbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'insertbackground')

    def test_insertborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'insertborderwidth',
                              0, 1.3, 2.6, 6, -2, '10p')

    def test_insertofftime(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'insertofftime', 100)

    def test_insertontime(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'insertontime', 100)

    def test_insertwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'insertwidth', 1.3, 2.6, -2, '10p')

    def test_jump(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'jump')

    def test_justify(self):
        widget = self.create()
        self.checkEnumParam(widget, 'justify', 'left', 'right', 'center',
                errmsg='bad justification "{}": must be '
                       'left, right, albo center')
        self.checkInvalidParam(widget, 'justify', '',
                errmsg='ambiguous justification "": must be '
                       'left, right, albo center')

    def test_orient(self):
        widget = self.create()
        self.assertEqual(str(widget['orient']), self.default_orient)
        self.checkEnumParam(widget, 'orient', 'horizontal', 'vertical')

    def test_padx(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'padx', 3, 4.4, 5.6, -2, '12m',
                              conv=self._conv_pad_pixels)

    def test_pady(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'pady', 3, 4.4, 5.6, -2, '12m',
                              conv=self._conv_pad_pixels)

    def test_relief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'relief')

    def test_repeatdelay(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'repeatdelay', -500, 500)

    def test_repeatinterval(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'repeatinterval', -500, 500)

    def test_selectbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'selectbackground')

    def test_selectborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'selectborderwidth', 1.3, 2.6, -2, '10p')

    def test_selectforeground(self):
        widget = self.create()
        self.checkColorParam(widget, 'selectforeground')

    def test_setgrid(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'setgrid')

    def test_state(self):
        widget = self.create()
        self.checkEnumParam(widget, 'state', 'active', 'disabled', 'normal')

    def test_takefocus(self):
        widget = self.create()
        self.checkParams(widget, 'takefocus', '0', '1', '')

    def test_text(self):
        widget = self.create()
        self.checkParams(widget, 'text', '', 'any string')

    def test_textvariable(self):
        widget = self.create()
        var = tkinter.StringVar(self.root)
        self.checkVariableParam(widget, 'textvariable', var)

    def test_troughcolor(self):
        widget = self.create()
        self.checkColorParam(widget, 'troughcolor')

    def test_underline(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'underline', 0, 1, 10)

    def test_wraplength(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'wraplength', 100)

    def test_xscrollcommand(self):
        widget = self.create()
        self.checkCommandParam(widget, 'xscrollcommand')

    def test_yscrollcommand(self):
        widget = self.create()
        self.checkCommandParam(widget, 'yscrollcommand')

    # non-standard but common options

    def test_command(self):
        widget = self.create()
        self.checkCommandParam(widget, 'command')

    def test_indicatoron(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'indicatoron')

    def test_offrelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'offrelief')

    def test_overrelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'overrelief')

    def test_selectcolor(self):
        widget = self.create()
        self.checkColorParam(widget, 'selectcolor')

    def test_selectimage(self):
        widget = self.create()
        self.checkImageParam(widget, 'selectimage')

    @requires_tcl(8, 5)
    def test_tristateimage(self):
        widget = self.create()
        self.checkImageParam(widget, 'tristateimage')

    @requires_tcl(8, 5)
    def test_tristatevalue(self):
        widget = self.create()
        self.checkParam(widget, 'tristatevalue', 'unknowable')

    def test_variable(self):
        widget = self.create()
        var = tkinter.DoubleVar(self.root)
        self.checkVariableParam(widget, 'variable', var)


klasa IntegerSizeTests:
    def test_height(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'height', 100, -100, 0)

    def test_width(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'width', 402, -402, 0)


klasa PixelSizeTests:
    def test_height(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'height', 100, 101.2, 102.6, -100, 0, '3c')

    def test_width(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'width', 402, 403.4, 404.6, -402, 0, '5i')


def add_standard_options(*source_classes):
    # This decorator adds test_xxx methods z source classes dla every xxx
    # option w the OPTIONS klasa attribute jeżeli they are nie defined explicitly.
    def decorator(cls):
        dla option w cls.OPTIONS:
            methodname = 'test_' + option
            jeżeli nie hasattr(cls, methodname):
                dla source_class w source_classes:
                    jeżeli hasattr(source_class, methodname):
                        setattr(cls, methodname,
                                getattr(source_class, methodname))
                        przerwij
                inaczej:
                    def test(self, option=option):
                        widget = self.create()
                        widget[option]
                        podnieś AssertionError('Option "%s" jest nie tested w %s' %
                                             (option, cls.__name__))
                    test.__name__ = methodname
                    setattr(cls, methodname, test)
        zwróć cls
    zwróć decorator

def setUpModule():
    jeżeli test.support.verbose:
        tcl = tkinter.Tcl()
        print('patchlevel =', tcl.call('info', 'patchlevel'))
