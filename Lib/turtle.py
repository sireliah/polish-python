#
# turtle.py: a Tkinter based turtle graphics module dla Python
# Version 1.1b - 4. 5. 2009
#
# Copyright (C) 2006 - 2010  Gregor Lingl
# email: glingl@aon.at
#
# This software jest provided 'as-is', without any express albo implied
# warranty.  In no event will the authors be held liable dla any damages
# arising z the use of this software.
#
# Permission jest granted to anyone to use this software dla any purpose,
# including commercial applications, oraz to alter it oraz redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must nie be misrepresented; you must nie
#    claim that you wrote the original software. If you use this software
#    w a product, an acknowledgment w the product documentation would be
#    appreciated but jest nie required.
# 2. Altered source versions must be plainly marked jako such, oraz must nie be
#    misrepresented jako being the original software.
# 3. This notice may nie be removed albo altered z any source distribution.


"""
Turtle graphics jest a popular way dla introducing programming to
kids. It was part of the original Logo programming language developed
by Wally Feurzig oraz Seymour Papert w 1966.

Imagine a robotic turtle starting at (0, 0) w the x-y plane. After an ``zaimportuj turtle``, give it
the command turtle.forward(15), oraz it moves (on-screen!) 15 pixels w
the direction it jest facing, drawing a line jako it moves. Give it the
command turtle.right(25), oraz it rotates in-place 25 degrees clockwise.

By combining together these oraz similar commands, intricate shapes oraz
pictures can easily be drawn.

----- turtle.py

This module jest an extended reimplementation of turtle.py z the
Python standard distribution up to Python 2.5. (See: http://www.python.org)

It tries to keep the merits of turtle.py oraz to be (nearly) 100%
compatible przy it. This means w the first place to enable the
learning programmer to use all the commands, classes oraz methods
interactively when using the module z within IDLE run with
the -n switch.

Roughly it has the following features added:

- Better animation of the turtle movements, especially of turning the
  turtle. So the turtles can more easily be used jako a visual feedback
  instrument by the (beginning) programmer.

- Different turtle shapes, gif-images jako turtle shapes, user defined
  oraz user controllable turtle shapes, among them compound
  (multicolored) shapes. Turtle shapes can be stretched oraz tilted, which
  makes turtles very versatile geometrical objects.

- Fine control over turtle movement oraz screen updates via delay(),
  oraz enhanced tracer() oraz speed() methods.

- Aliases dla the most commonly used commands, like fd dla forward etc.,
  following the early Logo traditions. This reduces the boring work of
  typing long sequences of commands, which often occur w a natural way
  when kids try to program fancy pictures on their first encounter with
  turtle graphics.

- Turtles now have an undo()-method przy configurable undo-buffer.

- Some simple commands/methods dla creating event driven programs
  (mouse-, key-, timer-events). Especially useful dla programming games.

- A scrollable Canvas class. The default scrollable Canvas can be
  extended interactively jako needed dopóki playing around przy the turtle(s).

- A TurtleScreen klasa przy methods controlling background color albo
  background image, window oraz canvas size oraz other properties of the
  TurtleScreen.

- There jest a method, setworldcoordinates(), to install a user defined
  coordinate-system dla the TurtleScreen.

- The implementation uses a 2-vector klasa named Vec2D, derived z tuple.
  This klasa jest public, so it can be imported by the application programmer,
  which makes certain types of computations very natural oraz compact.

- Appearance of the TurtleScreen oraz the Turtles at startup/zaimportuj can be
  configured by means of a turtle.cfg configuration file.
  The default configuration mimics the appearance of the old turtle module.

- If configured appropriately the module reads w docstrings z a docstring
  dictionary w some different language, supplied separately  oraz replaces
  the English ones by those read in. There jest a utility function
  write_docstringdict() to write a dictionary przy the original (English)
  docstrings to disc, so it can serve jako a template dla translations.

Behind the scenes there are some features included przy possible
extensions w mind. These will be commented oraz documented inaczejwhere.

"""

_ver = "turtle 1.1b- - dla Python 3.1   -  4. 5. 2009"

# print(_ver)

zaimportuj tkinter jako TK
zaimportuj types
zaimportuj math
zaimportuj time
zaimportuj inspect
zaimportuj sys

z os.path zaimportuj isfile, split, join
z copy zaimportuj deepcopy
z tkinter zaimportuj simpledialog

_tg_classes = ['ScrolledCanvas', 'TurtleScreen', 'Screen',
               'RawTurtle', 'Turtle', 'RawPen', 'Pen', 'Shape', 'Vec2D']
_tg_screen_functions = ['addshape', 'bgcolor', 'bgpic', 'bye',
        'clearscreen', 'colormode', 'delay', 'exitonclick', 'getcanvas',
        'getshapes', 'listen', 'mainloop', 'mode', 'numinput',
        'onkey', 'onkeypress', 'onkeyrelease', 'onscreenclick', 'ontimer',
        'register_shape', 'resetscreen', 'screensize', 'setup',
        'setworldcoordinates', 'textinput', 'title', 'tracer', 'turtles', 'update',
        'window_height', 'window_width']
_tg_turtle_functions = ['back', 'backward', 'begin_fill', 'begin_poly', 'bk',
        'circle', 'clear', 'clearstamp', 'clearstamps', 'clone', 'color',
        'degrees', 'distance', 'dot', 'down', 'end_fill', 'end_poly', 'fd',
        'fillcolor', 'filling', 'forward', 'get_poly', 'getpen', 'getscreen', 'get_shapepoly',
        'getturtle', 'goto', 'heading', 'hideturtle', 'home', 'ht', 'isdown',
        'isvisible', 'left', 'lt', 'onclick', 'ondrag', 'onrelease', 'pd',
        'pen', 'pencolor', 'pendown', 'pensize', 'penup', 'pos', 'position',
        'pu', 'radians', 'right', 'reset', 'resizemode', 'rt',
        'seth', 'setheading', 'setpos', 'setposition', 'settiltangle',
        'setundobuffer', 'setx', 'sety', 'shape', 'shapesize', 'shapetransform', 'shearfactor', 'showturtle',
        'speed', 'st', 'stamp', 'tilt', 'tiltangle', 'towards',
        'turtlesize', 'undo', 'undobufferentries', 'up', 'width',
        'write', 'xcor', 'ycor']
_tg_utilities = ['write_docstringdict', 'done']

__all__ = (_tg_classes + _tg_screen_functions + _tg_turtle_functions +
           _tg_utilities + ['Terminator']) # + _math_functions)

_alias_list = ['addshape', 'backward', 'bk', 'fd', 'ht', 'lt', 'pd', 'pos',
               'pu', 'rt', 'seth', 'setpos', 'setposition', 'st',
               'turtlesize', 'up', 'width']

_CFG = {"width" : 0.5,               # Screen
        "height" : 0.75,
        "canvwidth" : 400,
        "canvheight": 300,
        "leftright": Nic,
        "topbottom": Nic,
        "mode": "standard",          # TurtleScreen
        "colormode": 1.0,
        "delay": 10,
        "undobuffersize": 1000,      # RawTurtle
        "shape": "classic",
        "pencolor" : "black",
        "fillcolor" : "black",
        "resizemode" : "noresize",
        "visible" : Prawda,
        "language": "english",        # docstrings
        "exampleturtle": "turtle",
        "examplescreen": "screen",
        "title": "Python Turtle Graphics",
        "using_IDLE": Nieprawda
       }

def config_dict(filename):
    """Convert content of config-file into dictionary."""
    przy open(filename, "r") jako f:
        cfglines = f.readlines()
    cfgdict = {}
    dla line w cfglines:
        line = line.strip()
        jeżeli nie line albo line.startswith("#"):
            kontynuuj
        spróbuj:
            key, value = line.split("=")
        wyjąwszy:
            print("Bad line w config-file %s:\n%s" % (filename,line))
            kontynuuj
        key = key.strip()
        value = value.strip()
        jeżeli value w ["Prawda", "Nieprawda", "Nic", "''", '""']:
            value = eval(value)
        inaczej:
            spróbuj:
                jeżeli "." w value:
                    value = float(value)
                inaczej:
                    value = int(value)
            wyjąwszy:
                dalej # value need nie be converted
        cfgdict[key] = value
    zwróć cfgdict

def readconfig(cfgdict):
    """Read config-files, change configuration-dict accordingly.

    If there jest a turtle.cfg file w the current working directory,
    read it z there. If this contains an importconfig-value,
    say 'myway', construct filename turtle_mayway.cfg inaczej use
    turtle.cfg oraz read it z the import-directory, where
    turtle.py jest located.
    Update configuration dictionary first according to config-file,
    w the zaimportuj directory, then according to config-file w the
    current working directory.
    If no config-file jest found, the default configuration jest used.
    """
    default_cfg = "turtle.cfg"
    cfgdict1 = {}
    cfgdict2 = {}
    jeżeli isfile(default_cfg):
        cfgdict1 = config_dict(default_cfg)
    jeżeli "importconfig" w cfgdict1:
        default_cfg = "turtle_%s.cfg" % cfgdict1["importconfig"]
    spróbuj:
        head, tail = split(__file__)
        cfg_file2 = join(head, default_cfg)
    wyjąwszy:
        cfg_file2 = ""
    jeżeli isfile(cfg_file2):
        cfgdict2 = config_dict(cfg_file2)
    _CFG.update(cfgdict2)
    _CFG.update(cfgdict1)

spróbuj:
    readconfig(_CFG)
wyjąwszy:
    print ("No configfile read, reason unknown")


klasa Vec2D(tuple):
    """A 2 dimensional vector class, used jako a helper class
    dla implementing turtle graphics.
    May be useful dla turtle graphics programs also.
    Derived z tuple, so a vector jest a tuple!

    Provides (dla a, b vectors, k number):
       a+b vector addition
       a-b vector subtraction
       a*b inner product
       k*a oraz a*k multiplication przy scalar
       |a| absolute value of a
       a.rotate(angle) rotation
    """
    def __new__(cls, x, y):
        zwróć tuple.__new__(cls, (x, y))
    def __add__(self, other):
        zwróć Vec2D(self[0]+other[0], self[1]+other[1])
    def __mul__(self, other):
        jeżeli isinstance(other, Vec2D):
            zwróć self[0]*other[0]+self[1]*other[1]
        zwróć Vec2D(self[0]*other, self[1]*other)
    def __rmul__(self, other):
        jeżeli isinstance(other, int) albo isinstance(other, float):
            zwróć Vec2D(self[0]*other, self[1]*other)
    def __sub__(self, other):
        zwróć Vec2D(self[0]-other[0], self[1]-other[1])
    def __neg__(self):
        zwróć Vec2D(-self[0], -self[1])
    def __abs__(self):
        zwróć (self[0]**2 + self[1]**2)**0.5
    def rotate(self, angle):
        """rotate self counterclockwise by angle
        """
        perp = Vec2D(-self[1], self[0])
        angle = angle * math.pi / 180.0
        c, s = math.cos(angle), math.sin(angle)
        zwróć Vec2D(self[0]*c+perp[0]*s, self[1]*c+perp[1]*s)
    def __getnewargs__(self):
        zwróć (self[0], self[1])
    def __repr__(self):
        zwróć "(%.2f,%.2f)" % self


##############################################################################
### From here up to line    : Tkinter - Interface dla turtle.py            ###
### May be replaced by an interface to some different graphics toolkit     ###
##############################################################################

## helper functions dla Scrolled Canvas, to forward Canvas-methods
## to ScrolledCanvas class

def __methodDict(cls, _dict):
    """helper function dla Scrolled Canvas"""
    baseList = list(cls.__bases__)
    baseList.reverse()
    dla _super w baseList:
        __methodDict(_super, _dict)
    dla key, value w cls.__dict__.items():
        jeżeli type(value) == types.FunctionType:
            _dict[key] = value

def __methods(cls):
    """helper function dla Scrolled Canvas"""
    _dict = {}
    __methodDict(cls, _dict)
    zwróć _dict.keys()

__stringBody = (
    'def %(method)s(self, *args, **kw): zwróć ' +
    'self.%(attribute)s.%(method)s(*args, **kw)')

def __forwardmethods(fromClass, toClass, toPart, exclude = ()):
    ### MANY CHANGES ###
    _dict_1 = {}
    __methodDict(toClass, _dict_1)
    _dict = {}
    mfc = __methods(fromClass)
    dla ex w _dict_1.keys():
        jeżeli ex[:1] == '_' albo ex[-1:] == '_' albo ex w exclude albo ex w mfc:
            dalej
        inaczej:
            _dict[ex] = _dict_1[ex]

    dla method, func w _dict.items():
        d = {'method': method, 'func': func}
        jeżeli isinstance(toPart, str):
            execString = \
                __stringBody % {'method' : method, 'attribute' : toPart}
        exec(execString, d)
        setattr(fromClass, method, d[method])   ### NEWU!


klasa ScrolledCanvas(TK.Frame):
    """Modeled after the scrolled canvas klasa z Grayons's Tkinter book.

    Used jako the default canvas, which pops up automatically when
    using turtle graphics functions albo the Turtle class.
    """
    def __init__(self, master, width=500, height=350,
                                          canvwidth=600, canvheight=500):
        TK.Frame.__init__(self, master, width=width, height=height)
        self._rootwindow = self.winfo_toplevel()
        self.width, self.height = width, height
        self.canvwidth, self.canvheight = canvwidth, canvheight
        self.bg = "white"
        self._canvas = TK.Canvas(master, width=width, height=height,
                                 bg=self.bg, relief=TK.SUNKEN, borderwidth=2)
        self.hscroll = TK.Scrollbar(master, command=self._canvas.xview,
                                    orient=TK.HORIZONTAL)
        self.vscroll = TK.Scrollbar(master, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=self.hscroll.set,
                               yscrollcommand=self.vscroll.set)
        self.rowconfigure(0, weight=1, minsize=0)
        self.columnconfigure(0, weight=1, minsize=0)
        self._canvas.grid(padx=1, in_ = self, pady=1, row=0,
                column=0, rowspan=1, columnspan=1, sticky='news')
        self.vscroll.grid(padx=1, in_ = self, pady=1, row=0,
                column=1, rowspan=1, columnspan=1, sticky='news')
        self.hscroll.grid(padx=1, in_ = self, pady=1, row=1,
                column=0, rowspan=1, columnspan=1, sticky='news')
        self.reset()
        self._rootwindow.bind('<Configure>', self.onResize)

    def reset(self, canvwidth=Nic, canvheight=Nic, bg = Nic):
        """Adjust canvas oraz scrollbars according to given canvas size."""
        jeżeli canvwidth:
            self.canvwidth = canvwidth
        jeżeli canvheight:
            self.canvheight = canvheight
        jeżeli bg:
            self.bg = bg
        self._canvas.config(bg=bg,
                        scrollregion=(-self.canvwidth//2, -self.canvheight//2,
                                       self.canvwidth//2, self.canvheight//2))
        self._canvas.xview_moveto(0.5*(self.canvwidth - self.width + 30) /
                                                               self.canvwidth)
        self._canvas.yview_moveto(0.5*(self.canvheight- self.height + 30) /
                                                              self.canvheight)
        self.adjustScrolls()


    def adjustScrolls(self):
        """ Adjust scrollbars according to window- oraz canvas-size.
        """
        cwidth = self._canvas.winfo_width()
        cheight = self._canvas.winfo_height()
        self._canvas.xview_moveto(0.5*(self.canvwidth-cwidth)/self.canvwidth)
        self._canvas.yview_moveto(0.5*(self.canvheight-cheight)/self.canvheight)
        jeżeli cwidth < self.canvwidth albo cheight < self.canvheight:
            self.hscroll.grid(padx=1, in_ = self, pady=1, row=1,
                              column=0, rowspan=1, columnspan=1, sticky='news')
            self.vscroll.grid(padx=1, in_ = self, pady=1, row=0,
                              column=1, rowspan=1, columnspan=1, sticky='news')
        inaczej:
            self.hscroll.grid_forget()
            self.vscroll.grid_forget()

    def onResize(self, event):
        """self-explanatory"""
        self.adjustScrolls()

    def bbox(self, *args):
        """ 'forward' method, which canvas itself has inherited...
        """
        zwróć self._canvas.bbox(*args)

    def cget(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        zwróć self._canvas.cget(*args, **kwargs)

    def config(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.config(*args, **kwargs)

    def bind(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.bind(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.unbind(*args, **kwargs)

    def focus_force(self):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.focus_force()

__forwardmethods(ScrolledCanvas, TK.Canvas, '_canvas')


klasa _Root(TK.Tk):
    """Root klasa dla Screen based on Tkinter."""
    def __init__(self):
        TK.Tk.__init__(self)

    def setupcanvas(self, width, height, cwidth, cheight):
        self._canvas = ScrolledCanvas(self, width, height, cwidth, cheight)
        self._canvas.pack(expand=1, fill="both")

    def _getcanvas(self):
        zwróć self._canvas

    def set_geometry(self, width, height, startx, starty):
        self.geometry("%dx%d%+d%+d"%(width, height, startx, starty))

    def ondestroy(self, destroy):
        self.wm_protocol("WM_DELETE_WINDOW", destroy)

    def win_width(self):
        zwróć self.winfo_screenwidth()

    def win_height(self):
        zwróć self.winfo_screenheight()

Canvas = TK.Canvas


klasa TurtleScreenBase(object):
    """Provide the basic graphics functionality.
       Interface between Tkinter oraz turtle.py.

       To port turtle.py to some different graphics toolkit
       a corresponding TurtleScreenBase klasa has to be implemented.
    """

    @staticmethod
    def _blankimage():
        """return a blank image object
        """
        img = TK.PhotoImage(width=1, height=1)
        img.blank()
        zwróć img

    @staticmethod
    def _image(filename):
        """return an image object containing the
        imagedata z a gif-file named filename.
        """
        zwróć TK.PhotoImage(file=filename)

    def __init__(self, cv):
        self.cv = cv
        jeżeli isinstance(cv, ScrolledCanvas):
            w = self.cv.canvwidth
            h = self.cv.canvheight
        inaczej:  # expected: ordinary TK.Canvas
            w = int(self.cv.cget("width"))
            h = int(self.cv.cget("height"))
            self.cv.config(scrollregion = (-w//2, -h//2, w//2, h//2 ))
        self.canvwidth = w
        self.canvheight = h
        self.xscale = self.yscale = 1.0

    def _createpoly(self):
        """Create an invisible polygon item on canvas self.cv)
        """
        zwróć self.cv.create_polygon((0, 0, 0, 0, 0, 0), fill="", outline="")

    def _drawpoly(self, polyitem, coordlist, fill=Nic,
                  outline=Nic, width=Nic, top=Nieprawda):
        """Configure polygonitem polyitem according to provided
        arguments:
        coordlist jest sequence of coordinates
        fill jest filling color
        outline jest outline color
        top jest a boolean value, which specifies jeżeli polyitem
        will be put on top of the canvas' displaylist so it
        will nie be covered by other items.
        """
        cl = []
        dla x, y w coordlist:
            cl.append(x * self.xscale)
            cl.append(-y * self.yscale)
        self.cv.coords(polyitem, *cl)
        jeżeli fill jest nie Nic:
            self.cv.itemconfigure(polyitem, fill=fill)
        jeżeli outline jest nie Nic:
            self.cv.itemconfigure(polyitem, outline=outline)
        jeżeli width jest nie Nic:
            self.cv.itemconfigure(polyitem, width=width)
        jeżeli top:
            self.cv.tag_raise(polyitem)

    def _createline(self):
        """Create an invisible line item on canvas self.cv)
        """
        zwróć self.cv.create_line(0, 0, 0, 0, fill="", width=2,
                                   capstyle = TK.ROUND)

    def _drawline(self, lineitem, coordlist=Nic,
                  fill=Nic, width=Nic, top=Nieprawda):
        """Configure lineitem according to provided arguments:
        coordlist jest sequence of coordinates
        fill jest drawing color
        width jest width of drawn line.
        top jest a boolean value, which specifies jeżeli polyitem
        will be put on top of the canvas' displaylist so it
        will nie be covered by other items.
        """
        jeżeli coordlist jest nie Nic:
            cl = []
            dla x, y w coordlist:
                cl.append(x * self.xscale)
                cl.append(-y * self.yscale)
            self.cv.coords(lineitem, *cl)
        jeżeli fill jest nie Nic:
            self.cv.itemconfigure(lineitem, fill=fill)
        jeżeli width jest nie Nic:
            self.cv.itemconfigure(lineitem, width=width)
        jeżeli top:
            self.cv.tag_raise(lineitem)

    def _delete(self, item):
        """Delete graphics item z canvas.
        If item is"all" delete all graphics items.
        """
        self.cv.delete(item)

    def _update(self):
        """Redraw graphics items on canvas
        """
        self.cv.update()

    def _delay(self, delay):
        """Delay subsequent canvas actions dla delay ms."""
        self.cv.after(delay)

    def _iscolorstring(self, color):
        """Check jeżeli the string color jest a legal Tkinter color string.
        """
        spróbuj:
            rgb = self.cv.winfo_rgb(color)
            ok = Prawda
        wyjąwszy TK.TclError:
            ok = Nieprawda
        zwróć ok

    def _bgcolor(self, color=Nic):
        """Set canvas' backgroundcolor jeżeli color jest nie Nic,
        inaczej zwróć backgroundcolor."""
        jeżeli color jest nie Nic:
            self.cv.config(bg = color)
            self._update()
        inaczej:
            zwróć self.cv.cget("bg")

    def _write(self, pos, txt, align, font, pencolor):
        """Write txt at pos w canvas przy specified font
        oraz color.
        Return text item oraz x-coord of right bottom corner
        of text's bounding box."""
        x, y = pos
        x = x * self.xscale
        y = y * self.yscale
        anchor = {"left":"sw", "center":"s", "right":"se" }
        item = self.cv.create_text(x-1, -y, text = txt, anchor = anchor[align],
                                        fill = pencolor, font = font)
        x0, y0, x1, y1 = self.cv.bbox(item)
        self.cv.update()
        zwróć item, x1-1

##    def _dot(self, pos, size, color):
##        """may be implemented dla some other graphics toolkit"""

    def _onclick(self, item, fun, num=1, add=Nic):
        """Bind fun to mouse-click event on turtle.
        fun must be a function przy two arguments, the coordinates
        of the clicked point on the canvas.
        num, the number of the mouse-button defaults to 1
        """
        jeżeli fun jest Nic:
            self.cv.tag_unbind(item, "<Button-%s>" % num)
        inaczej:
            def eventfun(event):
                x, y = (self.cv.canvasx(event.x)/self.xscale,
                        -self.cv.canvasy(event.y)/self.yscale)
                fun(x, y)
            self.cv.tag_bind(item, "<Button-%s>" % num, eventfun, add)

    def _onrelease(self, item, fun, num=1, add=Nic):
        """Bind fun to mouse-button-release event on turtle.
        fun must be a function przy two arguments, the coordinates
        of the point on the canvas where mouse button jest released.
        num, the number of the mouse-button defaults to 1

        If a turtle jest clicked, first _onclick-event will be performed,
        then _onscreensclick-event.
        """
        jeżeli fun jest Nic:
            self.cv.tag_unbind(item, "<Button%s-ButtonRelease>" % num)
        inaczej:
            def eventfun(event):
                x, y = (self.cv.canvasx(event.x)/self.xscale,
                        -self.cv.canvasy(event.y)/self.yscale)
                fun(x, y)
            self.cv.tag_bind(item, "<Button%s-ButtonRelease>" % num,
                             eventfun, add)

    def _ondrag(self, item, fun, num=1, add=Nic):
        """Bind fun to mouse-move-event (przy pressed mouse button) on turtle.
        fun must be a function przy two arguments, the coordinates of the
        actual mouse position on the canvas.
        num, the number of the mouse-button defaults to 1

        Every sequence of mouse-move-events on a turtle jest preceded by a
        mouse-click event on that turtle.
        """
        jeżeli fun jest Nic:
            self.cv.tag_unbind(item, "<Button%s-Motion>" % num)
        inaczej:
            def eventfun(event):
                spróbuj:
                    x, y = (self.cv.canvasx(event.x)/self.xscale,
                           -self.cv.canvasy(event.y)/self.yscale)
                    fun(x, y)
                wyjąwszy:
                    dalej
            self.cv.tag_bind(item, "<Button%s-Motion>" % num, eventfun, add)

    def _onscreenclick(self, fun, num=1, add=Nic):
        """Bind fun to mouse-click event on canvas.
        fun must be a function przy two arguments, the coordinates
        of the clicked point on the canvas.
        num, the number of the mouse-button defaults to 1

        If a turtle jest clicked, first _onclick-event will be performed,
        then _onscreensclick-event.
        """
        jeżeli fun jest Nic:
            self.cv.unbind("<Button-%s>" % num)
        inaczej:
            def eventfun(event):
                x, y = (self.cv.canvasx(event.x)/self.xscale,
                        -self.cv.canvasy(event.y)/self.yscale)
                fun(x, y)
            self.cv.bind("<Button-%s>" % num, eventfun, add)

    def _onkeyrelease(self, fun, key):
        """Bind fun to key-release event of key.
        Canvas must have focus. See method listen
        """
        jeżeli fun jest Nic:
            self.cv.unbind("<KeyRelease-%s>" % key, Nic)
        inaczej:
            def eventfun(event):
                fun()
            self.cv.bind("<KeyRelease-%s>" % key, eventfun)

    def _onkeypress(self, fun, key=Nic):
        """If key jest given, bind fun to key-press event of key.
        Otherwise bind fun to any key-press.
        Canvas must have focus. See method listen.
        """
        jeżeli fun jest Nic:
            jeżeli key jest Nic:
                self.cv.unbind("<KeyPress>", Nic)
            inaczej:
                self.cv.unbind("<KeyPress-%s>" % key, Nic)
        inaczej:
            def eventfun(event):
                fun()
            jeżeli key jest Nic:
                self.cv.bind("<KeyPress>", eventfun)
            inaczej:
                self.cv.bind("<KeyPress-%s>" % key, eventfun)

    def _listen(self):
        """Set focus on canvas (in order to collect key-events)
        """
        self.cv.focus_force()

    def _ontimer(self, fun, t):
        """Install a timer, which calls fun after t milliseconds.
        """
        jeżeli t == 0:
            self.cv.after_idle(fun)
        inaczej:
            self.cv.after(t, fun)

    def _createimage(self, image):
        """Create oraz zwróć image item on canvas.
        """
        zwróć self.cv.create_image(0, 0, image=image)

    def _drawimage(self, item, pos, image):
        """Configure image item jako to draw image object
        at position (x,y) on canvas)
        """
        x, y = pos
        self.cv.coords(item, (x * self.xscale, -y * self.yscale))
        self.cv.itemconfig(item, image=image)

    def _setbgpic(self, item, image):
        """Configure image item jako to draw image object
        at center of canvas. Set item to the first item
        w the displaylist, so it will be drawn below
        any other item ."""
        self.cv.itemconfig(item, image=image)
        self.cv.tag_lower(item)

    def _type(self, item):
        """Return 'line' albo 'polygon' albo 'image' depending on
        type of item.
        """
        zwróć self.cv.type(item)

    def _pointlist(self, item):
        """returns list of coordinate-pairs of points of item
        Example (dla insiders):
        >>> z turtle zaimportuj *
        >>> getscreen()._pointlist(getturtle().turtle._item)
        [(0.0, 9.9999999999999982), (0.0, -9.9999999999999982),
        (9.9999999999999982, 0.0)]
        >>> """
        cl = self.cv.coords(item)
        pl = [(cl[i], -cl[i+1]) dla i w range(0, len(cl), 2)]
        zwróć  pl

    def _setscrollregion(self, srx1, sry1, srx2, sry2):
        self.cv.config(scrollregion=(srx1, sry1, srx2, sry2))

    def _rescale(self, xscalefactor, yscalefactor):
        items = self.cv.find_all()
        dla item w items:
            coordinates = list(self.cv.coords(item))
            newcoordlist = []
            dopóki coordinates:
                x, y = coordinates[:2]
                newcoordlist.append(x * xscalefactor)
                newcoordlist.append(y * yscalefactor)
                coordinates = coordinates[2:]
            self.cv.coords(item, *newcoordlist)

    def _resize(self, canvwidth=Nic, canvheight=Nic, bg=Nic):
        """Resize the canvas the turtles are drawing on. Does
        nie alter the drawing window.
        """
        # needs amendment
        jeżeli nie isinstance(self.cv, ScrolledCanvas):
            zwróć self.canvwidth, self.canvheight
        jeżeli canvwidth jest canvheight jest bg jest Nic:
            zwróć self.cv.canvwidth, self.cv.canvheight
        jeżeli canvwidth jest nie Nic:
            self.canvwidth = canvwidth
        jeżeli canvheight jest nie Nic:
            self.canvheight = canvheight
        self.cv.reset(canvwidth, canvheight, bg)

    def _window_size(self):
        """ Return the width oraz height of the turtle window.
        """
        width = self.cv.winfo_width()
        jeżeli width <= 1:  # the window isn't managed by a geometry manager
            width = self.cv['width']
        height = self.cv.winfo_height()
        jeżeli height <= 1: # the window isn't managed by a geometry manager
            height = self.cv['height']
        zwróć width, height

    def mainloop(self):
        """Starts event loop - calling Tkinter's mainloop function.

        No argument.

        Must be last statement w a turtle graphics program.
        Must NOT be used jeżeli a script jest run z within IDLE w -n mode
        (No subprocess) - dla interactive use of turtle graphics.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.mainloop()

        """
        TK.mainloop()

    def textinput(self, title, prompt):
        """Pop up a dialog window dla input of a string.

        Arguments: title jest the title of the dialog window,
        prompt jest a text mostly describing what information to input.

        Return the string input
        If the dialog jest canceled, zwróć Nic.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.textinput("NIM", "Name of first player:")

        """
        zwróć simpledialog.askstring(title, prompt)

    def numinput(self, title, prompt, default=Nic, minval=Nic, maxval=Nic):
        """Pop up a dialog window dla input of a number.

        Arguments: title jest the title of the dialog window,
        prompt jest a text mostly describing what numerical information to input.
        default: default value
        minval: minimum value dla imput
        maxval: maximum value dla input

        The number input must be w the range minval .. maxval jeżeli these are
        given. If not, a hint jest issued oraz the dialog remains open for
        correction. Return the number input.
        If the dialog jest canceled,  zwróć Nic.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.numinput("Poker", "Your stakes:", 1000, minval=10, maxval=10000)

        """
        zwróć simpledialog.askfloat(title, prompt, initialvalue=default,
                                     minvalue=minval, maxvalue=maxval)


##############################################################################
###                  End of Tkinter - interface                            ###
##############################################################################


klasa Terminator (Exception):
    """Will be podnieśd w TurtleScreen.update, jeżeli _RUNNING becomes Nieprawda.

    This stops execution of a turtle graphics script.
    Main purpose: use w the Demo-Viewer turtle.Demo.py.
    """
    dalej


klasa TurtleGraphicsError(Exception):
    """Some TurtleGraphics Error
    """


klasa Shape(object):
    """Data structure modeling shapes.

    attribute _type jest one of "polygon", "image", "compound"
    attribute _data jest - depending on _type a poygon-tuple,
    an image albo a list constructed using the addcomponent method.
    """
    def __init__(self, type_, data=Nic):
        self._type = type_
        jeżeli type_ == "polygon":
            jeżeli isinstance(data, list):
                data = tuple(data)
        albo_inaczej type_ == "image":
            jeżeli isinstance(data, str):
                jeżeli data.lower().endswith(".gif") oraz isfile(data):
                    data = TurtleScreen._image(data)
                # inaczej data assumed to be Photoimage
        albo_inaczej type_ == "compound":
            data = []
        inaczej:
            podnieś TurtleGraphicsError("There jest no shape type %s" % type_)
        self._data = data

    def addcomponent(self, poly, fill, outline=Nic):
        """Add component to a shape of type compound.

        Arguments: poly jest a polygon, i. e. a tuple of number pairs.
        fill jest the fillcolor of the component,
        outline jest the outline color of the component.

        call (dla a Shapeobject namend s):
        --   s.addcomponent(((0,0), (10,10), (-10,10)), "red", "blue")

        Example:
        >>> poly = ((0,0),(10,-5),(0,10),(-10,-5))
        >>> s = Shape("compound")
        >>> s.addcomponent(poly, "red", "blue")
        >>> # .. add more components oraz then use register_shape()
        """
        jeżeli self._type != "compound":
            podnieś TurtleGraphicsError("Cannot add component to %s Shape"
                                                                % self._type)
        jeżeli outline jest Nic:
            outline = fill
        self._data.append([poly, fill, outline])


klasa Tbuffer(object):
    """Ring buffer used jako undobuffer dla RawTurtle objects."""
    def __init__(self, bufsize=10):
        self.bufsize = bufsize
        self.buffer = [[Nic]] * bufsize
        self.ptr = -1
        self.cumulate = Nieprawda
    def reset(self, bufsize=Nic):
        jeżeli bufsize jest Nic:
            dla i w range(self.bufsize):
                self.buffer[i] = [Nic]
        inaczej:
            self.bufsize = bufsize
            self.buffer = [[Nic]] * bufsize
        self.ptr = -1
    def push(self, item):
        jeżeli self.bufsize > 0:
            jeżeli nie self.cumulate:
                self.ptr = (self.ptr + 1) % self.bufsize
                self.buffer[self.ptr] = item
            inaczej:
                self.buffer[self.ptr].append(item)
    def pop(self):
        jeżeli self.bufsize > 0:
            item = self.buffer[self.ptr]
            jeżeli item jest Nic:
                zwróć Nic
            inaczej:
                self.buffer[self.ptr] = [Nic]
                self.ptr = (self.ptr - 1) % self.bufsize
                zwróć (item)
    def nr_of_items(self):
        zwróć self.bufsize - self.buffer.count([Nic])
    def __repr__(self):
        zwróć str(self.buffer) + " " + str(self.ptr)



klasa TurtleScreen(TurtleScreenBase):
    """Provides screen oriented methods like setbg etc.

    Only relies upon the methods of TurtleScreenBase oraz NOT
    upon components of the underlying graphics toolkit -
    which jest Tkinter w this case.
    """
    _RUNNING = Prawda

    def __init__(self, cv, mode=_CFG["mode"],
                 colormode=_CFG["colormode"], delay=_CFG["delay"]):
        self._shapes = {
                   "arrow" : Shape("polygon", ((-10,0), (10,0), (0,10))),
                  "turtle" : Shape("polygon", ((0,16), (-2,14), (-1,10), (-4,7),
                              (-7,9), (-9,8), (-6,5), (-7,1), (-5,-3), (-8,-6),
                              (-6,-8), (-4,-5), (0,-7), (4,-5), (6,-8), (8,-6),
                              (5,-3), (7,1), (6,5), (9,8), (7,9), (4,7), (1,10),
                              (2,14))),
                  "circle" : Shape("polygon", ((10,0), (9.51,3.09), (8.09,5.88),
                              (5.88,8.09), (3.09,9.51), (0,10), (-3.09,9.51),
                              (-5.88,8.09), (-8.09,5.88), (-9.51,3.09), (-10,0),
                              (-9.51,-3.09), (-8.09,-5.88), (-5.88,-8.09),
                              (-3.09,-9.51), (-0.00,-10.00), (3.09,-9.51),
                              (5.88,-8.09), (8.09,-5.88), (9.51,-3.09))),
                  "square" : Shape("polygon", ((10,-10), (10,10), (-10,10),
                              (-10,-10))),
                "triangle" : Shape("polygon", ((10,-5.77), (0,11.55),
                              (-10,-5.77))),
                  "classic": Shape("polygon", ((0,0),(-5,-9),(0,-7),(5,-9))),
                   "blank" : Shape("image", self._blankimage())
                  }

        self._bgpics = {"nopic" : ""}

        TurtleScreenBase.__init__(self, cv)
        self._mode = mode
        self._delayvalue = delay
        self._colormode = _CFG["colormode"]
        self._keys = []
        self.clear()
        jeżeli sys.platform == 'darwin':
            # Force Turtle window to the front on OS X. This jest needed because
            # the Turtle window will show behind the Terminal window when you
            # start the demo z the command line.
            rootwindow = cv.winfo_toplevel()
            rootwindow.call('wm', 'attributes', '.', '-topmost', '1')
            rootwindow.call('wm', 'attributes', '.', '-topmost', '0')

    def clear(self):
        """Delete all drawings oraz all turtles z the TurtleScreen.

        No argument.

        Reset empty TurtleScreen to its initial state: white background,
        no backgroundimage, no eventbindings oraz tracing on.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.clear()

        Note: this method jest nie available jako function.
        """
        self._delayvalue = _CFG["delay"]
        self._colormode = _CFG["colormode"]
        self._delete("all")
        self._bgpic = self._createimage("")
        self._bgpicname = "nopic"
        self._tracing = 1
        self._updatecounter = 0
        self._turtles = []
        self.bgcolor("white")
        dla btn w 1, 2, 3:
            self.onclick(Nic, btn)
        self.onkeypress(Nic)
        dla key w self._keys[:]:
            self.onkey(Nic, key)
            self.onkeypress(Nic, key)
        Turtle._pen = Nic

    def mode(self, mode=Nic):
        """Set turtle-mode ('standard', 'logo' albo 'world') oraz perform reset.

        Optional argument:
        mode -- on of the strings 'standard', 'logo' albo 'world'

        Mode 'standard' jest compatible przy turtle.py.
        Mode 'logo' jest compatible przy most Logo-Turtle-Graphics.
        Mode 'world' uses userdefined 'worldcoordinates'. *Attention*: w
        this mode angles appear distorted jeżeli x/y unit-ratio doesn't equal 1.
        If mode jest nie given, zwróć the current mode.

             Mode      Initial turtle heading     positive angles
         ------------|-------------------------|-------------------
          'standard'    to the right (east)       counterclockwise
            'logo'        upward    (north)         clockwise

        Examples:
        >>> mode('logo')   # resets turtle heading to north
        >>> mode()
        'logo'
        """
        jeżeli mode jest Nic:
            zwróć self._mode
        mode = mode.lower()
        jeżeli mode nie w ["standard", "logo", "world"]:
            podnieś TurtleGraphicsError("No turtle-graphics-mode %s" % mode)
        self._mode = mode
        jeżeli mode w ["standard", "logo"]:
            self._setscrollregion(-self.canvwidth//2, -self.canvheight//2,
                                       self.canvwidth//2, self.canvheight//2)
            self.xscale = self.yscale = 1.0
        self.reset()

    def setworldcoordinates(self, llx, lly, urx, ury):
        """Set up a user defined coordinate-system.

        Arguments:
        llx -- a number, x-coordinate of lower left corner of canvas
        lly -- a number, y-coordinate of lower left corner of canvas
        urx -- a number, x-coordinate of upper right corner of canvas
        ury -- a number, y-coordinate of upper right corner of canvas

        Set up user coodinat-system oraz switch to mode 'world' jeżeli necessary.
        This performs a screen.reset. If mode 'world' jest already active,
        all drawings are redrawn according to the new coordinates.

        But ATTENTION: w user-defined coordinatesystems angles may appear
        distorted. (see Screen.mode())

        Example (dla a TurtleScreen instance named screen):
        >>> screen.setworldcoordinates(-10,-0.5,50,1.5)
        >>> dla _ w range(36):
        ...     left(10)
        ...     forward(0.5)
        """
        jeżeli self.mode() != "world":
            self.mode("world")
        xspan = float(urx - llx)
        yspan = float(ury - lly)
        wx, wy = self._window_size()
        self.screensize(wx-20, wy-20)
        oldxscale, oldyscale = self.xscale, self.yscale
        self.xscale = self.canvwidth / xspan
        self.yscale = self.canvheight / yspan
        srx1 = llx * self.xscale
        sry1 = -ury * self.yscale
        srx2 = self.canvwidth + srx1
        sry2 = self.canvheight + sry1
        self._setscrollregion(srx1, sry1, srx2, sry2)
        self._rescale(self.xscale/oldxscale, self.yscale/oldyscale)
        self.update()

    def register_shape(self, name, shape=Nic):
        """Adds a turtle shape to TurtleScreen's shapelist.

        Arguments:
        (1) name jest the name of a gif-file oraz shape jest Nic.
            Installs the corresponding image shape.
            !! Image-shapes DO NOT rotate when turning the turtle,
            !! so they do nie display the heading of the turtle!
        (2) name jest an arbitrary string oraz shape jest a tuple
            of pairs of coordinates. Installs the corresponding
            polygon shape
        (3) name jest an arbitrary string oraz shape jest a
            (compound) Shape object. Installs the corresponding
            compound shape.
        To use a shape, you have to issue the command shape(shapename).

        call: register_shape("turtle.gif")
        --or: register_shape("tri", ((0,0), (10,10), (-10,10)))

        Example (dla a TurtleScreen instance named screen):
        >>> screen.register_shape("triangle", ((5,-3),(0,5),(-5,-3)))

        """
        jeżeli shape jest Nic:
            # image
            jeżeli name.lower().endswith(".gif"):
                shape = Shape("image", self._image(name))
            inaczej:
                podnieś TurtleGraphicsError("Bad arguments dla register_shape.\n"
                                          + "Use  help(register_shape)" )
        albo_inaczej isinstance(shape, tuple):
            shape = Shape("polygon", shape)
        ## inaczej shape assumed to be Shape-instance
        self._shapes[name] = shape

    def _colorstr(self, color):
        """Return color string corresponding to args.

        Argument may be a string albo a tuple of three
        numbers corresponding to actual colormode,
        i.e. w the range 0<=n<=colormode.

        If the argument doesn't represent a color,
        an error jest podnieśd.
        """
        jeżeli len(color) == 1:
            color = color[0]
        jeżeli isinstance(color, str):
            jeżeli self._iscolorstring(color) albo color == "":
                zwróć color
            inaczej:
                podnieś TurtleGraphicsError("bad color string: %s" % str(color))
        spróbuj:
            r, g, b = color
        wyjąwszy:
            podnieś TurtleGraphicsError("bad color arguments: %s" % str(color))
        jeżeli self._colormode == 1.0:
            r, g, b = [round(255.0*x) dla x w (r, g, b)]
        jeżeli nie ((0 <= r <= 255) oraz (0 <= g <= 255) oraz (0 <= b <= 255)):
            podnieś TurtleGraphicsError("bad color sequence: %s" % str(color))
        zwróć "#%02x%02x%02x" % (r, g, b)

    def _color(self, cstr):
        jeżeli nie cstr.startswith("#"):
            zwróć cstr
        jeżeli len(cstr) == 7:
            cl = [int(cstr[i:i+2], 16) dla i w (1, 3, 5)]
        albo_inaczej len(cstr) == 4:
            cl = [16*int(cstr[h], 16) dla h w cstr[1:]]
        inaczej:
            podnieś TurtleGraphicsError("bad colorstring: %s" % cstr)
        zwróć tuple([c * self._colormode/255 dla c w cl])

    def colormode(self, cmode=Nic):
        """Return the colormode albo set it to 1.0 albo 255.

        Optional argument:
        cmode -- one of the values 1.0 albo 255

        r, g, b values of colortriples have to be w range 0..cmode.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.colormode()
        1.0
        >>> screen.colormode(255)
        >>> pencolor(240,160,80)
        """
        jeżeli cmode jest Nic:
            zwróć self._colormode
        jeżeli cmode == 1.0:
            self._colormode = float(cmode)
        albo_inaczej cmode == 255:
            self._colormode = int(cmode)

    def reset(self):
        """Reset all Turtles on the Screen to their initial state.

        No argument.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.reset()
        """
        dla turtle w self._turtles:
            turtle._setmode(self._mode)
            turtle.reset()

    def turtles(self):
        """Return the list of turtles on the screen.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.turtles()
        [<turtle.Turtle object at 0x00E11FB0>]
        """
        zwróć self._turtles

    def bgcolor(self, *args):
        """Set albo zwróć backgroundcolor of the TurtleScreen.

        Arguments (jeżeli given): a color string albo three numbers
        w the range 0..colormode albo a 3-tuple of such numbers.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.bgcolor("orange")
        >>> screen.bgcolor()
        'orange'
        >>> screen.bgcolor(0.5,0,0.5)
        >>> screen.bgcolor()
        '#800080'
        """
        jeżeli args:
            color = self._colorstr(args)
        inaczej:
            color = Nic
        color = self._bgcolor(color)
        jeżeli color jest nie Nic:
            color = self._color(color)
        zwróć color

    def tracer(self, n=Nic, delay=Nic):
        """Turns turtle animation on/off oraz set delay dla update drawings.

        Optional arguments:
        n -- nonnegative  integer
        delay -- nonnegative  integer

        If n jest given, only each n-th regular screen update jest really performed.
        (Can be used to accelerate the drawing of complex graphics.)
        Second arguments sets delay value (see RawTurtle.delay())

        Example (dla a TurtleScreen instance named screen):
        >>> screen.tracer(8, 25)
        >>> dist = 2
        >>> dla i w range(200):
        ...     fd(dist)
        ...     rt(90)
        ...     dist += 2
        """
        jeżeli n jest Nic:
            zwróć self._tracing
        self._tracing = int(n)
        self._updatecounter = 0
        jeżeli delay jest nie Nic:
            self._delayvalue = int(delay)
        jeżeli self._tracing:
            self.update()

    def delay(self, delay=Nic):
        """ Return albo set the drawing delay w milliseconds.

        Optional argument:
        delay -- positive integer

        Example (dla a TurtleScreen instance named screen):
        >>> screen.delay(15)
        >>> screen.delay()
        15
        """
        jeżeli delay jest Nic:
            zwróć self._delayvalue
        self._delayvalue = int(delay)

    def _incrementudc(self):
        """Increment update counter."""
        jeżeli nie TurtleScreen._RUNNING:
            TurtleScreen._RUNNING = Prawda
            podnieś Terminator
        jeżeli self._tracing > 0:
            self._updatecounter += 1
            self._updatecounter %= self._tracing

    def update(self):
        """Perform a TurtleScreen update.
        """
        tracing = self._tracing
        self._tracing = Prawda
        dla t w self.turtles():
            t._update_data()
            t._drawturtle()
        self._tracing = tracing
        self._update()

    def window_width(self):
        """ Return the width of the turtle window.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.window_width()
        640
        """
        zwróć self._window_size()[0]

    def window_height(self):
        """ Return the height of the turtle window.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.window_height()
        480
        """
        zwróć self._window_size()[1]

    def getcanvas(self):
        """Return the Canvas of this TurtleScreen.

        No argument.

        Example (dla a Screen instance named screen):
        >>> cv = screen.getcanvas()
        >>> cv
        <turtle.ScrolledCanvas instance at 0x010742D8>
        """
        zwróć self.cv

    def getshapes(self):
        """Return a list of names of all currently available turtle shapes.

        No argument.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.getshapes()
        ['arrow', 'blank', 'circle', ... , 'turtle']
        """
        zwróć sorted(self._shapes.keys())

    def onclick(self, fun, btn=1, add=Nic):
        """Bind fun to mouse-click event on canvas.

        Arguments:
        fun -- a function przy two arguments, the coordinates of the
               clicked point on the canvas.
        num -- the number of the mouse-button, defaults to 1

        Example (dla a TurtleScreen instance named screen)

        >>> screen.onclick(goto)
        >>> # Subsequently clicking into the TurtleScreen will
        >>> # make the turtle move to the clicked point.
        >>> screen.onclick(Nic)
        """
        self._onscreenclick(fun, btn, add)

    def onkey(self, fun, key):
        """Bind fun to key-release event of key.

        Arguments:
        fun -- a function przy no arguments
        key -- a string: key (e.g. "a") albo key-symbol (e.g. "space")

        In order to be able to register key-events, TurtleScreen
        must have focus. (See method listen.)

        Example (dla a TurtleScreen instance named screen):

        >>> def f():
        ...     fd(50)
        ...     lt(60)
        ...
        >>> screen.onkey(f, "Up")
        >>> screen.listen()

        Subsequently the turtle can be moved by repeatedly pressing
        the up-arrow key, consequently drawing a hexagon

        """
        jeżeli fun jest Nic:
            jeżeli key w self._keys:
                self._keys.remove(key)
        albo_inaczej key nie w self._keys:
            self._keys.append(key)
        self._onkeyrelease(fun, key)

    def onkeypress(self, fun, key=Nic):
        """Bind fun to key-press event of key jeżeli key jest given,
        albo to any key-press-event jeżeli no key jest given.

        Arguments:
        fun -- a function przy no arguments
        key -- a string: key (e.g. "a") albo key-symbol (e.g. "space")

        In order to be able to register key-events, TurtleScreen
        must have focus. (See method listen.)

        Example (dla a TurtleScreen instance named screen
        oraz a Turtle instance named turtle):

        >>> def f():
        ...     fd(50)
        ...     lt(60)
        ...
        >>> screen.onkeypress(f, "Up")
        >>> screen.listen()

        Subsequently the turtle can be moved by repeatedly pressing
        the up-arrow key, albo by keeping pressed the up-arrow key.
        consequently drawing a hexagon.
        """
        jeżeli fun jest Nic:
            jeżeli key w self._keys:
                self._keys.remove(key)
        albo_inaczej key jest nie Nic oraz key nie w self._keys:
            self._keys.append(key)
        self._onkeypress(fun, key)

    def listen(self, xdummy=Nic, ydummy=Nic):
        """Set focus on TurtleScreen (in order to collect key-events)

        No arguments.
        Dummy arguments are provided w order
        to be able to dalej listen to the onclick method.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.listen()
        """
        self._listen()

    def ontimer(self, fun, t=0):
        """Install a timer, which calls fun after t milliseconds.

        Arguments:
        fun -- a function przy no arguments.
        t -- a number >= 0

        Example (dla a TurtleScreen instance named screen):

        >>> running = Prawda
        >>> def f():
        ...     jeżeli running:
        ...             fd(50)
        ...             lt(60)
        ...             screen.ontimer(f, 250)
        ...
        >>> f()   # makes the turtle marching around
        >>> running = Nieprawda
        """
        self._ontimer(fun, t)

    def bgpic(self, picname=Nic):
        """Set background image albo zwróć name of current backgroundimage.

        Optional argument:
        picname -- a string, name of a gif-file albo "nopic".

        If picname jest a filename, set the corresponding image jako background.
        If picname jest "nopic", delete backgroundimage, jeżeli present.
        If picname jest Nic, zwróć the filename of the current backgroundimage.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.bgpic()
        'nopic'
        >>> screen.bgpic("landscape.gif")
        >>> screen.bgpic()
        'landscape.gif'
        """
        jeżeli picname jest Nic:
            zwróć self._bgpicname
        jeżeli picname nie w self._bgpics:
            self._bgpics[picname] = self._image(picname)
        self._setbgpic(self._bgpic, self._bgpics[picname])
        self._bgpicname = picname

    def screensize(self, canvwidth=Nic, canvheight=Nic, bg=Nic):
        """Resize the canvas the turtles are drawing on.

        Optional arguments:
        canvwidth -- positive integer, new width of canvas w pixels
        canvheight --  positive integer, new height of canvas w pixels
        bg -- colorstring albo color-tuple, new backgroundcolor
        If no arguments are given, zwróć current (canvaswidth, canvasheight)

        Do nie alter the drawing window. To observe hidden parts of
        the canvas use the scrollbars. (Can make visible those parts
        of a drawing, which were outside the canvas before!)

        Example (dla a Turtle instance named turtle):
        >>> turtle.screensize(2000,1500)
        >>> # e.g. to search dla an erroneously escaped turtle ;-)
        """
        zwróć self._resize(canvwidth, canvheight, bg)

    onscreenclick = onclick
    resetscreen = reset
    clearscreen = clear
    addshape = register_shape
    onkeyrelease = onkey

klasa TNavigator(object):
    """Navigation part of the RawTurtle.
    Implements methods dla turtle movement.
    """
    START_ORIENTATION = {
        "standard": Vec2D(1.0, 0.0),
        "world"   : Vec2D(1.0, 0.0),
        "logo"    : Vec2D(0.0, 1.0)  }
    DEFAULT_MODE = "standard"
    DEFAULT_ANGLEOFFSET = 0
    DEFAULT_ANGLEORIENT = 1

    def __init__(self, mode=DEFAULT_MODE):
        self._angleOffset = self.DEFAULT_ANGLEOFFSET
        self._angleOrient = self.DEFAULT_ANGLEORIENT
        self._mode = mode
        self.undobuffer = Nic
        self.degrees()
        self._mode = Nic
        self._setmode(mode)
        TNavigator.reset(self)

    def reset(self):
        """reset turtle to its initial values

        Will be overwritten by parent class
        """
        self._position = Vec2D(0.0, 0.0)
        self._orient =  TNavigator.START_ORIENTATION[self._mode]

    def _setmode(self, mode=Nic):
        """Set turtle-mode to 'standard', 'world' albo 'logo'.
        """
        jeżeli mode jest Nic:
            zwróć self._mode
        jeżeli mode nie w ["standard", "logo", "world"]:
            zwróć
        self._mode = mode
        jeżeli mode w ["standard", "world"]:
            self._angleOffset = 0
            self._angleOrient = 1
        inaczej: # mode == "logo":
            self._angleOffset = self._fullcircle/4.
            self._angleOrient = -1

    def _setDegreesPerAU(self, fullcircle):
        """Helper function dla degrees() oraz radians()"""
        self._fullcircle = fullcircle
        self._degreesPerAU = 360/fullcircle
        jeżeli self._mode == "standard":
            self._angleOffset = 0
        inaczej:
            self._angleOffset = fullcircle/4.

    def degrees(self, fullcircle=360.0):
        """ Set angle measurement units to degrees.

        Optional argument:
        fullcircle -  a number

        Set angle measurement units, i. e. set number
        of 'degrees' dla a full circle. Dafault value jest
        360 degrees.

        Example (dla a Turtle instance named turtle):
        >>> turtle.left(90)
        >>> turtle.heading()
        90

        Change angle measurement unit to grad (also known jako gon,
        grade, albo gradian oraz equals 1/100-th of the right angle.)
        >>> turtle.degrees(400.0)
        >>> turtle.heading()
        100

        """
        self._setDegreesPerAU(fullcircle)

    def radians(self):
        """ Set the angle measurement units to radians.

        No arguments.

        Example (dla a Turtle instance named turtle):
        >>> turtle.heading()
        90
        >>> turtle.radians()
        >>> turtle.heading()
        1.5707963267948966
        """
        self._setDegreesPerAU(2*math.pi)

    def _go(self, distance):
        """move turtle forward by specified distance"""
        ende = self._position + self._orient * distance
        self._goto(ende)

    def _rotate(self, angle):
        """Turn turtle counterclockwise by specified angle jeżeli angle > 0."""
        angle *= self._degreesPerAU
        self._orient = self._orient.rotate(angle)

    def _goto(self, end):
        """move turtle to position end."""
        self._position = end

    def forward(self, distance):
        """Move the turtle forward by the specified distance.

        Aliases: forward | fd

        Argument:
        distance -- a number (integer albo float)

        Move the turtle forward by the specified distance, w the direction
        the turtle jest headed.

        Example (dla a Turtle instance named turtle):
        >>> turtle.position()
        (0.00, 0.00)
        >>> turtle.forward(25)
        >>> turtle.position()
        (25.00,0.00)
        >>> turtle.forward(-75)
        >>> turtle.position()
        (-50.00,0.00)
        """
        self._go(distance)

    def back(self, distance):
        """Move the turtle backward by distance.

        Aliases: back | backward | bk

        Argument:
        distance -- a number

        Move the turtle backward by distance ,opposite to the direction the
        turtle jest headed. Do nie change the turtle's heading.

        Example (dla a Turtle instance named turtle):
        >>> turtle.position()
        (0.00, 0.00)
        >>> turtle.backward(30)
        >>> turtle.position()
        (-30.00, 0.00)
        """
        self._go(-distance)

    def right(self, angle):
        """Turn turtle right by angle units.

        Aliases: right | rt

        Argument:
        angle -- a number (integer albo float)

        Turn turtle right by angle units. (Units are by default degrees,
        but can be set via the degrees() oraz radians() functions.)
        Angle orientation depends on mode. (See this.)

        Example (dla a Turtle instance named turtle):
        >>> turtle.heading()
        22.0
        >>> turtle.right(45)
        >>> turtle.heading()
        337.0
        """
        self._rotate(-angle)

    def left(self, angle):
        """Turn turtle left by angle units.

        Aliases: left | lt

        Argument:
        angle -- a number (integer albo float)

        Turn turtle left by angle units. (Units are by default degrees,
        but can be set via the degrees() oraz radians() functions.)
        Angle orientation depends on mode. (See this.)

        Example (dla a Turtle instance named turtle):
        >>> turtle.heading()
        22.0
        >>> turtle.left(45)
        >>> turtle.heading()
        67.0
        """
        self._rotate(angle)

    def pos(self):
        """Return the turtle's current location (x,y), jako a Vec2D-vector.

        Aliases: pos | position

        No arguments.

        Example (dla a Turtle instance named turtle):
        >>> turtle.pos()
        (0.00, 240.00)
        """
        zwróć self._position

    def xcor(self):
        """ Return the turtle's x coordinate.

        No arguments.

        Example (dla a Turtle instance named turtle):
        >>> reset()
        >>> turtle.left(60)
        >>> turtle.forward(100)
        >>> print turtle.xcor()
        50.0
        """
        zwróć self._position[0]

    def ycor(self):
        """ Return the turtle's y coordinate
        ---
        No arguments.

        Example (dla a Turtle instance named turtle):
        >>> reset()
        >>> turtle.left(60)
        >>> turtle.forward(100)
        >>> print turtle.ycor()
        86.6025403784
        """
        zwróć self._position[1]


    def goto(self, x, y=Nic):
        """Move turtle to an absolute position.

        Aliases: setpos | setposition | goto:

        Arguments:
        x -- a number      albo     a pair/vector of numbers
        y -- a number             Nic

        call: goto(x, y)         # two coordinates
        --or: goto((x, y))       # a pair (tuple) of coordinates
        --or: goto(vec)          # e.g. jako returned by pos()

        Move turtle to an absolute position. If the pen jest down,
        a line will be drawn. The turtle's orientation does nie change.

        Example (dla a Turtle instance named turtle):
        >>> tp = turtle.pos()
        >>> tp
        (0.00, 0.00)
        >>> turtle.setpos(60,30)
        >>> turtle.pos()
        (60.00,30.00)
        >>> turtle.setpos((20,80))
        >>> turtle.pos()
        (20.00,80.00)
        >>> turtle.setpos(tp)
        >>> turtle.pos()
        (0.00,0.00)
        """
        jeżeli y jest Nic:
            self._goto(Vec2D(*x))
        inaczej:
            self._goto(Vec2D(x, y))

    def home(self):
        """Move turtle to the origin - coordinates (0,0).

        No arguments.

        Move turtle to the origin - coordinates (0,0) oraz set its
        heading to its start-orientation (which depends on mode).

        Example (dla a Turtle instance named turtle):
        >>> turtle.home()
        """
        self.goto(0, 0)
        self.setheading(0)

    def setx(self, x):
        """Set the turtle's first coordinate to x

        Argument:
        x -- a number (integer albo float)

        Set the turtle's first coordinate to x, leave second coordinate
        unchanged.

        Example (dla a Turtle instance named turtle):
        >>> turtle.position()
        (0.00, 240.00)
        >>> turtle.setx(10)
        >>> turtle.position()
        (10.00, 240.00)
        """
        self._goto(Vec2D(x, self._position[1]))

    def sety(self, y):
        """Set the turtle's second coordinate to y

        Argument:
        y -- a number (integer albo float)

        Set the turtle's first coordinate to x, second coordinate remains
        unchanged.

        Example (dla a Turtle instance named turtle):
        >>> turtle.position()
        (0.00, 40.00)
        >>> turtle.sety(-10)
        >>> turtle.position()
        (0.00, -10.00)
        """
        self._goto(Vec2D(self._position[0], y))

    def distance(self, x, y=Nic):
        """Return the distance z the turtle to (x,y) w turtle step units.

        Arguments:
        x -- a number   albo  a pair/vector of numbers   albo   a turtle instance
        y -- a number       Nic                            Nic

        call: distance(x, y)         # two coordinates
        --or: distance((x, y))       # a pair (tuple) of coordinates
        --or: distance(vec)          # e.g. jako returned by pos()
        --or: distance(mypen)        # where mypen jest another turtle

        Example (dla a Turtle instance named turtle):
        >>> turtle.pos()
        (0.00, 0.00)
        >>> turtle.distance(30,40)
        50.0
        >>> pen = Turtle()
        >>> pen.forward(77)
        >>> turtle.distance(pen)
        77.0
        """
        jeżeli y jest nie Nic:
            pos = Vec2D(x, y)
        jeżeli isinstance(x, Vec2D):
            pos = x
        albo_inaczej isinstance(x, tuple):
            pos = Vec2D(*x)
        albo_inaczej isinstance(x, TNavigator):
            pos = x._position
        zwróć abs(pos - self._position)

    def towards(self, x, y=Nic):
        """Return the angle of the line z the turtle's position to (x, y).

        Arguments:
        x -- a number   albo  a pair/vector of numbers   albo   a turtle instance
        y -- a number       Nic                            Nic

        call: distance(x, y)         # two coordinates
        --or: distance((x, y))       # a pair (tuple) of coordinates
        --or: distance(vec)          # e.g. jako returned by pos()
        --or: distance(mypen)        # where mypen jest another turtle

        Return the angle, between the line z turtle-position to position
        specified by x, y oraz the turtle's start orientation. (Depends on
        modes - "standard" albo "logo")

        Example (dla a Turtle instance named turtle):
        >>> turtle.pos()
        (10.00, 10.00)
        >>> turtle.towards(0,0)
        225.0
        """
        jeżeli y jest nie Nic:
            pos = Vec2D(x, y)
        jeżeli isinstance(x, Vec2D):
            pos = x
        albo_inaczej isinstance(x, tuple):
            pos = Vec2D(*x)
        albo_inaczej isinstance(x, TNavigator):
            pos = x._position
        x, y = pos - self._position
        result = round(math.atan2(y, x)*180.0/math.pi, 10) % 360.0
        result /= self._degreesPerAU
        zwróć (self._angleOffset + self._angleOrient*result) % self._fullcircle

    def heading(self):
        """ Return the turtle's current heading.

        No arguments.

        Example (dla a Turtle instance named turtle):
        >>> turtle.left(67)
        >>> turtle.heading()
        67.0
        """
        x, y = self._orient
        result = round(math.atan2(y, x)*180.0/math.pi, 10) % 360.0
        result /= self._degreesPerAU
        zwróć (self._angleOffset + self._angleOrient*result) % self._fullcircle

    def setheading(self, to_angle):
        """Set the orientation of the turtle to to_angle.

        Aliases:  setheading | seth

        Argument:
        to_angle -- a number (integer albo float)

        Set the orientation of the turtle to to_angle.
        Here are some common directions w degrees:

         standard - mode:          logo-mode:
        -------------------|--------------------
           0 - east                0 - north
          90 - north              90 - east
         180 - west              180 - south
         270 - south             270 - west

        Example (dla a Turtle instance named turtle):
        >>> turtle.setheading(90)
        >>> turtle.heading()
        90
        """
        angle = (to_angle - self.heading())*self._angleOrient
        full = self._fullcircle
        angle = (angle+full/2.)%full - full/2.
        self._rotate(angle)

    def circle(self, radius, extent = Nic, steps = Nic):
        """ Draw a circle przy given radius.

        Arguments:
        radius -- a number
        extent (optional) -- a number
        steps (optional) -- an integer

        Draw a circle przy given radius. The center jest radius units left
        of the turtle; extent - an angle - determines which part of the
        circle jest drawn. If extent jest nie given, draw the entire circle.
        If extent jest nie a full circle, one endpoint of the arc jest the
        current pen position. Draw the arc w counterclockwise direction
        jeżeli radius jest positive, otherwise w clockwise direction. Finally
        the direction of the turtle jest changed by the amount of extent.

        As the circle jest approximated by an inscribed regular polygon,
        steps determines the number of steps to use. If nie given,
        it will be calculated automatically. Maybe used to draw regular
        polygons.

        call: circle(radius)                  # full circle
        --or: circle(radius, extent)          # arc
        --or: circle(radius, extent, steps)
        --or: circle(radius, steps=6)         # 6-sided polygon

        Example (dla a Turtle instance named turtle):
        >>> turtle.circle(50)
        >>> turtle.circle(120, 180)  # semicircle
        """
        jeżeli self.undobuffer:
            self.undobuffer.push(["seq"])
            self.undobuffer.cumulate = Prawda
        speed = self.speed()
        jeżeli extent jest Nic:
            extent = self._fullcircle
        jeżeli steps jest Nic:
            frac = abs(extent)/self._fullcircle
            steps = 1+int(min(11+abs(radius)/6.0, 59.0)*frac)
        w = 1.0 * extent / steps
        w2 = 0.5 * w
        l = 2.0 * radius * math.sin(w2*math.pi/180.0*self._degreesPerAU)
        jeżeli radius < 0:
            l, w, w2 = -l, -w, -w2
        tr = self._tracer()
        dl = self._delay()
        jeżeli speed == 0:
            self._tracer(0, 0)
        inaczej:
            self.speed(0)
        self._rotate(w2)
        dla i w range(steps):
            self.speed(speed)
            self._go(l)
            self.speed(0)
            self._rotate(w)
        self._rotate(-w2)
        jeżeli speed == 0:
            self._tracer(tr, dl)
        self.speed(speed)
        jeżeli self.undobuffer:
            self.undobuffer.cumulate = Nieprawda

## three dummy methods to be implemented by child class:

    def speed(self, s=0):
        """dummy method - to be overwritten by child class"""
    def _tracer(self, a=Nic, b=Nic):
        """dummy method - to be overwritten by child class"""
    def _delay(self, n=Nic):
        """dummy method - to be overwritten by child class"""

    fd = forward
    bk = back
    backward = back
    rt = right
    lt = left
    position = pos
    setpos = goto
    setposition = goto
    seth = setheading


klasa TPen(object):
    """Drawing part of the RawTurtle.
    Implements drawing properties.
    """
    def __init__(self, resizemode=_CFG["resizemode"]):
        self._resizemode = resizemode # albo "user" albo "noresize"
        self.undobuffer = Nic
        TPen._reset(self)

    def _reset(self, pencolor=_CFG["pencolor"],
                     fillcolor=_CFG["fillcolor"]):
        self._pensize = 1
        self._shown = Prawda
        self._pencolor = pencolor
        self._fillcolor = fillcolor
        self._drawing = Prawda
        self._speed = 3
        self._stretchfactor = (1., 1.)
        self._shearfactor = 0.
        self._tilt = 0.
        self._shapetrafo = (1., 0., 0., 1.)
        self._outlinewidth = 1

    def resizemode(self, rmode=Nic):
        """Set resizemode to one of the values: "auto", "user", "noresize".

        (Optional) Argument:
        rmode -- one of the strings "auto", "user", "noresize"

        Different resizemodes have the following effects:
          - "auto" adapts the appearance of the turtle
                   corresponding to the value of pensize.
          - "user" adapts the appearance of the turtle according to the
                   values of stretchfactor oraz outlinewidth (outline),
                   which are set by shapesize()
          - "noresize" no adaption of the turtle's appearance takes place.
        If no argument jest given, zwróć current resizemode.
        resizemode("user") jest called by a call of shapesize przy arguments.


        Examples (dla a Turtle instance named turtle):
        >>> turtle.resizemode("noresize")
        >>> turtle.resizemode()
        'noresize'
        """
        jeżeli rmode jest Nic:
            zwróć self._resizemode
        rmode = rmode.lower()
        jeżeli rmode w ["auto", "user", "noresize"]:
            self.pen(resizemode=rmode)

    def pensize(self, width=Nic):
        """Set albo zwróć the line thickness.

        Aliases:  pensize | width

        Argument:
        width -- positive number

        Set the line thickness to width albo zwróć it. If resizemode jest set
        to "auto" oraz turtleshape jest a polygon, that polygon jest drawn with
        the same line thickness. If no argument jest given, current pensize
        jest returned.

        Example (dla a Turtle instance named turtle):
        >>> turtle.pensize()
        1
        >>> turtle.pensize(10)   # z here on lines of width 10 are drawn
        """
        jeżeli width jest Nic:
            zwróć self._pensize
        self.pen(pensize=width)


    def penup(self):
        """Pull the pen up -- no drawing when moving.

        Aliases: penup | pu | up

        No argument

        Example (dla a Turtle instance named turtle):
        >>> turtle.penup()
        """
        jeżeli nie self._drawing:
            zwróć
        self.pen(pendown=Nieprawda)

    def pendown(self):
        """Pull the pen down -- drawing when moving.

        Aliases: pendown | pd | down

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> turtle.pendown()
        """
        jeżeli self._drawing:
            zwróć
        self.pen(pendown=Prawda)

    def isdown(self):
        """Return Prawda jeżeli pen jest down, Nieprawda jeżeli it's up.

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> turtle.penup()
        >>> turtle.isdown()
        Nieprawda
        >>> turtle.pendown()
        >>> turtle.isdown()
        Prawda
        """
        zwróć self._drawing

    def speed(self, speed=Nic):
        """ Return albo set the turtle's speed.

        Optional argument:
        speed -- an integer w the range 0..10 albo a speedstring (see below)

        Set the turtle's speed to an integer value w the range 0 .. 10.
        If no argument jest given: zwróć current speed.

        If input jest a number greater than 10 albo smaller than 0.5,
        speed jest set to 0.
        Speedstrings  are mapped to speedvalues w the following way:
            'fastest' :  0
            'fast'    :  10
            'normal'  :  6
            'slow'    :  3
            'slowest' :  1
        speeds z 1 to 10 enforce increasingly faster animation of
        line drawing oraz turtle turning.

        Attention:
        speed = 0 : *no* animation takes place. forward/back makes turtle jump
        oraz likewise left/right make the turtle turn instantly.

        Example (dla a Turtle instance named turtle):
        >>> turtle.speed(3)
        """
        speeds = {'fastest':0, 'fast':10, 'normal':6, 'slow':3, 'slowest':1 }
        jeżeli speed jest Nic:
            zwróć self._speed
        jeżeli speed w speeds:
            speed = speeds[speed]
        albo_inaczej 0.5 < speed < 10.5:
            speed = int(round(speed))
        inaczej:
            speed = 0
        self.pen(speed=speed)

    def color(self, *args):
        """Return albo set the pencolor oraz fillcolor.

        Arguments:
        Several input formats are allowed.
        They use 0, 1, 2, albo 3 arguments jako follows:

        color()
            Return the current pencolor oraz the current fillcolor
            jako a pair of color specification strings jako are returned
            by pencolor oraz fillcolor.
        color(colorstring), color((r,g,b)), color(r,g,b)
            inputs jako w pencolor, set both, fillcolor oraz pencolor,
            to the given value.
        color(colorstring1, colorstring2),
        color((r1,g1,b1), (r2,g2,b2))
            equivalent to pencolor(colorstring1) oraz fillcolor(colorstring2)
            oraz analogously, jeżeli the other input format jest used.

        If turtleshape jest a polygon, outline oraz interior of that polygon
        jest drawn przy the newly set colors.
        For mor info see: pencolor, fillcolor

        Example (dla a Turtle instance named turtle):
        >>> turtle.color('red', 'green')
        >>> turtle.color()
        ('red', 'green')
        >>> colormode(255)
        >>> color((40, 80, 120), (160, 200, 240))
        >>> color()
        ('#285078', '#a0c8f0')
        """
        jeżeli args:
            l = len(args)
            jeżeli l == 1:
                pcolor = fcolor = args[0]
            albo_inaczej l == 2:
                pcolor, fcolor = args
            albo_inaczej l == 3:
                pcolor = fcolor = args
            pcolor = self._colorstr(pcolor)
            fcolor = self._colorstr(fcolor)
            self.pen(pencolor=pcolor, fillcolor=fcolor)
        inaczej:
            zwróć self._color(self._pencolor), self._color(self._fillcolor)

    def pencolor(self, *args):
        """ Return albo set the pencolor.

        Arguments:
        Four input formats are allowed:
          - pencolor()
            Return the current pencolor jako color specification string,
            possibly w hex-number format (see example).
            May be used jako input to another color/pencolor/fillcolor call.
          - pencolor(colorstring)
            s jest a Tk color specification string, such jako "red" albo "yellow"
          - pencolor((r, g, b))
            *a tuple* of r, g, oraz b, which represent, an RGB color,
            oraz each of r, g, oraz b are w the range 0..colormode,
            where colormode jest either 1.0 albo 255
          - pencolor(r, g, b)
            r, g, oraz b represent an RGB color, oraz each of r, g, oraz b
            are w the range 0..colormode

        If turtleshape jest a polygon, the outline of that polygon jest drawn
        przy the newly set pencolor.

        Example (dla a Turtle instance named turtle):
        >>> turtle.pencolor('brown')
        >>> tup = (0.2, 0.8, 0.55)
        >>> turtle.pencolor(tup)
        >>> turtle.pencolor()
        '#33cc8c'
        """
        jeżeli args:
            color = self._colorstr(args)
            jeżeli color == self._pencolor:
                zwróć
            self.pen(pencolor=color)
        inaczej:
            zwróć self._color(self._pencolor)

    def fillcolor(self, *args):
        """ Return albo set the fillcolor.

        Arguments:
        Four input formats are allowed:
          - fillcolor()
            Return the current fillcolor jako color specification string,
            possibly w hex-number format (see example).
            May be used jako input to another color/pencolor/fillcolor call.
          - fillcolor(colorstring)
            s jest a Tk color specification string, such jako "red" albo "yellow"
          - fillcolor((r, g, b))
            *a tuple* of r, g, oraz b, which represent, an RGB color,
            oraz each of r, g, oraz b are w the range 0..colormode,
            where colormode jest either 1.0 albo 255
          - fillcolor(r, g, b)
            r, g, oraz b represent an RGB color, oraz each of r, g, oraz b
            are w the range 0..colormode

        If turtleshape jest a polygon, the interior of that polygon jest drawn
        przy the newly set fillcolor.

        Example (dla a Turtle instance named turtle):
        >>> turtle.fillcolor('violet')
        >>> col = turtle.pencolor()
        >>> turtle.fillcolor(col)
        >>> turtle.fillcolor(0, .5, 0)
        """
        jeżeli args:
            color = self._colorstr(args)
            jeżeli color == self._fillcolor:
                zwróć
            self.pen(fillcolor=color)
        inaczej:
            zwróć self._color(self._fillcolor)

    def showturtle(self):
        """Makes the turtle visible.

        Aliases: showturtle | st

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> turtle.hideturtle()
        >>> turtle.showturtle()
        """
        self.pen(shown=Prawda)

    def hideturtle(self):
        """Makes the turtle invisible.

        Aliases: hideturtle | ht

        No argument.

        It's a good idea to do this dopóki you're w the
        middle of a complicated drawing, because hiding
        the turtle speeds up the drawing observably.

        Example (dla a Turtle instance named turtle):
        >>> turtle.hideturtle()
        """
        self.pen(shown=Nieprawda)

    def isvisible(self):
        """Return Prawda jeżeli the Turtle jest shown, Nieprawda jeżeli it's hidden.

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> turtle.hideturtle()
        >>> print turtle.isvisible():
        Nieprawda
        """
        zwróć self._shown

    def pen(self, pen=Nic, **pendict):
        """Return albo set the pen's attributes.

        Arguments:
            pen -- a dictionary przy some albo all of the below listed keys.
            **pendict -- one albo more keyword-arguments przy the below
                         listed keys jako keywords.

        Return albo set the pen's attributes w a 'pen-dictionary'
        przy the following key/value pairs:
           "shown"      :   Prawda/Nieprawda
           "pendown"    :   Prawda/Nieprawda
           "pencolor"   :   color-string albo color-tuple
           "fillcolor"  :   color-string albo color-tuple
           "pensize"    :   positive number
           "speed"      :   number w range 0..10
           "resizemode" :   "auto" albo "user" albo "noresize"
           "stretchfactor": (positive number, positive number)
           "shearfactor":   number
           "outline"    :   positive number
           "tilt"       :   number

        This dictionary can be used jako argument dla a subsequent
        pen()-call to restore the former pen-state. Moreover one
        albo more of these attributes can be provided jako keyword-arguments.
        This can be used to set several pen attributes w one statement.


        Examples (dla a Turtle instance named turtle):
        >>> turtle.pen(fillcolor="black", pencolor="red", pensize=10)
        >>> turtle.pen()
        {'pensize': 10, 'shown': Prawda, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'red', 'pendown': Prawda, 'fillcolor': 'black',
        'stretchfactor': (1,1), 'speed': 3, 'shearfactor': 0.0}
        >>> penstate=turtle.pen()
        >>> turtle.color("yellow","")
        >>> turtle.penup()
        >>> turtle.pen()
        {'pensize': 10, 'shown': Prawda, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'yellow', 'pendown': Nieprawda, 'fillcolor': '',
        'stretchfactor': (1,1), 'speed': 3, 'shearfactor': 0.0}
        >>> p.pen(penstate, fillcolor="green")
        >>> p.pen()
        {'pensize': 10, 'shown': Prawda, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'red', 'pendown': Prawda, 'fillcolor': 'green',
        'stretchfactor': (1,1), 'speed': 3, 'shearfactor': 0.0}
        """
        _pd =  {"shown"         : self._shown,
                "pendown"       : self._drawing,
                "pencolor"      : self._pencolor,
                "fillcolor"     : self._fillcolor,
                "pensize"       : self._pensize,
                "speed"         : self._speed,
                "resizemode"    : self._resizemode,
                "stretchfactor" : self._stretchfactor,
                "shearfactor"   : self._shearfactor,
                "outline"       : self._outlinewidth,
                "tilt"          : self._tilt
               }

        jeżeli nie (pen albo pendict):
            zwróć _pd

        jeżeli isinstance(pen, dict):
            p = pen
        inaczej:
            p = {}
        p.update(pendict)

        _p_buf = {}
        dla key w p:
            _p_buf[key] = _pd[key]

        jeżeli self.undobuffer:
            self.undobuffer.push(("pen", _p_buf))

        newLine = Nieprawda
        jeżeli "pendown" w p:
            jeżeli self._drawing != p["pendown"]:
                newLine = Prawda
        jeżeli "pencolor" w p:
            jeżeli isinstance(p["pencolor"], tuple):
                p["pencolor"] = self._colorstr((p["pencolor"],))
            jeżeli self._pencolor != p["pencolor"]:
                newLine = Prawda
        jeżeli "pensize" w p:
            jeżeli self._pensize != p["pensize"]:
                newLine = Prawda
        jeżeli newLine:
            self._newLine()
        jeżeli "pendown" w p:
            self._drawing = p["pendown"]
        jeżeli "pencolor" w p:
            self._pencolor = p["pencolor"]
        jeżeli "pensize" w p:
            self._pensize = p["pensize"]
        jeżeli "fillcolor" w p:
            jeżeli isinstance(p["fillcolor"], tuple):
                p["fillcolor"] = self._colorstr((p["fillcolor"],))
            self._fillcolor = p["fillcolor"]
        jeżeli "speed" w p:
            self._speed = p["speed"]
        jeżeli "resizemode" w p:
            self._resizemode = p["resizemode"]
        jeżeli "stretchfactor" w p:
            sf = p["stretchfactor"]
            jeżeli isinstance(sf, (int, float)):
                sf = (sf, sf)
            self._stretchfactor = sf
        jeżeli "shearfactor" w p:
            self._shearfactor = p["shearfactor"]
        jeżeli "outline" w p:
            self._outlinewidth = p["outline"]
        jeżeli "shown" w p:
            self._shown = p["shown"]
        jeżeli "tilt" w p:
            self._tilt = p["tilt"]
        jeżeli "stretchfactor" w p albo "tilt" w p albo "shearfactor" w p:
            scx, scy = self._stretchfactor
            shf = self._shearfactor
            sa, ca = math.sin(self._tilt), math.cos(self._tilt)
            self._shapetrafo = ( scx*ca, scy*(shf*ca + sa),
                                -scx*sa, scy*(ca - shf*sa))
        self._update()

## three dummy methods to be implemented by child class:

    def _newLine(self, usePos = Prawda):
        """dummy method - to be overwritten by child class"""
    def _update(self, count=Prawda, forced=Nieprawda):
        """dummy method - to be overwritten by child class"""
    def _color(self, args):
        """dummy method - to be overwritten by child class"""
    def _colorstr(self, args):
        """dummy method - to be overwritten by child class"""

    width = pensize
    up = penup
    pu = penup
    pd = pendown
    down = pendown
    st = showturtle
    ht = hideturtle


klasa _TurtleImage(object):
    """Helper class: Datatype to store Turtle attributes
    """

    def __init__(self, screen, shapeIndex):
        self.screen = screen
        self._type = Nic
        self._setshape(shapeIndex)

    def _setshape(self, shapeIndex):
        screen = self.screen
        self.shapeIndex = shapeIndex
        jeżeli self._type == "polygon" == screen._shapes[shapeIndex]._type:
            zwróć
        jeżeli self._type == "image" == screen._shapes[shapeIndex]._type:
            zwróć
        jeżeli self._type w ["image", "polygon"]:
            screen._delete(self._item)
        albo_inaczej self._type == "compound":
            dla item w self._item:
                screen._delete(item)
        self._type = screen._shapes[shapeIndex]._type
        jeżeli self._type == "polygon":
            self._item = screen._createpoly()
        albo_inaczej self._type == "image":
            self._item = screen._createimage(screen._shapes["blank"]._data)
        albo_inaczej self._type == "compound":
            self._item = [screen._createpoly() dla item w
                                          screen._shapes[shapeIndex]._data]


klasa RawTurtle(TPen, TNavigator):
    """Animation part of the RawTurtle.
    Puts RawTurtle upon a TurtleScreen oraz provides tools for
    its animation.
    """
    screens = []

    def __init__(self, canvas=Nic,
                 shape=_CFG["shape"],
                 undobuffersize=_CFG["undobuffersize"],
                 visible=_CFG["visible"]):
        jeżeli isinstance(canvas, _Screen):
            self.screen = canvas
        albo_inaczej isinstance(canvas, TurtleScreen):
            jeżeli canvas nie w RawTurtle.screens:
                RawTurtle.screens.append(canvas)
            self.screen = canvas
        albo_inaczej isinstance(canvas, (ScrolledCanvas, Canvas)):
            dla screen w RawTurtle.screens:
                jeżeli screen.cv == canvas:
                    self.screen = screen
                    przerwij
            inaczej:
                self.screen = TurtleScreen(canvas)
                RawTurtle.screens.append(self.screen)
        inaczej:
            podnieś TurtleGraphicsError("bad canvas argument %s" % canvas)

        screen = self.screen
        TNavigator.__init__(self, screen.mode())
        TPen.__init__(self)
        screen._turtles.append(self)
        self.drawingLineItem = screen._createline()
        self.turtle = _TurtleImage(screen, shape)
        self._poly = Nic
        self._creatingPoly = Nieprawda
        self._fillitem = self._fillpath = Nic
        self._shown = visible
        self._hidden_from_screen = Nieprawda
        self.currentLineItem = screen._createline()
        self.currentLine = [self._position]
        self.items = [self.currentLineItem]
        self.stampItems = []
        self._undobuffersize = undobuffersize
        self.undobuffer = Tbuffer(undobuffersize)
        self._update()

    def reset(self):
        """Delete the turtle's drawings oraz restore its default values.

        No argument.

        Delete the turtle's drawings z the screen, re-center the turtle
        oraz set variables to the default values.

        Example (dla a Turtle instance named turtle):
        >>> turtle.position()
        (0.00,-22.00)
        >>> turtle.heading()
        100.0
        >>> turtle.reset()
        >>> turtle.position()
        (0.00,0.00)
        >>> turtle.heading()
        0.0
        """
        TNavigator.reset(self)
        TPen._reset(self)
        self._clear()
        self._drawturtle()
        self._update()

    def setundobuffer(self, size):
        """Set albo disable undobuffer.

        Argument:
        size -- an integer albo Nic

        If size jest an integer an empty undobuffer of given size jest installed.
        Size gives the maximum number of turtle-actions that can be undone
        by the undo() function.
        If size jest Nic, no undobuffer jest present.

        Example (dla a Turtle instance named turtle):
        >>> turtle.setundobuffer(42)
        """
        jeżeli size jest Nic albo size <= 0:
            self.undobuffer = Nic
        inaczej:
            self.undobuffer = Tbuffer(size)

    def undobufferentries(self):
        """Return count of entries w the undobuffer.

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> dopóki undobufferentries():
        ...     undo()
        """
        jeżeli self.undobuffer jest Nic:
            zwróć 0
        zwróć self.undobuffer.nr_of_items()

    def _clear(self):
        """Delete all of pen's drawings"""
        self._fillitem = self._fillpath = Nic
        dla item w self.items:
            self.screen._delete(item)
        self.currentLineItem = self.screen._createline()
        self.currentLine = []
        jeżeli self._drawing:
            self.currentLine.append(self._position)
        self.items = [self.currentLineItem]
        self.clearstamps()
        self.setundobuffer(self._undobuffersize)


    def clear(self):
        """Delete the turtle's drawings z the screen. Do nie move turtle.

        No arguments.

        Delete the turtle's drawings z the screen. Do nie move turtle.
        State oraz position of the turtle jako well jako drawings of other
        turtles are nie affected.

        Examples (dla a Turtle instance named turtle):
        >>> turtle.clear()
        """
        self._clear()
        self._update()

    def _update_data(self):
        self.screen._incrementudc()
        jeżeli self.screen._updatecounter != 0:
            zwróć
        jeżeli len(self.currentLine)>1:
            self.screen._drawline(self.currentLineItem, self.currentLine,
                                  self._pencolor, self._pensize)

    def _update(self):
        """Perform a Turtle-data update.
        """
        screen = self.screen
        jeżeli screen._tracing == 0:
            zwróć
        albo_inaczej screen._tracing == 1:
            self._update_data()
            self._drawturtle()
            screen._update()                  # TurtleScreenBase
            screen._delay(screen._delayvalue) # TurtleScreenBase
        inaczej:
            self._update_data()
            jeżeli screen._updatecounter == 0:
                dla t w screen.turtles():
                    t._drawturtle()
                screen._update()

    def _tracer(self, flag=Nic, delay=Nic):
        """Turns turtle animation on/off oraz set delay dla update drawings.

        Optional arguments:
        n -- nonnegative  integer
        delay -- nonnegative  integer

        If n jest given, only each n-th regular screen update jest really performed.
        (Can be used to accelerate the drawing of complex graphics.)
        Second arguments sets delay value (see RawTurtle.delay())

        Example (dla a Turtle instance named turtle):
        >>> turtle.tracer(8, 25)
        >>> dist = 2
        >>> dla i w range(200):
        ...     turtle.fd(dist)
        ...     turtle.rt(90)
        ...     dist += 2
        """
        zwróć self.screen.tracer(flag, delay)

    def _color(self, args):
        zwróć self.screen._color(args)

    def _colorstr(self, args):
        zwróć self.screen._colorstr(args)

    def _cc(self, args):
        """Convert colortriples to hexstrings.
        """
        jeżeli isinstance(args, str):
            zwróć args
        spróbuj:
            r, g, b = args
        wyjąwszy:
            podnieś TurtleGraphicsError("bad color arguments: %s" % str(args))
        jeżeli self.screen._colormode == 1.0:
            r, g, b = [round(255.0*x) dla x w (r, g, b)]
        jeżeli nie ((0 <= r <= 255) oraz (0 <= g <= 255) oraz (0 <= b <= 255)):
            podnieś TurtleGraphicsError("bad color sequence: %s" % str(args))
        zwróć "#%02x%02x%02x" % (r, g, b)

    def clone(self):
        """Create oraz zwróć a clone of the turtle.

        No argument.

        Create oraz zwróć a clone of the turtle przy same position, heading
        oraz turtle properties.

        Example (dla a Turtle instance named mick):
        mick = Turtle()
        joe = mick.clone()
        """
        screen = self.screen
        self._newLine(self._drawing)

        turtle = self.turtle
        self.screen = Nic
        self.turtle = Nic  # too make self deepcopy-able

        q = deepcopy(self)

        self.screen = screen
        self.turtle = turtle

        q.screen = screen
        q.turtle = _TurtleImage(screen, self.turtle.shapeIndex)

        screen._turtles.append(q)
        ttype = screen._shapes[self.turtle.shapeIndex]._type
        jeżeli ttype == "polygon":
            q.turtle._item = screen._createpoly()
        albo_inaczej ttype == "image":
            q.turtle._item = screen._createimage(screen._shapes["blank"]._data)
        albo_inaczej ttype == "compound":
            q.turtle._item = [screen._createpoly() dla item w
                              screen._shapes[self.turtle.shapeIndex]._data]
        q.currentLineItem = screen._createline()
        q._update()
        zwróć q

    def shape(self, name=Nic):
        """Set turtle shape to shape przy given name / zwróć current shapename.

        Optional argument:
        name -- a string, which jest a valid shapename

        Set turtle shape to shape przy given name or, jeżeli name jest nie given,
        zwróć name of current shape.
        Shape przy name must exist w the TurtleScreen's shape dictionary.
        Initially there are the following polygon shapes:
        'arrow', 'turtle', 'circle', 'square', 'triangle', 'classic'.
        To learn about how to deal przy shapes see Screen-method register_shape.

        Example (dla a Turtle instance named turtle):
        >>> turtle.shape()
        'arrow'
        >>> turtle.shape("turtle")
        >>> turtle.shape()
        'turtle'
        """
        jeżeli name jest Nic:
            zwróć self.turtle.shapeIndex
        jeżeli nie name w self.screen.getshapes():
            podnieś TurtleGraphicsError("There jest no shape named %s" % name)
        self.turtle._setshape(name)
        self._update()

    def shapesize(self, stretch_wid=Nic, stretch_len=Nic, outline=Nic):
        """Set/return turtle's stretchfactors/outline. Set resizemode to "user".

        Optional arguments:
           stretch_wid : positive number
           stretch_len : positive number
           outline  : positive number

        Return albo set the pen's attributes x/y-stretchfactors and/or outline.
        Set resizemode to "user".
        If oraz only jeżeli resizemode jest set to "user", the turtle will be displayed
        stretched according to its stretchfactors:
        stretch_wid jest stretchfactor perpendicular to orientation
        stretch_len jest stretchfactor w direction of turtles orientation.
        outline determines the width of the shapes's outline.

        Examples (dla a Turtle instance named turtle):
        >>> turtle.resizemode("user")
        >>> turtle.shapesize(5, 5, 12)
        >>> turtle.shapesize(outline=8)
        """
        jeżeli stretch_wid jest stretch_len jest outline jest Nic:
            stretch_wid, stretch_len = self._stretchfactor
            zwróć stretch_wid, stretch_len, self._outlinewidth
        jeżeli stretch_wid == 0 albo stretch_len == 0:
            podnieś TurtleGraphicsError("stretch_wid/stretch_len must nie be zero")
        jeżeli stretch_wid jest nie Nic:
            jeżeli stretch_len jest Nic:
                stretchfactor = stretch_wid, stretch_wid
            inaczej:
                stretchfactor = stretch_wid, stretch_len
        albo_inaczej stretch_len jest nie Nic:
            stretchfactor = self._stretchfactor[0], stretch_len
        inaczej:
            stretchfactor = self._stretchfactor
        jeżeli outline jest Nic:
            outline = self._outlinewidth
        self.pen(resizemode="user",
                 stretchfactor=stretchfactor, outline=outline)

    def shearfactor(self, shear=Nic):
        """Set albo zwróć the current shearfactor.

        Optional argument: shear -- number, tangent of the shear angle

        Shear the turtleshape according to the given shearfactor shear,
        which jest the tangent of the shear angle. DO NOT change the
        turtle's heading (direction of movement).
        If shear jest nie given: zwróć the current shearfactor, i. e. the
        tangent of the shear angle, by which lines parallel to the
        heading of the turtle are sheared.

        Examples (dla a Turtle instance named turtle):
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.shearfactor(0.5)
        >>> turtle.shearfactor()
        >>> 0.5
        """
        jeżeli shear jest Nic:
            zwróć self._shearfactor
        self.pen(resizemode="user", shearfactor=shear)

    def settiltangle(self, angle):
        """Rotate the turtleshape to point w the specified direction

        Argument: angle -- number

        Rotate the turtleshape to point w the direction specified by angle,
        regardless of its current tilt-angle. DO NOT change the turtle's
        heading (direction of movement).


        Examples (dla a Turtle instance named turtle):
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.settiltangle(45)
        >>> stamp()
        >>> turtle.fd(50)
        >>> turtle.settiltangle(-45)
        >>> stamp()
        >>> turtle.fd(50)
        """
        tilt = -angle * self._degreesPerAU * self._angleOrient
        tilt = (tilt * math.pi / 180.0) % (2*math.pi)
        self.pen(resizemode="user", tilt=tilt)

    def tiltangle(self, angle=Nic):
        """Set albo zwróć the current tilt-angle.

        Optional argument: angle -- number

        Rotate the turtleshape to point w the direction specified by angle,
        regardless of its current tilt-angle. DO NOT change the turtle's
        heading (direction of movement).
        If angle jest nie given: zwróć the current tilt-angle, i. e. the angle
        between the orientation of the turtleshape oraz the heading of the
        turtle (its direction of movement).

        Deprecated since Python 3.1

        Examples (dla a Turtle instance named turtle):
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.tilt(45)
        >>> turtle.tiltangle()
        """
        jeżeli angle jest Nic:
            tilt = -self._tilt * (180.0/math.pi) * self._angleOrient
            zwróć (tilt / self._degreesPerAU) % self._fullcircle
        inaczej:
            self.settiltangle(angle)

    def tilt(self, angle):
        """Rotate the turtleshape by angle.

        Argument:
        angle - a number

        Rotate the turtleshape by angle z its current tilt-angle,
        but do NOT change the turtle's heading (direction of movement).

        Examples (dla a Turtle instance named turtle):
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.tilt(30)
        >>> turtle.fd(50)
        >>> turtle.tilt(30)
        >>> turtle.fd(50)
        """
        self.settiltangle(angle + self.tiltangle())

    def shapetransform(self, t11=Nic, t12=Nic, t21=Nic, t22=Nic):
        """Set albo zwróć the current transformation matrix of the turtle shape.

        Optional arguments: t11, t12, t21, t22 -- numbers.

        If none of the matrix elements are given, zwróć the transformation
        matrix.
        Otherwise set the given elements oraz transform the turtleshape
        according to the matrix consisting of first row t11, t12 oraz
        second row t21, 22.
        Modify stretchfactor, shearfactor oraz tiltangle according to the
        given matrix.

        Examples (dla a Turtle instance named turtle):
        >>> turtle.shape("square")
        >>> turtle.shapesize(4,2)
        >>> turtle.shearfactor(-0.5)
        >>> turtle.shapetransform()
        (4.0, -1.0, -0.0, 2.0)
        """
        jeżeli t11 jest t12 jest t21 jest t22 jest Nic:
            zwróć self._shapetrafo
        m11, m12, m21, m22 = self._shapetrafo
        jeżeli t11 jest nie Nic: m11 = t11
        jeżeli t12 jest nie Nic: m12 = t12
        jeżeli t21 jest nie Nic: m21 = t21
        jeżeli t22 jest nie Nic: m22 = t22
        jeżeli t11 * t22 - t12 * t21 == 0:
            podnieś TurtleGraphicsError("Bad shape transform matrix: must nie be singular")
        self._shapetrafo = (m11, m12, m21, m22)
        alfa = math.atan2(-m21, m11) % (2 * math.pi)
        sa, ca = math.sin(alfa), math.cos(alfa)
        a11, a12, a21, a22 = (ca*m11 - sa*m21, ca*m12 - sa*m22,
                              sa*m11 + ca*m21, sa*m12 + ca*m22)
        self._stretchfactor = a11, a22
        self._shearfactor = a12/a22
        self._tilt = alfa
        self.pen(resizemode="user")


    def _polytrafo(self, poly):
        """Computes transformed polygon shapes z a shape
        according to current position oraz heading.
        """
        screen = self.screen
        p0, p1 = self._position
        e0, e1 = self._orient
        e = Vec2D(e0, e1 * screen.yscale / screen.xscale)
        e0, e1 = (1.0 / abs(e)) * e
        zwróć [(p0+(e1*x+e0*y)/screen.xscale, p1+(-e0*x+e1*y)/screen.yscale)
                                                           dla (x, y) w poly]

    def get_shapepoly(self):
        """Return the current shape polygon jako tuple of coordinate pairs.

        No argument.

        Examples (dla a Turtle instance named turtle):
        >>> turtle.shape("square")
        >>> turtle.shapetransform(4, -1, 0, 2)
        >>> turtle.get_shapepoly()
        ((50, -20), (30, 20), (-50, 20), (-30, -20))

        """
        shape = self.screen._shapes[self.turtle.shapeIndex]
        jeżeli shape._type == "polygon":
            zwróć self._getshapepoly(shape._data, shape._type == "compound")
        # inaczej zwróć Nic

    def _getshapepoly(self, polygon, compound=Nieprawda):
        """Calculate transformed shape polygon according to resizemode
        oraz shapetransform.
        """
        jeżeli self._resizemode == "user" albo compound:
            t11, t12, t21, t22 = self._shapetrafo
        albo_inaczej self._resizemode == "auto":
            l = max(1, self._pensize/5.0)
            t11, t12, t21, t22 = l, 0, 0, l
        albo_inaczej self._resizemode == "noresize":
            zwróć polygon
        zwróć tuple([(t11*x + t12*y, t21*x + t22*y) dla (x, y) w polygon])

    def _drawturtle(self):
        """Manages the correct rendering of the turtle przy respect to
        its shape, resizemode, stretch oraz tilt etc."""
        screen = self.screen
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        titem = self.turtle._item
        jeżeli self._shown oraz screen._updatecounter == 0 oraz screen._tracing > 0:
            self._hidden_from_screen = Nieprawda
            tshape = shape._data
            jeżeli ttype == "polygon":
                jeżeli self._resizemode == "noresize": w = 1
                albo_inaczej self._resizemode == "auto": w = self._pensize
                inaczej: w =self._outlinewidth
                shape = self._polytrafo(self._getshapepoly(tshape))
                fc, oc = self._fillcolor, self._pencolor
                screen._drawpoly(titem, shape, fill=fc, outline=oc,
                                                      width=w, top=Prawda)
            albo_inaczej ttype == "image":
                screen._drawimage(titem, self._position, tshape)
            albo_inaczej ttype == "compound":
                dla item, (poly, fc, oc) w zip(titem, tshape):
                    poly = self._polytrafo(self._getshapepoly(poly, Prawda))
                    screen._drawpoly(item, poly, fill=self._cc(fc),
                                     outline=self._cc(oc), width=self._outlinewidth, top=Prawda)
        inaczej:
            jeżeli self._hidden_from_screen:
                zwróć
            jeżeli ttype == "polygon":
                screen._drawpoly(titem, ((0, 0), (0, 0), (0, 0)), "", "")
            albo_inaczej ttype == "image":
                screen._drawimage(titem, self._position,
                                          screen._shapes["blank"]._data)
            albo_inaczej ttype == "compound":
                dla item w titem:
                    screen._drawpoly(item, ((0, 0), (0, 0), (0, 0)), "", "")
            self._hidden_from_screen = Prawda

##############################  stamp stuff  ###############################

    def stamp(self):
        """Stamp a copy of the turtleshape onto the canvas oraz zwróć its id.

        No argument.

        Stamp a copy of the turtle shape onto the canvas at the current
        turtle position. Return a stamp_id dla that stamp, which can be
        used to delete it by calling clearstamp(stamp_id).

        Example (dla a Turtle instance named turtle):
        >>> turtle.color("blue")
        >>> turtle.stamp()
        13
        >>> turtle.fd(50)
        """
        screen = self.screen
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        tshape = shape._data
        jeżeli ttype == "polygon":
            stitem = screen._createpoly()
            jeżeli self._resizemode == "noresize": w = 1
            albo_inaczej self._resizemode == "auto": w = self._pensize
            inaczej: w =self._outlinewidth
            shape = self._polytrafo(self._getshapepoly(tshape))
            fc, oc = self._fillcolor, self._pencolor
            screen._drawpoly(stitem, shape, fill=fc, outline=oc,
                                                  width=w, top=Prawda)
        albo_inaczej ttype == "image":
            stitem = screen._createimage("")
            screen._drawimage(stitem, self._position, tshape)
        albo_inaczej ttype == "compound":
            stitem = []
            dla element w tshape:
                item = screen._createpoly()
                stitem.append(item)
            stitem = tuple(stitem)
            dla item, (poly, fc, oc) w zip(stitem, tshape):
                poly = self._polytrafo(self._getshapepoly(poly, Prawda))
                screen._drawpoly(item, poly, fill=self._cc(fc),
                                 outline=self._cc(oc), width=self._outlinewidth, top=Prawda)
        self.stampItems.append(stitem)
        self.undobuffer.push(("stamp", stitem))
        zwróć stitem

    def _clearstamp(self, stampid):
        """does the work dla clearstamp() oraz clearstamps()
        """
        jeżeli stampid w self.stampItems:
            jeżeli isinstance(stampid, tuple):
                dla subitem w stampid:
                    self.screen._delete(subitem)
            inaczej:
                self.screen._delete(stampid)
            self.stampItems.remove(stampid)
        # Delete stampitem z undobuffer jeżeli necessary
        # jeżeli clearstamp jest called directly.
        item = ("stamp", stampid)
        buf = self.undobuffer
        jeżeli item nie w buf.buffer:
            zwróć
        index = buf.buffer.index(item)
        buf.buffer.remove(item)
        jeżeli index <= buf.ptr:
            buf.ptr = (buf.ptr - 1) % buf.bufsize
        buf.buffer.insert((buf.ptr+1)%buf.bufsize, [Nic])

    def clearstamp(self, stampid):
        """Delete stamp przy given stampid

        Argument:
        stampid - an integer, must be zwróć value of previous stamp() call.

        Example (dla a Turtle instance named turtle):
        >>> turtle.color("blue")
        >>> astamp = turtle.stamp()
        >>> turtle.fd(50)
        >>> turtle.clearstamp(astamp)
        """
        self._clearstamp(stampid)
        self._update()

    def clearstamps(self, n=Nic):
        """Delete all albo first/last n of turtle's stamps.

        Optional argument:
        n -- an integer

        If n jest Nic, delete all of pen's stamps,
        inaczej jeżeli n > 0 delete first n stamps
        inaczej jeżeli n < 0 delete last n stamps.

        Example (dla a Turtle instance named turtle):
        >>> dla i w range(8):
        ...     turtle.stamp(); turtle.fd(30)
        ...
        >>> turtle.clearstamps(2)
        >>> turtle.clearstamps(-2)
        >>> turtle.clearstamps()
        """
        jeżeli n jest Nic:
            toDelete = self.stampItems[:]
        albo_inaczej n >= 0:
            toDelete = self.stampItems[:n]
        inaczej:
            toDelete = self.stampItems[n:]
        dla item w toDelete:
            self._clearstamp(item)
        self._update()

    def _goto(self, end):
        """Move the pen to the point end, thereby drawing a line
        jeżeli pen jest down. All other methods dla turtle movement depend
        on this one.
        """
        ## Version przy undo-stuff
        go_modes = ( self._drawing,
                     self._pencolor,
                     self._pensize,
                     isinstance(self._fillpath, list))
        screen = self.screen
        undo_entry = ("go", self._position, end, go_modes,
                      (self.currentLineItem,
                      self.currentLine[:],
                      screen._pointlist(self.currentLineItem),
                      self.items[:])
                      )
        jeżeli self.undobuffer:
            self.undobuffer.push(undo_entry)
        start = self._position
        jeżeli self._speed oraz screen._tracing == 1:
            diff = (end-start)
            diffsq = (diff[0]*screen.xscale)**2 + (diff[1]*screen.yscale)**2
            nhops = 1+int((diffsq**0.5)/(3*(1.1**self._speed)*self._speed))
            delta = diff * (1.0/nhops)
            dla n w range(1, nhops):
                jeżeli n == 1:
                    top = Prawda
                inaczej:
                    top = Nieprawda
                self._position = start + delta * n
                jeżeli self._drawing:
                    screen._drawline(self.drawingLineItem,
                                     (start, self._position),
                                     self._pencolor, self._pensize, top)
                self._update()
            jeżeli self._drawing:
                screen._drawline(self.drawingLineItem, ((0, 0), (0, 0)),
                                               fill="", width=self._pensize)
        # Turtle now at end,
        jeżeli self._drawing: # now update currentLine
            self.currentLine.append(end)
        jeżeli isinstance(self._fillpath, list):
            self._fillpath.append(end)
        ######    vererbung!!!!!!!!!!!!!!!!!!!!!!
        self._position = end
        jeżeli self._creatingPoly:
            self._poly.append(end)
        jeżeli len(self.currentLine) > 42: # 42! answer to the ultimate question
                                       # of life, the universe oraz everything
            self._newLine()
        self._update() #count=Prawda)

    def _undogoto(self, entry):
        """Reverse a _goto. Used dla undo()
        """
        old, new, go_modes, coodata = entry
        drawing, pc, ps, filling = go_modes
        cLI, cL, pl, items = coodata
        screen = self.screen
        jeżeli abs(self._position - new) > 0.5:
            print ("undogoto: HALLO-DA-STIMMT-WAS-NICHT!")
        # restore former situation
        self.currentLineItem = cLI
        self.currentLine = cL

        jeżeli pl == [(0, 0), (0, 0)]:
            usepc = ""
        inaczej:
            usepc = pc
        screen._drawline(cLI, pl, fill=usepc, width=ps)

        todelete = [i dla i w self.items jeżeli (i nie w items) oraz
                                       (screen._type(i) == "line")]
        dla i w todelete:
            screen._delete(i)
            self.items.remove(i)

        start = old
        jeżeli self._speed oraz screen._tracing == 1:
            diff = old - new
            diffsq = (diff[0]*screen.xscale)**2 + (diff[1]*screen.yscale)**2
            nhops = 1+int((diffsq**0.5)/(3*(1.1**self._speed)*self._speed))
            delta = diff * (1.0/nhops)
            dla n w range(1, nhops):
                jeżeli n == 1:
                    top = Prawda
                inaczej:
                    top = Nieprawda
                self._position = new + delta * n
                jeżeli drawing:
                    screen._drawline(self.drawingLineItem,
                                     (start, self._position),
                                     pc, ps, top)
                self._update()
            jeżeli drawing:
                screen._drawline(self.drawingLineItem, ((0, 0), (0, 0)),
                                               fill="", width=ps)
        # Turtle now at position old,
        self._position = old
        ##  jeżeli undo jest done during creating a polygon, the last vertex
        ##  will be deleted. jeżeli the polygon jest entirely deleted,
        ##  creatingPoly will be set to Nieprawda.
        ##  Polygons created before the last one will nie be affected by undo()
        jeżeli self._creatingPoly:
            jeżeli len(self._poly) > 0:
                self._poly.pop()
            jeżeli self._poly == []:
                self._creatingPoly = Nieprawda
                self._poly = Nic
        jeżeli filling:
            jeżeli self._fillpath == []:
                self._fillpath = Nic
                print("Unwahrscheinlich w _undogoto!")
            albo_inaczej self._fillpath jest nie Nic:
                self._fillpath.pop()
        self._update() #count=Prawda)

    def _rotate(self, angle):
        """Turns pen clockwise by angle.
        """
        jeżeli self.undobuffer:
            self.undobuffer.push(("rot", angle, self._degreesPerAU))
        angle *= self._degreesPerAU
        neworient = self._orient.rotate(angle)
        tracing = self.screen._tracing
        jeżeli tracing == 1 oraz self._speed > 0:
            anglevel = 3.0 * self._speed
            steps = 1 + int(abs(angle)/anglevel)
            delta = 1.0*angle/steps
            dla _ w range(steps):
                self._orient = self._orient.rotate(delta)
                self._update()
        self._orient = neworient
        self._update()

    def _newLine(self, usePos=Prawda):
        """Closes current line item oraz starts a new one.
           Remark: jeżeli current line became too long, animation
           performance (via _drawline) slowed down considerably.
        """
        jeżeli len(self.currentLine) > 1:
            self.screen._drawline(self.currentLineItem, self.currentLine,
                                      self._pencolor, self._pensize)
            self.currentLineItem = self.screen._createline()
            self.items.append(self.currentLineItem)
        inaczej:
            self.screen._drawline(self.currentLineItem, top=Prawda)
        self.currentLine = []
        jeżeli usePos:
            self.currentLine = [self._position]

    def filling(self):
        """Return fillstate (Prawda jeżeli filling, Nieprawda inaczej).

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> turtle.begin_fill()
        >>> jeżeli turtle.filling():
        ...     turtle.pensize(5)
        ... inaczej:
        ...     turtle.pensize(3)
        """
        zwróć isinstance(self._fillpath, list)

    def begin_fill(self):
        """Called just before drawing a shape to be filled.

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> turtle.color("black", "red")
        >>> turtle.begin_fill()
        >>> turtle.circle(60)
        >>> turtle.end_fill()
        """
        jeżeli nie self.filling():
            self._fillitem = self.screen._createpoly()
            self.items.append(self._fillitem)
        self._fillpath = [self._position]
        self._newLine()
        jeżeli self.undobuffer:
            self.undobuffer.push(("beginfill", self._fillitem))
        self._update()


    def end_fill(self):
        """Fill the shape drawn after the call begin_fill().

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> turtle.color("black", "red")
        >>> turtle.begin_fill()
        >>> turtle.circle(60)
        >>> turtle.end_fill()
        """
        jeżeli self.filling():
            jeżeli len(self._fillpath) > 2:
                self.screen._drawpoly(self._fillitem, self._fillpath,
                                      fill=self._fillcolor)
                jeżeli self.undobuffer:
                    self.undobuffer.push(("dofill", self._fillitem))
            self._fillitem = self._fillpath = Nic
            self._update()

    def dot(self, size=Nic, *color):
        """Draw a dot przy diameter size, using color.

        Optional arguments:
        size -- an integer >= 1 (jeżeli given)
        color -- a colorstring albo a numeric color tuple

        Draw a circular dot przy diameter size, using color.
        If size jest nie given, the maximum of pensize+4 oraz 2*pensize jest used.

        Example (dla a Turtle instance named turtle):
        >>> turtle.dot()
        >>> turtle.fd(50); turtle.dot(20, "blue"); turtle.fd(50)
        """
        jeżeli nie color:
            jeżeli isinstance(size, (str, tuple)):
                color = self._colorstr(size)
                size = self._pensize + max(self._pensize, 4)
            inaczej:
                color = self._pencolor
                jeżeli nie size:
                    size = self._pensize + max(self._pensize, 4)
        inaczej:
            jeżeli size jest Nic:
                size = self._pensize + max(self._pensize, 4)
            color = self._colorstr(color)
        jeżeli hasattr(self.screen, "_dot"):
            item = self.screen._dot(self._position, size, color)
            self.items.append(item)
            jeżeli self.undobuffer:
                self.undobuffer.push(("dot", item))
        inaczej:
            pen = self.pen()
            jeżeli self.undobuffer:
                self.undobuffer.push(["seq"])
                self.undobuffer.cumulate = Prawda
            spróbuj:
                jeżeli self.resizemode() == 'auto':
                    self.ht()
                self.pendown()
                self.pensize(size)
                self.pencolor(color)
                self.forward(0)
            w_końcu:
                self.pen(pen)
            jeżeli self.undobuffer:
                self.undobuffer.cumulate = Nieprawda

    def _write(self, txt, align, font):
        """Performs the writing dla write()
        """
        item, end = self.screen._write(self._position, txt, align, font,
                                                          self._pencolor)
        self.items.append(item)
        jeżeli self.undobuffer:
            self.undobuffer.push(("wri", item))
        zwróć end

    def write(self, arg, move=Nieprawda, align="left", font=("Arial", 8, "normal")):
        """Write text at the current turtle position.

        Arguments:
        arg -- info, which jest to be written to the TurtleScreen
        move (optional) -- Prawda/Nieprawda
        align (optional) -- one of the strings "left", "center" albo right"
        font (optional) -- a triple (fontname, fontsize, fonttype)

        Write text - the string representation of arg - at the current
        turtle position according to align ("left", "center" albo right")
        oraz przy the given font.
        If move jest Prawda, the pen jest moved to the bottom-right corner
        of the text. By default, move jest Nieprawda.

        Example (dla a Turtle instance named turtle):
        >>> turtle.write('Home = ', Prawda, align="center")
        >>> turtle.write((0,0), Prawda)
        """
        jeżeli self.undobuffer:
            self.undobuffer.push(["seq"])
            self.undobuffer.cumulate = Prawda
        end = self._write(str(arg), align.lower(), font)
        jeżeli move:
            x, y = self.pos()
            self.setpos(end, y)
        jeżeli self.undobuffer:
            self.undobuffer.cumulate = Nieprawda

    def begin_poly(self):
        """Start recording the vertices of a polygon.

        No argument.

        Start recording the vertices of a polygon. Current turtle position
        jest first point of polygon.

        Example (dla a Turtle instance named turtle):
        >>> turtle.begin_poly()
        """
        self._poly = [self._position]
        self._creatingPoly = Prawda

    def end_poly(self):
        """Stop recording the vertices of a polygon.

        No argument.

        Stop recording the vertices of a polygon. Current turtle position jest
        last point of polygon. This will be connected przy the first point.

        Example (dla a Turtle instance named turtle):
        >>> turtle.end_poly()
        """
        self._creatingPoly = Nieprawda

    def get_poly(self):
        """Return the lastly recorded polygon.

        No argument.

        Example (dla a Turtle instance named turtle):
        >>> p = turtle.get_poly()
        >>> turtle.register_shape("myFavouriteShape", p)
        """
        ## check jeżeli there jest any poly?
        jeżeli self._poly jest nie Nic:
            zwróć tuple(self._poly)

    def getscreen(self):
        """Return the TurtleScreen object, the turtle jest drawing  on.

        No argument.

        Return the TurtleScreen object, the turtle jest drawing  on.
        So TurtleScreen-methods can be called dla that object.

        Example (dla a Turtle instance named turtle):
        >>> ts = turtle.getscreen()
        >>> ts
        <turtle.TurtleScreen object at 0x0106B770>
        >>> ts.bgcolor("pink")
        """
        zwróć self.screen

    def getturtle(self):
        """Return the Turtleobject itself.

        No argument.

        Only reasonable use: jako a function to zwróć the 'anonymous turtle':

        Example:
        >>> pet = getturtle()
        >>> pet.fd(50)
        >>> pet
        <turtle.Turtle object at 0x0187D810>
        >>> turtles()
        [<turtle.Turtle object at 0x0187D810>]
        """
        zwróć self

    getpen = getturtle


    ################################################################
    ### screen oriented methods recurring to methods of TurtleScreen
    ################################################################

    def _delay(self, delay=Nic):
        """Set delay value which determines speed of turtle animation.
        """
        zwróć self.screen.delay(delay)

    def onclick(self, fun, btn=1, add=Nic):
        """Bind fun to mouse-click event on this turtle on canvas.

        Arguments:
        fun --  a function przy two arguments, to which will be assigned
                the coordinates of the clicked point on the canvas.
        num --  number of the mouse-button defaults to 1 (left mouse button).
        add --  Prawda albo Nieprawda. If Prawda, new binding will be added, otherwise
                it will replace a former binding.

        Example dla the anonymous turtle, i. e. the procedural way:

        >>> def turn(x, y):
        ...     left(360)
        ...
        >>> onclick(turn)  # Now clicking into the turtle will turn it.
        >>> onclick(Nic)  # event-binding will be removed
        """
        self.screen._onclick(self.turtle._item, fun, btn, add)
        self._update()

    def onrelease(self, fun, btn=1, add=Nic):
        """Bind fun to mouse-button-release event on this turtle on canvas.

        Arguments:
        fun -- a function przy two arguments, to which will be assigned
                the coordinates of the clicked point on the canvas.
        num --  number of the mouse-button defaults to 1 (left mouse button).

        Example (dla a MyTurtle instance named joe):
        >>> klasa MyTurtle(Turtle):
        ...     def glow(self,x,y):
        ...             self.fillcolor("red")
        ...     def unglow(self,x,y):
        ...             self.fillcolor("")
        ...
        >>> joe = MyTurtle()
        >>> joe.onclick(joe.glow)
        >>> joe.onrelease(joe.unglow)

        Clicking on joe turns fillcolor red, unclicking turns it to
        transparent.
        """
        self.screen._onrelease(self.turtle._item, fun, btn, add)
        self._update()

    def ondrag(self, fun, btn=1, add=Nic):
        """Bind fun to mouse-move event on this turtle on canvas.

        Arguments:
        fun -- a function przy two arguments, to which will be assigned
               the coordinates of the clicked point on the canvas.
        num -- number of the mouse-button defaults to 1 (left mouse button).

        Every sequence of mouse-move-events on a turtle jest preceded by a
        mouse-click event on that turtle.

        Example (dla a Turtle instance named turtle):
        >>> turtle.ondrag(turtle.goto)

        Subsequently clicking oraz dragging a Turtle will move it
        across the screen thereby producing handdrawings (jeżeli pen jest
        down).
        """
        self.screen._ondrag(self.turtle._item, fun, btn, add)


    def _undo(self, action, data):
        """Does the main part of the work dla undo()
        """
        jeżeli self.undobuffer jest Nic:
            zwróć
        jeżeli action == "rot":
            angle, degPAU = data
            self._rotate(-angle*degPAU/self._degreesPerAU)
            dummy = self.undobuffer.pop()
        albo_inaczej action == "stamp":
            stitem = data[0]
            self.clearstamp(stitem)
        albo_inaczej action == "go":
            self._undogoto(data)
        albo_inaczej action w ["wri", "dot"]:
            item = data[0]
            self.screen._delete(item)
            self.items.remove(item)
        albo_inaczej action == "dofill":
            item = data[0]
            self.screen._drawpoly(item, ((0, 0),(0, 0),(0, 0)),
                                  fill="", outline="")
        albo_inaczej action == "beginfill":
            item = data[0]
            self._fillitem = self._fillpath = Nic
            jeżeli item w self.items:
                self.screen._delete(item)
                self.items.remove(item)
        albo_inaczej action == "pen":
            TPen.pen(self, data[0])
            self.undobuffer.pop()

    def undo(self):
        """undo (repeatedly) the last turtle action.

        No argument.

        undo (repeatedly) the last turtle action.
        Number of available undo actions jest determined by the size of
        the undobuffer.

        Example (dla a Turtle instance named turtle):
        >>> dla i w range(4):
        ...     turtle.fd(50); turtle.lt(80)
        ...
        >>> dla i w range(8):
        ...     turtle.undo()
        ...
        """
        jeżeli self.undobuffer jest Nic:
            zwróć
        item = self.undobuffer.pop()
        action = item[0]
        data = item[1:]
        jeżeli action == "seq":
            dopóki data:
                item = data.pop()
                self._undo(item[0], item[1:])
        inaczej:
            self._undo(action, data)

    turtlesize = shapesize

RawPen = RawTurtle

###  Screen - Singleton  ########################

def Screen():
    """Return the singleton screen object.
    If none exists at the moment, create a new one oraz zwróć it,
    inaczej zwróć the existing one."""
    jeżeli Turtle._screen jest Nic:
        Turtle._screen = _Screen()
    zwróć Turtle._screen

klasa _Screen(TurtleScreen):

    _root = Nic
    _canvas = Nic
    _title = _CFG["title"]

    def __init__(self):
        # XXX there jest no need dla this code to be conditional,
        # jako there will be only a single _Screen instance, anyway
        # XXX actually, the turtle demo jest injecting root window,
        # so perhaps the conditional creation of a root should be
        # preserved (perhaps by dalejing it jako an optional parameter)
        jeżeli _Screen._root jest Nic:
            _Screen._root = self._root = _Root()
            self._root.title(_Screen._title)
            self._root.ondestroy(self._destroy)
        jeżeli _Screen._canvas jest Nic:
            width = _CFG["width"]
            height = _CFG["height"]
            canvwidth = _CFG["canvwidth"]
            canvheight = _CFG["canvheight"]
            leftright = _CFG["leftright"]
            topbottom = _CFG["topbottom"]
            self._root.setupcanvas(width, height, canvwidth, canvheight)
            _Screen._canvas = self._root._getcanvas()
            TurtleScreen.__init__(self, _Screen._canvas)
            self.setup(width, height, leftright, topbottom)

    def setup(self, width=_CFG["width"], height=_CFG["height"],
              startx=_CFG["leftright"], starty=_CFG["topbottom"]):
        """ Set the size oraz position of the main window.

        Arguments:
        width: jako integer a size w pixels, jako float a fraction of the screen.
          Default jest 50% of screen.
        height: jako integer the height w pixels, jako float a fraction of the
          screen. Default jest 75% of screen.
        startx: jeżeli positive, starting position w pixels z the left
          edge of the screen, jeżeli negative z the right edge
          Default, startx=Nic jest to center window horizontally.
        starty: jeżeli positive, starting position w pixels z the top
          edge of the screen, jeżeli negative z the bottom edge
          Default, starty=Nic jest to center window vertically.

        Examples (dla a Screen instance named screen):
        >>> screen.setup (width=200, height=200, startx=0, starty=0)

        sets window to 200x200 pixels, w upper left of screen

        >>> screen.setup(width=.75, height=0.5, startx=Nic, starty=Nic)

        sets window to 75% of screen by 50% of screen oraz centers
        """
        jeżeli nie hasattr(self._root, "set_geometry"):
            zwróć
        sw = self._root.win_width()
        sh = self._root.win_height()
        jeżeli isinstance(width, float) oraz 0 <= width <= 1:
            width = sw*width
        jeżeli startx jest Nic:
            startx = (sw - width) / 2
        jeżeli isinstance(height, float) oraz 0 <= height <= 1:
            height = sh*height
        jeżeli starty jest Nic:
            starty = (sh - height) / 2
        self._root.set_geometry(width, height, startx, starty)
        self.update()

    def title(self, titlestring):
        """Set title of turtle-window

        Argument:
        titlestring -- a string, to appear w the titlebar of the
                       turtle graphics window.

        This jest a method of Screen-class. Not available dla TurtleScreen-
        objects.

        Example (dla a Screen instance named screen):
        >>> screen.title("Welcome to the turtle-zoo!")
        """
        jeżeli _Screen._root jest nie Nic:
            _Screen._root.title(titlestring)
        _Screen._title = titlestring

    def _destroy(self):
        root = self._root
        jeżeli root jest _Screen._root:
            Turtle._pen = Nic
            Turtle._screen = Nic
            _Screen._root = Nic
            _Screen._canvas = Nic
        TurtleScreen._RUNNING = Nieprawda
        root.destroy()

    def bye(self):
        """Shut the turtlegraphics window.

        Example (dla a TurtleScreen instance named screen):
        >>> screen.bye()
        """
        self._destroy()

    def exitonclick(self):
        """Go into mainloop until the mouse jest clicked.

        No arguments.

        Bind bye() method to mouseclick on TurtleScreen.
        If "using_IDLE" - value w configuration dictionary jest Nieprawda
        (default value), enter mainloop.
        If IDLE przy -n switch (no subprocess) jest used, this value should be
        set to Prawda w turtle.cfg. In this case IDLE's mainloop
        jest active also dla the client script.

        This jest a method of the Screen-class oraz nie available for
        TurtleScreen instances.

        Example (dla a Screen instance named screen):
        >>> screen.exitonclick()

        """
        def exitGracefully(x, y):
            """Screen.bye() przy two dummy-parameters"""
            self.bye()
        self.onclick(exitGracefully)
        jeżeli _CFG["using_IDLE"]:
            zwróć
        spróbuj:
            mainloop()
        wyjąwszy AttributeError:
            exit(0)

klasa Turtle(RawTurtle):
    """RawTurtle auto-creating (scrolled) canvas.

    When a Turtle object jest created albo a function derived z some
    Turtle method jest called a TurtleScreen object jest automatically created.
    """
    _pen = Nic
    _screen = Nic

    def __init__(self,
                 shape=_CFG["shape"],
                 undobuffersize=_CFG["undobuffersize"],
                 visible=_CFG["visible"]):
        jeżeli Turtle._screen jest Nic:
            Turtle._screen = Screen()
        RawTurtle.__init__(self, Turtle._screen,
                           shape=shape,
                           undobuffersize=undobuffersize,
                           visible=visible)

Pen = Turtle

def write_docstringdict(filename="turtle_docstringdict"):
    """Create oraz write docstring-dictionary to file.

    Optional argument:
    filename -- a string, used jako filename
                default value jest turtle_docstringdict

    Has to be called explicitly, (nie used by the turtle-graphics classes)
    The docstring dictionary will be written to the Python script <filname>.py
    It jest intended to serve jako a template dla translation of the docstrings
    into different languages.
    """
    docsdict = {}

    dla methodname w _tg_screen_functions:
        key = "_Screen."+methodname
        docsdict[key] = eval(key).__doc__
    dla methodname w _tg_turtle_functions:
        key = "Turtle."+methodname
        docsdict[key] = eval(key).__doc__

    przy open("%s.py" % filename,"w") jako f:
        keys = sorted([x dla x w docsdict.keys()
                            jeżeli x.split('.')[1] nie w _alias_list])
        f.write('docsdict = {\n\n')
        dla key w keys[:-1]:
            f.write('%s :\n' % repr(key))
            f.write('        """%s\n""",\n\n' % docsdict[key])
        key = keys[-1]
        f.write('%s :\n' % repr(key))
        f.write('        """%s\n"""\n\n' % docsdict[key])
        f.write("}\n")
        f.close()

def read_docstrings(lang):
    """Read w docstrings z lang-specific docstring dictionary.

    Transfer docstrings, translated to lang, z a dictionary-file
    to the methods of classes Screen oraz Turtle oraz - w revised form -
    to the corresponding functions.
    """
    modname = "turtle_docstringdict_%(language)s" % {'language':lang.lower()}
    module = __import__(modname)
    docsdict = module.docsdict
    dla key w docsdict:
        spróbuj:
#            eval(key).im_func.__doc__ = docsdict[key]
            eval(key).__doc__ = docsdict[key]
        wyjąwszy:
            print("Bad docstring-enspróbuj: %s" % key)

_LANGUAGE = _CFG["language"]

spróbuj:
    jeżeli _LANGUAGE != "english":
        read_docstrings(_LANGUAGE)
wyjąwszy ImportError:
    print("Cannot find docsdict for", _LANGUAGE)
wyjąwszy:
    print ("Unknown Error when trying to zaimportuj %s-docstring-dictionary" %
                                                                  _LANGUAGE)


def getmethparlist(ob):
    """Get strings describing the arguments dla the given object

    Returns a pair of strings representing function parameter lists
    including parenthesis.  The first string jest suitable dla use w
    function definition oraz the second jest suitable dla use w function
    call.  The "self" parameter jest nie included.
    """
    defText = callText = ""
    # bit of a hack dla methods - turn it into a function
    # but we drop the "self" param.
    # Try oraz build one dla Python defined functions
    args, varargs, varkw = inspect.getargs(ob.__code__)
    items2 = args[1:]
    realArgs = args[1:]
    defaults = ob.__defaults__ albo []
    defaults = ["=%r" % (value,) dla value w defaults]
    defaults = [""] * (len(realArgs)-len(defaults)) + defaults
    items1 = [arg + dflt dla arg, dflt w zip(realArgs, defaults)]
    jeżeli varargs jest nie Nic:
        items1.append("*" + varargs)
        items2.append("*" + varargs)
    jeżeli varkw jest nie Nic:
        items1.append("**" + varkw)
        items2.append("**" + varkw)
    defText = ", ".join(items1)
    defText = "(%s)" % defText
    callText = ", ".join(items2)
    callText = "(%s)" % callText
    zwróć defText, callText

def _turtle_docrevise(docstr):
    """To reduce docstrings z RawTurtle klasa dla functions
    """
    zaimportuj re
    jeżeli docstr jest Nic:
        zwróć Nic
    turtlename = _CFG["exampleturtle"]
    newdocstr = docstr.replace("%s." % turtlename,"")
    parexp = re.compile(r' \(.+ %s\):' % turtlename)
    newdocstr = parexp.sub(":", newdocstr)
    zwróć newdocstr

def _screen_docrevise(docstr):
    """To reduce docstrings z TurtleScreen klasa dla functions
    """
    zaimportuj re
    jeżeli docstr jest Nic:
        zwróć Nic
    screenname = _CFG["examplescreen"]
    newdocstr = docstr.replace("%s." % screenname,"")
    parexp = re.compile(r' \(.+ %s\):' % screenname)
    newdocstr = parexp.sub(":", newdocstr)
    zwróć newdocstr

## The following mechanism makes all methods of RawTurtle oraz Turtle available
## jako functions. So we can enhance, change, add, delete methods to these
## classes oraz do nie need to change anything here.

__func_body = """\
def {name}{paramslist}:
    jeżeli {obj} jest Nic:
        jeżeli nie TurtleScreen._RUNNING:
            TurtleScreen._RUNNING = Prawda
            podnieś Terminator
        {obj} = {init}
    spróbuj:
        zwróć {obj}.{name}{argslist}
    wyjąwszy TK.TclError:
        jeżeli nie TurtleScreen._RUNNING:
            TurtleScreen._RUNNING = Prawda
            podnieś Terminator
        podnieś
"""

def _make_global_funcs(functions, cls, obj, init, docrevise):
    dla methodname w functions:
        method = getattr(cls, methodname)
        pl1, pl2 = getmethparlist(method)
        jeżeli pl1 == "":
            print(">>>>>>", pl1, pl2)
            kontynuuj
        defstr = __func_body.format(obj=obj, init=init, name=methodname,
                                    paramslist=pl1, argslist=pl2)
        exec(defstr, globals())
        globals()[methodname].__doc__ = docrevise(method.__doc__)

_make_global_funcs(_tg_screen_functions, _Screen,
                   'Turtle._screen', 'Screen()', _screen_docrevise)
_make_global_funcs(_tg_turtle_functions, Turtle,
                   'Turtle._pen', 'Turtle()', _turtle_docrevise)


done = mainloop

jeżeli __name__ == "__main__":
    def switchpen():
        jeżeli isdown():
            pu()
        inaczej:
            pd()

    def demo1():
        """Demo of old turtle.py - module"""
        reset()
        tracer(Prawda)
        up()
        backward(100)
        down()
        # draw 3 squares; the last filled
        width(3)
        dla i w range(3):
            jeżeli i == 2:
                begin_fill()
            dla _ w range(4):
                forward(20)
                left(90)
            jeżeli i == 2:
                color("maroon")
                end_fill()
            up()
            forward(30)
            down()
        width(1)
        color("black")
        # move out of the way
        tracer(Nieprawda)
        up()
        right(90)
        forward(100)
        right(90)
        forward(100)
        right(180)
        down()
        # some text
        write("startstart", 1)
        write("start", 1)
        color("red")
        # staircase
        dla i w range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)
        # filled staircase
        tracer(Prawda)
        begin_fill()
        dla i w range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)
        end_fill()
        # more text

    def demo2():
        """Demo of some new features."""
        speed(1)
        st()
        pensize(3)
        setheading(towards(0, 0))
        radius = distance(0, 0)/2.0
        rt(90)
        dla _ w range(18):
            switchpen()
            circle(radius, 10)
        write("wait a moment...")
        dopóki undobufferentries():
            undo()
        reset()
        lt(90)
        colormode(255)
        laenge = 10
        pencolor("green")
        pensize(3)
        lt(180)
        dla i w range(-2, 16):
            jeżeli i > 0:
                begin_fill()
                fillcolor(255-15*i, 0, 15*i)
            dla _ w range(3):
                fd(laenge)
                lt(120)
            end_fill()
            laenge += 10
            lt(15)
            speed((speed()+1)%12)
        #end_fill()

        lt(120)
        pu()
        fd(70)
        rt(30)
        pd()
        color("red","yellow")
        speed(0)
        begin_fill()
        dla _ w range(4):
            circle(50, 90)
            rt(90)
            fd(30)
            rt(90)
        end_fill()
        lt(90)
        pu()
        fd(30)
        pd()
        shape("turtle")

        tri = getturtle()
        tri.resizemode("auto")
        turtle = Turtle()
        turtle.resizemode("auto")
        turtle.shape("turtle")
        turtle.reset()
        turtle.left(90)
        turtle.speed(0)
        turtle.up()
        turtle.goto(280, 40)
        turtle.lt(30)
        turtle.down()
        turtle.speed(6)
        turtle.color("blue","orange")
        turtle.pensize(2)
        tri.speed(6)
        setheading(towards(turtle))
        count = 1
        dopóki tri.distance(turtle) > 4:
            turtle.fd(3.5)
            turtle.lt(0.6)
            tri.setheading(tri.towards(turtle))
            tri.fd(4)
            jeżeli count % 20 == 0:
                turtle.stamp()
                tri.stamp()
                switchpen()
            count += 1
        tri.write("CAUGHT! ", font=("Arial", 16, "bold"), align="right")
        tri.pencolor("black")
        tri.pencolor("red")

        def baba(xdummy, ydummy):
            clearscreen()
            bye()

        time.sleep(2)

        dopóki undobufferentries():
            tri.undo()
            turtle.undo()
        tri.fd(50)
        tri.write("  Click me!", font = ("Courier", 12, "bold") )
        tri.onclick(baba, 1)

    demo1()
    demo2()
    exitonclick()
