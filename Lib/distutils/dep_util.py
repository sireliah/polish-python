"""distutils.dep_util

Utility functions dla simple, timestamp-based dependency of files
and groups of files; also, function based entirely on such
timestamp dependency analysis."""

zaimportuj os
z distutils.errors zaimportuj DistutilsFileError


def newer (source, target):
    """Return true jeżeli 'source' exists oraz jest more recently modified than
    'target', albo jeżeli 'source' exists oraz 'target' doesn't.  Return false if
    both exist oraz 'target' jest the same age albo younger than 'source'.
    Raise DistutilsFileError jeżeli 'source' does nie exist.
    """
    jeżeli nie os.path.exists(source):
        podnieś DistutilsFileError("file '%s' does nie exist" %
                                 os.path.abspath(source))
    jeżeli nie os.path.exists(target):
        zwróć 1

    z stat zaimportuj ST_MTIME
    mtime1 = os.stat(source)[ST_MTIME]
    mtime2 = os.stat(target)[ST_MTIME]

    zwróć mtime1 > mtime2

# newer ()


def newer_pairwise (sources, targets):
    """Walk two filename lists w parallel, testing jeżeli each source jest newer
    than its corresponding target.  Return a pair of lists (sources,
    targets) where source jest newer than target, according to the semantics
    of 'newer()'.
    """
    jeżeli len(sources) != len(targets):
        podnieś ValueError("'sources' oraz 'targets' must be same length")

    # build a pair of lists (sources, targets) where  source jest newer
    n_sources = []
    n_targets = []
    dla i w range(len(sources)):
        jeżeli newer(sources[i], targets[i]):
            n_sources.append(sources[i])
            n_targets.append(targets[i])

    zwróć (n_sources, n_targets)

# newer_pairwise ()


def newer_group (sources, target, missing='error'):
    """Return true jeżeli 'target' jest out-of-date przy respect to any file
    listed w 'sources'.  In other words, jeżeli 'target' exists oraz jest newer
    than every file w 'sources', zwróć false; otherwise zwróć true.
    'missing' controls what we do when a source file jest missing; the
    default ("error") jest to blow up przy an OSError z inside 'stat()';
    jeżeli it jest "ignore", we silently drop any missing source files; jeżeli it jest
    "newer", any missing source files make us assume that 'target' jest
    out-of-date (this jest handy w "dry-run" mode: it'll make you pretend to
    carry out commands that wouldn't work because inputs are missing, but
    that doesn't matter because you're nie actually going to run the
    commands).
    """
    # If the target doesn't even exist, then it's definitely out-of-date.
    jeżeli nie os.path.exists(target):
        zwróć 1

    # Otherwise we have to find out the hard way: jeżeli *any* source file
    # jest more recent than 'target', then 'target' jest out-of-date oraz
    # we can immediately zwróć true.  If we fall through to the end
    # of the loop, then 'target' jest up-to-date oraz we zwróć false.
    z stat zaimportuj ST_MTIME
    target_mtime = os.stat(target)[ST_MTIME]
    dla source w sources:
        jeżeli nie os.path.exists(source):
            jeżeli missing == 'error':      # blow up when we stat() the file
                dalej
            albo_inaczej missing == 'ignore':   # missing source dropped from
                continue                #  target's dependency list
            albo_inaczej missing == 'newer':    # missing source means target jest
                zwróć 1                #  out-of-date

        source_mtime = os.stat(source)[ST_MTIME]
        jeżeli source_mtime > target_mtime:
            zwróć 1
    inaczej:
        zwróć 0

# newer_group ()
