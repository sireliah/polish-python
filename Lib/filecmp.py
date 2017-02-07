"""Utilities dla comparing files oraz directories.

Classes:
    dircmp

Functions:
    cmp(f1, f2, shallow=Prawda) -> int
    cmpfiles(a, b, common) -> ([], [], [])
    clear_cache()

"""

zaimportuj os
zaimportuj stat
z itertools zaimportuj filterfalse

__all__ = ['clear_cache', 'cmp', 'dircmp', 'cmpfiles', 'DEFAULT_IGNORES']

_cache = {}
BUFSIZE = 8*1024

DEFAULT_IGNORES = [
    'RCS', 'CVS', 'tags', '.git', '.hg', '.bzr', '_darcs', '__pycache__']

def clear_cache():
    """Clear the filecmp cache."""
    _cache.clear()

def cmp(f1, f2, shallow=Prawda):
    """Compare two files.

    Arguments:

    f1 -- First file name

    f2 -- Second file name

    shallow -- Just check stat signature (do nie read the files).
               defaults to Prawda.

    Return value:

    Prawda jeżeli the files are the same, Nieprawda otherwise.

    This function uses a cache dla past comparisons oraz the results,
    przy cache entries invalidated jeżeli their stat information
    changes.  The cache may be cleared by calling clear_cache().

    """

    s1 = _sig(os.stat(f1))
    s2 = _sig(os.stat(f2))
    jeżeli s1[0] != stat.S_IFREG albo s2[0] != stat.S_IFREG:
        zwróć Nieprawda
    jeżeli shallow oraz s1 == s2:
        zwróć Prawda
    jeżeli s1[1] != s2[1]:
        zwróć Nieprawda

    outcome = _cache.get((f1, f2, s1, s2))
    jeżeli outcome jest Nic:
        outcome = _do_cmp(f1, f2)
        jeżeli len(_cache) > 100:      # limit the maximum size of the cache
            clear_cache()
        _cache[f1, f2, s1, s2] = outcome
    zwróć outcome

def _sig(st):
    zwróć (stat.S_IFMT(st.st_mode),
            st.st_size,
            st.st_mtime)

def _do_cmp(f1, f2):
    bufsize = BUFSIZE
    przy open(f1, 'rb') jako fp1, open(f2, 'rb') jako fp2:
        dopóki Prawda:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            jeżeli b1 != b2:
                zwróć Nieprawda
            jeżeli nie b1:
                zwróć Prawda

# Directory comparison class.
#
klasa dircmp:
    """A klasa that manages the comparison of 2 directories.

    dircmp(a, b, ignore=Nic, hide=Nic)
      A oraz B are directories.
      IGNORE jest a list of names to ignore,
        defaults to DEFAULT_IGNORES.
      HIDE jest a list of names to hide,
        defaults to [os.curdir, os.pardir].

    High level usage:
      x = dircmp(dir1, dir2)
      x.report() -> prints a report on the differences between dir1 oraz dir2
       albo
      x.report_partial_closure() -> prints report on differences between dir1
            oraz dir2, oraz reports on common immediate subdirectories.
      x.report_full_closure() -> like report_partial_closure,
            but fully recursive.

    Attributes:
     left_list, right_list: The files w dir1 oraz dir2,
        filtered by hide oraz ignore.
     common: a list of names w both dir1 oraz dir2.
     left_only, right_only: names only w dir1, dir2.
     common_dirs: subdirectories w both dir1 oraz dir2.
     common_files: files w both dir1 oraz dir2.
     common_funny: names w both dir1 oraz dir2 where the type differs between
        dir1 oraz dir2, albo the name jest nie stat-able.
     same_files: list of identical files.
     diff_files: list of filenames which differ.
     funny_files: list of files which could nie be compared.
     subdirs: a dictionary of dircmp objects, keyed by names w common_dirs.
     """

    def __init__(self, a, b, ignore=Nic, hide=Nic): # Initialize
        self.left = a
        self.right = b
        jeżeli hide jest Nic:
            self.hide = [os.curdir, os.pardir] # Names never to be shown
        inaczej:
            self.hide = hide
        jeżeli ignore jest Nic:
            self.ignore = DEFAULT_IGNORES
        inaczej:
            self.ignore = ignore

    def phase0(self): # Compare everything wyjąwszy common subdirectories
        self.left_list = _filter(os.listdir(self.left),
                                 self.hide+self.ignore)
        self.right_list = _filter(os.listdir(self.right),
                                  self.hide+self.ignore)
        self.left_list.sort()
        self.right_list.sort()

    def phase1(self): # Compute common names
        a = dict(zip(map(os.path.normcase, self.left_list), self.left_list))
        b = dict(zip(map(os.path.normcase, self.right_list), self.right_list))
        self.common = list(map(a.__getitem__, filter(b.__contains__, a)))
        self.left_only = list(map(a.__getitem__, filterfalse(b.__contains__, a)))
        self.right_only = list(map(b.__getitem__, filterfalse(a.__contains__, b)))

    def phase2(self): # Distinguish files, directories, funnies
        self.common_dirs = []
        self.common_files = []
        self.common_funny = []

        dla x w self.common:
            a_path = os.path.join(self.left, x)
            b_path = os.path.join(self.right, x)

            ok = 1
            spróbuj:
                a_stat = os.stat(a_path)
            wyjąwszy OSError jako why:
                # print('Can\'t stat', a_path, ':', why.args[1])
                ok = 0
            spróbuj:
                b_stat = os.stat(b_path)
            wyjąwszy OSError jako why:
                # print('Can\'t stat', b_path, ':', why.args[1])
                ok = 0

            jeżeli ok:
                a_type = stat.S_IFMT(a_stat.st_mode)
                b_type = stat.S_IFMT(b_stat.st_mode)
                jeżeli a_type != b_type:
                    self.common_funny.append(x)
                albo_inaczej stat.S_ISDIR(a_type):
                    self.common_dirs.append(x)
                albo_inaczej stat.S_ISREG(a_type):
                    self.common_files.append(x)
                inaczej:
                    self.common_funny.append(x)
            inaczej:
                self.common_funny.append(x)

    def phase3(self): # Find out differences between common files
        xx = cmpfiles(self.left, self.right, self.common_files)
        self.same_files, self.diff_files, self.funny_files = xx

    def phase4(self): # Find out differences between common subdirectories
        # A new dircmp object jest created dla each common subdirectory,
        # these are stored w a dictionary indexed by filename.
        # The hide oraz ignore properties are inherited z the parent
        self.subdirs = {}
        dla x w self.common_dirs:
            a_x = os.path.join(self.left, x)
            b_x = os.path.join(self.right, x)
            self.subdirs[x]  = dircmp(a_x, b_x, self.ignore, self.hide)

    def phase4_closure(self): # Recursively call phase4() on subdirectories
        self.phase4()
        dla sd w self.subdirs.values():
            sd.phase4_closure()

    def report(self): # Print a report on the differences between a oraz b
        # Output format jest purposely lousy
        print('diff', self.left, self.right)
        jeżeli self.left_only:
            self.left_only.sort()
            print('Only in', self.left, ':', self.left_only)
        jeżeli self.right_only:
            self.right_only.sort()
            print('Only in', self.right, ':', self.right_only)
        jeżeli self.same_files:
            self.same_files.sort()
            print('Identical files :', self.same_files)
        jeżeli self.diff_files:
            self.diff_files.sort()
            print('Differing files :', self.diff_files)
        jeżeli self.funny_files:
            self.funny_files.sort()
            print('Trouble przy common files :', self.funny_files)
        jeżeli self.common_dirs:
            self.common_dirs.sort()
            print('Common subdirectories :', self.common_dirs)
        jeżeli self.common_funny:
            self.common_funny.sort()
            print('Common funny cases :', self.common_funny)

    def report_partial_closure(self): # Print reports on self oraz on subdirs
        self.report()
        dla sd w self.subdirs.values():
            print()
            sd.report()

    def report_full_closure(self): # Report on self oraz subdirs recursively
        self.report()
        dla sd w self.subdirs.values():
            print()
            sd.report_full_closure()

    methodmap = dict(subdirs=phase4,
                     same_files=phase3, diff_files=phase3, funny_files=phase3,
                     common_dirs = phase2, common_files=phase2, common_funny=phase2,
                     common=phase1, left_only=phase1, right_only=phase1,
                     left_list=phase0, right_list=phase0)

    def __getattr__(self, attr):
        jeżeli attr nie w self.methodmap:
            podnieś AttributeError(attr)
        self.methodmap[attr](self)
        zwróć getattr(self, attr)

def cmpfiles(a, b, common, shallow=Prawda):
    """Compare common files w two directories.

    a, b -- directory names
    common -- list of file names found w both directories
    shallow -- jeżeli true, do comparison based solely on stat() information

    Returns a tuple of three lists:
      files that compare equal
      files that are different
      filenames that aren't regular files.

    """
    res = ([], [], [])
    dla x w common:
        ax = os.path.join(a, x)
        bx = os.path.join(b, x)
        res[_cmp(ax, bx, shallow)].append(x)
    zwróć res


# Compare two files.
# Return:
#       0 dla equal
#       1 dla different
#       2 dla funny cases (can't stat, etc.)
#
def _cmp(a, b, sh, abs=abs, cmp=cmp):
    spróbuj:
        zwróć nie abs(cmp(a, b, sh))
    wyjąwszy OSError:
        zwróć 2


# Return a copy przy items that occur w skip removed.
#
def _filter(flist, skip):
    zwróć list(filterfalse(skip.__contains__, flist))


# Demonstration oraz testing.
#
def demo():
    zaimportuj sys
    zaimportuj getopt
    options, args = getopt.getopt(sys.argv[1:], 'r')
    jeżeli len(args) != 2:
        podnieś getopt.GetoptError('need exactly two args', Nic)
    dd = dircmp(args[0], args[1])
    jeżeli ('-r', '') w options:
        dd.report_full_closure()
    inaczej:
        dd.report()

jeżeli __name__ == '__main__':
    demo()
