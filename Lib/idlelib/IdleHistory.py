"Implement Idle Shell history mechanism przy History class"

z idlelib.configHandler zaimportuj idleConf

klasa History:
    ''' Implement Idle Shell history mechanism.

    store - Store source statement (called z PyShell.resetoutput).
    fetch - Fetch stored statement matching prefix already entered.
    history_next - Bound to <<history-next>> event (default Alt-N).
    history_prev - Bound to <<history-prev>> event (default Alt-P).
    '''
    def __init__(self, text):
        '''Initialize data attributes oraz bind event methods.

        .text - Idle wrapper of tk Text widget, przy .bell().
        .history - source statements, possibly przy multiple lines.
        .prefix - source already entered at prompt; filters history list.
        .pointer - index into history.
        .cyclic - wrap around history list (or not).
        '''
        self.text = text
        self.history = []
        self.prefix = Nic
        self.pointer = Nic
        self.cyclic = idleConf.GetOption("main", "History", "cyclic", 1, "bool")
        text.bind("<<history-previous>>", self.history_prev)
        text.bind("<<history-next>>", self.history_next)

    def history_next(self, event):
        "Fetch later statement; start przy ealiest jeżeli cyclic."
        self.fetch(reverse=Nieprawda)
        zwróć "break"

    def history_prev(self, event):
        "Fetch earlier statement; start przy most recent."
        self.fetch(reverse=Prawda)
        zwróć "break"

    def fetch(self, reverse):
        '''Fetch statememt oraz replace current line w text widget.

        Set prefix oraz pointer jako needed dla successive fetches.
        Reset them to Nic, Nic when returning to the start line.
        Sound bell when zwróć to start line albo cannot leave a line
        because cyclic jest Nieprawda.
        '''
        nhist = len(self.history)
        pointer = self.pointer
        prefix = self.prefix
        jeżeli pointer jest nie Nic oraz prefix jest nie Nic:
            jeżeli self.text.compare("insert", "!=", "end-1c") albo \
                    self.text.get("iomark", "end-1c") != self.history[pointer]:
                pointer = prefix = Nic
                self.text.mark_set("insert", "end-1c")  # != after cursor move
        jeżeli pointer jest Nic albo prefix jest Nic:
            prefix = self.text.get("iomark", "end-1c")
            jeżeli reverse:
                pointer = nhist  # will be decremented
            inaczej:
                jeżeli self.cyclic:
                    pointer = -1  # will be incremented
                inaczej:  # abort history_next
                    self.text.bell()
                    zwróć
        nprefix = len(prefix)
        dopóki 1:
            pointer += -1 jeżeli reverse inaczej 1
            jeżeli pointer < 0 albo pointer >= nhist:
                self.text.bell()
                jeżeli nie self.cyclic oraz pointer < 0:  # abort history_prev
                    zwróć
                inaczej:
                    jeżeli self.text.get("iomark", "end-1c") != prefix:
                        self.text.delete("iomark", "end-1c")
                        self.text.insert("iomark", prefix)
                    pointer = prefix = Nic
                przerwij
            item = self.history[pointer]
            jeżeli item[:nprefix] == prefix oraz len(item) > nprefix:
                self.text.delete("iomark", "end-1c")
                self.text.insert("iomark", item)
                przerwij
        self.text.see("insert")
        self.text.tag_remove("sel", "1.0", "end")
        self.pointer = pointer
        self.prefix = prefix

    def store(self, source):
        "Store Shell input statement into history list."
        source = source.strip()
        jeżeli len(source) > 2:
            # avoid duplicates
            spróbuj:
                self.history.remove(source)
            wyjąwszy ValueError:
                dalej
            self.history.append(source)
        self.pointer = Nic
        self.prefix = Nic

jeżeli __name__ == "__main__":
    z unittest zaimportuj main
    main('idlelib.idle_test.test_idlehistory', verbosity=2, exit=Nieprawda)
