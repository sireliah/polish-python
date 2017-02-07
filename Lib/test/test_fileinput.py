'''
Tests dla fileinput module.
Nick Mathewson
'''
zaimportuj os
zaimportuj sys
zaimportuj re
zaimportuj fileinput
zaimportuj collections
zaimportuj builtins
zaimportuj unittest

spróbuj:
    zaimportuj bz2
wyjąwszy ImportError:
    bz2 = Nic
spróbuj:
    zaimportuj gzip
wyjąwszy ImportError:
    gzip = Nic

z io zaimportuj BytesIO, StringIO
z fileinput zaimportuj FileInput, hook_encoded

z test.support zaimportuj verbose, TESTFN, run_unittest, check_warnings
z test.support zaimportuj unlink jako safe_unlink
z unittest zaimportuj mock


# The fileinput module has 2 interfaces: the FileInput klasa which does
# all the work, oraz a few functions (input, etc.) that use a global _state
# variable.

# Write lines (a list of lines) to temp file number i, oraz zwróć the
# temp file's name.
def writeTmp(i, lines, mode='w'):  # opening w text mode jest the default
    name = TESTFN + str(i)
    f = open(name, mode)
    dla line w lines:
        f.write(line)
    f.close()
    zwróć name

def remove_tempfiles(*names):
    dla name w names:
        jeżeli name:
            safe_unlink(name)

klasa BufferSizesTests(unittest.TestCase):
    def test_buffer_sizes(self):
        # First, run the tests przy default oraz teeny buffer size.
        dla round, bs w (0, 0), (1, 30):
            t1 = t2 = t3 = t4 = Nic
            spróbuj:
                t1 = writeTmp(1, ["Line %s of file 1\n" % (i+1) dla i w range(15)])
                t2 = writeTmp(2, ["Line %s of file 2\n" % (i+1) dla i w range(10)])
                t3 = writeTmp(3, ["Line %s of file 3\n" % (i+1) dla i w range(5)])
                t4 = writeTmp(4, ["Line %s of file 4\n" % (i+1) dla i w range(1)])
                self.buffer_size_test(t1, t2, t3, t4, bs, round)
            w_końcu:
                remove_tempfiles(t1, t2, t3, t4)

    def buffer_size_test(self, t1, t2, t3, t4, bs=0, round=0):
        pat = re.compile(r'LINE (\d+) OF FILE (\d+)')

        start = 1 + round*6
        jeżeli verbose:
            print('%s. Simple iteration (bs=%s)' % (start+0, bs))
        fi = FileInput(files=(t1, t2, t3, t4), bufsize=bs)
        lines = list(fi)
        fi.close()
        self.assertEqual(len(lines), 31)
        self.assertEqual(lines[4], 'Line 5 of file 1\n')
        self.assertEqual(lines[30], 'Line 1 of file 4\n')
        self.assertEqual(fi.lineno(), 31)
        self.assertEqual(fi.filename(), t4)

        jeżeli verbose:
            print('%s. Status variables (bs=%s)' % (start+1, bs))
        fi = FileInput(files=(t1, t2, t3, t4), bufsize=bs)
        s = "x"
        dopóki s oraz s != 'Line 6 of file 2\n':
            s = fi.readline()
        self.assertEqual(fi.filename(), t2)
        self.assertEqual(fi.lineno(), 21)
        self.assertEqual(fi.filelineno(), 6)
        self.assertNieprawda(fi.isfirstline())
        self.assertNieprawda(fi.isstdin())

        jeżeli verbose:
            print('%s. Nextfile (bs=%s)' % (start+2, bs))
        fi.nextfile()
        self.assertEqual(fi.readline(), 'Line 1 of file 3\n')
        self.assertEqual(fi.lineno(), 22)
        fi.close()

        jeżeli verbose:
            print('%s. Stdin (bs=%s)' % (start+3, bs))
        fi = FileInput(files=(t1, t2, t3, t4, '-'), bufsize=bs)
        savestdin = sys.stdin
        spróbuj:
            sys.stdin = StringIO("Line 1 of stdin\nLine 2 of stdin\n")
            lines = list(fi)
            self.assertEqual(len(lines), 33)
            self.assertEqual(lines[32], 'Line 2 of stdin\n')
            self.assertEqual(fi.filename(), '<stdin>')
            fi.nextfile()
        w_końcu:
            sys.stdin = savestdin

        jeżeli verbose:
            print('%s. Boundary conditions (bs=%s)' % (start+4, bs))
        fi = FileInput(files=(t1, t2, t3, t4), bufsize=bs)
        self.assertEqual(fi.lineno(), 0)
        self.assertEqual(fi.filename(), Nic)
        fi.nextfile()
        self.assertEqual(fi.lineno(), 0)
        self.assertEqual(fi.filename(), Nic)

        jeżeli verbose:
            print('%s. Inplace (bs=%s)' % (start+5, bs))
        savestdout = sys.stdout
        spróbuj:
            fi = FileInput(files=(t1, t2, t3, t4), inplace=1, bufsize=bs)
            dla line w fi:
                line = line[:-1].upper()
                print(line)
            fi.close()
        w_końcu:
            sys.stdout = savestdout

        fi = FileInput(files=(t1, t2, t3, t4), bufsize=bs)
        dla line w fi:
            self.assertEqual(line[-1], '\n')
            m = pat.match(line[:-1])
            self.assertNotEqual(m, Nic)
            self.assertEqual(int(m.group(1)), fi.filelineno())
        fi.close()

klasa UnconditionallyRaise:
    def __init__(self, exception_type):
        self.exception_type = exception_type
        self.invoked = Nieprawda
    def __call__(self, *args, **kwargs):
        self.invoked = Prawda
        podnieś self.exception_type()

klasa FileInputTests(unittest.TestCase):

    def test_zero_byte_files(self):
        t1 = t2 = t3 = t4 = Nic
        spróbuj:
            t1 = writeTmp(1, [""])
            t2 = writeTmp(2, [""])
            t3 = writeTmp(3, ["The only line there is.\n"])
            t4 = writeTmp(4, [""])
            fi = FileInput(files=(t1, t2, t3, t4))

            line = fi.readline()
            self.assertEqual(line, 'The only line there is.\n')
            self.assertEqual(fi.lineno(), 1)
            self.assertEqual(fi.filelineno(), 1)
            self.assertEqual(fi.filename(), t3)

            line = fi.readline()
            self.assertNieprawda(line)
            self.assertEqual(fi.lineno(), 1)
            self.assertEqual(fi.filelineno(), 0)
            self.assertEqual(fi.filename(), t4)
            fi.close()
        w_końcu:
            remove_tempfiles(t1, t2, t3, t4)

    def test_files_that_dont_end_with_newline(self):
        t1 = t2 = Nic
        spróbuj:
            t1 = writeTmp(1, ["A\nB\nC"])
            t2 = writeTmp(2, ["D\nE\nF"])
            fi = FileInput(files=(t1, t2))
            lines = list(fi)
            self.assertEqual(lines, ["A\n", "B\n", "C", "D\n", "E\n", "F"])
            self.assertEqual(fi.filelineno(), 3)
            self.assertEqual(fi.lineno(), 6)
        w_końcu:
            remove_tempfiles(t1, t2)

##     def test_unicode_filenames(self):
##         # XXX A unicode string jest always returned by writeTmp.
##         #     So jest this needed?
##         spróbuj:
##             t1 = writeTmp(1, ["A\nB"])
##             encoding = sys.getfilesystemencoding()
##             jeżeli encoding jest Nic:
##                 encoding = 'ascii'
##             fi = FileInput(files=str(t1, encoding))
##             lines = list(fi)
##             self.assertEqual(lines, ["A\n", "B"])
##         w_końcu:
##             remove_tempfiles(t1)

    def test_fileno(self):
        t1 = t2 = Nic
        spróbuj:
            t1 = writeTmp(1, ["A\nB"])
            t2 = writeTmp(2, ["C\nD"])
            fi = FileInput(files=(t1, t2))
            self.assertEqual(fi.fileno(), -1)
            line =next( fi)
            self.assertNotEqual(fi.fileno(), -1)
            fi.nextfile()
            self.assertEqual(fi.fileno(), -1)
            line = list(fi)
            self.assertEqual(fi.fileno(), -1)
        w_końcu:
            remove_tempfiles(t1, t2)

    def test_opening_mode(self):
        spróbuj:
            # invalid mode, should podnieś ValueError
            fi = FileInput(mode="w")
            self.fail("FileInput should reject invalid mode argument")
        wyjąwszy ValueError:
            dalej
        t1 = Nic
        spróbuj:
            # try opening w universal newline mode
            t1 = writeTmp(1, [b"A\nB\r\nC\rD"], mode="wb")
            przy check_warnings(('', DeprecationWarning)):
                fi = FileInput(files=t1, mode="U")
            przy check_warnings(('', DeprecationWarning)):
                lines = list(fi)
            self.assertEqual(lines, ["A\n", "B\n", "C\n", "D"])
        w_końcu:
            remove_tempfiles(t1)

    def test_stdin_binary_mode(self):
        przy mock.patch('sys.stdin') jako m_stdin:
            m_stdin.buffer = BytesIO(b'spam, bacon, sausage, oraz spam')
            fi = FileInput(files=['-'], mode='rb')
            lines = list(fi)
            self.assertEqual(lines, [b'spam, bacon, sausage, oraz spam'])

    def test_file_opening_hook(self):
        spróbuj:
            # cannot use openhook oraz inplace mode
            fi = FileInput(inplace=1, openhook=lambda f, m: Nic)
            self.fail("FileInput should podnieś jeżeli both inplace "
                             "and openhook arguments are given")
        wyjąwszy ValueError:
            dalej
        spróbuj:
            fi = FileInput(openhook=1)
            self.fail("FileInput should check openhook dla being callable")
        wyjąwszy ValueError:
            dalej

        klasa CustomOpenHook:
            def __init__(self):
                self.invoked = Nieprawda
            def __call__(self, *args):
                self.invoked = Prawda
                zwróć open(*args)

        t = writeTmp(1, ["\n"])
        self.addCleanup(remove_tempfiles, t)
        custom_open_hook = CustomOpenHook()
        przy FileInput([t], openhook=custom_open_hook) jako fi:
            fi.readline()
        self.assertPrawda(custom_open_hook.invoked, "openhook nie invoked")

    def test_readline(self):
        przy open(TESTFN, 'wb') jako f:
            f.write(b'A\nB\r\nC\r')
            # Fill TextIOWrapper buffer.
            f.write(b'123456789\n' * 1000)
            # Issue #20501: readline() shouldn't read whole file.
            f.write(b'\x80')
        self.addCleanup(safe_unlink, TESTFN)

        przy FileInput(files=TESTFN,
                       openhook=hook_encoded('ascii'), bufsize=8) jako fi:
            spróbuj:
                self.assertEqual(fi.readline(), 'A\n')
                self.assertEqual(fi.readline(), 'B\n')
                self.assertEqual(fi.readline(), 'C\n')
            wyjąwszy UnicodeDecodeError:
                self.fail('Read to end of file')
            przy self.assertRaises(UnicodeDecodeError):
                # Read to the end of file.
                list(fi)

    def test_context_manager(self):
        spróbuj:
            t1 = writeTmp(1, ["A\nB\nC"])
            t2 = writeTmp(2, ["D\nE\nF"])
            przy FileInput(files=(t1, t2)) jako fi:
                lines = list(fi)
            self.assertEqual(lines, ["A\n", "B\n", "C", "D\n", "E\n", "F"])
            self.assertEqual(fi.filelineno(), 3)
            self.assertEqual(fi.lineno(), 6)
            self.assertEqual(fi._files, ())
        w_końcu:
            remove_tempfiles(t1, t2)

    def test_close_on_exception(self):
        spróbuj:
            t1 = writeTmp(1, [""])
            przy FileInput(files=t1) jako fi:
                podnieś OSError
        wyjąwszy OSError:
            self.assertEqual(fi._files, ())
        w_końcu:
            remove_tempfiles(t1)

    def test_empty_files_list_specified_to_constructor(self):
        przy FileInput(files=[]) jako fi:
            self.assertEqual(fi._files, ('-',))

    def test__getitem__(self):
        """Tests invoking FileInput.__getitem__() przy the current
           line number"""
        t = writeTmp(1, ["line1\n", "line2\n"])
        self.addCleanup(remove_tempfiles, t)
        przy FileInput(files=[t]) jako fi:
            retval1 = fi[0]
            self.assertEqual(retval1, "line1\n")
            retval2 = fi[1]
            self.assertEqual(retval2, "line2\n")

    def test__getitem__invalid_key(self):
        """Tests invoking FileInput.__getitem__() przy an index unequal to
           the line number"""
        t = writeTmp(1, ["line1\n", "line2\n"])
        self.addCleanup(remove_tempfiles, t)
        przy FileInput(files=[t]) jako fi:
            przy self.assertRaises(RuntimeError) jako cm:
                fi[1]
        self.assertEqual(cm.exception.args, ("accessing lines out of order",))

    def test__getitem__eof(self):
        """Tests invoking FileInput.__getitem__() przy the line number but at
           end-of-input"""
        t = writeTmp(1, [])
        self.addCleanup(remove_tempfiles, t)
        przy FileInput(files=[t]) jako fi:
            przy self.assertRaises(IndexError) jako cm:
                fi[0]
        self.assertEqual(cm.exception.args, ("end of input reached",))

    def test_nextfile_oserror_deleting_backup(self):
        """Tests invoking FileInput.nextfile() when the attempt to delete
           the backup file would podnieś OSError.  This error jest expected to be
           silently ignored"""

        os_unlink_orig = os.unlink
        os_unlink_replacement = UnconditionallyRaise(OSError)
        spróbuj:
            t = writeTmp(1, ["\n"])
            self.addCleanup(remove_tempfiles, t)
            przy FileInput(files=[t], inplace=Prawda) jako fi:
                next(fi) # make sure the file jest opened
                os.unlink = os_unlink_replacement
                fi.nextfile()
        w_końcu:
            os.unlink = os_unlink_orig

        # sanity check to make sure that our test scenario was actually hit
        self.assertPrawda(os_unlink_replacement.invoked,
                        "os.unlink() was nie invoked")

    def test_readline_os_fstat_raises_OSError(self):
        """Tests invoking FileInput.readline() when os.fstat() podnieśs OSError.
           This exception should be silently discarded."""

        os_fstat_orig = os.fstat
        os_fstat_replacement = UnconditionallyRaise(OSError)
        spróbuj:
            t = writeTmp(1, ["\n"])
            self.addCleanup(remove_tempfiles, t)
            przy FileInput(files=[t], inplace=Prawda) jako fi:
                os.fstat = os_fstat_replacement
                fi.readline()
        w_końcu:
            os.fstat = os_fstat_orig

        # sanity check to make sure that our test scenario was actually hit
        self.assertPrawda(os_fstat_replacement.invoked,
                        "os.fstat() was nie invoked")

    @unittest.skipIf(nie hasattr(os, "chmod"), "os.chmod does nie exist")
    def test_readline_os_chmod_raises_OSError(self):
        """Tests invoking FileInput.readline() when os.chmod() podnieśs OSError.
           This exception should be silently discarded."""

        os_chmod_orig = os.chmod
        os_chmod_replacement = UnconditionallyRaise(OSError)
        spróbuj:
            t = writeTmp(1, ["\n"])
            self.addCleanup(remove_tempfiles, t)
            przy FileInput(files=[t], inplace=Prawda) jako fi:
                os.chmod = os_chmod_replacement
                fi.readline()
        w_końcu:
            os.chmod = os_chmod_orig

        # sanity check to make sure that our test scenario was actually hit
        self.assertPrawda(os_chmod_replacement.invoked,
                        "os.fstat() was nie invoked")

    def test_fileno_when_ValueError_raised(self):
        klasa FilenoRaisesValueError(UnconditionallyRaise):
            def __init__(self):
                UnconditionallyRaise.__init__(self, ValueError)
            def fileno(self):
                self.__call__()

        unconditionally_raise_ValueError = FilenoRaisesValueError()
        t = writeTmp(1, ["\n"])
        self.addCleanup(remove_tempfiles, t)
        przy FileInput(files=[t]) jako fi:
            file_backup = fi._file
            spróbuj:
                fi._file = unconditionally_raise_ValueError
                result = fi.fileno()
            w_końcu:
                fi._file = file_backup # make sure the file gets cleaned up

        # sanity check to make sure that our test scenario was actually hit
        self.assertPrawda(unconditionally_raise_ValueError.invoked,
                        "_file.fileno() was nie invoked")

        self.assertEqual(result, -1, "fileno() should zwróć -1")

klasa MockFileInput:
    """A klasa that mocks out fileinput.FileInput dla use during unit tests"""

    def __init__(self, files=Nic, inplace=Nieprawda, backup="", bufsize=0,
                 mode="r", openhook=Nic):
        self.files = files
        self.inplace = inplace
        self.backup = backup
        self.bufsize = bufsize
        self.mode = mode
        self.openhook = openhook
        self._file = Nic
        self.invocation_counts = collections.defaultdict(lambda: 0)
        self.return_values = {}

    def close(self):
        self.invocation_counts["close"] += 1

    def nextfile(self):
        self.invocation_counts["nextfile"] += 1
        zwróć self.return_values["nextfile"]

    def filename(self):
        self.invocation_counts["filename"] += 1
        zwróć self.return_values["filename"]

    def lineno(self):
        self.invocation_counts["lineno"] += 1
        zwróć self.return_values["lineno"]

    def filelineno(self):
        self.invocation_counts["filelineno"] += 1
        zwróć self.return_values["filelineno"]

    def fileno(self):
        self.invocation_counts["fileno"] += 1
        zwróć self.return_values["fileno"]

    def isfirstline(self):
        self.invocation_counts["isfirstline"] += 1
        zwróć self.return_values["isfirstline"]

    def isstdin(self):
        self.invocation_counts["isstdin"] += 1
        zwróć self.return_values["isstdin"]

klasa BaseFileInputGlobalMethodsTest(unittest.TestCase):
    """Base klasa dla unit tests dla the global function of
       the fileinput module."""

    def setUp(self):
        self._orig_state = fileinput._state
        self._orig_FileInput = fileinput.FileInput
        fileinput.FileInput = MockFileInput

    def tearDown(self):
        fileinput.FileInput = self._orig_FileInput
        fileinput._state = self._orig_state

    def assertExactlyOneInvocation(self, mock_file_input, method_name):
        # assert that the method przy the given name was invoked once
        actual_count = mock_file_input.invocation_counts[method_name]
        self.assertEqual(actual_count, 1, method_name)
        # assert that no other unexpected methods were invoked
        actual_total_count = len(mock_file_input.invocation_counts)
        self.assertEqual(actual_total_count, 1)

klasa Test_fileinput_input(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.input()"""

    def test_state_is_not_Nic_and_state_file_is_not_Nic(self):
        """Tests invoking fileinput.input() when fileinput._state jest nie Nic
           oraz its _file attribute jest also nie Nic.  Expect RuntimeError to
           be podnieśd przy a meaningful error message oraz dla fileinput._state
           to *not* be modified."""
        instance = MockFileInput()
        instance._file = object()
        fileinput._state = instance
        przy self.assertRaises(RuntimeError) jako cm:
            fileinput.input()
        self.assertEqual(("input() already active",), cm.exception.args)
        self.assertIs(instance, fileinput._state, "fileinput._state")

    def test_state_is_not_Nic_and_state_file_is_Nic(self):
        """Tests invoking fileinput.input() when fileinput._state jest nie Nic
           but its _file attribute *is* Nic.  Expect it to create oraz zwróć
           a new fileinput.FileInput object przy all method parameters dalejed
           explicitly to the __init__() method; also ensure that
           fileinput._state jest set to the returned instance."""
        instance = MockFileInput()
        instance._file = Nic
        fileinput._state = instance
        self.do_test_call_input()

    def test_state_is_Nic(self):
        """Tests invoking fileinput.input() when fileinput._state jest Nic
           Expect it to create oraz zwróć a new fileinput.FileInput object
           przy all method parameters dalejed explicitly to the __init__()
           method; also ensure that fileinput._state jest set to the returned
           instance."""
        fileinput._state = Nic
        self.do_test_call_input()

    def do_test_call_input(self):
        """Tests that fileinput.input() creates a new fileinput.FileInput
           object, dalejing the given parameters unmodified to
           fileinput.FileInput.__init__().  Note that this test depends on the
           monkey patching of fileinput.FileInput done by setUp()."""
        files = object()
        inplace = object()
        backup = object()
        bufsize = object()
        mode = object()
        openhook = object()

        # call fileinput.input() przy different values dla each argument
        result = fileinput.input(files=files, inplace=inplace, backup=backup,
                                 bufsize=bufsize,
            mode=mode, openhook=openhook)

        # ensure fileinput._state was set to the returned object
        self.assertIs(result, fileinput._state, "fileinput._state")

        # ensure the parameters to fileinput.input() were dalejed directly
        # to FileInput.__init__()
        self.assertIs(files, result.files, "files")
        self.assertIs(inplace, result.inplace, "inplace")
        self.assertIs(backup, result.backup, "backup")
        self.assertIs(bufsize, result.bufsize, "bufsize")
        self.assertIs(mode, result.mode, "mode")
        self.assertIs(openhook, result.openhook, "openhook")

klasa Test_fileinput_close(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.close()"""

    def test_state_is_Nic(self):
        """Tests that fileinput.close() does nothing jeżeli fileinput._state
           jest Nic"""
        fileinput._state = Nic
        fileinput.close()
        self.assertIsNic(fileinput._state)

    def test_state_is_not_Nic(self):
        """Tests that fileinput.close() invokes close() on fileinput._state
           oraz sets _state=Nic"""
        instance = MockFileInput()
        fileinput._state = instance
        fileinput.close()
        self.assertExactlyOneInvocation(instance, "close")
        self.assertIsNic(fileinput._state)

klasa Test_fileinput_nextfile(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.nextfile()"""

    def test_state_is_Nic(self):
        """Tests fileinput.nextfile() when fileinput._state jest Nic.
           Ensure that it podnieśs RuntimeError przy a meaningful error message
           oraz does nie modify fileinput._state"""
        fileinput._state = Nic
        przy self.assertRaises(RuntimeError) jako cm:
            fileinput.nextfile()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsNic(fileinput._state)

    def test_state_is_not_Nic(self):
        """Tests fileinput.nextfile() when fileinput._state jest nie Nic.
           Ensure that it invokes fileinput._state.nextfile() exactly once,
           returns whatever it returns, oraz does nie modify fileinput._state
           to point to a different object."""
        nextfile_retval = object()
        instance = MockFileInput()
        instance.return_values["nextfile"] = nextfile_retval
        fileinput._state = instance
        retval = fileinput.nextfile()
        self.assertExactlyOneInvocation(instance, "nextfile")
        self.assertIs(retval, nextfile_retval)
        self.assertIs(fileinput._state, instance)

klasa Test_fileinput_filename(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.filename()"""

    def test_state_is_Nic(self):
        """Tests fileinput.filename() when fileinput._state jest Nic.
           Ensure that it podnieśs RuntimeError przy a meaningful error message
           oraz does nie modify fileinput._state"""
        fileinput._state = Nic
        przy self.assertRaises(RuntimeError) jako cm:
            fileinput.filename()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsNic(fileinput._state)

    def test_state_is_not_Nic(self):
        """Tests fileinput.filename() when fileinput._state jest nie Nic.
           Ensure that it invokes fileinput._state.filename() exactly once,
           returns whatever it returns, oraz does nie modify fileinput._state
           to point to a different object."""
        filename_retval = object()
        instance = MockFileInput()
        instance.return_values["filename"] = filename_retval
        fileinput._state = instance
        retval = fileinput.filename()
        self.assertExactlyOneInvocation(instance, "filename")
        self.assertIs(retval, filename_retval)
        self.assertIs(fileinput._state, instance)

klasa Test_fileinput_lineno(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.lineno()"""

    def test_state_is_Nic(self):
        """Tests fileinput.lineno() when fileinput._state jest Nic.
           Ensure that it podnieśs RuntimeError przy a meaningful error message
           oraz does nie modify fileinput._state"""
        fileinput._state = Nic
        przy self.assertRaises(RuntimeError) jako cm:
            fileinput.lineno()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsNic(fileinput._state)

    def test_state_is_not_Nic(self):
        """Tests fileinput.lineno() when fileinput._state jest nie Nic.
           Ensure that it invokes fileinput._state.lineno() exactly once,
           returns whatever it returns, oraz does nie modify fileinput._state
           to point to a different object."""
        lineno_retval = object()
        instance = MockFileInput()
        instance.return_values["lineno"] = lineno_retval
        fileinput._state = instance
        retval = fileinput.lineno()
        self.assertExactlyOneInvocation(instance, "lineno")
        self.assertIs(retval, lineno_retval)
        self.assertIs(fileinput._state, instance)

klasa Test_fileinput_filelineno(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.filelineno()"""

    def test_state_is_Nic(self):
        """Tests fileinput.filelineno() when fileinput._state jest Nic.
           Ensure that it podnieśs RuntimeError przy a meaningful error message
           oraz does nie modify fileinput._state"""
        fileinput._state = Nic
        przy self.assertRaises(RuntimeError) jako cm:
            fileinput.filelineno()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsNic(fileinput._state)

    def test_state_is_not_Nic(self):
        """Tests fileinput.filelineno() when fileinput._state jest nie Nic.
           Ensure that it invokes fileinput._state.filelineno() exactly once,
           returns whatever it returns, oraz does nie modify fileinput._state
           to point to a different object."""
        filelineno_retval = object()
        instance = MockFileInput()
        instance.return_values["filelineno"] = filelineno_retval
        fileinput._state = instance
        retval = fileinput.filelineno()
        self.assertExactlyOneInvocation(instance, "filelineno")
        self.assertIs(retval, filelineno_retval)
        self.assertIs(fileinput._state, instance)

klasa Test_fileinput_fileno(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.fileno()"""

    def test_state_is_Nic(self):
        """Tests fileinput.fileno() when fileinput._state jest Nic.
           Ensure that it podnieśs RuntimeError przy a meaningful error message
           oraz does nie modify fileinput._state"""
        fileinput._state = Nic
        przy self.assertRaises(RuntimeError) jako cm:
            fileinput.fileno()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsNic(fileinput._state)

    def test_state_is_not_Nic(self):
        """Tests fileinput.fileno() when fileinput._state jest nie Nic.
           Ensure that it invokes fileinput._state.fileno() exactly once,
           returns whatever it returns, oraz does nie modify fileinput._state
           to point to a different object."""
        fileno_retval = object()
        instance = MockFileInput()
        instance.return_values["fileno"] = fileno_retval
        instance.fileno_retval = fileno_retval
        fileinput._state = instance
        retval = fileinput.fileno()
        self.assertExactlyOneInvocation(instance, "fileno")
        self.assertIs(retval, fileno_retval)
        self.assertIs(fileinput._state, instance)

klasa Test_fileinput_isfirstline(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.isfirstline()"""

    def test_state_is_Nic(self):
        """Tests fileinput.isfirstline() when fileinput._state jest Nic.
           Ensure that it podnieśs RuntimeError przy a meaningful error message
           oraz does nie modify fileinput._state"""
        fileinput._state = Nic
        przy self.assertRaises(RuntimeError) jako cm:
            fileinput.isfirstline()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsNic(fileinput._state)

    def test_state_is_not_Nic(self):
        """Tests fileinput.isfirstline() when fileinput._state jest nie Nic.
           Ensure that it invokes fileinput._state.isfirstline() exactly once,
           returns whatever it returns, oraz does nie modify fileinput._state
           to point to a different object."""
        isfirstline_retval = object()
        instance = MockFileInput()
        instance.return_values["isfirstline"] = isfirstline_retval
        fileinput._state = instance
        retval = fileinput.isfirstline()
        self.assertExactlyOneInvocation(instance, "isfirstline")
        self.assertIs(retval, isfirstline_retval)
        self.assertIs(fileinput._state, instance)

klasa Test_fileinput_isstdin(BaseFileInputGlobalMethodsTest):
    """Unit tests dla fileinput.isstdin()"""

    def test_state_is_Nic(self):
        """Tests fileinput.isstdin() when fileinput._state jest Nic.
           Ensure that it podnieśs RuntimeError przy a meaningful error message
           oraz does nie modify fileinput._state"""
        fileinput._state = Nic
        przy self.assertRaises(RuntimeError) jako cm:
            fileinput.isstdin()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsNic(fileinput._state)

    def test_state_is_not_Nic(self):
        """Tests fileinput.isstdin() when fileinput._state jest nie Nic.
           Ensure that it invokes fileinput._state.isstdin() exactly once,
           returns whatever it returns, oraz does nie modify fileinput._state
           to point to a different object."""
        isstdin_retval = object()
        instance = MockFileInput()
        instance.return_values["isstdin"] = isstdin_retval
        fileinput._state = instance
        retval = fileinput.isstdin()
        self.assertExactlyOneInvocation(instance, "isstdin")
        self.assertIs(retval, isstdin_retval)
        self.assertIs(fileinput._state, instance)

klasa InvocationRecorder:
    def __init__(self):
        self.invocation_count = 0
    def __call__(self, *args, **kwargs):
        self.invocation_count += 1
        self.last_invocation = (args, kwargs)

klasa Test_hook_compressed(unittest.TestCase):
    """Unit tests dla fileinput.hook_compressed()"""

    def setUp(self):
        self.fake_open = InvocationRecorder()

    def test_empty_string(self):
        self.do_test_use_builtin_open("", 1)

    def test_no_ext(self):
        self.do_test_use_builtin_open("abcd", 2)

    @unittest.skipUnless(gzip, "Requires gzip oraz zlib")
    def test_gz_ext_fake(self):
        original_open = gzip.open
        gzip.open = self.fake_open
        spróbuj:
            result = fileinput.hook_compressed("test.gz", 3)
        w_końcu:
            gzip.open = original_open

        self.assertEqual(self.fake_open.invocation_count, 1)
        self.assertEqual(self.fake_open.last_invocation, (("test.gz", 3), {}))

    @unittest.skipUnless(bz2, "Requires bz2")
    def test_bz2_ext_fake(self):
        original_open = bz2.BZ2File
        bz2.BZ2File = self.fake_open
        spróbuj:
            result = fileinput.hook_compressed("test.bz2", 4)
        w_końcu:
            bz2.BZ2File = original_open

        self.assertEqual(self.fake_open.invocation_count, 1)
        self.assertEqual(self.fake_open.last_invocation, (("test.bz2", 4), {}))

    def test_blah_ext(self):
        self.do_test_use_builtin_open("abcd.blah", 5)

    def test_gz_ext_builtin(self):
        self.do_test_use_builtin_open("abcd.Gz", 6)

    def test_bz2_ext_builtin(self):
        self.do_test_use_builtin_open("abcd.Bz2", 7)

    def do_test_use_builtin_open(self, filename, mode):
        original_open = self.replace_builtin_open(self.fake_open)
        spróbuj:
            result = fileinput.hook_compressed(filename, mode)
        w_końcu:
            self.replace_builtin_open(original_open)

        self.assertEqual(self.fake_open.invocation_count, 1)
        self.assertEqual(self.fake_open.last_invocation,
                         ((filename, mode), {}))

    @staticmethod
    def replace_builtin_open(new_open_func):
        original_open = builtins.open
        builtins.open = new_open_func
        zwróć original_open

klasa Test_hook_encoded(unittest.TestCase):
    """Unit tests dla fileinput.hook_encoded()"""

    def test(self):
        encoding = object()
        result = fileinput.hook_encoded(encoding)

        fake_open = InvocationRecorder()
        original_open = builtins.open
        builtins.open = fake_open
        spróbuj:
            filename = object()
            mode = object()
            open_result = result(filename, mode)
        w_końcu:
            builtins.open = original_open

        self.assertEqual(fake_open.invocation_count, 1)

        args, kwargs = fake_open.last_invocation
        self.assertIs(args[0], filename)
        self.assertIs(args[1], mode)
        self.assertIs(kwargs.pop('encoding'), encoding)
        self.assertNieprawda(kwargs)

    def test_modes(self):
        przy open(TESTFN, 'wb') jako f:
            # UTF-7 jest a convenient, seldom used encoding
            f.write(b'A\nB\r\nC\rD+IKw-')
        self.addCleanup(safe_unlink, TESTFN)

        def check(mode, expected_lines):
            przy FileInput(files=TESTFN, mode=mode,
                           openhook=hook_encoded('utf-7')) jako fi:
                lines = list(fi)
            self.assertEqual(lines, expected_lines)

        check('r', ['A\n', 'B\n', 'C\n', 'D\u20ac'])
        przy self.assertWarns(DeprecationWarning):
            check('rU', ['A\n', 'B\n', 'C\n', 'D\u20ac'])
        przy self.assertWarns(DeprecationWarning):
            check('U', ['A\n', 'B\n', 'C\n', 'D\u20ac'])
        przy self.assertRaises(ValueError):
            check('rb', ['A\n', 'B\r\n', 'C\r', 'D\u20ac'])


jeżeli __name__ == "__main__":
    unittest.main()
