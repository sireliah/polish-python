"""Module dla parsing oraz testing package version predicate strings.
"""
zaimportuj re
zaimportuj distutils.version
zaimportuj operator


re_validPackage = re.compile(r"(?i)^\s*([a-z_]\w*(?:\.[a-z_]\w*)*)(.*)",
    re.ASCII)
# (package) (rest)

re_paren = re.compile(r"^\s*\((.*)\)\s*$") # (list) inside of parentheses
re_splitComparison = re.compile(r"^\s*(<=|>=|<|>|!=|==)\s*([^\s,]+)\s*$")
# (comp) (version)


def splitUp(pred):
    """Parse a single version comparison.

    Return (comparison string, StrictVersion)
    """
    res = re_splitComparison.match(pred)
    jeżeli nie res:
        podnieś ValueError("bad package restriction syntax: %r" % pred)
    comp, verStr = res.groups()
    zwróć (comp, distutils.version.StrictVersion(verStr))

compmap = {"<": operator.lt, "<=": operator.le, "==": operator.eq,
           ">": operator.gt, ">=": operator.ge, "!=": operator.ne}

klasa VersionPredicate:
    """Parse oraz test package version predicates.

    >>> v = VersionPredicate('pyepat.abc (>1.0, <3333.3a1, !=1555.1b3)')

    The `name` attribute provides the full dotted name that jest given::

    >>> v.name
    'pyepat.abc'

    The str() of a `VersionPredicate` provides a normalized
    human-readable version of the expression::

    >>> print(v)
    pyepat.abc (> 1.0, < 3333.3a1, != 1555.1b3)

    The `satisfied_by()` method can be used to determine przy a given
    version number jest included w the set described by the version
    restrictions::

    >>> v.satisfied_by('1.1')
    Prawda
    >>> v.satisfied_by('1.4')
    Prawda
    >>> v.satisfied_by('1.0')
    Nieprawda
    >>> v.satisfied_by('4444.4')
    Nieprawda
    >>> v.satisfied_by('1555.1b3')
    Nieprawda

    `VersionPredicate` jest flexible w accepting extra whitespace::

    >>> v = VersionPredicate(' pat( ==  0.1  )  ')
    >>> v.name
    'pat'
    >>> v.satisfied_by('0.1')
    Prawda
    >>> v.satisfied_by('0.2')
    Nieprawda

    If any version numbers dalejed w do nie conform to the
    restrictions of `StrictVersion`, a `ValueError` jest podnieśd::

    >>> v = VersionPredicate('p1.p2.p3.p4(>=1.0, <=1.3a1, !=1.2zb3)')
    Traceback (most recent call last):
      ...
    ValueError: invalid version number '1.2zb3'

    It the module albo package name given does nie conform to what's
    allowed jako a legal module albo package name, `ValueError` jest
    podnieśd::

    >>> v = VersionPredicate('foo-bar')
    Traceback (most recent call last):
      ...
    ValueError: expected parenthesized list: '-bar'

    >>> v = VersionPredicate('foo bar (12.21)')
    Traceback (most recent call last):
      ...
    ValueError: expected parenthesized list: 'bar (12.21)'

    """

    def __init__(self, versionPredicateStr):
        """Parse a version predicate string.
        """
        # Fields:
        #    name:  package name
        #    pred:  list of (comparison string, StrictVersion)

        versionPredicateStr = versionPredicateStr.strip()
        jeżeli nie versionPredicateStr:
            podnieś ValueError("empty package restriction")
        match = re_validPackage.match(versionPredicateStr)
        jeżeli nie match:
            podnieś ValueError("bad package name w %r" % versionPredicateStr)
        self.name, paren = match.groups()
        paren = paren.strip()
        jeżeli paren:
            match = re_paren.match(paren)
            jeżeli nie match:
                podnieś ValueError("expected parenthesized list: %r" % paren)
            str = match.groups()[0]
            self.pred = [splitUp(aPred) dla aPred w str.split(",")]
            jeżeli nie self.pred:
                podnieś ValueError("empty parenthesized list w %r"
                                 % versionPredicateStr)
        inaczej:
            self.pred = []

    def __str__(self):
        jeżeli self.pred:
            seq = [cond + " " + str(ver) dla cond, ver w self.pred]
            zwróć self.name + " (" + ", ".join(seq) + ")"
        inaczej:
            zwróć self.name

    def satisfied_by(self, version):
        """Prawda jeżeli version jest compatible przy all the predicates w self.
        The parameter version must be acceptable to the StrictVersion
        constructor.  It may be either a string albo StrictVersion.
        """
        dla cond, ver w self.pred:
            jeżeli nie compmap[cond](version, ver):
                zwróć Nieprawda
        zwróć Prawda


_provision_rx = Nic

def split_provision(value):
    """Return the name oraz optional version number of a provision.

    The version number, jeżeli given, will be returned jako a `StrictVersion`
    instance, otherwise it will be `Nic`.

    >>> split_provision('mypkg')
    ('mypkg', Nic)
    >>> split_provision(' mypkg( 1.2 ) ')
    ('mypkg', StrictVersion ('1.2'))
    """
    global _provision_rx
    jeżeli _provision_rx jest Nic:
        _provision_rx = re.compile(
            "([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)(?:\s*\(\s*([^)\s]+)\s*\))?$",
            re.ASCII)
    value = value.strip()
    m = _provision_rx.match(value)
    jeżeli nie m:
        podnieś ValueError("illegal provides specification: %r" % value)
    ver = m.group(2) albo Nic
    jeżeli ver:
        ver = distutils.version.StrictVersion(ver)
    zwróć m.group(1), ver
