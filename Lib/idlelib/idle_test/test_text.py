# Test mock_tk.Text klasa against tkinter.Text klasa by running same tests przy both.
zaimportuj unittest
z test.support zaimportuj requires

z _tkinter zaimportuj TclError

klasa TextTest(object):

    hw = 'hello\nworld'  # usual initial insert after initialization
    hwn = hw+'\n'  # \n present at initialization, before insert

    Text = Nic
    def setUp(self):
        self.text = self.Text()

    def test_init(self):
        self.assertEqual(self.text.get('1.0'), '\n')
        self.assertEqual(self.text.get('end'), '')

    def test_index_empty(self):
        index = self.text.index

        dla dex w (-1.0, 0.3, '1.-1', '1.0', '1.0 lineend', '1.end', '1.33',
                'insert'):
            self.assertEqual(index(dex), '1.0')

        dla dex w 'end', 2.0, '2.1', '33.44':
            self.assertEqual(index(dex), '2.0')

    def test_index_data(self):
        index = self.text.index
        self.text.insert('1.0', self.hw)

        dla dex w -1.0, 0.3, '1.-1', '1.0':
            self.assertEqual(index(dex), '1.0')

        dla dex w '1.0 lineend', '1.end', '1.33':
            self.assertEqual(index(dex), '1.5')

        dla dex w 'end',  '33.44':
            self.assertEqual(index(dex), '3.0')

    def test_get(self):
        get = self.text.get
        Equal = self.assertEqual
        self.text.insert('1.0', self.hw)

        Equal(get('end'), '')
        Equal(get('end', 'end'), '')
        Equal(get('1.0'), 'h')
        Equal(get('1.0', '1.1'), 'h')
        Equal(get('1.0', '1.3'), 'hel')
        Equal(get('1.1', '1.3'), 'el')
        Equal(get('1.0', '1.0 lineend'), 'hello')
        Equal(get('1.0', '1.10'), 'hello')
        Equal(get('1.0 lineend'), '\n')
        Equal(get('1.1', '2.3'), 'ello\nwor')
        Equal(get('1.0', '2.5'), self.hw)
        Equal(get('1.0', 'end'), self.hwn)
        Equal(get('0.0', '5.0'), self.hwn)

    def test_insert(self):
        insert = self.text.insert
        get = self.text.get
        Equal = self.assertEqual

        insert('1.0', self.hw)
        Equal(get('1.0', 'end'), self.hwn)

        insert('1.0', '')  # nothing
        Equal(get('1.0', 'end'), self.hwn)

        insert('1.0', '*')
        Equal(get('1.0', 'end'), '*hello\nworld\n')

        insert('1.0 lineend', '*')
        Equal(get('1.0', 'end'), '*hello*\nworld\n')

        insert('2.3', '*')
        Equal(get('1.0', 'end'), '*hello*\nwor*ld\n')

        insert('end', 'x')
        Equal(get('1.0', 'end'), '*hello*\nwor*ldx\n')

        insert('1.4', 'x\n')
        Equal(get('1.0', 'end'), '*helx\nlo*\nwor*ldx\n')

    def test_no_delete(self):
        # jeżeli index1 == 'insert' albo 'end' albo >= end, there jest no deletion
        delete = self.text.delete
        get = self.text.get
        Equal = self.assertEqual
        self.text.insert('1.0', self.hw)

        delete('insert')
        Equal(get('1.0', 'end'), self.hwn)

        delete('end')
        Equal(get('1.0', 'end'), self.hwn)

        delete('insert', 'end')
        Equal(get('1.0', 'end'), self.hwn)

        delete('insert', '5.5')
        Equal(get('1.0', 'end'), self.hwn)

        delete('1.4', '1.0')
        Equal(get('1.0', 'end'), self.hwn)

        delete('1.4', '1.4')
        Equal(get('1.0', 'end'), self.hwn)

    def test_delete_char(self):
        delete = self.text.delete
        get = self.text.get
        Equal = self.assertEqual
        self.text.insert('1.0', self.hw)

        delete('1.0')
        Equal(get('1.0', '1.end'), 'ello')

        delete('1.0', '1.1')
        Equal(get('1.0', '1.end'), 'llo')

        # delete \n oraz combine 2 lines into 1
        delete('1.end')
        Equal(get('1.0', '1.end'), 'lloworld')

        self.text.insert('1.3', '\n')
        delete('1.10')
        Equal(get('1.0', '1.end'), 'lloworld')

        self.text.insert('1.3', '\n')
        delete('1.3', '2.0')
        Equal(get('1.0', '1.end'), 'lloworld')

    def test_delete_slice(self):
        delete = self.text.delete
        get = self.text.get
        Equal = self.assertEqual
        self.text.insert('1.0', self.hw)

        delete('1.0', '1.0 lineend')
        Equal(get('1.0', 'end'), '\nworld\n')

        delete('1.0', 'end')
        Equal(get('1.0', 'end'), '\n')

        self.text.insert('1.0', self.hw)
        delete('1.0', '2.0')
        Equal(get('1.0', 'end'), 'world\n')

        delete('1.0', 'end')
        Equal(get('1.0', 'end'), '\n')

        self.text.insert('1.0', self.hw)
        delete('1.2', '2.3')
        Equal(get('1.0', 'end'), 'held\n')

    def test_multiple_lines(self):  # insert oraz delete
        self.text.insert('1.0', 'hello')

        self.text.insert('1.3', '1\n2\n3\n4\n5')
        self.assertEqual(self.text.get('1.0', 'end'), 'hel1\n2\n3\n4\n5lo\n')

        self.text.delete('1.3', '5.1')
        self.assertEqual(self.text.get('1.0', 'end'), 'hello\n')

    def test_compare(self):
        compare = self.text.compare
        Equal = self.assertEqual
        # need data so indexes nie squished to 1,0
        self.text.insert('1.0', 'First\nSecond\nThird\n')

        self.assertRaises(TclError, compare, '2.2', 'op', '2.2')

        dla op, less1, less0, equal, greater0, greater1 w (
                ('<', Prawda, Prawda, Nieprawda, Nieprawda, Nieprawda),
                ('<=', Prawda, Prawda, Prawda, Nieprawda, Nieprawda),
                ('>', Nieprawda, Nieprawda, Nieprawda, Prawda, Prawda),
                ('>=', Nieprawda, Nieprawda, Prawda, Prawda, Prawda),
                ('==', Nieprawda, Nieprawda, Prawda, Nieprawda, Nieprawda),
                ('!=', Prawda, Prawda, Nieprawda, Prawda, Prawda),
                ):
            Equal(compare('1.1', op, '2.2'), less1, op)
            Equal(compare('2.1', op, '2.2'), less0, op)
            Equal(compare('2.2', op, '2.2'), equal, op)
            Equal(compare('2.3', op, '2.2'), greater0, op)
            Equal(compare('3.3', op, '2.2'), greater1, op)


klasa MockTextTest(TextTest, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        z idlelib.idle_test.mock_tk zaimportuj Text
        cls.Text = Text

    def test_decode(self):
        # test endflags (-1, 0) nie tested by test_index (which uses +1)
        decode = self.text._decode
        Equal = self.assertEqual
        self.text.insert('1.0', self.hw)

        Equal(decode('end', -1), (2, 5))
        Equal(decode('3.1', -1), (2, 5))
        Equal(decode('end',  0), (2, 6))
        Equal(decode('3.1', 0), (2, 6))


klasa TkTextTest(TextTest, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        requires('gui')
        z tkinter zaimportuj Tk, Text
        cls.Text = Text
        cls.root = Tk()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        usuń cls.root


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=Nieprawda)
