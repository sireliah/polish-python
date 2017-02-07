"""Tests dla distutils.msvc9compiler."""
zaimportuj sys
zaimportuj unittest
zaimportuj os

z distutils.errors zaimportuj DistutilsPlatformError
z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest

# A manifest przy the only assembly reference being the msvcrt assembly, so
# should have the assembly completely stripped.  Note that although the
# assembly has a <security> reference the assembly jest removed - that jest
# currently a "feature", nie a bug :)
_MANIFEST_WITH_ONLY_MSVC_REFERENCE = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
          manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC90.CRT"
         version="9.0.21022.8" processorArchitecture="x86"
         publicKeyToken="XXXX">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
</assembly>
"""

# A manifest przy references to assemblies other than msvcrt.  When processed,
# this assembly should be returned przy just the msvcrt part removed.
_MANIFEST_WITH_MULTIPLE_REFERENCES = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
          manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC90.CRT"
         version="9.0.21022.8" processorArchitecture="x86"
         publicKeyToken="XXXX">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC90.MFC"
        version="9.0.21022.8" processorArchitecture="x86"
        publicKeyToken="XXXX"></assemblyIdentity>
    </dependentAssembly>
  </dependency>
</assembly>
"""

_CLEANED_MANIFEST = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
          manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>

  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC90.MFC"
        version="9.0.21022.8" processorArchitecture="x86"
        publicKeyToken="XXXX"></assemblyIdentity>
    </dependentAssembly>
  </dependency>
</assembly>"""

jeżeli sys.platform=="win32":
    z distutils.msvccompiler zaimportuj get_build_version
    jeżeli get_build_version()>=8.0:
        SKIP_MESSAGE = Nic
    inaczej:
        SKIP_MESSAGE = "These tests are only dla MSVC8.0 albo above"
inaczej:
    SKIP_MESSAGE = "These tests are only dla win32"

@unittest.skipUnless(SKIP_MESSAGE jest Nic, SKIP_MESSAGE)
klasa msvc9compilerTestCase(support.TempdirManager,
                            unittest.TestCase):

    def test_no_compiler(self):
        # makes sure query_vcvarsall podnieśs
        # a DistutilsPlatformError jeżeli the compiler
        # jest nie found
        z distutils.msvc9compiler zaimportuj query_vcvarsall
        def _find_vcvarsall(version):
            zwróć Nic

        z distutils zaimportuj msvc9compiler
        old_find_vcvarsall = msvc9compiler.find_vcvarsall
        msvc9compiler.find_vcvarsall = _find_vcvarsall
        spróbuj:
            self.assertRaises(DistutilsPlatformError, query_vcvarsall,
                             'wont find this version')
        w_końcu:
            msvc9compiler.find_vcvarsall = old_find_vcvarsall

    def test_reg_class(self):
        z distutils.msvc9compiler zaimportuj Reg
        self.assertRaises(KeyError, Reg.get_value, 'xxx', 'xxx')

        # looking dla values that should exist on all
        # windows registeries versions.
        path = r'Control Panel\Desktop'
        v = Reg.get_value(path, 'dragfullwindows')
        self.assertIn(v, ('0', '1', '2'))

        zaimportuj winreg
        HKCU = winreg.HKEY_CURRENT_USER
        keys = Reg.read_keys(HKCU, 'xxxx')
        self.assertEqual(keys, Nic)

        keys = Reg.read_keys(HKCU, r'Control Panel')
        self.assertIn('Desktop', keys)

    def test_remove_visual_c_ref(self):
        z distutils.msvc9compiler zaimportuj MSVCCompiler
        tempdir = self.mkdtemp()
        manifest = os.path.join(tempdir, 'manifest')
        f = open(manifest, 'w')
        spróbuj:
            f.write(_MANIFEST_WITH_MULTIPLE_REFERENCES)
        w_końcu:
            f.close()

        compiler = MSVCCompiler()
        compiler._remove_visual_c_ref(manifest)

        # see what we got
        f = open(manifest)
        spróbuj:
            # removing trailing spaces
            content = '\n'.join([line.rstrip() dla line w f.readlines()])
        w_końcu:
            f.close()

        # makes sure the manifest was properly cleaned
        self.assertEqual(content, _CLEANED_MANIFEST)

    def test_remove_entire_manifest(self):
        z distutils.msvc9compiler zaimportuj MSVCCompiler
        tempdir = self.mkdtemp()
        manifest = os.path.join(tempdir, 'manifest')
        f = open(manifest, 'w')
        spróbuj:
            f.write(_MANIFEST_WITH_ONLY_MSVC_REFERENCE)
        w_końcu:
            f.close()

        compiler = MSVCCompiler()
        got = compiler._remove_visual_c_ref(manifest)
        self.assertIsNic(got)


def test_suite():
    zwróć unittest.makeSuite(msvc9compilerTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
