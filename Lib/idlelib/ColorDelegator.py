zaimportuj time
zaimportuj re
zaimportuj keyword
zaimportuj builtins
z idlelib.Delegator zaimportuj Delegator
z idlelib.configHandler zaimportuj idleConf

DEBUG = Nieprawda

def any(name, alternates):
    "Return a named group pattern matching list of alternates."
    zwróć "(?P<%s>" % name + "|".join(alternates) + ")"

def make_pat():
    kw = r"\b" + any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) dla name w dir(builtins)
                                        jeżeli nie name.startswith('_') oraz \
                                        name nie w keyword.kwlist]
    # self.file = open("file") :
    # 1st 'file' colorized normal, 2nd jako builtin, 3rd jako string
    builtin = r"([^.'\"\\#]\b|^)" + any("BUILTIN", builtinlist) + r"\b"
    comment = any("COMMENT", [r"#[^\n]*"])
    stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR|rb|rB|Rb|RB)?"
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = any("STRING", [sq3string, dq3string, sqstring, dqstring])
    zwróć kw + "|" + builtin + "|" + comment + "|" + string +\
           "|" + any("SYNC", [r"\n"])

prog = re.compile(make_pat(), re.S)
idprog = re.compile(r"\s+(\w+)", re.S)

klasa ColorDelegator(Delegator):

    def __init__(self):
        Delegator.__init__(self)
        self.prog = prog
        self.idprog = idprog
        self.LoadTagDefs()

    def setdelegate(self, delegate):
        jeżeli self.delegate jest nie Nic:
            self.unbind("<<toggle-auto-coloring>>")
        Delegator.setdelegate(self, delegate)
        jeżeli delegate jest nie Nic:
            self.config_colors()
            self.bind("<<toggle-auto-coloring>>", self.toggle_colorize_event)
            self.notify_range("1.0", "end")
        inaczej:
            # No delegate - stop any colorizing
            self.stop_colorizing = Prawda
            self.allow_colorizing = Nieprawda

    def config_colors(self):
        dla tag, cnf w self.tagdefs.items():
            jeżeli cnf:
                self.tag_configure(tag, **cnf)
        self.tag_raise('sel')

    def LoadTagDefs(self):
        theme = idleConf.GetOption('main','Theme','name')
        self.tagdefs = {
            "COMMENT": idleConf.GetHighlight(theme, "comment"),
            "KEYWORD": idleConf.GetHighlight(theme, "keyword"),
            "BUILTIN": idleConf.GetHighlight(theme, "builtin"),
            "STRING": idleConf.GetHighlight(theme, "string"),
            "DEFINITION": idleConf.GetHighlight(theme, "definition"),
            "SYNC": {'background':Nic,'foreground':Nic},
            "TODO": {'background':Nic,'foreground':Nic},
            "ERROR": idleConf.GetHighlight(theme, "error"),
            # The following jest used by ReplaceDialog:
            "hit": idleConf.GetHighlight(theme, "hit"),
            }

        jeżeli DEBUG: print('tagdefs',self.tagdefs)

    def insert(self, index, chars, tags=Nic):
        index = self.index(index)
        self.delegate.insert(index, chars, tags)
        self.notify_range(index, index + "+%dc" % len(chars))

    def delete(self, index1, index2=Nic):
        index1 = self.index(index1)
        self.delegate.delete(index1, index2)
        self.notify_range(index1)

    after_id = Nic
    allow_colorizing = Prawda
    colorizing = Nieprawda

    def notify_range(self, index1, index2=Nic):
        self.tag_add("TODO", index1, index2)
        jeżeli self.after_id:
            jeżeli DEBUG: print("colorizing already scheduled")
            zwróć
        jeżeli self.colorizing:
            self.stop_colorizing = Prawda
            jeżeli DEBUG: print("stop colorizing")
        jeżeli self.allow_colorizing:
            jeżeli DEBUG: print("schedule colorizing")
            self.after_id = self.after(1, self.recolorize)

    close_when_done = Nic # Window to be closed when done colorizing

    def close(self, close_when_done=Nic):
        jeżeli self.after_id:
            after_id = self.after_id
            self.after_id = Nic
            jeżeli DEBUG: print("cancel scheduled recolorizer")
            self.after_cancel(after_id)
        self.allow_colorizing = Nieprawda
        self.stop_colorizing = Prawda
        jeżeli close_when_done:
            jeżeli nie self.colorizing:
                close_when_done.destroy()
            inaczej:
                self.close_when_done = close_when_done

    def toggle_colorize_event(self, event):
        jeżeli self.after_id:
            after_id = self.after_id
            self.after_id = Nic
            jeżeli DEBUG: print("cancel scheduled recolorizer")
            self.after_cancel(after_id)
        jeżeli self.allow_colorizing oraz self.colorizing:
            jeżeli DEBUG: print("stop colorizing")
            self.stop_colorizing = Prawda
        self.allow_colorizing = nie self.allow_colorizing
        jeżeli self.allow_colorizing oraz nie self.colorizing:
            self.after_id = self.after(1, self.recolorize)
        jeżeli DEBUG:
            print("auto colorizing turned",\
                  self.allow_colorizing oraz "on" albo "off")
        zwróć "break"

    def recolorize(self):
        self.after_id = Nic
        jeżeli nie self.delegate:
            jeżeli DEBUG: print("no delegate")
            zwróć
        jeżeli nie self.allow_colorizing:
            jeżeli DEBUG: print("auto colorizing jest off")
            zwróć
        jeżeli self.colorizing:
            jeżeli DEBUG: print("already colorizing")
            zwróć
        spróbuj:
            self.stop_colorizing = Nieprawda
            self.colorizing = Prawda
            jeżeli DEBUG: print("colorizing...")
            t0 = time.perf_counter()
            self.recolorize_main()
            t1 = time.perf_counter()
            jeżeli DEBUG: print("%.3f seconds" % (t1-t0))
        w_końcu:
            self.colorizing = Nieprawda
        jeżeli self.allow_colorizing oraz self.tag_nextrange("TODO", "1.0"):
            jeżeli DEBUG: print("reschedule colorizing")
            self.after_id = self.after(1, self.recolorize)
        jeżeli self.close_when_done:
            top = self.close_when_done
            self.close_when_done = Nic
            top.destroy()

    def recolorize_main(self):
        next = "1.0"
        dopóki Prawda:
            item = self.tag_nextrange("TODO", next)
            jeżeli nie item:
                przerwij
            head, tail = item
            self.tag_remove("SYNC", head, tail)
            item = self.tag_prevrange("SYNC", head)
            jeżeli item:
                head = item[1]
            inaczej:
                head = "1.0"

            chars = ""
            next = head
            lines_to_get = 1
            ok = Nieprawda
            dopóki nie ok:
                mark = next
                next = self.index(mark + "+%d lines linestart" %
                                         lines_to_get)
                lines_to_get = min(lines_to_get * 2, 100)
                ok = "SYNC" w self.tag_names(next + "-1c")
                line = self.get(mark, next)
                ##print head, "get", mark, next, "->", repr(line)
                jeżeli nie line:
                    zwróć
                dla tag w self.tagdefs:
                    self.tag_remove(tag, mark, next)
                chars = chars + line
                m = self.prog.search(chars)
                dopóki m:
                    dla key, value w m.groupdict().items():
                        jeżeli value:
                            a, b = m.span(key)
                            self.tag_add(key,
                                         head + "+%dc" % a,
                                         head + "+%dc" % b)
                            jeżeli value w ("def", "class"):
                                m1 = self.idprog.match(chars, b)
                                jeżeli m1:
                                    a, b = m1.span(1)
                                    self.tag_add("DEFINITION",
                                                 head + "+%dc" % a,
                                                 head + "+%dc" % b)
                    m = self.prog.search(chars, m.end())
                jeżeli "SYNC" w self.tag_names(next + "-1c"):
                    head = next
                    chars = ""
                inaczej:
                    ok = Nieprawda
                jeżeli nie ok:
                    # We're w an inconsistent state, oraz the call to
                    # update may tell us to stop.  It may also change
                    # the correct value dla "next" (since this jest a
                    # line.col string, nie a true mark).  So leave a
                    # crumb telling the next invocation to resume here
                    # w case update tells us to leave.
                    self.tag_add("TODO", next)
                self.update()
                jeżeli self.stop_colorizing:
                    jeżeli DEBUG: print("colorizing stopped")
                    zwróć

    def removecolors(self):
        dla tag w self.tagdefs:
            self.tag_remove(tag, "1.0", "end")

def _color_delegator(parent):  # htest #
    z tkinter zaimportuj Toplevel, Text
    z idlelib.Percolator zaimportuj Percolator

    top = Toplevel(parent)
    top.title("Test ColorDelegator")
    top.geometry("200x100+%d+%d" % (parent.winfo_rootx() + 200,
                  parent.winfo_rooty() + 150))
    source = "jeżeli somename: x = 'abc' # comment\nprint\n"
    text = Text(top, background="white")
    text.pack(expand=1, fill="both")
    text.insert("insert", source)
    text.focus_set()

    p = Percolator(text)
    d = ColorDelegator()
    p.insertfilter(d)

jeżeli __name__ == "__main__":
    z idlelib.idle_test.htest zaimportuj run
    run(_color_delegator)
