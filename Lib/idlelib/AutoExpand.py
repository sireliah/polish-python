'''Complete the current word before the cursor przy words w the editor.

Each menu selection albo shortcut key selection replaces the word przy a
different word przy the same prefix. The search dla matches begins
before the target oraz moves toward the top of the editor. It then starts
after the cursor oraz moves down. It then returns to the original word oraz
the cycle starts again.

Changing the current text line albo leaving the cursor w a different
place before requesting the next selection causes AutoExpand to reset
its state.

This jest an extension file oraz there jest only one instance of AutoExpand.
'''
zaimportuj string
zaimportuj re

###$ event <<expand-word>>
###$ win <Alt-slash>
###$ unix <Alt-slash>

klasa AutoExpand:

    menudefs = [
        ('edit', [
            ('E_xpand Word', '<<expand-word>>'),
         ]),
    ]

    wordchars = string.ascii_letters + string.digits + "_"

    def __init__(self, editwin):
        self.text = editwin.text
        self.state = Nic

    def expand_word_event(self, event):
        "Replace the current word przy the next expansion."
        curinsert = self.text.index("insert")
        curline = self.text.get("insert linestart", "insert lineend")
        jeżeli nie self.state:
            words = self.getwords()
            index = 0
        inaczej:
            words, index, insert, line = self.state
            jeżeli insert != curinsert albo line != curline:
                words = self.getwords()
                index = 0
        jeżeli nie words:
            self.text.bell()
            zwróć "break"
        word = self.getprevword()
        self.text.delete("insert - %d chars" % len(word), "insert")
        newword = words[index]
        index = (index + 1) % len(words)
        jeżeli index == 0:
            self.text.bell()            # Warn we cycled around
        self.text.insert("insert", newword)
        curinsert = self.text.index("insert")
        curline = self.text.get("insert linestart", "insert lineend")
        self.state = words, index, curinsert, curline
        zwróć "break"

    def getwords(self):
        "Return a list of words that match the prefix before the cursor."
        word = self.getprevword()
        jeżeli nie word:
            zwróć []
        before = self.text.get("1.0", "insert wordstart")
        wbefore = re.findall(r"\b" + word + r"\w+\b", before)
        usuń before
        after = self.text.get("insert wordend", "end")
        wafter = re.findall(r"\b" + word + r"\w+\b", after)
        usuń after
        jeżeli nie wbefore oraz nie wafter:
            zwróć []
        words = []
        dict = {}
        # search backwards through words before
        wbefore.reverse()
        dla w w wbefore:
            jeżeli dict.get(w):
                kontynuuj
            words.append(w)
            dict[w] = w
        # search onwards through words after
        dla w w wafter:
            jeżeli dict.get(w):
                kontynuuj
            words.append(w)
            dict[w] = w
        words.append(word)
        zwróć words

    def getprevword(self):
        "Return the word prefix before the cursor."
        line = self.text.get("insert linestart", "insert")
        i = len(line)
        dopóki i > 0 oraz line[i-1] w self.wordchars:
            i = i-1
        zwróć line[i:]

jeżeli __name__ == '__main__':
    zaimportuj unittest
    unittest.main('idlelib.idle_test.test_autoexpand', verbosity=2)
