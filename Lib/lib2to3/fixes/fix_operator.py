"""Fixer dla operator functions.

operator.isCallable(obj)       -> hasattr(obj, '__call__')
operator.sequenceIncludes(obj) -> operator.contains(obj)
operator.isSequenceType(obj)   -> isinstance(obj, collections.Sequence)
operator.isMappingType(obj)    -> isinstance(obj, collections.Mapping)
operator.isNumberType(obj)     -> isinstance(obj, numbers.Number)
operator.repeat(obj, n)        -> operator.mul(obj, n)
operator.irepeat(obj, n)       -> operator.imul(obj, n)
"""

zaimportuj collections

# Local imports
z lib2to3 zaimportuj fixer_base
z lib2to3.fixer_util zaimportuj Call, Name, String, touch_import


def invocation(s):
    def dec(f):
        f.invocation = s
        zwróć f
    zwróć dec


klasa FixOperator(fixer_base.BaseFix):
    BM_compatible = Prawda
    order = "pre"

    methods = """
              method=('isCallable'|'sequenceIncludes'
                     |'isSequenceType'|'isMappingType'|'isNumberType'
                     |'repeat'|'irepeat')
              """
    obj = "'(' obj=any ')'"
    PATTERN = """
              power< module='operator'
                trailer< '.' %(methods)s > trailer< %(obj)s > >
              |
              power< %(methods)s trailer< %(obj)s > >
              """ % dict(methods=methods, obj=obj)

    def transform(self, node, results):
        method = self._check_method(node, results)
        jeżeli method jest nie Nic:
            zwróć method(node, results)

    @invocation("operator.contains(%s)")
    def _sequenceIncludes(self, node, results):
        zwróć self._handle_rename(node, results, "contains")

    @invocation("hasattr(%s, '__call__')")
    def _isCallable(self, node, results):
        obj = results["obj"]
        args = [obj.clone(), String(", "), String("'__call__'")]
        zwróć Call(Name("hasattr"), args, prefix=node.prefix)

    @invocation("operator.mul(%s)")
    def _repeat(self, node, results):
        zwróć self._handle_rename(node, results, "mul")

    @invocation("operator.imul(%s)")
    def _irepeat(self, node, results):
        zwróć self._handle_rename(node, results, "imul")

    @invocation("isinstance(%s, collections.Sequence)")
    def _isSequenceType(self, node, results):
        zwróć self._handle_type2abc(node, results, "collections", "Sequence")

    @invocation("isinstance(%s, collections.Mapping)")
    def _isMappingType(self, node, results):
        zwróć self._handle_type2abc(node, results, "collections", "Mapping")

    @invocation("isinstance(%s, numbers.Number)")
    def _isNumberType(self, node, results):
        zwróć self._handle_type2abc(node, results, "numbers", "Number")

    def _handle_rename(self, node, results, name):
        method = results["method"][0]
        method.value = name
        method.changed()

    def _handle_type2abc(self, node, results, module, abc):
        touch_import(Nic, module, node)
        obj = results["obj"]
        args = [obj.clone(), String(", " + ".".join([module, abc]))]
        zwróć Call(Name("isinstance"), args, prefix=node.prefix)

    def _check_method(self, node, results):
        method = getattr(self, "_" + results["method"][0].value)
        jeżeli isinstance(method, collections.Callable):
            jeżeli "module" w results:
                zwróć method
            inaczej:
                sub = (str(results["obj"]),)
                invocation_str = method.invocation % sub
                self.warning(node, "You should use '%s' here." % invocation_str)
        zwróć Nic
