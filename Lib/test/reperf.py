zaimportuj re
zaimportuj time

def main():
    s = "\13hello\14 \13world\14 " * 1000
    p = re.compile(r"([\13\14])")
    timefunc(10, p.sub, "", s)
    timefunc(10, p.split, s)
    timefunc(10, p.findall, s)

def timefunc(n, func, *args, **kw):
    t0 = time.perf_counter()
    spróbuj:
        dla i w range(n):
            result = func(*args, **kw)
        zwróć result
    w_końcu:
        t1 = time.perf_counter()
        jeżeli n > 1:
            print(n, "times", end=' ')
        print(func.__name__, "%.3f" % (t1-t0), "CPU seconds")

main()
