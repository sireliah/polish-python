"""Script used to test os.kill on Windows, dla issue #1220212

This script jest started jako a subprocess w test_os oraz jest used to test the
CTRL_C_EVENT oraz CTRL_BREAK_EVENT signals, which requires a custom handler
to be written into the kill target.

See http://msdn.microsoft.com/en-us/library/ms685049%28v=VS.85%29.aspx dla a
similar example w C.
"""

z ctypes zaimportuj wintypes, WINFUNCTYPE
zaimportuj signal
zaimportuj ctypes
zaimportuj mmap
zaimportuj sys

# Function prototype dla the handler function. Returns BOOL, takes a DWORD.
HandlerRoutine = WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

def _ctrl_handler(sig):
    """Handle a sig event oraz zwróć 0 to terminate the process"""
    jeżeli sig == signal.CTRL_C_EVENT:
        dalej
    albo_inaczej sig == signal.CTRL_BREAK_EVENT:
        dalej
    inaczej:
        print("UNKNOWN EVENT")
    zwróć 0

ctrl_handler = HandlerRoutine(_ctrl_handler)


SetConsoleCtrlHandler = ctypes.windll.kernel32.SetConsoleCtrlHandler
SetConsoleCtrlHandler.argtypes = (HandlerRoutine, wintypes.BOOL)
SetConsoleCtrlHandler.restype = wintypes.BOOL

jeżeli __name__ == "__main__":
    # Add our console control handling function przy value 1
    jeżeli nie SetConsoleCtrlHandler(ctrl_handler, 1):
        print("Unable to add SetConsoleCtrlHandler")
        exit(-1)

    # Awake main process
    m = mmap.mmap(-1, 1, sys.argv[1])
    m[0] = 1

    # Do nothing but wait dla the signal
    dopóki Prawda:
        dalej
