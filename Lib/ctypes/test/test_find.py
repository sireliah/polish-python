zaimportuj unittest
zaimportuj os
zaimportuj sys
zaimportuj test.support
z ctypes zaimportuj *
z ctypes.util zaimportuj find_library

# On some systems, loading the OpenGL libraries needs the RTLD_GLOBAL mode.
klasa Test_OpenGL_libs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lib_gl = lib_glu = lib_gle = Nic
        jeżeli sys.platform == "win32":
            lib_gl = find_library("OpenGL32")
            lib_glu = find_library("Glu32")
        albo_inaczej sys.platform == "darwin":
            lib_gl = lib_glu = find_library("OpenGL")
        inaczej:
            lib_gl = find_library("GL")
            lib_glu = find_library("GLU")
            lib_gle = find_library("gle")

        ## print, dla debugging
        jeżeli test.support.verbose:
            print("OpenGL libraries:")
            dla item w (("GL", lib_gl),
                         ("GLU", lib_glu),
                         ("gle", lib_gle)):
                print("\t", item)

        cls.gl = cls.glu = cls.gle = Nic
        jeżeli lib_gl:
            spróbuj:
                cls.gl = CDLL(lib_gl, mode=RTLD_GLOBAL)
            wyjąwszy OSError:
                dalej
        jeżeli lib_glu:
            spróbuj:
                cls.glu = CDLL(lib_glu, RTLD_GLOBAL)
            wyjąwszy OSError:
                dalej
        jeżeli lib_gle:
            spróbuj:
                cls.gle = CDLL(lib_gle)
            wyjąwszy OSError:
                dalej

    @classmethod
    def tearDownClass(cls):
        cls.gl = cls.glu = cls.gle = Nic

    def test_gl(self):
        jeżeli self.gl jest Nic:
            self.skipTest('lib_gl nie available')
        self.gl.glClearIndex

    def test_glu(self):
        jeżeli self.glu jest Nic:
            self.skipTest('lib_glu nie available')
        self.glu.gluBeginCurve

    def test_gle(self):
        jeżeli self.gle jest Nic:
            self.skipTest('lib_gle nie available')
        self.gle.gleGetJoinStyle

# On platforms where the default shared library suffix jest '.so',
# at least some libraries can be loaded jako attributes of the cdll
# object, since ctypes now tries loading the lib again
# przy '.so' appended of the first try fails.
#
# Won't work dla libc, unfortunately.  OTOH, it isn't
# needed dla libc since this jest already mapped into the current
# process (?)
#
# On MAC OSX, it won't work either, because dlopen() needs a full path,
# oraz the default suffix jest either none albo '.dylib'.
@unittest.skip('test disabled')
@unittest.skipUnless(os.name=="posix" oraz sys.platform != "darwin",
                     'test nie suitable dla this platform')
klasa LoadLibs(unittest.TestCase):
    def test_libm(self):
        zaimportuj math
        libm = cdll.libm
        sqrt = libm.sqrt
        sqrt.argtypes = (c_double,)
        sqrt.restype = c_double
        self.assertEqual(sqrt(2), math.sqrt(2))

jeżeli __name__ == "__main__":
    unittest.main()
