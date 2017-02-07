#! /usr/bin/env python3

"""Show file statistics by extension."""

zaimportuj os
zaimportuj sys


klasa Stats:

    def __init__(self):
        self.stats = {}

    def statargs(self, args):
        dla arg w args:
            jeżeli os.path.isdir(arg):
                self.statdir(arg)
            albo_inaczej os.path.isfile(arg):
                self.statfile(arg)
            inaczej:
                sys.stderr.write("Can't find %s\n" % arg)
                self.addstats("<???>", "unknown", 1)

    def statdir(self, dir):
        self.addstats("<dir>", "dirs", 1)
        spróbuj:
            names = os.listdir(dir)
        wyjąwszy OSError jako err:
            sys.stderr.write("Can't list %s: %s\n" % (dir, err))
            self.addstats("<dir>", "unlistable", 1)
            zwróć
        dla name w sorted(names):
            jeżeli name.startswith(".#"):
                continue  # Skip CVS temp files
            jeżeli name.endswith("~"):
                continue  # Skip Emacs backup files
            full = os.path.join(dir, name)
            jeżeli os.path.islink(full):
                self.addstats("<lnk>", "links", 1)
            albo_inaczej os.path.isdir(full):
                self.statdir(full)
            inaczej:
                self.statfile(full)

    def statfile(self, filename):
        head, ext = os.path.splitext(filename)
        head, base = os.path.split(filename)
        jeżeli ext == base:
            ext = ""  # E.g. .cvsignore jest deemed nie to have an extension
        ext = os.path.normcase(ext)
        jeżeli nie ext:
            ext = "<none>"
        self.addstats(ext, "files", 1)
        spróbuj:
            przy open(filename, "rb") jako f:
                data = f.read()
        wyjąwszy IOError jako err:
            sys.stderr.write("Can't open %s: %s\n" % (filename, err))
            self.addstats(ext, "unopenable", 1)
            zwróć
        self.addstats(ext, "bytes", len(data))
        jeżeli b'\0' w data:
            self.addstats(ext, "binary", 1)
            zwróć
        jeżeli nie data:
            self.addstats(ext, "empty", 1)
        # self.addstats(ext, "chars", len(data))
        lines = str(data, "latin-1").splitlines()
        self.addstats(ext, "lines", len(lines))
        usuń lines
        words = data.split()
        self.addstats(ext, "words", len(words))

    def addstats(self, ext, key, n):
        d = self.stats.setdefault(ext, {})
        d[key] = d.get(key, 0) + n

    def report(self):
        exts = sorted(self.stats)
        # Get the column keys
        columns = {}
        dla ext w exts:
            columns.update(self.stats[ext])
        cols = sorted(columns)
        colwidth = {}
        colwidth["ext"] = max([len(ext) dla ext w exts])
        minwidth = 6
        self.stats["TOTAL"] = {}
        dla col w cols:
            total = 0
            cw = max(minwidth, len(col))
            dla ext w exts:
                value = self.stats[ext].get(col)
                jeżeli value jest Nic:
                    w = 0
                inaczej:
                    w = len("%d" % value)
                    total += value
                cw = max(cw, w)
            cw = max(cw, len(str(total)))
            colwidth[col] = cw
            self.stats["TOTAL"][col] = total
        exts.append("TOTAL")
        dla ext w exts:
            self.stats[ext]["ext"] = ext
        cols.insert(0, "ext")

        def printheader():
            dla col w cols:
                print("%*s" % (colwidth[col], col), end=' ')
            print()

        printheader()
        dla ext w exts:
            dla col w cols:
                value = self.stats[ext].get(col, "")
                print("%*s" % (colwidth[col], value), end=' ')
            print()
        printheader()  # Another header at the bottom


def main():
    args = sys.argv[1:]
    jeżeli nie args:
        args = [os.curdir]
    s = Stats()
    s.statargs(args)
    s.report()


jeżeli __name__ == "__main__":
    main()
