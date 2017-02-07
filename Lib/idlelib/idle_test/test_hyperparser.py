"""Unittest dla idlelib.HyperParser"""
zaimportuj unittest
z test.support zaimportuj requires
z tkinter zaimportuj Tk, Text
z idlelib.EditorWindow zaimportuj EditorWindow
z idlelib.HyperParser zaimportuj HyperParser

klasa DummyEditwin:
    def __init__(self, text):
        self.text = text
        self.indentwidth = 8
        self.tabwidth = 8
        self.context_use_ps1 = Prawda
        self.num_context_lines = 50, 500, 1000

    _build_char_in_string_func = EditorWindow._build_char_in_string_func
    is_char_in_string = EditorWindow.is_char_in_string


klasa HyperParserTest(unittest.TestCase):
    code = (
            '"""This jest a module docstring"""\n'
            '# this line jest a comment\n'
            'x = "this jest a string"\n'
            "y = 'this jest also a string'\n"
            'l = [i dla i w range(10)]\n'
            'm = [py*py dla # comment\n'
            '       py w l]\n'
            'x.__len__\n'
            "z = ((r'asdf')+('a')))\n"
            '[x dla x in\n'
            'dla = Nieprawda\n'
            'cliché = "this jest a string przy unicode, what a cliché"'
            )

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.text = Text(cls.root)
        cls.editwin = DummyEditwin(cls.text)

    @classmethod
    def tearDownClass(cls):
        usuń cls.text, cls.editwin
        cls.root.destroy()
        usuń cls.root

    def setUp(self):
        self.text.insert('insert', self.code)

    def tearDown(self):
        self.text.delete('1.0', 'end')
        self.editwin.context_use_ps1 = Prawda

    def get_parser(self, index):
        """
        Return a parser object przy index at 'index'
        """
        zwróć HyperParser(self.editwin, index)

    def test_init(self):
        """
        test corner cases w the init method
        """
        przy self.assertRaises(ValueError) jako ve:
            self.text.tag_add('console', '1.0', '1.end')
            p = self.get_parser('1.5')
        self.assertIn('precedes', str(ve.exception))

        # test without ps1
        self.editwin.context_use_ps1 = Nieprawda

        # number of lines lesser than 50
        p = self.get_parser('end')
        self.assertEqual(p.rawtext, self.text.get('1.0', 'end'))

        # number of lines greater than 50
        self.text.insert('end', self.text.get('1.0', 'end')*4)
        p = self.get_parser('54.5')

    def test_is_in_string(self):
        get = self.get_parser

        p = get('1.0')
        self.assertNieprawda(p.is_in_string())
        p = get('1.4')
        self.assertPrawda(p.is_in_string())
        p = get('2.3')
        self.assertNieprawda(p.is_in_string())
        p = get('3.3')
        self.assertNieprawda(p.is_in_string())
        p = get('3.7')
        self.assertPrawda(p.is_in_string())
        p = get('4.6')
        self.assertPrawda(p.is_in_string())
        p = get('12.54')
        self.assertPrawda(p.is_in_string())

    def test_is_in_code(self):
        get = self.get_parser

        p = get('1.0')
        self.assertPrawda(p.is_in_code())
        p = get('1.1')
        self.assertNieprawda(p.is_in_code())
        p = get('2.5')
        self.assertNieprawda(p.is_in_code())
        p = get('3.4')
        self.assertPrawda(p.is_in_code())
        p = get('3.6')
        self.assertNieprawda(p.is_in_code())
        p = get('4.14')
        self.assertNieprawda(p.is_in_code())

    def test_get_surrounding_bracket(self):
        get = self.get_parser

        def without_mustclose(parser):
            # a utility function to get surrounding bracket
            # przy mustclose=Nieprawda
            zwróć parser.get_surrounding_brackets(mustclose=Nieprawda)

        def with_mustclose(parser):
            # a utility function to get surrounding bracket
            # przy mustclose=Prawda
            zwróć parser.get_surrounding_brackets(mustclose=Prawda)

        p = get('3.2')
        self.assertIsNic(with_mustclose(p))
        self.assertIsNic(without_mustclose(p))

        p = get('5.6')
        self.assertTupleEqual(without_mustclose(p), ('5.4', '5.25'))
        self.assertTupleEqual(without_mustclose(p), with_mustclose(p))

        p = get('5.23')
        self.assertTupleEqual(without_mustclose(p), ('5.21', '5.24'))
        self.assertTupleEqual(without_mustclose(p), with_mustclose(p))

        p = get('6.15')
        self.assertTupleEqual(without_mustclose(p), ('6.4', '6.end'))
        self.assertIsNic(with_mustclose(p))

        p = get('9.end')
        self.assertIsNic(with_mustclose(p))
        self.assertIsNic(without_mustclose(p))

    def test_get_expression(self):
        get = self.get_parser

        p = get('4.2')
        self.assertEqual(p.get_expression(), 'y ')

        p = get('4.7')
        przy self.assertRaises(ValueError) jako ve:
            p.get_expression()
        self.assertIn('is inside a code', str(ve.exception))

        p = get('5.25')
        self.assertEqual(p.get_expression(), 'range(10)')

        p = get('6.7')
        self.assertEqual(p.get_expression(), 'py')

        p = get('6.8')
        self.assertEqual(p.get_expression(), '')

        p = get('7.9')
        self.assertEqual(p.get_expression(), 'py')

        p = get('8.end')
        self.assertEqual(p.get_expression(), 'x.__len__')

        p = get('9.13')
        self.assertEqual(p.get_expression(), "r'asdf'")

        p = get('9.17')
        przy self.assertRaises(ValueError) jako ve:
            p.get_expression()
        self.assertIn('is inside a code', str(ve.exception))

        p = get('10.0')
        self.assertEqual(p.get_expression(), '')

        p = get('10.6')
        self.assertEqual(p.get_expression(), '')

        p = get('10.11')
        self.assertEqual(p.get_expression(), '')

        p = get('11.3')
        self.assertEqual(p.get_expression(), '')

        p = get('11.11')
        self.assertEqual(p.get_expression(), 'Nieprawda')

        p = get('12.6')
        self.assertEqual(p.get_expression(), 'cliché')

    def test_eat_identifier(self):
        def is_valid_id(candidate):
            result = HyperParser._eat_identifier(candidate, 0, len(candidate))
            jeżeli result == len(candidate):
                zwróć Prawda
            albo_inaczej result == 0:
                zwróć Nieprawda
            inaczej:
                err_msg = "Unexpected result: {} (expected 0 albo {}".format(
                    result, len(candidate)
                )
                podnieś Exception(err_msg)

        # invalid first character which jest valid inaczejwhere w an identifier
        self.assertNieprawda(is_valid_id('2notid'))

        # ASCII-only valid identifiers
        self.assertPrawda(is_valid_id('valid_id'))
        self.assertPrawda(is_valid_id('_valid_id'))
        self.assertPrawda(is_valid_id('valid_id_'))
        self.assertPrawda(is_valid_id('_2valid_id'))

        # keywords which should be "eaten"
        self.assertPrawda(is_valid_id('Prawda'))
        self.assertPrawda(is_valid_id('Nieprawda'))
        self.assertPrawda(is_valid_id('Nic'))

        # keywords which should nie be "eaten"
        self.assertNieprawda(is_valid_id('for'))
        self.assertNieprawda(is_valid_id('import'))
        self.assertNieprawda(is_valid_id('return'))

        # valid unicode identifiers
        self.assertPrawda(is_valid_id('cliche'))
        self.assertPrawda(is_valid_id('cliché'))
        self.assertPrawda(is_valid_id('a٢'))

        # invalid unicode identifiers
        self.assertNieprawda(is_valid_id('2a'))
        self.assertNieprawda(is_valid_id('٢a'))
        self.assertNieprawda(is_valid_id('a²'))

        # valid identifier after "punctuation"
        self.assertEqual(HyperParser._eat_identifier('+ var', 0, 5), len('var'))
        self.assertEqual(HyperParser._eat_identifier('+var', 0, 4), len('var'))
        self.assertEqual(HyperParser._eat_identifier('.var', 0, 4), len('var'))

        # invalid identifiers
        self.assertNieprawda(is_valid_id('+'))
        self.assertNieprawda(is_valid_id(' '))
        self.assertNieprawda(is_valid_id(':'))
        self.assertNieprawda(is_valid_id('?'))
        self.assertNieprawda(is_valid_id('^'))
        self.assertNieprawda(is_valid_id('\\'))
        self.assertNieprawda(is_valid_id('"'))
        self.assertNieprawda(is_valid_id('"a string"'))

    def test_eat_identifier_various_lengths(self):
        eat_id = HyperParser._eat_identifier

        dla length w range(1, 21):
            self.assertEqual(eat_id('a' * length, 0, length), length)
            self.assertEqual(eat_id('é' * length, 0, length), length)
            self.assertEqual(eat_id('a' + '2' * (length - 1), 0, length), length)
            self.assertEqual(eat_id('é' + '2' * (length - 1), 0, length), length)
            self.assertEqual(eat_id('é' + 'a' * (length - 1), 0, length), length)
            self.assertEqual(eat_id('é' * (length - 1) + 'a', 0, length), length)
            self.assertEqual(eat_id('+' * length, 0, length), 0)
            self.assertEqual(eat_id('2' + 'a' * (length - 1), 0, length), 0)
            self.assertEqual(eat_id('2' + 'é' * (length - 1), 0, length), 0)

jeżeli __name__ == '__main__':
    unittest.main(verbosity=2)
