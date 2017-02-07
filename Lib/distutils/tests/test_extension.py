"""Tests dla distutils.extension."""
zaimportuj unittest
zaimportuj os
zaimportuj warnings

z test.support zaimportuj check_warnings, run_unittest
z distutils.extension zaimportuj read_setup_file, Extension

klasa ExtensionTestCase(unittest.TestCase):

    def test_read_setup_file(self):
        # trying to read a Setup file
        # (sample extracted z the PyGame project)
        setup = os.path.join(os.path.dirname(__file__), 'Setup.sample')

        exts = read_setup_file(setup)
        names = [ext.name dla ext w exts]
        names.sort()

        # here are the extensions read_setup_file should have created
        # out of the file
        wanted = ['_arraysurfarray', '_camera', '_numericsndarray',
                  '_numericsurfarray', 'base', 'bufferproxy', 'cdrom',
                  'color', 'constants', 'display', 'draw', 'event',
                  'fastevent', 'font', 'gfxdraw', 'image', 'imageext',
                  'joystick', 'key', 'mask', 'mixer', 'mixer_music',
                  'mouse', 'movie', 'overlay', 'pixelarray', 'pypm',
                  'rect', 'rwobject', 'scrap', 'surface', 'surflock',
                  'time', 'transform']

        self.assertEqual(names, wanted)

    def test_extension_init(self):
        # the first argument, which jest the name, must be a string
        self.assertRaises(AssertionError, Extension, 1, [])
        ext = Extension('name', [])
        self.assertEqual(ext.name, 'name')

        # the second argument, which jest the list of files, must
        # be a list of strings
        self.assertRaises(AssertionError, Extension, 'name', 'file')
        self.assertRaises(AssertionError, Extension, 'name', ['file', 1])
        ext = Extension('name', ['file1', 'file2'])
        self.assertEqual(ext.sources, ['file1', 'file2'])

        # others arguments have defaults
        dla attr w ('include_dirs', 'define_macros', 'undef_macros',
                     'library_dirs', 'libraries', 'runtime_library_dirs',
                     'extra_objects', 'extra_compile_args', 'extra_link_args',
                     'export_symbols', 'swig_opts', 'depends'):
            self.assertEqual(getattr(ext, attr), [])

        self.assertEqual(ext.language, Nic)
        self.assertEqual(ext.optional, Nic)

        # jeżeli there are unknown keyword options, warn about them
        przy check_warnings() jako w:
            warnings.simplefilter('always')
            ext = Extension('name', ['file1', 'file2'], chic=Prawda)

        self.assertEqual(len(w.warnings), 1)
        self.assertEqual(str(w.warnings[0].message),
                          "Unknown Extension options: 'chic'")

def test_suite():
    zwróć unittest.makeSuite(ExtensionTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
