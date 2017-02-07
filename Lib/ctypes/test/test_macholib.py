zaimportuj os
zaimportuj sys
zaimportuj unittest

# Bob Ippolito:
#
# Ok.. the code to find the filename dla __getattr__ should look
# something like:
#
# zaimportuj os
# z macholib.dyld zaimportuj dyld_find
#
# def find_lib(name):
#      possible = ['lib'+name+'.dylib', name+'.dylib',
#      name+'.framework/'+name]
#      dla dylib w possible:
#          spróbuj:
#              zwróć os.path.realpath(dyld_find(dylib))
#          wyjąwszy ValueError:
#              dalej
#      podnieś ValueError, "%s nie found" % (name,)
#
# It'll have output like this:
#
#  >>> find_lib('pthread')
# '/usr/lib/libSystem.B.dylib'
#  >>> find_lib('z')
# '/usr/lib/libz.1.dylib'
#  >>> find_lib('IOKit')
# '/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit'
#
# -bob

z ctypes.macholib.dyld zaimportuj dyld_find

def find_lib(name):
    possible = ['lib'+name+'.dylib', name+'.dylib', name+'.framework/'+name]
    dla dylib w possible:
        spróbuj:
            zwróć os.path.realpath(dyld_find(dylib))
        wyjąwszy ValueError:
            dalej
    podnieś ValueError("%s nie found" % (name,))

klasa MachOTest(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "darwin", 'OSX-specific test')
    def test_find(self):

        self.assertEqual(find_lib('pthread'),
                             '/usr/lib/libSystem.B.dylib')

        result = find_lib('z')
        # Issue #21093: dyld default search path includes $HOME/lib oraz
        # /usr/local/lib before /usr/lib, which caused test failures if
        # a local copy of libz exists w one of them. Now ignore the head
        # of the path.
        self.assertRegex(result, r".*/lib/libz\..*.*\.dylib")

        self.assertEqual(find_lib('IOKit'),
                             '/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit')

jeżeli __name__ == "__main__":
    unittest.main()
