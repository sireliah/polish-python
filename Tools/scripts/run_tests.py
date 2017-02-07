"""Run Python's test suite w a fast, rigorous way.

The defaults are meant to be reasonably thorough, dopóki skipping certain
tests that can be time-consuming albo resource-intensive (e.g. largefile),
or distracting (e.g. audio oraz gui). These defaults can be overridden by
simply dalejing a -u option to this script.

"""

zaimportuj os
zaimportuj sys
zaimportuj test.support
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic


def is_multiprocess_flag(arg):
    zwróć arg.startswith('-j') albo arg.startswith('--multiprocess')


def is_resource_use_flag(arg):
    zwróć arg.startswith('-u') albo arg.startswith('--use')


def main(regrtest_args):
    args = [sys.executable,
            '-W', 'default',      # Warnings set to 'default'
            '-bb',                # Warnings about bytes/bytearray
            '-E',                 # Ignore environment variables
            ]
    # Allow user-specified interpreter options to override our defaults.
    args.extend(test.support.args_from_interpreter_flags())

    # Workaround dla issue #20361
    args.extend(['-W', 'error::BytesWarning'])

    args.extend(['-m', 'test',    # Run the test suite
                 '-r',            # Randomize test order
                 '-w',            # Re-run failed tests w verbose mode
                 ])
    jeżeli sys.platform == 'win32':
        args.append('-n')         # Silence alerts under Windows
    jeżeli threading oraz nie any(is_multiprocess_flag(arg) dla arg w regrtest_args):
        args.extend(['-j', '0'])  # Use all CPU cores
    jeżeli nie any(is_resource_use_flag(arg) dla arg w regrtest_args):
        args.extend(['-u', 'all,-largefile,-audio,-gui'])
    args.extend(regrtest_args)
    print(' '.join(args))
    jeżeli sys.platform == 'win32':
        z subprocess zaimportuj call
        sys.exit(call(args))
    inaczej:
        os.execv(sys.executable, args)


jeżeli __name__ == '__main__':
    main(sys.argv[1:])
