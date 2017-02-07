z . zaimportuj util jako test_util
machinery = test_util.import_importlib('importlib.machinery')

zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj unittest
z test zaimportuj support
z distutils.util zaimportuj get_platform
z contextlib zaimportuj contextmanager
z .util zaimportuj temp_module

support.import_module('winreg', required_on=['win'])
z winreg zaimportuj (
    CreateKey, HKEY_CURRENT_USER,
    SetValue, REG_SZ, KEY_ALL_ACCESS,
    EnumKey, CloseKey, DeleteKey, OpenKey
)

def delete_registry_tree(root, subkey):
    spróbuj:
        hkey = OpenKey(root, subkey, access=KEY_ALL_ACCESS)
    wyjąwszy OSError:
        # subkey does nie exist
        zwróć
    dopóki Prawda:
        spróbuj:
            subsubkey = EnumKey(hkey, 0)
        wyjąwszy OSError:
            # no more subkeys
            przerwij
        delete_registry_tree(hkey, subsubkey)
    CloseKey(hkey)
    DeleteKey(root, subkey)

@contextmanager
def setup_module(machinery, name, path=Nic):
    jeżeli machinery.WindowsRegistryFinder.DEBUG_BUILD:
        root = machinery.WindowsRegistryFinder.REGISTRY_KEY_DEBUG
    inaczej:
        root = machinery.WindowsRegistryFinder.REGISTRY_KEY
    key = root.format(fullname=name,
                      sys_version=sys.version[:3])
    spróbuj:
        przy temp_module(name, "a = 1") jako location:
            subkey = CreateKey(HKEY_CURRENT_USER, key)
            jeżeli path jest Nic:
                path = location + ".py"
            SetValue(subkey, "", REG_SZ, path)
            uzyskaj
    w_końcu:
        jeżeli machinery.WindowsRegistryFinder.DEBUG_BUILD:
            key = os.path.dirname(key)
        delete_registry_tree(HKEY_CURRENT_USER, key)


@unittest.skipUnless(sys.platform.startswith('win'), 'requires Windows')
klasa WindowsRegistryFinderTests:
    # The module name jest process-specific, allowing for
    # simultaneous runs of the same test on a single machine.
    test_module = "spamham{}".format(os.getpid())

    def test_find_spec_missing(self):
        spec = self.machinery.WindowsRegistryFinder.find_spec('spam')
        self.assertIs(spec, Nic)

    def test_find_module_missing(self):
        loader = self.machinery.WindowsRegistryFinder.find_module('spam')
        self.assertIs(loader, Nic)

    def test_module_found(self):
        przy setup_module(self.machinery, self.test_module):
            loader = self.machinery.WindowsRegistryFinder.find_module(self.test_module)
            spec = self.machinery.WindowsRegistryFinder.find_spec(self.test_module)
            self.assertIsNot(loader, Nic)
            self.assertIsNot(spec, Nic)

    def test_module_not_found(self):
        przy setup_module(self.machinery, self.test_module, path="."):
            loader = self.machinery.WindowsRegistryFinder.find_module(self.test_module)
            spec = self.machinery.WindowsRegistryFinder.find_spec(self.test_module)
            self.assertIsNic(loader)
            self.assertIsNic(spec)

(Frozen_WindowsRegistryFinderTests,
 Source_WindowsRegistryFinderTests
 ) = test_util.test_both(WindowsRegistryFinderTests, machinery=machinery)

@unittest.skipUnless(sys.platform.startswith('win'), 'requires Windows')
klasa WindowsExtensionSuffixTests:
    def test_tagged_suffix(self):
        suffixes = self.machinery.EXTENSION_SUFFIXES
        expected_tag = ".cp{0.major}{0.minor}-{1}.pyd".format(sys.version_info,
            re.sub('[^a-zA-Z0-9]', '_', get_platform()))
        spróbuj:
            untagged_i = suffixes.index(".pyd")
        wyjąwszy ValueError:
            untagged_i = suffixes.index("_d.pyd")
            expected_tag = "_d" + expected_tag

        self.assertIn(expected_tag, suffixes)

        # Ensure the tags are w the correct order
        tagged_i = suffixes.index(expected_tag)
        self.assertLess(tagged_i, untagged_i)

(Frozen_WindowsExtensionSuffixTests,
 Source_WindowsExtensionSuffixTests
 ) = test_util.test_both(WindowsExtensionSuffixTests, machinery=machinery)
