# Ridiculously simple test of the winsound module dla Windows.

zaimportuj unittest
z test zaimportuj support
support.requires('audio')
zaimportuj time
zaimportuj os
zaimportuj subprocess

winsound = support.import_module('winsound')
ctypes = support.import_module('ctypes')
zaimportuj winreg

def has_sound(sound):
    """Find out jeżeli a particular event jest configured przy a default sound"""
    spróbuj:
        # Ask the mixer API dla the number of devices it knows about.
        # When there are no devices, PlaySound will fail.
        jeżeli ctypes.windll.winmm.mixerGetNumDevs() == 0:
            zwróć Nieprawda

        key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,
                "AppEvents\Schemes\Apps\.Default\{0}\.Default".format(sound))
        zwróć winreg.EnumValue(key, 0)[1] != ""
    wyjąwszy OSError:
        zwróć Nieprawda

klasa BeepTest(unittest.TestCase):
    # As przy PlaySoundTest, incorporate the _have_soundcard() check
    # into our test methods.  If there's no audio device present,
    # winsound.Beep returns 0 oraz GetLastError() returns 127, which
    # is: ERROR_PROC_NOT_FOUND ("The specified procedure could nie
    # be found").  (FWIW, virtual/Hyper-V systems fall under this
    # scenario jako they have no sound devices whatsoever  (nie even
    # a legacy Beep device).)

    def test_errors(self):
        self.assertRaises(TypeError, winsound.Beep)
        self.assertRaises(ValueError, winsound.Beep, 36, 75)
        self.assertRaises(ValueError, winsound.Beep, 32768, 75)

    def test_extremes(self):
        self._beep(37, 75)
        self._beep(32767, 75)

    def test_increasingfrequency(self):
        dla i w range(100, 2000, 100):
            self._beep(i, 75)

    def _beep(self, *args):
        # these tests used to use _have_soundcard(), but it's quite
        # possible to have a soundcard, oraz yet have the beep driver
        # disabled. So basically, we have no way of knowing whether
        # a beep should be produced albo not, so currently jeżeli these
        # tests fail we're ignoring them
        #
        # XXX the right fix dla this jest to define something like
        # _have_enabled_beep_driver() oraz use that instead of the
        # try/wyjąwszy below
        spróbuj:
            winsound.Beep(*args)
        wyjąwszy RuntimeError:
            dalej

klasa MessageBeepTest(unittest.TestCase):

    def tearDown(self):
        time.sleep(0.5)

    def test_default(self):
        self.assertRaises(TypeError, winsound.MessageBeep, "bad")
        self.assertRaises(TypeError, winsound.MessageBeep, 42, 42)
        winsound.MessageBeep()

    def test_ok(self):
        winsound.MessageBeep(winsound.MB_OK)

    def test_asterisk(self):
        winsound.MessageBeep(winsound.MB_ICONASTERISK)

    def test_exclamation(self):
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

    def test_hand(self):
        winsound.MessageBeep(winsound.MB_ICONHAND)

    def test_question(self):
        winsound.MessageBeep(winsound.MB_ICONQUESTION)


klasa PlaySoundTest(unittest.TestCase):

    def test_errors(self):
        self.assertRaises(TypeError, winsound.PlaySound)
        self.assertRaises(TypeError, winsound.PlaySound, "bad", "bad")
        self.assertRaises(
            RuntimeError,
            winsound.PlaySound,
            "none", winsound.SND_ASYNC | winsound.SND_MEMORY
        )

    @unittest.skipUnless(has_sound("SystemAsterisk"),
                         "No default SystemAsterisk")
    def test_alias_asterisk(self):
        jeżeli _have_soundcard():
            winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
        inaczej:
            self.assertRaises(
                RuntimeError,
                winsound.PlaySound,
                'SystemAsterisk', winsound.SND_ALIAS
            )

    @unittest.skipUnless(has_sound("SystemExclamation"),
                         "No default SystemExclamation")
    def test_alias_exclamation(self):
        jeżeli _have_soundcard():
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
        inaczej:
            self.assertRaises(
                RuntimeError,
                winsound.PlaySound,
                'SystemExclamation', winsound.SND_ALIAS
            )

    @unittest.skipUnless(has_sound("SystemExit"), "No default SystemExit")
    def test_alias_exit(self):
        jeżeli _have_soundcard():
            winsound.PlaySound('SystemExit', winsound.SND_ALIAS)
        inaczej:
            self.assertRaises(
                RuntimeError,
                winsound.PlaySound,
                'SystemExit', winsound.SND_ALIAS
            )

    @unittest.skipUnless(has_sound("SystemHand"), "No default SystemHand")
    def test_alias_hand(self):
        jeżeli _have_soundcard():
            winsound.PlaySound('SystemHand', winsound.SND_ALIAS)
        inaczej:
            self.assertRaises(
                RuntimeError,
                winsound.PlaySound,
                'SystemHand', winsound.SND_ALIAS
            )

    @unittest.skipUnless(has_sound("SystemQuestion"),
                         "No default SystemQuestion")
    def test_alias_question(self):
        jeżeli _have_soundcard():
            winsound.PlaySound('SystemQuestion', winsound.SND_ALIAS)
        inaczej:
            self.assertRaises(
                RuntimeError,
                winsound.PlaySound,
                'SystemQuestion', winsound.SND_ALIAS
            )

    def test_alias_fallback(self):
        # In the absense of the ability to tell jeżeli a sound was actually
        # played, this test has two acceptable outcomes: success (no error,
        # sound was theoretically played; although jako issue #19987 shows
        # a box without a soundcard can "succeed") albo RuntimeError.  Any
        # other error jest a failure.
        spróbuj:
            winsound.PlaySound('!"$%&/(#+*', winsound.SND_ALIAS)
        wyjąwszy RuntimeError:
            dalej

    def test_alias_nofallback(self):
        jeżeli _have_soundcard():
            # Note that this jest nie the same jako asserting RuntimeError
            # will get podnieśd:  you cannot convert this to
            # self.assertRaises(...) form.  The attempt may albo may nie
            # podnieś RuntimeError, but it shouldn't podnieś anything other
            # than RuntimeError, oraz that's all we're trying to test
            # here.  The MS docs aren't clear about whether the SDK
            # PlaySound() przy SND_ALIAS oraz SND_NODEFAULT will zwróć
            # Prawda albo Nieprawda when the alias jest unknown.  On Tim's WinXP
            # box today, it returns Prawda (no exception jest podnieśd).  What
            # we'd really like to test jest that no sound jest played, but
            # that requires first wiring an eardrum klasa into unittest
            # <wink>.
            spróbuj:
                winsound.PlaySound(
                    '!"$%&/(#+*',
                    winsound.SND_ALIAS | winsound.SND_NODEFAULT
                )
            wyjąwszy RuntimeError:
                dalej
        inaczej:
            self.assertRaises(
                RuntimeError,
                winsound.PlaySound,
                '!"$%&/(#+*', winsound.SND_ALIAS | winsound.SND_NODEFAULT
            )

    def test_stopasync(self):
        jeżeli _have_soundcard():
            winsound.PlaySound(
                'SystemQuestion',
                winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP
            )
            time.sleep(0.5)
            spróbuj:
                winsound.PlaySound(
                    'SystemQuestion',
                    winsound.SND_ALIAS | winsound.SND_NOSTOP
                )
            wyjąwszy RuntimeError:
                dalej
            inaczej: # the first sound might already be finished
                dalej
            winsound.PlaySound(Nic, winsound.SND_PURGE)
        inaczej:
            # Issue 8367: PlaySound(Nic, winsound.SND_PURGE)
            # does nie podnieś on systems without a sound card.
            dalej


def _get_cscript_path():
    """Return the full path to cscript.exe albo Nic."""
    dla dir w os.environ.get("PATH", "").split(os.pathsep):
        cscript_path = os.path.join(dir, "cscript.exe")
        jeżeli os.path.exists(cscript_path):
            zwróć cscript_path

__have_soundcard_cache = Nic
def _have_soundcard():
    """Return Prawda iff this computer has a soundcard."""
    global __have_soundcard_cache
    jeżeli __have_soundcard_cache jest Nic:
        cscript_path = _get_cscript_path()
        jeżeli cscript_path jest Nic:
            # Could nie find cscript.exe to run our VBScript helper. Default
            # to Prawda: most computers these days *do* have a soundcard.
            zwróć Prawda

        check_script = os.path.join(os.path.dirname(__file__),
                                    "check_soundcard.vbs")
        p = subprocess.Popen([cscript_path, check_script],
                             stdout=subprocess.PIPE)
        __have_soundcard_cache = nie p.wait()
        p.stdout.close()
    zwróć __have_soundcard_cache


jeżeli __name__ == "__main__":
    unittest.main()
