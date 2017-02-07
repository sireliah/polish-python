"""Fixer dla function definitions przy tuple parameters.

def func(((a, b), c), d):
    ...

    ->

def func(x, d):
    ((a, b), c) = x
    ...

It will also support lambdas:

    lambda (x, y): x + y -> lambda t: t[0] + t[1]

    # The parens are a syntax error w Python 3
    lambda (x): x + y -> lambda x: x + y
"""
# Author: Collin Winter

# Local imports
z .. zaimportuj pytree
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Assign, Name, Newline, Number, Subscript, syms

def is_docstring(stmt):
    zwróć isinstance(stmt, pytree.Node) oraz \
           stmt.children[0].type == token.STRING

klasa FixTupleParams(fixer_base.BaseFix):
    run_order = 4 #use a lower order since lambda jest part of other
                  #patterns
    BM_compatible = Prawda

    PATTERN = """
              funcdef< 'def' any parameters< '(' args=any ')' >
                       ['->' any] ':' suite=any+ >
              |
              lambda=
              lambdef< 'lambda' args=vfpdef< '(' inner=any ')' >
                       ':' body=any
              >
              """

    def transform(self, node, results):
        jeżeli "lambda" w results:
            zwróć self.transform_lambda(node, results)

        new_lines = []
        suite = results["suite"]
        args = results["args"]
        # This crap jest so "def foo(...): x = 5; y = 7" jest handled correctly.
        # TODO(cwinter): suite-cleanup
        jeżeli suite[0].children[1].type == token.INDENT:
            start = 2
            indent = suite[0].children[1].value
            end = Newline()
        inaczej:
            start = 0
            indent = "; "
            end = pytree.Leaf(token.INDENT, "")

        # We need access to self dla new_name(), oraz making this a method
        #  doesn't feel right. Closing over self oraz new_lines makes the
        #  code below cleaner.
        def handle_tuple(tuple_arg, add_prefix=Nieprawda):
            n = Name(self.new_name())
            arg = tuple_arg.clone()
            arg.prefix = ""
            stmt = Assign(arg, n.clone())
            jeżeli add_prefix:
                n.prefix = " "
            tuple_arg.replace(n)
            new_lines.append(pytree.Node(syms.simple_stmt,
                                         [stmt, end.clone()]))

        jeżeli args.type == syms.tfpdef:
            handle_tuple(args)
        albo_inaczej args.type == syms.typedargslist:
            dla i, arg w enumerate(args.children):
                jeżeli arg.type == syms.tfpdef:
                    # Without add_prefix, the emitted code jest correct,
                    #  just ugly.
                    handle_tuple(arg, add_prefix=(i > 0))

        jeżeli nie new_lines:
            zwróć

        # This isn't strictly necessary, but it plays nicely przy other fixers.
        # TODO(cwinter) get rid of this when children becomes a smart list
        dla line w new_lines:
            line.parent = suite[0]

        # TODO(cwinter) suite-cleanup
        after = start
        jeżeli start == 0:
            new_lines[0].prefix = " "
        albo_inaczej is_docstring(suite[0].children[start]):
            new_lines[0].prefix = indent
            after = start + 1

        dla line w new_lines:
            line.parent = suite[0]
        suite[0].children[after:after] = new_lines
        dla i w range(after+1, after+len(new_lines)+1):
            suite[0].children[i].prefix = indent
        suite[0].changed()

    def transform_lambda(self, node, results):
        args = results["args"]
        body = results["body"]
        inner = simplify_args(results["inner"])

        # Replace lambda ((((x)))): x  przy lambda x: x
        jeżeli inner.type == token.NAME:
            inner = inner.clone()
            inner.prefix = " "
            args.replace(inner)
            zwróć

        params = find_params(args)
        to_index = map_to_index(params)
        tup_name = self.new_name(tuple_name(params))

        new_param = Name(tup_name, prefix=" ")
        args.replace(new_param.clone())
        dla n w body.post_order():
            jeżeli n.type == token.NAME oraz n.value w to_index:
                subscripts = [c.clone() dla c w to_index[n.value]]
                new = pytree.Node(syms.power,
                                  [new_param.clone()] + subscripts)
                new.prefix = n.prefix
                n.replace(new)


### Helper functions dla transform_lambda()

def simplify_args(node):
    jeżeli node.type w (syms.vfplist, token.NAME):
        zwróć node
    albo_inaczej node.type == syms.vfpdef:
        # These look like vfpdef< '(' x ')' > where x jest NAME
        # albo another vfpdef instance (leading to recursion).
        dopóki node.type == syms.vfpdef:
            node = node.children[1]
        zwróć node
    podnieś RuntimeError("Received unexpected node %s" % node)

def find_params(node):
    jeżeli node.type == syms.vfpdef:
        zwróć find_params(node.children[1])
    albo_inaczej node.type == token.NAME:
        zwróć node.value
    zwróć [find_params(c) dla c w node.children jeżeli c.type != token.COMMA]

def map_to_index(param_list, prefix=[], d=Nic):
    jeżeli d jest Nic:
        d = {}
    dla i, obj w enumerate(param_list):
        trailer = [Subscript(Number(str(i)))]
        jeżeli isinstance(obj, list):
            map_to_index(obj, trailer, d=d)
        inaczej:
            d[obj] = prefix + trailer
    zwróć d

def tuple_name(param_list):
    l = []
    dla obj w param_list:
        jeżeli isinstance(obj, list):
            l.append(tuple_name(obj))
        inaczej:
            l.append(obj)
    zwróć "_".join(l)
