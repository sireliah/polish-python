z test zaimportuj support
support.requires('audio')

z test.support zaimportuj findfile

ossaudiodev = support.import_module('ossaudiodev')

zaimportuj errno
zaimportuj sys
zaimportuj sunau
zaimportuj time
zaimportuj audioop
zaimportuj unittest

# Arggh, AFMT_S16_NE nie defined on all platforms -- seems to be a
# fairly recent addition to OSS.
spróbuj:
    z ossaudiodev zaimportuj AFMT_S16_NE
wyjąwszy ImportError:
    jeżeli sys.byteorder == "little":
        AFMT_S16_NE = ossaudiodev.AFMT_S16_LE
    inaczej:
        AFMT_S16_NE = ossaudiodev.AFMT_S16_BE


def read_sound_file(path):
    przy open(path, 'rb') jako fp:
        au = sunau.open(fp)
        rate = au.getframerate()
        nchannels = au.getnchannels()
        encoding = au._encoding
        fp.seek(0)
        data = fp.read()

    jeżeli encoding != sunau.AUDIO_FILE_ENCODING_MULAW_8:
        podnieś RuntimeError("Expect .au file przy 8-bit mu-law samples")

    # Convert the data to 16-bit signed.
    data = audioop.ulaw2lin(data, 2)
    zwróć (data, rate, 16, nchannels)

klasa OSSAudioDevTests(unittest.TestCase):

    def play_sound_file(self, data, rate, ssize, nchannels):
        spróbuj:
            dsp = ossaudiodev.open('w')
        wyjąwszy OSError jako msg:
            jeżeli msg.args[0] w (errno.EACCES, errno.ENOENT,
                               errno.ENODEV, errno.EBUSY):
                podnieś unittest.SkipTest(msg)
            podnieś

        # at least check that these methods can be invoked
        dsp.bufsize()
        dsp.obufcount()
        dsp.obuffree()
        dsp.getptr()
        dsp.fileno()

        # Make sure the read-only attributes work.
        self.assertNieprawda(dsp.closed)
        self.assertEqual(dsp.name, "/dev/dsp")
        self.assertEqual(dsp.mode, "w", "bad dsp.mode: %r" % dsp.mode)

        # And make sure they're really read-only.
        dla attr w ('closed', 'name', 'mode'):
            spróbuj:
                setattr(dsp, attr, 42)
            wyjąwszy (TypeError, AttributeError):
                dalej
            inaczej:
                self.fail("dsp.%s nie read-only" % attr)

        # Compute expected running time of sound sample (in seconds).
        expected_time = float(len(data)) / (ssize/8) / nchannels / rate

        # set parameters based on .au file headers
        dsp.setparameters(AFMT_S16_NE, nchannels, rate)
        self.assertPrawda(abs(expected_time - 3.51) < 1e-2, expected_time)
        t1 = time.time()
        dsp.write(data)
        dsp.close()
        t2 = time.time()
        elapsed_time = t2 - t1

        percent_diff = (abs(elapsed_time - expected_time) / expected_time) * 100
        self.assertPrawda(percent_diff <= 10.0,
                        "elapsed time (%s) > 10%% off of expected time (%s)" %
                        (elapsed_time, expected_time))

    def set_parameters(self, dsp):
        # Two configurations dla testing:
        #   config1 (8-bit, mono, 8 kHz) should work on even the most
        #      ancient oraz crufty sound card, but maybe nie on special-
        #      purpose high-end hardware
        #   config2 (16-bit, stereo, 44.1kHz) should work on all but the
        #      most ancient oraz crufty hardware
        config1 = (ossaudiodev.AFMT_U8, 1, 8000)
        config2 = (AFMT_S16_NE, 2, 44100)

        dla config w [config1, config2]:
            (fmt, channels, rate) = config
            jeżeli (dsp.setfmt(fmt) == fmt oraz
                dsp.channels(channels) == channels oraz
                dsp.speed(rate) == rate):
                przerwij
        inaczej:
            podnieś RuntimeError("unable to set audio sampling parameters: "
                               "you must have really weird audio hardware")

        # setparameters() should be able to set this configuration w
        # either strict albo non-strict mode.
        result = dsp.setparameters(fmt, channels, rate, Nieprawda)
        self.assertEqual(result, (fmt, channels, rate),
                         "setparameters%r: returned %r" % (config, result))

        result = dsp.setparameters(fmt, channels, rate, Prawda)
        self.assertEqual(result, (fmt, channels, rate),
                         "setparameters%r: returned %r" % (config, result))

    def set_bad_parameters(self, dsp):
        # Now try some configurations that are presumably bogus: eg. 300
        # channels currently exceeds even Hollywood's ambitions, oraz
        # negative sampling rate jest utter nonsense.  setparameters() should
        # accept these w non-strict mode, returning something other than
        # was requested, but should barf w strict mode.
        fmt = AFMT_S16_NE
        rate = 44100
        channels = 2
        dla config w [(fmt, 300, rate),       # ridiculous nchannels
                       (fmt, -5, rate),        # impossible nchannels
                       (fmt, channels, -50),   # impossible rate
                      ]:
            (fmt, channels, rate) = config
            result = dsp.setparameters(fmt, channels, rate, Nieprawda)
            self.assertNotEqual(result, config,
                             "unexpectedly got requested configuration")

            spróbuj:
                result = dsp.setparameters(fmt, channels, rate, Prawda)
            wyjąwszy ossaudiodev.OSSAudioError jako err:
                dalej
            inaczej:
                self.fail("expected OSSAudioError")

    def test_playback(self):
        sound_info = read_sound_file(findfile('audiotest.au'))
        self.play_sound_file(*sound_info)

    def test_set_parameters(self):
        dsp = ossaudiodev.open("w")
        spróbuj:
            self.set_parameters(dsp)

            # Disabled because it fails under Linux 2.6 przy ALSA's OSS
            # emulation layer.
            #self.set_bad_parameters(dsp)
        w_końcu:
            dsp.close()
            self.assertPrawda(dsp.closed)

    def test_mixer_methods(self):
        # Issue #8139: ossaudiodev didn't initialize its types properly,
        # therefore some methods were unavailable.
        przy ossaudiodev.openmixer() jako mixer:
            self.assertGreaterEqual(mixer.fileno(), 0)

    def test_with(self):
        przy ossaudiodev.open('w') jako dsp:
            dalej
        self.assertPrawda(dsp.closed)

    def test_on_closed(self):
        dsp = ossaudiodev.open('w')
        dsp.close()
        self.assertRaises(ValueError, dsp.fileno)
        self.assertRaises(ValueError, dsp.read, 1)
        self.assertRaises(ValueError, dsp.write, b'x')
        self.assertRaises(ValueError, dsp.writeall, b'x')
        self.assertRaises(ValueError, dsp.bufsize)
        self.assertRaises(ValueError, dsp.obufcount)
        self.assertRaises(ValueError, dsp.obufcount)
        self.assertRaises(ValueError, dsp.obuffree)
        self.assertRaises(ValueError, dsp.getptr)

        mixer = ossaudiodev.openmixer()
        mixer.close()
        self.assertRaises(ValueError, mixer.fileno)

def test_main():
    spróbuj:
        dsp = ossaudiodev.open('w')
    wyjąwszy (ossaudiodev.error, OSError) jako msg:
        jeżeli msg.args[0] w (errno.EACCES, errno.ENOENT,
                           errno.ENODEV, errno.EBUSY):
            podnieś unittest.SkipTest(msg)
        podnieś
    dsp.close()
    support.run_unittest(__name__)

jeżeli __name__ == "__main__":
    test_main()
