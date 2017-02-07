# Used by test_doctest.py.

klasa TwoNames:
    '''f() oraz g() are two names dla the same method'''

    def f(self):
        '''
        >>> print(TwoNames().f())
        f
        '''
        zwróć 'f'

    g = f # define an alias dla f
