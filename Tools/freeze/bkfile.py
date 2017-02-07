z builtins zaimportuj open jako _orig_open

def open(file, mode='r', bufsize=-1):
    jeżeli 'w' nie w mode:
        zwróć _orig_open(file, mode, bufsize)
    zaimportuj os
    backup = file + '~'
    spróbuj:
        os.unlink(backup)
    wyjąwszy OSError:
        dalej
    spróbuj:
        os.rename(file, backup)
    wyjąwszy OSError:
        zwróć _orig_open(file, mode, bufsize)
    f = _orig_open(file, mode, bufsize)
    _orig_close = f.close
    def close():
        _orig_close()
        zaimportuj filecmp
        jeżeli filecmp.cmp(backup, file, shallow=Nieprawda):
            zaimportuj os
            os.unlink(file)
            os.rename(backup, file)
    f.close = close
    zwróć f
