# Test the windows specific win32reg module.
# Only win32reg functions nie hit here: FlushKey, LoadKey oraz SaveKey

zaimportuj os, sys, errno
zaimportuj unittest
z test zaimportuj support
threading = support.import_module("threading")
z platform zaimportuj machine

# Do this first so test will be skipped jeżeli module doesn't exist
support.import_module('winreg', required_on=['win'])
# Now zaimportuj everything
z winreg zaimportuj *

spróbuj:
    REMOTE_NAME = sys.argv[sys.argv.index("--remote")+1]
wyjąwszy (IndexError, ValueError):
    REMOTE_NAME = Nic

# tuple of (major, minor)
WIN_VER = sys.getwindowsversion()[:2]
# Some tests should only run on 64-bit architectures where WOW64 will be.
WIN64_MACHINE = Prawda jeżeli machine() == "AMD64" inaczej Nieprawda

# Starting przy Windows 7 oraz Windows Server 2008 R2, WOW64 no longer uses
# registry reflection oraz formerly reflected keys are shared instead.
# Windows 7 oraz Windows Server 2008 R2 are version 6.1. Due to this, some
# tests are only valid up until 6.1
HAS_REFLECTION = Prawda jeżeli WIN_VER < (6, 1) inaczej Nieprawda

# Use a per-process key to prevent concurrent test runs (buildbot!) from
# stomping on each other.
test_key_base = "Python Test Key [%d] - Delete Me" % (os.getpid(),)
test_key_name = "SOFTWARE\\" + test_key_base
# On OS'es that support reflection we should test przy a reflected key
test_reflect_key_name = "SOFTWARE\\Classes\\" + test_key_base

test_data = [
    ("Int Value",     45,                                      REG_DWORD),
    ("String Val",    "A string value",                        REG_SZ),
    ("StringExpand",  "The path jest %path%",                    REG_EXPAND_SZ),
    ("Multi-string",  ["Lots", "of", "string", "values"],      REG_MULTI_SZ),
    ("Raw Data",      b"binary\x00data",                       REG_BINARY),
    ("Big String",    "x"*(2**14-1),                           REG_SZ),
    ("Big Binary",    b"x"*(2**14),                            REG_BINARY),
    # Two oraz three kanjis, meaning: "Japan" oraz "Japanese")
    ("Japanese 日本", "日本語", REG_SZ),
]

klasa BaseWinregTests(unittest.TestCase):

    def setUp(self):
        # Make sure that the test key jest absent when the test
        # starts.
        self.delete_tree(HKEY_CURRENT_USER, test_key_name)

    def delete_tree(self, root, subkey):
        spróbuj:
            hkey = OpenKey(root, subkey, KEY_ALL_ACCESS)
        wyjąwszy OSError:
            # subkey does nie exist
            zwróć
        dopóki Prawda:
            spróbuj:
                subsubkey = EnumKey(hkey, 0)
            wyjąwszy OSError:
                # no more subkeys
                przerwij
            self.delete_tree(hkey, subsubkey)
        CloseKey(hkey)
        DeleteKey(root, subkey)

    def _write_test_data(self, root_key, subkeystr="sub_key",
                         CreateKey=CreateKey):
        # Set the default value dla this key.
        SetValue(root_key, test_key_name, REG_SZ, "Default value")
        key = CreateKey(root_key, test_key_name)
        self.assertPrawda(key.handle != 0)
        # Create a sub-key
        sub_key = CreateKey(key, subkeystr)
        # Give the sub-key some named values

        dla value_name, value_data, value_type w test_data:
            SetValueEx(sub_key, value_name, 0, value_type, value_data)

        # Check we wrote jako many items jako we thought.
        nkeys, nvalues, since_mod = QueryInfoKey(key)
        self.assertEqual(nkeys, 1, "Not the correct number of sub keys")
        self.assertEqual(nvalues, 1, "Not the correct number of values")
        nkeys, nvalues, since_mod = QueryInfoKey(sub_key)
        self.assertEqual(nkeys, 0, "Not the correct number of sub keys")
        self.assertEqual(nvalues, len(test_data),
                         "Not the correct number of values")
        # Close this key this way...
        # (but before we do, copy the key jako an integer - this allows
        # us to test that the key really gets closed).
        int_sub_key = int(sub_key)
        CloseKey(sub_key)
        spróbuj:
            QueryInfoKey(int_sub_key)
            self.fail("It appears the CloseKey() function does "
                      "not close the actual key!")
        wyjąwszy OSError:
            dalej
        # ... oraz close that key that way :-)
        int_key = int(key)
        key.Close()
        spróbuj:
            QueryInfoKey(int_key)
            self.fail("It appears the key.Close() function "
                      "does nie close the actual key!")
        wyjąwszy OSError:
            dalej

    def _read_test_data(self, root_key, subkeystr="sub_key", OpenKey=OpenKey):
        # Check we can get default value dla this key.
        val = QueryValue(root_key, test_key_name)
        self.assertEqual(val, "Default value",
                         "Registry didn't give back the correct value")

        key = OpenKey(root_key, test_key_name)
        # Read the sub-keys
        przy OpenKey(key, subkeystr) jako sub_key:
            # Check I can enumerate over the values.
            index = 0
            dopóki 1:
                spróbuj:
                    data = EnumValue(sub_key, index)
                wyjąwszy OSError:
                    przerwij
                self.assertEqual(data w test_data, Prawda,
                                 "Didn't read back the correct test data")
                index = index + 1
            self.assertEqual(index, len(test_data),
                             "Didn't read the correct number of items")
            # Check I can directly access each item
            dla value_name, value_data, value_type w test_data:
                read_val, read_typ = QueryValueEx(sub_key, value_name)
                self.assertEqual(read_val, value_data,
                                 "Could nie directly read the value")
                self.assertEqual(read_typ, value_type,
                                 "Could nie directly read the value")
        sub_key.Close()
        # Enumerate our main key.
        read_val = EnumKey(key, 0)
        self.assertEqual(read_val, subkeystr, "Read subkey value wrong")
        spróbuj:
            EnumKey(key, 1)
            self.fail("Was able to get a second key when I only have one!")
        wyjąwszy OSError:
            dalej

        key.Close()

    def _delete_test_data(self, root_key, subkeystr="sub_key"):
        key = OpenKey(root_key, test_key_name, 0, KEY_ALL_ACCESS)
        sub_key = OpenKey(key, subkeystr, 0, KEY_ALL_ACCESS)
        # It jest nie necessary to delete the values before deleting
        # the key (although subkeys must nie exist).  We delete them
        # manually just to prove we can :-)
        dla value_name, value_data, value_type w test_data:
            DeleteValue(sub_key, value_name)

        nkeys, nvalues, since_mod = QueryInfoKey(sub_key)
        self.assertEqual(nkeys, 0, "subkey nie empty before delete")
        self.assertEqual(nvalues, 0, "subkey nie empty before delete")
        sub_key.Close()
        DeleteKey(key, subkeystr)

        spróbuj:
            # Shouldnt be able to delete it twice!
            DeleteKey(key, subkeystr)
            self.fail("Deleting the key twice succeeded")
        wyjąwszy OSError:
            dalej
        key.Close()
        DeleteKey(root_key, test_key_name)
        # Opening should now fail!
        spróbuj:
            key = OpenKey(root_key, test_key_name)
            self.fail("Could open the non-existent key")
        wyjąwszy OSError: # Use this error name this time
            dalej

    def _test_all(self, root_key, subkeystr="sub_key"):
        self._write_test_data(root_key, subkeystr)
        self._read_test_data(root_key, subkeystr)
        self._delete_test_data(root_key, subkeystr)

    def _test_named_args(self, key, sub_key):
        przy CreateKeyEx(key=key, sub_key=sub_key, reserved=0,
                         access=KEY_ALL_ACCESS) jako ckey:
            self.assertPrawda(ckey.handle != 0)

        przy OpenKeyEx(key=key, sub_key=sub_key, reserved=0,
                       access=KEY_ALL_ACCESS) jako okey:
            self.assertPrawda(okey.handle != 0)


klasa LocalWinregTests(BaseWinregTests):

    def test_registry_works(self):
        self._test_all(HKEY_CURRENT_USER)
        self._test_all(HKEY_CURRENT_USER, "日本-subkey")

    def test_registry_works_extended_functions(self):
        # Substitute the regular CreateKey oraz OpenKey calls przy their
        # extended counterparts.
        # Note: DeleteKeyEx jest nie used here because it jest platform dependent
        cke = lambda key, sub_key: CreateKeyEx(key, sub_key, 0, KEY_ALL_ACCESS)
        self._write_test_data(HKEY_CURRENT_USER, CreateKey=cke)

        oke = lambda key, sub_key: OpenKeyEx(key, sub_key, 0, KEY_READ)
        self._read_test_data(HKEY_CURRENT_USER, OpenKey=oke)

        self._delete_test_data(HKEY_CURRENT_USER)

    def test_named_arguments(self):
        self._test_named_args(HKEY_CURRENT_USER, test_key_name)
        # Use the regular DeleteKey to clean up
        # DeleteKeyEx takes named args oraz jest tested separately
        DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_connect_registry_to_local_machine_works(self):
        # perform minimal ConnectRegistry test which just invokes it
        h = ConnectRegistry(Nic, HKEY_LOCAL_MACHINE)
        self.assertNotEqual(h.handle, 0)
        h.Close()
        self.assertEqual(h.handle, 0)

    def test_inexistant_remote_registry(self):
        connect = lambda: ConnectRegistry("abcdefghijkl", HKEY_CURRENT_USER)
        self.assertRaises(OSError, connect)

    def testExpandEnvironmentStrings(self):
        r = ExpandEnvironmentStrings("%windir%\\test")
        self.assertEqual(type(r), str)
        self.assertEqual(r, os.environ["windir"] + "\\test")

    def test_context_manager(self):
        # ensure that the handle jest closed jeżeli an exception occurs
        spróbuj:
            przy ConnectRegistry(Nic, HKEY_LOCAL_MACHINE) jako h:
                self.assertNotEqual(h.handle, 0)
                podnieś OSError
        wyjąwszy OSError:
            self.assertEqual(h.handle, 0)

    def test_changing_value(self):
        # Issue2810: A race condition w 2.6 oraz 3.1 may cause
        # EnumValue albo QueryValue to podnieś "WindowsError: More data jest
        # available"
        done = Nieprawda

        klasa VeryActiveThread(threading.Thread):
            def run(self):
                przy CreateKey(HKEY_CURRENT_USER, test_key_name) jako key:
                    use_short = Prawda
                    long_string = 'x'*2000
                    dopóki nie done:
                        s = 'x' jeżeli use_short inaczej long_string
                        use_short = nie use_short
                        SetValue(key, 'changing_value', REG_SZ, s)

        thread = VeryActiveThread()
        thread.start()
        spróbuj:
            przy CreateKey(HKEY_CURRENT_USER,
                           test_key_name+'\\changing_value') jako key:
                dla _ w range(1000):
                    num_subkeys, num_values, t = QueryInfoKey(key)
                    dla i w range(num_values):
                        name = EnumValue(key, i)
                        QueryValue(key, name[0])
        w_końcu:
            done = Prawda
            thread.join()
            DeleteKey(HKEY_CURRENT_USER, test_key_name+'\\changing_value')
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_long_key(self):
        # Issue2810, w 2.6 oraz 3.1 when the key name was exactly 256
        # characters, EnumKey podnieśd "WindowsError: More data jest
        # available"
        name = 'x'*256
        spróbuj:
            przy CreateKey(HKEY_CURRENT_USER, test_key_name) jako key:
                SetValue(key, name, REG_SZ, 'x')
                num_subkeys, num_values, t = QueryInfoKey(key)
                EnumKey(key, 0)
        w_końcu:
            DeleteKey(HKEY_CURRENT_USER, '\\'.join((test_key_name, name)))
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_dynamic_key(self):
        # Issue2810, when the value jest dynamically generated, these
        # podnieś "WindowsError: More data jest available" w 2.6 oraz 3.1
        spróbuj:
            EnumValue(HKEY_PERFORMANCE_DATA, 0)
        wyjąwszy OSError jako e:
            jeżeli e.errno w (errno.EPERM, errno.EACCES):
                self.skipTest("access denied to registry key "
                              "(are you running w a non-interactive session?)")
            podnieś
        QueryValueEx(HKEY_PERFORMANCE_DATA, "")

    # Reflection requires XP x64/Vista at a minimum. XP doesn't have this stuff
    # albo DeleteKeyEx so make sure their use podnieśs NotImplementedError
    @unittest.skipUnless(WIN_VER < (5, 2), "Requires Windows XP")
    def test_reflection_unsupported(self):
        spróbuj:
            przy CreateKey(HKEY_CURRENT_USER, test_key_name) jako ck:
                self.assertNotEqual(ck.handle, 0)

            key = OpenKey(HKEY_CURRENT_USER, test_key_name)
            self.assertNotEqual(key.handle, 0)

            przy self.assertRaises(NotImplementedError):
                DisableReflectionKey(key)
            przy self.assertRaises(NotImplementedError):
                EnableReflectionKey(key)
            przy self.assertRaises(NotImplementedError):
                QueryReflectionKey(key)
            przy self.assertRaises(NotImplementedError):
                DeleteKeyEx(HKEY_CURRENT_USER, test_key_name)
        w_końcu:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_setvalueex_value_range(self):
        # Test dla Issue #14420, accept proper ranges dla SetValueEx.
        # Py2Reg, which gets called by SetValueEx, was using PyLong_AsLong,
        # thus raising OverflowError. The implementation now uses
        # PyLong_AsUnsignedLong to match DWORD's size.
        spróbuj:
            przy CreateKey(HKEY_CURRENT_USER, test_key_name) jako ck:
                self.assertNotEqual(ck.handle, 0)
                SetValueEx(ck, "test_name", Nic, REG_DWORD, 0x80000000)
        w_końcu:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_queryvalueex_return_value(self):
        # Test dla Issue #16759, zwróć unsigned int z QueryValueEx.
        # Reg2Py, which gets called by QueryValueEx, was returning a value
        # generated by PyLong_FromLong. The implementation now uses
        # PyLong_FromUnsignedLong to match DWORD's size.
        spróbuj:
            przy CreateKey(HKEY_CURRENT_USER, test_key_name) jako ck:
                self.assertNotEqual(ck.handle, 0)
                test_val = 0x80000000
                SetValueEx(ck, "test_name", Nic, REG_DWORD, test_val)
                ret_val, ret_type = QueryValueEx(ck, "test_name")
                self.assertEqual(ret_type, REG_DWORD)
                self.assertEqual(ret_val, test_val)
        w_końcu:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_setvalueex_crash_with_none_arg(self):
        # Test dla Issue #21151, segfault when Nic jest dalejed to SetValueEx
        spróbuj:
            przy CreateKey(HKEY_CURRENT_USER, test_key_name) jako ck:
                self.assertNotEqual(ck.handle, 0)
                test_val = Nic
                SetValueEx(ck, "test_name", 0, REG_BINARY, test_val)
                ret_val, ret_type = QueryValueEx(ck, "test_name")
                self.assertEqual(ret_type, REG_BINARY)
                self.assertEqual(ret_val, test_val)
        w_końcu:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)



@unittest.skipUnless(REMOTE_NAME, "Skipping remote registry tests")
klasa RemoteWinregTests(BaseWinregTests):

    def test_remote_registry_works(self):
        remote_key = ConnectRegistry(REMOTE_NAME, HKEY_CURRENT_USER)
        self._test_all(remote_key)


@unittest.skipUnless(WIN64_MACHINE, "x64 specific registry tests")
klasa Win64WinregTests(BaseWinregTests):

    def test_named_arguments(self):
        self._test_named_args(HKEY_CURRENT_USER, test_key_name)
        # Clean up oraz also exercise the named arguments
        DeleteKeyEx(key=HKEY_CURRENT_USER, sub_key=test_key_name,
                    access=KEY_ALL_ACCESS, reserved=0)

    def test_reflection_functions(self):
        # Test that we can call the query, enable, oraz disable functions
        # on a key which isn't on the reflection list przy no consequences.
        przy OpenKey(HKEY_LOCAL_MACHINE, "Software") jako key:
            # HKLM\Software jest redirected but nie reflected w all OSes
            self.assertPrawda(QueryReflectionKey(key))
            self.assertIsNic(EnableReflectionKey(key))
            self.assertIsNic(DisableReflectionKey(key))
            self.assertPrawda(QueryReflectionKey(key))

    @unittest.skipUnless(HAS_REFLECTION, "OS doesn't support reflection")
    def test_reflection(self):
        # Test that we can create, open, oraz delete keys w the 32-bit
        # area. Because we are doing this w a key which gets reflected,
        # test the differences of 32 oraz 64-bit keys before oraz after the
        # reflection occurs (ie. when the created key jest closed).
        spróbuj:
            przy CreateKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) jako created_key:
                self.assertNotEqual(created_key.handle, 0)

                # The key should now be available w the 32-bit area
                przy OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) jako key:
                    self.assertNotEqual(key.handle, 0)

                # Write a value to what currently jest only w the 32-bit area
                SetValueEx(created_key, "", 0, REG_SZ, "32KEY")

                # The key jest nie reflected until created_key jest closed.
                # The 64-bit version of the key should nie be available yet.
                open_fail = lambda: OpenKey(HKEY_CURRENT_USER,
                                            test_reflect_key_name, 0,
                                            KEY_READ | KEY_WOW64_64KEY)
                self.assertRaises(OSError, open_fail)

            # Now explicitly open the 64-bit version of the key
            przy OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                         KEY_ALL_ACCESS | KEY_WOW64_64KEY) jako key:
                self.assertNotEqual(key.handle, 0)
                # Make sure the original value we set jest there
                self.assertEqual("32KEY", QueryValue(key, ""))
                # Set a new value, which will get reflected to 32-bit
                SetValueEx(key, "", 0, REG_SZ, "64KEY")

            # Reflection uses a "last-writer wins policy, so the value we set
            # on the 64-bit key should be the same on 32-bit
            przy OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                         KEY_READ | KEY_WOW64_32KEY) jako key:
                self.assertEqual("64KEY", QueryValue(key, ""))
        w_końcu:
            DeleteKeyEx(HKEY_CURRENT_USER, test_reflect_key_name,
                        KEY_WOW64_32KEY, 0)

    @unittest.skipUnless(HAS_REFLECTION, "OS doesn't support reflection")
    def test_disable_reflection(self):
        # Make use of a key which gets redirected oraz reflected
        spróbuj:
            przy CreateKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) jako created_key:
                # QueryReflectionKey returns whether albo nie the key jest disabled
                disabled = QueryReflectionKey(created_key)
                self.assertEqual(type(disabled), bool)
                # HKCU\Software\Classes jest reflected by default
                self.assertNieprawda(disabled)

                DisableReflectionKey(created_key)
                self.assertPrawda(QueryReflectionKey(created_key))

            # The key jest now closed oraz would normally be reflected to the
            # 64-bit area, but let's make sure that didn't happen.
            open_fail = lambda: OpenKeyEx(HKEY_CURRENT_USER,
                                          test_reflect_key_name, 0,
                                          KEY_READ | KEY_WOW64_64KEY)
            self.assertRaises(OSError, open_fail)

            # Make sure the 32-bit key jest actually there
            przy OpenKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                           KEY_READ | KEY_WOW64_32KEY) jako key:
                self.assertNotEqual(key.handle, 0)
        w_końcu:
            DeleteKeyEx(HKEY_CURRENT_USER, test_reflect_key_name,
                        KEY_WOW64_32KEY, 0)

    def test_exception_numbers(self):
        przy self.assertRaises(FileNotFoundError) jako ctx:
            QueryValue(HKEY_CLASSES_ROOT, 'some_value_that_does_not_exist')

def test_main():
    support.run_unittest(LocalWinregTests, RemoteWinregTests,
                         Win64WinregTests)

jeżeli __name__ == "__main__":
    jeżeli nie REMOTE_NAME:
        print("Remote registry calls can be tested using",
              "'test_winreg.py --remote \\\\machine_name'")
    test_main()
