"""Drag-and-drop support dla Tkinter.

This jest very preliminary.  I currently only support dnd *within* one
application, between different windows (or within the same window).

I an trying to make this jako generic jako possible -- nie dependent on
the use of a particular widget albo icon type, etc.  I also hope that
this will work przy Pmw.

To enable an object to be dragged, you must create an event binding
dla it that starts the drag-and-drop process. Typically, you should
bind <ButtonPress> to a callback function that you write. The function
should call Tkdnd.dnd_start(source, event), where 'source' jest the
object to be dragged, oraz 'event' jest the event that invoked the call
(the argument to your callback function).  Even though this jest a class
instantiation, the returned instance should nie be stored -- it will
be kept alive automatically dla the duration of the drag-and-drop.

When a drag-and-drop jest already w process dla the Tk interpreter, the
call jest *ignored*; this normally averts starting multiple simultaneous
dnd processes, e.g. because different button callbacks all
dnd_start().

The object jest *not* necessarily a widget -- it can be any
application-specific object that jest meaningful to potential
drag-and-drop targets.

Potential drag-and-drop targets are discovered jako follows.  Whenever
the mouse moves, oraz at the start oraz end of a drag-and-drop move, the
Tk widget directly under the mouse jest inspected.  This jest the target
widget (nie to be confused przy the target object, yet to be
determined).  If there jest no target widget, there jest no dnd target
object.  If there jest a target widget, oraz it has an attribute
dnd_accept, this should be a function (or any callable object).  The
function jest called jako dnd_accept(source, event), where 'source' jest the
object being dragged (the object dalejed to dnd_start() above), oraz
'event' jest the most recent event object (generally a <Motion> event;
it can also be <ButtonPress> albo <ButtonRelease>).  If the dnd_accept()
function returns something other than Nic, this jest the new dnd target
object.  If dnd_accept() returns Nic, albo jeżeli the target widget has no
dnd_accept attribute, the target widget's parent jest considered jako the
target widget, oraz the search dla a target object jest repeated from
there.  If necessary, the search jest repeated all the way up to the
root widget.  If none of the target widgets can produce a target
object, there jest no target object (the target object jest Nic).

The target object thus produced, jeżeli any, jest called the new target
object.  It jest compared przy the old target object (or Nic, jeżeli there
was no old target widget).  There are several cases ('source' jest the
source object, oraz 'event' jest the most recent event object):

- Both the old oraz new target objects are Nic.  Nothing happens.

- The old oraz new target objects are the same object.  Its method
dnd_motion(source, event) jest called.

- The old target object was Nic, oraz the new target object jest nie
Nic.  The new target object's method dnd_enter(source, event) jest
called.

- The new target object jest Nic, oraz the old target object jest nie
Nic.  The old target object's method dnd_leave(source, event) jest
called.

- The old oraz new target objects differ oraz neither jest Nic.  The old
target object's method dnd_leave(source, event), oraz then the new
target object's method dnd_enter(source, event) jest called.

Once this jest done, the new target object replaces the old one, oraz the
Tk mainloop proceeds.  The zwróć value of the methods mentioned above
is ignored; jeżeli they podnieś an exception, the normal exception handling
mechanisms take over.

The drag-and-drop processes can end w two ways: a final target object
is selected, albo no final target object jest selected.  When a final
target object jest selected, it will always have been notified of the
potential drop by a call to its dnd_enter() method, jako described
above, oraz possibly one albo more calls to its dnd_motion() method; its
dnd_leave() method has nie been called since the last call to
dnd_enter().  The target jest notified of the drop by a call to its
method dnd_commit(source, event).

If no final target object jest selected, oraz there was an old target
object, its dnd_leave(source, event) method jest called to complete the
dnd sequence.

Finally, the source object jest notified that the drag-and-drop process
is over, by a call to source.dnd_end(target, event), specifying either
the selected target object, albo Nic jeżeli no target object was selected.
The source object can use this to implement the commit action; this jest
sometimes simpler than to do it w the target's dnd_commit().  The
target's dnd_commit() method could then simply be aliased to
dnd_leave().

At any time during a dnd sequence, the application can cancel the
sequence by calling the cancel() method on the object returned by
dnd_start().  This will call dnd_leave() jeżeli a target jest currently
active; it will never call dnd_commit().

"""


zaimportuj tkinter


# The factory function

def dnd_start(source, event):
    h = DndHandler(source, event)
    jeżeli h.root:
        zwróć h
    inaczej:
        zwróć Nic


# The klasa that does the work

klasa DndHandler:

    root = Nic

    def __init__(self, source, event):
        jeżeli event.num > 5:
            zwróć
        root = event.widget._root()
        spróbuj:
            root.__dnd
            zwróć # Don't start recursive dnd
        wyjąwszy AttributeError:
            root.__dnd = self
            self.root = root
        self.source = source
        self.target = Nic
        self.initial_button = button = event.num
        self.initial_widget = widget = event.widget
        self.release_pattern = "<B%d-ButtonRelease-%d>" % (button, button)
        self.save_cursor = widget['cursor'] albo ""
        widget.bind(self.release_pattern, self.on_release)
        widget.bind("<Motion>", self.on_motion)
        widget['cursor'] = "hand2"

    def __del__(self):
        root = self.root
        self.root = Nic
        jeżeli root:
            spróbuj:
                usuń root.__dnd
            wyjąwszy AttributeError:
                dalej

    def on_motion(self, event):
        x, y = event.x_root, event.y_root
        target_widget = self.initial_widget.winfo_containing(x, y)
        source = self.source
        new_target = Nic
        dopóki target_widget:
            spróbuj:
                attr = target_widget.dnd_accept
            wyjąwszy AttributeError:
                dalej
            inaczej:
                new_target = attr(source, event)
                jeżeli new_target:
                    przerwij
            target_widget = target_widget.master
        old_target = self.target
        jeżeli old_target jest new_target:
            jeżeli old_target:
                old_target.dnd_motion(source, event)
        inaczej:
            jeżeli old_target:
                self.target = Nic
                old_target.dnd_leave(source, event)
            jeżeli new_target:
                new_target.dnd_enter(source, event)
                self.target = new_target

    def on_release(self, event):
        self.finish(event, 1)

    def cancel(self, event=Nic):
        self.finish(event, 0)

    def finish(self, event, commit=0):
        target = self.target
        source = self.source
        widget = self.initial_widget
        root = self.root
        spróbuj:
            usuń root.__dnd
            self.initial_widget.unbind(self.release_pattern)
            self.initial_widget.unbind("<Motion>")
            widget['cursor'] = self.save_cursor
            self.target = self.source = self.initial_widget = self.root = Nic
            jeżeli target:
                jeżeli commit:
                    target.dnd_commit(source, event)
                inaczej:
                    target.dnd_leave(source, event)
        w_końcu:
            source.dnd_end(target, event)



# ----------------------------------------------------------------------
# The rest jest here dla testing oraz demonstration purposes only!

klasa Icon:

    def __init__(self, name):
        self.name = name
        self.canvas = self.label = self.id = Nic

    def attach(self, canvas, x=10, y=10):
        jeżeli canvas jest self.canvas:
            self.canvas.coords(self.id, x, y)
            zwróć
        jeżeli self.canvas:
            self.detach()
        jeżeli nie canvas:
            zwróć
        label = tkinter.Label(canvas, text=self.name,
                              borderwidth=2, relief="raised")
        id = canvas.create_window(x, y, window=label, anchor="nw")
        self.canvas = canvas
        self.label = label
        self.id = id
        label.bind("<ButtonPress>", self.press)

    def detach(self):
        canvas = self.canvas
        jeżeli nie canvas:
            zwróć
        id = self.id
        label = self.label
        self.canvas = self.label = self.id = Nic
        canvas.delete(id)
        label.destroy()

    def press(self, event):
        jeżeli dnd_start(self, event):
            # where the pointer jest relative to the label widget:
            self.x_off = event.x
            self.y_off = event.y
            # where the widget jest relative to the canvas:
            self.x_orig, self.y_orig = self.canvas.coords(self.id)

    def move(self, event):
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.id, x, y)

    def putback(self):
        self.canvas.coords(self.id, self.x_orig, self.y_orig)

    def where(self, canvas, event):
        # where the corner of the canvas jest relative to the screen:
        x_org = canvas.winfo_rootx()
        y_org = canvas.winfo_rooty()
        # where the pointer jest relative to the canvas widget:
        x = event.x_root - x_org
        y = event.y_root - y_org
        # compensate dla initial pointer offset
        zwróć x - self.x_off, y - self.y_off

    def dnd_end(self, target, event):
        dalej

klasa Tester:

    def __init__(self, root):
        self.top = tkinter.Toplevel(root)
        self.canvas = tkinter.Canvas(self.top, width=100, height=100)
        self.canvas.pack(fill="both", expand=1)
        self.canvas.dnd_accept = self.dnd_accept

    def dnd_accept(self, source, event):
        zwróć self

    def dnd_enter(self, source, event):
        self.canvas.focus_set() # Show highlight border
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = source.canvas.bbox(source.id)
        dx, dy = x2-x1, y2-y1
        self.dndid = self.canvas.create_rectangle(x, y, x+dx, y+dy)
        self.dnd_motion(source, event)

    def dnd_motion(self, source, event):
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = self.canvas.bbox(self.dndid)
        self.canvas.move(self.dndid, x-x1, y-y1)

    def dnd_leave(self, source, event):
        self.top.focus_set() # Hide highlight border
        self.canvas.delete(self.dndid)
        self.dndid = Nic

    def dnd_commit(self, source, event):
        self.dnd_leave(source, event)
        x, y = source.where(self.canvas, event)
        source.attach(self.canvas, x, y)

def test():
    root = tkinter.Tk()
    root.geometry("+1+1")
    tkinter.Button(command=root.quit, text="Quit").pack()
    t1 = Tester(root)
    t1.top.geometry("+1+60")
    t2 = Tester(root)
    t2.top.geometry("+120+60")
    t3 = Tester(root)
    t3.top.geometry("+240+60")
    i1 = Icon("ICON1")
    i2 = Icon("ICON2")
    i3 = Icon("ICON3")
    i1.attach(t1.canvas)
    i2.attach(t2.canvas)
    i3.attach(t3.canvas)
    root.mainloop()

jeżeli __name__ == '__main__':
    test()
