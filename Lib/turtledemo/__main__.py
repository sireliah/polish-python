#!/usr/bin/env python3

"""
  ----------------------------------------------
      turtleDemo - Help
  ----------------------------------------------

  This document has two sections:

  (1) How to use the demo viewer
  (2) How to add your own demos to the demo repository


  (1) How to use the demo viewer.

  Select a demoscript z the example menu.
  The (syntax colored) source code appears w the left
  source code window. IT CANNOT BE EDITED, but ONLY VIEWED!

  The demo viewer windows can be resized. The divider between text
  oraz canvas can be moved by grabbing it przy the mouse. The text font
  size can be changed z the menu oraz przy Control/Command '-'/'+'.
  It can also be changed on most systems przy Control-mousewheel
  when the mouse jest over the text.

  Press START button to start the demo.
  Stop execution by pressing the STOP button.
  Clear screen by pressing the CLEAR button.
  Restart by pressing the START button again.

  SPECIAL demos, such jako clock.py are those which run EVENTDRIVEN.

      Press START button to start the demo.

      - Until the EVENTLOOP jest entered everything works
      jako w an ordinary demo script.

      - When the EVENTLOOP jest entered, you control the
      application by using the mouse and/or keys (or it's
      controlled by some timer events)
      To stop it you can oraz must press the STOP button.

      While the EVENTLOOP jest running, the examples menu jest disabled.

      - Only after having pressed the STOP button, you may
      restart it albo choose another example script.

   * * * * * * * *
   In some rare situations there may occur interferences/conflicts
   between events concerning the demo script oraz those concerning the
   demo-viewer. (They run w the same process.) Strange behaviour may be
   the consequence oraz w the worst case you must close oraz restart the
   viewer.
   * * * * * * * *


   (2) How to add your own demos to the demo repository

   - Place the file w the same directory jako turtledemo/__main__.py
     IMPORTANT! When imported, the demo should nie modify the system
     by calling functions w other modules, such jako sys, tkinter, albo
     turtle. Global variables should be initialized w main().

   - The code must contain a main() function which will
     be executed by the viewer (see provided example scripts).
     It may zwróć a string which will be displayed w the Label below
     the source code window (when execution has finished.)

   - In order to run mydemo.py by itself, such jako during development,
     add the following at the end of the file:

    jeżeli __name__ == '__main__':
        main()
        mainloop()  # keep window open

    python -m turtledemo.mydemo  # will then run it

   - If the demo jest EVENT DRIVEN, main must zwróć the string
     "EVENTLOOP". This informs the demo viewer that the script jest
     still running oraz must be stopped by the user!

     If an "EVENTLOOP" demo runs by itself, jako przy clock, which uses
     ontimer, albo minimal_hanoi, which loops by recursion, then the
     code should catch the turtle.Terminator exception that will be
     podnieśd when the user presses the STOP button.  (Paint jest nie such
     a demo; it only acts w response to mouse clicks oraz movements.)
"""
zaimportuj sys
zaimportuj os

z tkinter zaimportuj *
z idlelib.Percolator zaimportuj Percolator
z idlelib.ColorDelegator zaimportuj ColorDelegator
z idlelib.textView zaimportuj view_text
z turtledemo zaimportuj __doc__ jako about_turtledemo

zaimportuj turtle
zaimportuj time

demo_dir = os.path.dirname(os.path.abspath(__file__))
darwin = sys.platform == 'darwin'

STARTUP = 1
READY = 2
RUNNING = 3
DONE = 4
EVENTDRIVEN = 5

menufont = ("Arial", 12, NORMAL)
btnfont = ("Arial", 12, 'bold')
txtfont = ['Lucida Console', 10, 'normal']

MINIMUM_FONT_SIZE = 6
MAXIMUM_FONT_SIZE = 100
font_sizes = [8, 9, 10, 11, 12, 14, 18, 20, 22, 24, 30]

def getExampleEntries():
    zwróć [entry[:-3] dla entry w os.listdir(demo_dir) if
            entry.endswith(".py") oraz entry[0] != '_']

help_entries = (  # (help_label,  help_doc)
    ('Turtledemo help', __doc__),
    ('About turtledemo', about_turtledemo),
    ('About turtle module', turtle.__doc__),
    )

klasa DemoWindow(object):

    def __init__(self, filename=Nic):
        self.root = root = turtle._root = Tk()
        root.title('Python turtle-graphics examples')
        root.wm_protocol("WM_DELETE_WINDOW", self._destroy)

        jeżeli darwin:
            zaimportuj subprocess
            # Make sure we are the currently activated OS X application
            # so that our menu bar appears.
            p = subprocess.Popen(
                    [
                        'osascript',
                        '-e', 'tell application "System Events"',
                        '-e', 'set frontmost of the first process whose '
                              'unix id jest {} to true'.format(os.getpid()),
                        '-e', 'end tell',
                    ],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,)

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, minsize=90, weight=1)
        root.grid_columnconfigure(2, minsize=90, weight=1)
        root.grid_columnconfigure(3, minsize=90, weight=1)

        self.mBar = Menu(root, relief=RAISED, borderwidth=2)
        self.mBar.add_cascade(menu=self.makeLoadDemoMenu(self.mBar),
                              label='Examples', underline=0)
        self.mBar.add_cascade(menu=self.makeFontMenu(self.mBar),
                              label='Fontsize', underline=0)
        self.mBar.add_cascade(menu=self.makeHelpMenu(self.mBar),
                              label='Help', underline=0)
        root['menu'] = self.mBar

        pane = PanedWindow(orient=HORIZONTAL, sashwidth=5,
                           sashrelief=SOLID, bg='#ddd')
        pane.add(self.makeTextFrame(pane))
        pane.add(self.makeGraphFrame(pane))
        pane.grid(row=0, columnspan=4, sticky='news')

        self.output_lbl = Label(root, height= 1, text=" --- ", bg="#ddf",
                                font=("Arial", 16, 'normal'), borderwidth=2,
                                relief=RIDGE)
        self.start_btn = Button(root, text=" START ", font=btnfont,
                                fg="white", disabledforeground = "#fed",
                                command=self.startDemo)
        self.stop_btn = Button(root, text=" STOP ", font=btnfont,
                               fg="white", disabledforeground = "#fed",
                               command=self.stopIt)
        self.clear_btn = Button(root, text=" CLEAR ", font=btnfont,
                                fg="white", disabledforeground="#fed",
                                command = self.clearCanvas)
        self.output_lbl.grid(row=1, column=0, sticky='news', padx=(0,5))
        self.start_btn.grid(row=1, column=1, sticky='ew')
        self.stop_btn.grid(row=1, column=2, sticky='ew')
        self.clear_btn.grid(row=1, column=3, sticky='ew')

        Percolator(self.text).insertfilter(ColorDelegator())
        self.dirty = Nieprawda
        self.exitflag = Nieprawda
        jeżeli filename:
            self.loadfile(filename)
        self.configGUI(DISABLED, DISABLED, DISABLED,
                       "Choose example z menu", "black")
        self.state = STARTUP


    def onResize(self, event):
        cwidth = self._canvas.winfo_width()
        cheight = self._canvas.winfo_height()
        self._canvas.xview_moveto(0.5*(self.canvwidth-cwidth)/self.canvwidth)
        self._canvas.yview_moveto(0.5*(self.canvheight-cheight)/self.canvheight)

    def makeTextFrame(self, root):
        self.text_frame = text_frame = Frame(root)
        self.text = text = Text(text_frame, name='text', padx=5,
                                wrap='none', width=45)

        self.vbar = vbar = Scrollbar(text_frame, name='vbar')
        vbar['command'] = text.yview
        vbar.pack(side=LEFT, fill=Y)
        self.hbar = hbar = Scrollbar(text_frame, name='hbar', orient=HORIZONTAL)
        hbar['command'] = text.xview
        hbar.pack(side=BOTTOM, fill=X)
        text['yscrollcommand'] = vbar.set
        text['xscrollcommand'] = hbar.set

        text['font'] = tuple(txtfont)
        shortcut = 'Command' jeżeli darwin inaczej 'Control'
        text.bind_all('<%s-minus>' % shortcut, self.decrease_size)
        text.bind_all('<%s-underscore>' % shortcut, self.decrease_size)
        text.bind_all('<%s-equal>' % shortcut, self.increase_size)
        text.bind_all('<%s-plus>' % shortcut, self.increase_size)
        text.bind('<Control-MouseWheel>', self.update_mousewheel)
        text.bind('<Control-Button-4>', self.increase_size)
        text.bind('<Control-Button-5>', self.decrease_size)

        text.pack(side=LEFT, fill=BOTH, expand=1)
        zwróć text_frame

    def makeGraphFrame(self, root):
        turtle._Screen._root = root
        self.canvwidth = 1000
        self.canvheight = 800
        turtle._Screen._canvas = self._canvas = canvas = turtle.ScrolledCanvas(
                root, 800, 600, self.canvwidth, self.canvheight)
        canvas.adjustScrolls()
        canvas._rootwindow.bind('<Configure>', self.onResize)
        canvas._canvas['borderwidth'] = 0

        self.screen = _s_ = turtle.Screen()
        turtle.TurtleScreen.__init__(_s_, _s_._canvas)
        self.scanvas = _s_._canvas
        turtle.RawTurtle.screens = [_s_]
        zwróć canvas

    def set_txtsize(self, size):
        txtfont[1] = size
        self.text['font'] = tuple(txtfont)
        self.output_lbl['text'] = 'Font size %d' % size

    def decrease_size(self, dummy=Nic):
        self.set_txtsize(max(txtfont[1] - 1, MINIMUM_FONT_SIZE))
        zwróć 'break'

    def increase_size(self, dummy=Nic):
        self.set_txtsize(min(txtfont[1] + 1, MAXIMUM_FONT_SIZE))
        zwróć 'break'

    def update_mousewheel(self, event):
        # For wheel up, event.delte = 120 on Windows, -1 on darwin.
        # X-11 sends Control-Button-4 event instead.
        jeżeli (event.delta < 0) == (nie darwin):
            zwróć self.decrease_size()
        inaczej:
            zwróć self.increase_size()

    def configGUI(self, start, stop, clear, txt="", color="blue"):
        self.start_btn.config(state=start,
                              bg="#d00" jeżeli start == NORMAL inaczej "#fca")
        self.stop_btn.config(state=stop,
                             bg="#d00" jeżeli stop == NORMAL inaczej "#fca")
        self.clear_btn.config(state=clear,
                              bg="#d00" jeżeli clear == NORMAL inaczej"#fca")
        self.output_lbl.config(text=txt, fg=color)

    def makeLoadDemoMenu(self, master):
        menu = Menu(master)

        dla entry w getExampleEntries():
            def load(entry=entry):
                self.loadfile(entry)
            menu.add_command(label=entry, underline=0,
                             font=menufont, command=load)
        zwróć menu

    def makeFontMenu(self, master):
        menu = Menu(master)
        menu.add_command(label="Decrease (C-'-')", command=self.decrease_size,
                         font=menufont)
        menu.add_command(label="Increase (C-'+')", command=self.increase_size,
                         font=menufont)
        menu.add_separator()

        dla size w font_sizes:
            def resize(size=size):
                self.set_txtsize(size)
            menu.add_command(label=str(size), underline=0,
                             font=menufont, command=resize)
        zwróć menu

    def makeHelpMenu(self, master):
        menu = Menu(master)

        dla help_label, help_file w help_entries:
            def show(help_label=help_label, help_file=help_file):
                view_text(self.root, help_label, help_file)
            menu.add_command(label=help_label, font=menufont, command=show)
        zwróć menu

    def refreshCanvas(self):
        jeżeli self.dirty:
            self.screen.clear()
            self.dirty=Nieprawda

    def loadfile(self, filename):
        self.clearCanvas()
        turtle.TurtleScreen._RUNNING = Nieprawda
        modname = 'turtledemo.' + filename
        __import__(modname)
        self.module = sys.modules[modname]
        przy open(self.module.__file__, 'r') jako f:
            chars = f.read()
        self.text.delete("1.0", "end")
        self.text.insert("1.0", chars)
        self.root.title(filename + " - a Python turtle graphics example")
        self.configGUI(NORMAL, DISABLED, DISABLED,
                       "Press start button", "red")
        self.state = READY

    def startDemo(self):
        self.refreshCanvas()
        self.dirty = Prawda
        turtle.TurtleScreen._RUNNING = Prawda
        self.configGUI(DISABLED, NORMAL, DISABLED,
                       "demo running...", "black")
        self.screen.clear()
        self.screen.mode("standard")
        self.state = RUNNING

        spróbuj:
            result = self.module.main()
            jeżeli result == "EVENTLOOP":
                self.state = EVENTDRIVEN
            inaczej:
                self.state = DONE
        wyjąwszy turtle.Terminator:
            jeżeli self.root jest Nic:
                zwróć
            self.state = DONE
            result = "stopped!"
        jeżeli self.state == DONE:
            self.configGUI(NORMAL, DISABLED, NORMAL,
                           result)
        albo_inaczej self.state == EVENTDRIVEN:
            self.exitflag = Prawda
            self.configGUI(DISABLED, NORMAL, DISABLED,
                           "use mouse/keys albo STOP", "red")

    def clearCanvas(self):
        self.refreshCanvas()
        self.screen._delete("all")
        self.scanvas.config(cursor="")
        self.configGUI(NORMAL, DISABLED, DISABLED)

    def stopIt(self):
        jeżeli self.exitflag:
            self.clearCanvas()
            self.exitflag = Nieprawda
            self.configGUI(NORMAL, DISABLED, DISABLED,
                           "STOPPED!", "red")
        turtle.TurtleScreen._RUNNING = Nieprawda

    def _destroy(self):
        turtle.TurtleScreen._RUNNING = Nieprawda
        self.root.destroy()
        self.root = Nic


def main():
    demo = DemoWindow()
    demo.root.mainloop()

jeżeli __name__ == '__main__':
    main()
