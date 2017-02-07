"""Something just to look at via pydoc."""

zaimportuj types

klasa A_classic:
    "A classic class."
    def A_method(self):
        "Method defined w A."
    def AB_method(self):
        "Method defined w A oraz B."
    def AC_method(self):
        "Method defined w A oraz C."
    def AD_method(self):
        "Method defined w A oraz D."
    def ABC_method(self):
        "Method defined w A, B oraz C."
    def ABD_method(self):
        "Method defined w A, B oraz D."
    def ACD_method(self):
        "Method defined w A, C oraz D."
    def ABCD_method(self):
        "Method defined w A, B, C oraz D."


klasa B_classic(A_classic):
    "A classic class, derived z A_classic."
    def AB_method(self):
        "Method defined w A oraz B."
    def ABC_method(self):
        "Method defined w A, B oraz C."
    def ABD_method(self):
        "Method defined w A, B oraz D."
    def ABCD_method(self):
        "Method defined w A, B, C oraz D."
    def B_method(self):
        "Method defined w B."
    def BC_method(self):
        "Method defined w B oraz C."
    def BD_method(self):
        "Method defined w B oraz D."
    def BCD_method(self):
        "Method defined w B, C oraz D."

klasa C_classic(A_classic):
    "A classic class, derived z A_classic."
    def AC_method(self):
        "Method defined w A oraz C."
    def ABC_method(self):
        "Method defined w A, B oraz C."
    def ACD_method(self):
        "Method defined w A, C oraz D."
    def ABCD_method(self):
        "Method defined w A, B, C oraz D."
    def BC_method(self):
        "Method defined w B oraz C."
    def BCD_method(self):
        "Method defined w B, C oraz D."
    def C_method(self):
        "Method defined w C."
    def CD_method(self):
        "Method defined w C oraz D."

klasa D_classic(B_classic, C_classic):
    "A classic class, derived z B_classic oraz C_classic."
    def AD_method(self):
        "Method defined w A oraz D."
    def ABD_method(self):
        "Method defined w A, B oraz D."
    def ACD_method(self):
        "Method defined w A, C oraz D."
    def ABCD_method(self):
        "Method defined w A, B, C oraz D."
    def BD_method(self):
        "Method defined w B oraz D."
    def BCD_method(self):
        "Method defined w B, C oraz D."
    def CD_method(self):
        "Method defined w C oraz D."
    def D_method(self):
        "Method defined w D."


klasa A_new(object):
    "A new-style class."

    def A_method(self):
        "Method defined w A."
    def AB_method(self):
        "Method defined w A oraz B."
    def AC_method(self):
        "Method defined w A oraz C."
    def AD_method(self):
        "Method defined w A oraz D."
    def ABC_method(self):
        "Method defined w A, B oraz C."
    def ABD_method(self):
        "Method defined w A, B oraz D."
    def ACD_method(self):
        "Method defined w A, C oraz D."
    def ABCD_method(self):
        "Method defined w A, B, C oraz D."

    def A_classmethod(cls, x):
        "A klasa method defined w A."
    A_classmethod = classmethod(A_classmethod)

    def A_staticmethod():
        "A static method defined w A."
    A_staticmethod = staticmethod(A_staticmethod)

    def _getx(self):
        "A property getter function."
    def _setx(self, value):
        "A property setter function."
    def _delx(self):
        "A property deleter function."
    A_property = property(fdel=_delx, fget=_getx, fset=_setx,
                          doc="A sample property defined w A.")

    A_int_alias = int

klasa B_new(A_new):
    "A new-style class, derived z A_new."

    def AB_method(self):
        "Method defined w A oraz B."
    def ABC_method(self):
        "Method defined w A, B oraz C."
    def ABD_method(self):
        "Method defined w A, B oraz D."
    def ABCD_method(self):
        "Method defined w A, B, C oraz D."
    def B_method(self):
        "Method defined w B."
    def BC_method(self):
        "Method defined w B oraz C."
    def BD_method(self):
        "Method defined w B oraz D."
    def BCD_method(self):
        "Method defined w B, C oraz D."

klasa C_new(A_new):
    "A new-style class, derived z A_new."

    def AC_method(self):
        "Method defined w A oraz C."
    def ABC_method(self):
        "Method defined w A, B oraz C."
    def ACD_method(self):
        "Method defined w A, C oraz D."
    def ABCD_method(self):
        "Method defined w A, B, C oraz D."
    def BC_method(self):
        "Method defined w B oraz C."
    def BCD_method(self):
        "Method defined w B, C oraz D."
    def C_method(self):
        "Method defined w C."
    def CD_method(self):
        "Method defined w C oraz D."

klasa D_new(B_new, C_new):
    """A new-style class, derived z B_new oraz C_new.
    """

    def AD_method(self):
        "Method defined w A oraz D."
    def ABD_method(self):
        "Method defined w A, B oraz D."
    def ACD_method(self):
        "Method defined w A, C oraz D."
    def ABCD_method(self):
        "Method defined w A, B, C oraz D."
    def BD_method(self):
        "Method defined w B oraz D."
    def BCD_method(self):
        "Method defined w B, C oraz D."
    def CD_method(self):
        "Method defined w C oraz D."
    def D_method(self):
        "Method defined w D."

klasa FunkyProperties(object):
    """From SF bug 472347, by Roeland Rengelink.

    Property getters etc may nie be vanilla functions albo methods,
    oraz this used to make GUI pydoc blow up.
    """

    def __init__(self):
        self.desc = {'x':0}

    klasa get_desc:
        def __init__(self, attr):
            self.attr = attr
        def __call__(self, inst):
            print('Get called', self, inst)
            zwróć inst.desc[self.attr]
    klasa set_desc:
        def __init__(self, attr):
            self.attr = attr
        def __call__(self, inst, val):
            print('Set called', self, inst, val)
            inst.desc[self.attr] = val
    klasa del_desc:
        def __init__(self, attr):
            self.attr = attr
        def __call__(self, inst):
            print('Del called', self, inst)
            usuń inst.desc[self.attr]

    x = property(get_desc('x'), set_desc('x'), del_desc('x'), 'prop x')


submodule = types.ModuleType(__name__ + '.submodule',
    """A submodule, which should appear w its parent's summary""")
