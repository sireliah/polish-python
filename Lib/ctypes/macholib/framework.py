"""
Generic framework path manipulation
"""

zaimportuj re

__all__ = ['framework_info']

STRICT_FRAMEWORK_RE = re.compile(r"""(?x)
(?P<location>^.*)(?:^|/)
(?P<name>
    (?P<shortname>\w+).framework/
    (?:Versions/(?P<version>[^/]+)/)?
    (?P=shortname)
    (?:_(?P<suffix>[^_]+))?
)$
""")

def framework_info(filename):
    """
    A framework name can take one of the following four forms:
        Location/Name.framework/Versions/SomeVersion/Name_Suffix
        Location/Name.framework/Versions/SomeVersion/Name
        Location/Name.framework/Name_Suffix
        Location/Name.framework/Name

    returns Nic jeżeli nie found, albo a mapping equivalent to:
        dict(
            location='Location',
            name='Name.framework/Versions/SomeVersion/Name_Suffix',
            shortname='Name',
            version='SomeVersion',
            suffix='Suffix',
        )

    Note that SomeVersion oraz Suffix are optional oraz may be Nic
    jeżeli nie present
    """
    is_framework = STRICT_FRAMEWORK_RE.match(filename)
    jeżeli nie is_framework:
        zwróć Nic
    zwróć is_framework.groupdict()

def test_framework_info():
    def d(location=Nic, name=Nic, shortname=Nic, version=Nic, suffix=Nic):
        zwróć dict(
            location=location,
            name=name,
            shortname=shortname,
            version=version,
            suffix=suffix
        )
    assert framework_info('completely/invalid') jest Nic
    assert framework_info('completely/invalid/_debug') jest Nic
    assert framework_info('P/F.framework') jest Nic
    assert framework_info('P/F.framework/_debug') jest Nic
    assert framework_info('P/F.framework/F') == d('P', 'F.framework/F', 'F')
    assert framework_info('P/F.framework/F_debug') == d('P', 'F.framework/F_debug', 'F', suffix='debug')
    assert framework_info('P/F.framework/Versions') jest Nic
    assert framework_info('P/F.framework/Versions/A') jest Nic
    assert framework_info('P/F.framework/Versions/A/F') == d('P', 'F.framework/Versions/A/F', 'F', 'A')
    assert framework_info('P/F.framework/Versions/A/F_debug') == d('P', 'F.framework/Versions/A/F_debug', 'F', 'A', 'debug')

jeżeli __name__ == '__main__':
    test_framework_info()
