zaimportuj string
z tkinter zaimportuj *

z idlelib.Delegator zaimportuj Delegator

#$ event <<redo>>
#$ win <Control-y>
#$ unix <Alt-z>

#$ event <<undo>>
#$ win <Control-z>
#$ unix <Control-z>

#$ event <<dump-undo-state>>
#$ win <Control-backslash>
#$ unix <Control-backslash>


klasa UndoDelegator(Delegator):

    max_undo = 1000

    def __init__(self):
        Delegator.__init__(self)
        self.reset_undo()

    def setdelegate(self, delegate):
        jeżeli self.delegate jest nie Nic:
            self.unbind("<<undo>>")
            self.unbind("<<redo>>")
            self.unbind("<<dump-undo-state>>")
        Delegator.setdelegate(self, delegate)
        jeżeli delegate jest nie Nic:
            self.bind("<<undo>>", self.undo_event)
            self.bind("<<redo>>", self.redo_event)
            self.bind("<<dump-undo-state>>", self.dump_event)

    def dump_event(self, event):
        z pprint zaimportuj pprint
        pprint(self.undolist[:self.pointer])
        print("pointer:", self.pointer, end=' ')
        print("saved:", self.saved, end=' ')
        print("can_merge:", self.can_merge, end=' ')
        print("get_saved():", self.get_saved())
        pprint(self.undolist[self.pointer:])
        zwróć "break"

    def reset_undo(self):
        self.was_saved = -1
        self.pointer = 0
        self.undolist = []
        self.undoblock = 0  # albo a CommandSequence instance
        self.set_saved(1)

    def set_saved(self, flag):
        jeżeli flag:
            self.saved = self.pointer
        inaczej:
            self.saved = -1
        self.can_merge = Nieprawda
        self.check_saved()

    def get_saved(self):
        zwróć self.saved == self.pointer

    saved_change_hook = Nic

    def set_saved_change_hook(self, hook):
        self.saved_change_hook = hook

    was_saved = -1

    def check_saved(self):
        is_saved = self.get_saved()
        jeżeli is_saved != self.was_saved:
            self.was_saved = is_saved
            jeżeli self.saved_change_hook:
                self.saved_change_hook()

    def insert(self, index, chars, tags=Nic):
        self.addcmd(InsertCommand(index, chars, tags))

    def delete(self, index1, index2=Nic):
        self.addcmd(DeleteCommand(index1, index2))

    # Clients should call undo_block_start() oraz undo_block_stop()
    # around a sequence of editing cmds to be treated jako a unit by
    # undo & redo.  Nested matching calls are OK, oraz the inner calls
    # then act like nops.  OK too jeżeli no editing cmds, albo only one
    # editing cmd, jest issued w between:  jeżeli no cmds, the whole
    # sequence has no effect; oraz jeżeli only one cmd, that cmd jest entered
    # directly into the undo list, jako jeżeli undo_block_xxx hadn't been
    # called.  The intent of all that jest to make this scheme easy
    # to use:  all the client has to worry about jest making sure each
    # _start() call jest matched by a _stop() call.

    def undo_block_start(self):
        jeżeli self.undoblock == 0:
            self.undoblock = CommandSequence()
        self.undoblock.bump_depth()

    def undo_block_stop(self):
        jeżeli self.undoblock.bump_depth(-1) == 0:
            cmd = self.undoblock
            self.undoblock = 0
            jeżeli len(cmd) > 0:
                jeżeli len(cmd) == 1:
                    # no need to wrap a single cmd
                    cmd = cmd.getcmd(0)
                # this blk of cmds, albo single cmd, has already
                # been done, so don't execute it again
                self.addcmd(cmd, 0)

    def addcmd(self, cmd, execute=Prawda):
        jeżeli execute:
            cmd.do(self.delegate)
        jeżeli self.undoblock != 0:
            self.undoblock.append(cmd)
            zwróć
        jeżeli self.can_merge oraz self.pointer > 0:
            lastcmd = self.undolist[self.pointer-1]
            jeżeli lastcmd.merge(cmd):
                zwróć
        self.undolist[self.pointer:] = [cmd]
        jeżeli self.saved > self.pointer:
            self.saved = -1
        self.pointer = self.pointer + 1
        jeżeli len(self.undolist) > self.max_undo:
            ##print "truncating undo list"
            usuń self.undolist[0]
            self.pointer = self.pointer - 1
            jeżeli self.saved >= 0:
                self.saved = self.saved - 1
        self.can_merge = Prawda
        self.check_saved()

    def undo_event(self, event):
        jeżeli self.pointer == 0:
            self.bell()
            zwróć "break"
        cmd = self.undolist[self.pointer - 1]
        cmd.undo(self.delegate)
        self.pointer = self.pointer - 1
        self.can_merge = Nieprawda
        self.check_saved()
        zwróć "break"

    def redo_event(self, event):
        jeżeli self.pointer >= len(self.undolist):
            self.bell()
            zwróć "break"
        cmd = self.undolist[self.pointer]
        cmd.redo(self.delegate)
        self.pointer = self.pointer + 1
        self.can_merge = Nieprawda
        self.check_saved()
        zwróć "break"


klasa Command:

    # Base klasa dla Undoable commands

    tags = Nic

    def __init__(self, index1, index2, chars, tags=Nic):
        self.marks_before = {}
        self.marks_after = {}
        self.index1 = index1
        self.index2 = index2
        self.chars = chars
        jeżeli tags:
            self.tags = tags

    def __repr__(self):
        s = self.__class__.__name__
        t = (self.index1, self.index2, self.chars, self.tags)
        jeżeli self.tags jest Nic:
            t = t[:-1]
        zwróć s + repr(t)

    def do(self, text):
        dalej

    def redo(self, text):
        dalej

    def undo(self, text):
        dalej

    def merge(self, cmd):
        zwróć 0

    def save_marks(self, text):
        marks = {}
        dla name w text.mark_names():
            jeżeli name != "insert" oraz name != "current":
                marks[name] = text.index(name)
        zwróć marks

    def set_marks(self, text, marks):
        dla name, index w marks.items():
            text.mark_set(name, index)


klasa InsertCommand(Command):

    # Undoable insert command

    def __init__(self, index1, chars, tags=Nic):
        Command.__init__(self, index1, Nic, chars, tags)

    def do(self, text):
        self.marks_before = self.save_marks(text)
        self.index1 = text.index(self.index1)
        jeżeli text.compare(self.index1, ">", "end-1c"):
            # Insert before the final newline
            self.index1 = text.index("end-1c")
        text.insert(self.index1, self.chars, self.tags)
        self.index2 = text.index("%s+%dc" % (self.index1, len(self.chars)))
        self.marks_after = self.save_marks(text)
        ##sys.__stderr__.write("do: %s\n" % self)

    def redo(self, text):
        text.mark_set('insert', self.index1)
        text.insert(self.index1, self.chars, self.tags)
        self.set_marks(text, self.marks_after)
        text.see('insert')
        ##sys.__stderr__.write("redo: %s\n" % self)

    def undo(self, text):
        text.mark_set('insert', self.index1)
        text.delete(self.index1, self.index2)
        self.set_marks(text, self.marks_before)
        text.see('insert')
        ##sys.__stderr__.write("undo: %s\n" % self)

    def merge(self, cmd):
        jeżeli self.__class__ jest nie cmd.__class__:
            zwróć Nieprawda
        jeżeli self.index2 != cmd.index1:
            zwróć Nieprawda
        jeżeli self.tags != cmd.tags:
            zwróć Nieprawda
        jeżeli len(cmd.chars) != 1:
            zwróć Nieprawda
        jeżeli self.chars oraz \
           self.classify(self.chars[-1]) != self.classify(cmd.chars):
            zwróć Nieprawda
        self.index2 = cmd.index2
        self.chars = self.chars + cmd.chars
        zwróć Prawda

    alphanumeric = string.ascii_letters + string.digits + "_"

    def classify(self, c):
        jeżeli c w self.alphanumeric:
            zwróć "alphanumeric"
        jeżeli c == "\n":
            zwróć "newline"
        zwróć "punctuation"


klasa DeleteCommand(Command):

    # Undoable delete command

    def __init__(self, index1, index2=Nic):
        Command.__init__(self, index1, index2, Nic, Nic)

    def do(self, text):
        self.marks_before = self.save_marks(text)
        self.index1 = text.index(self.index1)
        jeżeli self.index2:
            self.index2 = text.index(self.index2)
        inaczej:
            self.index2 = text.index(self.index1 + " +1c")
        jeżeli text.compare(self.index2, ">", "end-1c"):
            # Don't delete the final newline
            self.index2 = text.index("end-1c")
        self.chars = text.get(self.index1, self.index2)
        text.delete(self.index1, self.index2)
        self.marks_after = self.save_marks(text)
        ##sys.__stderr__.write("do: %s\n" % self)

    def redo(self, text):
        text.mark_set('insert', self.index1)
        text.delete(self.index1, self.index2)
        self.set_marks(text, self.marks_after)
        text.see('insert')
        ##sys.__stderr__.write("redo: %s\n" % self)

    def undo(self, text):
        text.mark_set('insert', self.index1)
        text.insert(self.index1, self.chars)
        self.set_marks(text, self.marks_before)
        text.see('insert')
        ##sys.__stderr__.write("undo: %s\n" % self)

klasa CommandSequence(Command):

    # Wrapper dla a sequence of undoable cmds to be undone/redone
    # jako a unit

    def __init__(self):
        self.cmds = []
        self.depth = 0

    def __repr__(self):
        s = self.__class__.__name__
        strs = []
        dla cmd w self.cmds:
            strs.append("    %r" % (cmd,))
        zwróć s + "(\n" + ",\n".join(strs) + "\n)"

    def __len__(self):
        zwróć len(self.cmds)

    def append(self, cmd):
        self.cmds.append(cmd)

    def getcmd(self, i):
        zwróć self.cmds[i]

    def redo(self, text):
        dla cmd w self.cmds:
            cmd.redo(text)

    def undo(self, text):
        cmds = self.cmds[:]
        cmds.reverse()
        dla cmd w cmds:
            cmd.undo(text)

    def bump_depth(self, incr=1):
        self.depth = self.depth + incr
        zwróć self.depth

def _undo_delegator(parent):
    z idlelib.Percolator zaimportuj Percolator
    root = Tk()
    root.title("Test UndoDelegator")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))

    text = Text(root)
    text.config(height=10)
    text.pack()
    text.focus_set()
    p = Percolator(text)
    d = UndoDelegator()
    p.insertfilter(d)

    undo = Button(root, text="Undo", command=lambda:d.undo_event(Nic))
    undo.pack(side='left')
    redo = Button(root, text="Redo", command=lambda:d.redo_event(Nic))
    redo.pack(side='left')
    dump = Button(root, text="Dump", command=lambda:d.dump_event(Nic))
    dump.pack(side='left')

    root.mainloop()

jeżeli __name__ == "__main__":
    z idlelib.idle_test.htest zaimportuj run
    run(_undo_delegator)
