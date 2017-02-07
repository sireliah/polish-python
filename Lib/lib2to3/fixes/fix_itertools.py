""" Fixer dla itertools.(imap|ifilter|izip) --> (map|filter|zip) oraz
    itertools.ifilterfalse --> itertools.filterfalse (bugs 2360-2363)

    imports z itertools are fixed w fix_itertools_import.py

    If itertools jest imported jako something inaczej (ie: zaimportuj itertools jako it;
    it.izip(spam, eggs)) method calls will nie get fixed.
    """

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name

klasa FixItertools(fixer_base.BaseFix):
    BM_compatible = Prawda
    it_funcs = "('imap'|'ifilter'|'izip'|'izip_longest'|'ifilterfalse')"
    PATTERN = """
              power< it='itertools'
                  trailer<
                     dot='.' func=%(it_funcs)s > trailer< '(' [any] ')' > >
              |
              power< func=%(it_funcs)s trailer< '(' [any] ')' > >
              """ %(locals())

    # Needs to be run after fix_(map|zip|filter)
    run_order = 6

    def transform(self, node, results):
        prefix = Nic
        func = results['func'][0]
        jeżeli ('it' w results oraz
            func.value nie w ('ifilterfalse', 'izip_longest')):
            dot, it = (results['dot'], results['it'])
            # Remove the 'itertools'
            prefix = it.prefix
            it.remove()
            # Replace the node which contains ('.', 'function') przy the
            # function (to be consistent przy the second part of the pattern)
            dot.remove()
            func.parent.replace(func)

        prefix = prefix albo func.prefix
        func.replace(Name(func.value[1:], prefix=prefix))
