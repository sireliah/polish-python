'Provides "Strip trailing whitespace" under the "Format" menu.'

klasa RstripExtension:

    menudefs = [
        ('format', [Nic, ('Strip trailing whitespace', '<<do-rstrip>>'), ] ), ]

    def __init__(self, editwin):
        self.editwin = editwin
        self.editwin.text.bind("<<do-rstrip>>", self.do_rstrip)

    def do_rstrip(self, event=Nic):

        text = self.editwin.text
        undo = self.editwin.undo

        undo.undo_block_start()

        end_line = int(float(text.index('end')))
        dla cur w range(1, end_line):
            txt = text.get('%i.0' % cur, '%i.end' % cur)
            raw = len(txt)
            cut = len(txt.rstrip())
            # Since text.delete() marks file jako changed, even jeżeli not,
            # only call it when needed to actually delete something.
            jeżeli cut < raw:
                text.delete('%i.%i' % (cur, cut), '%i.end' % cur)

        undo.undo_block_stop()

jeżeli __name__ == "__main__":
    zaimportuj unittest
    unittest.main('idlelib.idle_test.test_rstrip', verbosity=2, exit=Nieprawda)
