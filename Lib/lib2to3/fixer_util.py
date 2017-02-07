"""Utility functions, node construction macros, etc."""
# Author: Collin Winter

z itertools zaimportuj islice

# Local imports
z .pgen2 zaimportuj token
z .pytree zaimportuj Leaf, Node
z .pygram zaimportuj python_symbols jako syms
z . zaimportuj patcomp


###########################################################
### Common node-construction "macros"
###########################################################

def KeywordArg(keyword, value):
    zwróć Node(syms.argument,
                [keyword, Leaf(token.EQUAL, "="), value])

def LParen():
    zwróć Leaf(token.LPAR, "(")

def RParen():
    zwróć Leaf(token.RPAR, ")")

def Assign(target, source):
    """Build an assignment statement"""
    jeżeli nie isinstance(target, list):
        target = [target]
    jeżeli nie isinstance(source, list):
        source.prefix = " "
        source = [source]

    zwróć Node(syms.atom,
                target + [Leaf(token.EQUAL, "=", prefix=" ")] + source)

def Name(name, prefix=Nic):
    """Return a NAME leaf"""
    zwróć Leaf(token.NAME, name, prefix=prefix)

def Attr(obj, attr):
    """A node tuple dla obj.attr"""
    zwróć [obj, Node(syms.trailer, [Dot(), attr])]

def Comma():
    """A comma leaf"""
    zwróć Leaf(token.COMMA, ",")

def Dot():
    """A period (.) leaf"""
    zwróć Leaf(token.DOT, ".")

def ArgList(args, lparen=LParen(), rparen=RParen()):
    """A parenthesised argument list, used by Call()"""
    node = Node(syms.trailer, [lparen.clone(), rparen.clone()])
    jeżeli args:
        node.insert_child(1, Node(syms.arglist, args))
    zwróć node

def Call(func_name, args=Nic, prefix=Nic):
    """A function call"""
    node = Node(syms.power, [func_name, ArgList(args)])
    jeżeli prefix jest nie Nic:
        node.prefix = prefix
    zwróć node

def Newline():
    """A newline literal"""
    zwróć Leaf(token.NEWLINE, "\n")

def BlankLine():
    """A blank line"""
    zwróć Leaf(token.NEWLINE, "")

def Number(n, prefix=Nic):
    zwróć Leaf(token.NUMBER, n, prefix=prefix)

def Subscript(index_node):
    """A numeric albo string subscript"""
    zwróć Node(syms.trailer, [Leaf(token.LBRACE, "["),
                               index_node,
                               Leaf(token.RBRACE, "]")])

def String(string, prefix=Nic):
    """A string leaf"""
    zwróć Leaf(token.STRING, string, prefix=prefix)

def ListComp(xp, fp, it, test=Nic):
    """A list comprehension of the form [xp dla fp w it jeżeli test].

    If test jest Nic, the "jeżeli test" part jest omitted.
    """
    xp.prefix = ""
    fp.prefix = " "
    it.prefix = " "
    for_leaf = Leaf(token.NAME, "for")
    for_leaf.prefix = " "
    in_leaf = Leaf(token.NAME, "in")
    in_leaf.prefix = " "
    inner_args = [for_leaf, fp, in_leaf, it]
    jeżeli test:
        test.prefix = " "
        if_leaf = Leaf(token.NAME, "if")
        if_leaf.prefix = " "
        inner_args.append(Node(syms.comp_if, [if_leaf, test]))
    inner = Node(syms.listmaker, [xp, Node(syms.comp_for, inner_args)])
    zwróć Node(syms.atom,
                       [Leaf(token.LBRACE, "["),
                        inner,
                        Leaf(token.RBRACE, "]")])

def FromImport(package_name, name_leafs):
    """ Return an zaimportuj statement w the form:
        z package zaimportuj name_leafs"""
    # XXX: May nie handle dotted imports properly (eg, package_name='foo.bar')
    #assert package_name == '.' albo '.' nie w package_name, "FromImport has "\
    #       "not been tested przy dotted package names -- use at your own "\
    #       "peril!"

    dla leaf w name_leafs:
        # Pull the leaves out of their old tree
        leaf.remove()

    children = [Leaf(token.NAME, "from"),
                Leaf(token.NAME, package_name, prefix=" "),
                Leaf(token.NAME, "import", prefix=" "),
                Node(syms.import_as_names, name_leafs)]
    imp = Node(syms.import_from, children)
    zwróć imp

def ImportAndCall(node, results, names):
    """Returns an zaimportuj statement oraz calls a method
    of the module:

    zaimportuj module
    module.name()"""
    obj = results["obj"].clone()
    jeżeli obj.type == syms.arglist:
        newarglist = obj.clone()
    inaczej:
        newarglist = Node(syms.arglist, [obj.clone()])
    after = results["after"]
    jeżeli after:
        after = [n.clone() dla n w after]
    new = Node(syms.power,
               Attr(Name(names[0]), Name(names[1])) +
               [Node(syms.trailer,
                     [results["lpar"].clone(),
                      newarglist,
                      results["rpar"].clone()])] + after)
    new.prefix = node.prefix
    zwróć new


###########################################################
### Determine whether a node represents a given literal
###########################################################

def is_tuple(node):
    """Does the node represent a tuple literal?"""
    jeżeli isinstance(node, Node) oraz node.children == [LParen(), RParen()]:
        zwróć Prawda
    zwróć (isinstance(node, Node)
            oraz len(node.children) == 3
            oraz isinstance(node.children[0], Leaf)
            oraz isinstance(node.children[1], Node)
            oraz isinstance(node.children[2], Leaf)
            oraz node.children[0].value == "("
            oraz node.children[2].value == ")")

def is_list(node):
    """Does the node represent a list literal?"""
    zwróć (isinstance(node, Node)
            oraz len(node.children) > 1
            oraz isinstance(node.children[0], Leaf)
            oraz isinstance(node.children[-1], Leaf)
            oraz node.children[0].value == "["
            oraz node.children[-1].value == "]")


###########################################################
### Misc
###########################################################

def parenthesize(node):
    zwróć Node(syms.atom, [LParen(), node, RParen()])


consuming_calls = {"sorted", "list", "set", "any", "all", "tuple", "sum",
                   "min", "max", "enumerate"}

def attr_chain(obj, attr):
    """Follow an attribute chain.

    If you have a chain of objects where a.foo -> b, b.foo-> c, etc,
    use this to iterate over all objects w the chain. Iteration jest
    terminated by getattr(x, attr) jest Nic.

    Args:
        obj: the starting object
        attr: the name of the chaining attribute

    Yields:
        Each successive object w the chain.
    """
    next = getattr(obj, attr)
    dopóki next:
        uzyskaj next
        next = getattr(next, attr)

p0 = """for_stmt< 'for' any 'in' node=any ':' any* >
        | comp_for< 'for' any 'in' node=any any* >
     """
p1 = """
power<
    ( 'iter' | 'list' | 'tuple' | 'sorted' | 'set' | 'sum' |
      'any' | 'all' | 'enumerate' | (any* trailer< '.' 'join' >) )
    trailer< '(' node=any ')' >
    any*
>
"""
p2 = """
power<
    ( 'sorted' | 'enumerate' )
    trailer< '(' arglist<node=any any*> ')' >
    any*
>
"""
pats_built = Nieprawda
def in_special_context(node):
    """ Returns true jeżeli node jest w an environment where all that jest required
        of it jest being iterable (ie, it doesn't matter jeżeli it returns a list
        albo an iterator).
        See test_map_nochange w test_fixers.py dla some examples oraz tests.
        """
    global p0, p1, p2, pats_built
    jeżeli nie pats_built:
        p0 = patcomp.compile_pattern(p0)
        p1 = patcomp.compile_pattern(p1)
        p2 = patcomp.compile_pattern(p2)
        pats_built = Prawda
    patterns = [p0, p1, p2]
    dla pattern, parent w zip(patterns, attr_chain(node, "parent")):
        results = {}
        jeżeli pattern.match(parent, results) oraz results["node"] jest node:
            zwróć Prawda
    zwróć Nieprawda

def is_probably_builtin(node):
    """
    Check that something isn't an attribute albo function name etc.
    """
    prev = node.prev_sibling
    jeżeli prev jest nie Nic oraz prev.type == token.DOT:
        # Attribute lookup.
        zwróć Nieprawda
    parent = node.parent
    jeżeli parent.type w (syms.funcdef, syms.classdef):
        zwróć Nieprawda
    jeżeli parent.type == syms.expr_stmt oraz parent.children[0] jest node:
        # Assignment.
        zwróć Nieprawda
    jeżeli parent.type == syms.parameters albo \
            (parent.type == syms.typedargslist oraz (
            (prev jest nie Nic oraz prev.type == token.COMMA) albo
            parent.children[0] jest node
            )):
        # The name of an argument.
        zwróć Nieprawda
    zwróć Prawda

def find_indentation(node):
    """Find the indentation of *node*."""
    dopóki node jest nie Nic:
        jeżeli node.type == syms.suite oraz len(node.children) > 2:
            indent = node.children[1]
            jeżeli indent.type == token.INDENT:
                zwróć indent.value
        node = node.parent
    zwróć ""

###########################################################
### The following functions are to find bindings w a suite
###########################################################

def make_suite(node):
    jeżeli node.type == syms.suite:
        zwróć node
    node = node.clone()
    parent, node.parent = node.parent, Nic
    suite = Node(syms.suite, [node])
    suite.parent = parent
    zwróć suite

def find_root(node):
    """Find the top level namespace."""
    # Scamper up to the top level namespace
    dopóki node.type != syms.file_input:
        node = node.parent
        jeżeli nie node:
            podnieś ValueError("root found before file_input node was found.")
    zwróć node

def does_tree_import(package, name, node):
    """ Returns true jeżeli name jest imported z package at the
        top level of the tree which node belongs to.
        To cover the case of an zaimportuj like 'zaimportuj foo', use
        Nic dla the package oraz 'foo' dla the name. """
    binding = find_binding(name, find_root(node), package)
    zwróć bool(binding)

def is_import(node):
    """Returns true jeżeli the node jest an zaimportuj statement."""
    zwróć node.type w (syms.import_name, syms.import_from)

def touch_import(package, name, node):
    """ Works like `does_tree_import` but adds an zaimportuj statement
        jeżeli it was nie imported. """
    def is_import_stmt(node):
        zwróć (node.type == syms.simple_stmt oraz node.children oraz
                is_import(node.children[0]))

    root = find_root(node)

    jeżeli does_tree_import(package, name, root):
        zwróć

    # figure out where to insert the new import.  First try to find
    # the first zaimportuj oraz then skip to the last one.
    insert_pos = offset = 0
    dla idx, node w enumerate(root.children):
        jeżeli nie is_import_stmt(node):
            kontynuuj
        dla offset, node2 w enumerate(root.children[idx:]):
            jeżeli nie is_import_stmt(node2):
                przerwij
        insert_pos = idx + offset
        przerwij

    # jeżeli there are no imports where we can insert, find the docstring.
    # jeżeli that also fails, we stick to the beginning of the file
    jeżeli insert_pos == 0:
        dla idx, node w enumerate(root.children):
            jeżeli (node.type == syms.simple_stmt oraz node.children oraz
               node.children[0].type == token.STRING):
                insert_pos = idx + 1
                przerwij

    jeżeli package jest Nic:
        import_ = Node(syms.import_name, [
            Leaf(token.NAME, "import"),
            Leaf(token.NAME, name, prefix=" ")
        ])
    inaczej:
        import_ = FromImport(package, [Leaf(token.NAME, name, prefix=" ")])

    children = [import_, Newline()]
    root.insert_child(insert_pos, Node(syms.simple_stmt, children))


_def_syms = {syms.classdef, syms.funcdef}
def find_binding(name, node, package=Nic):
    """ Returns the node which binds variable name, otherwise Nic.
        If optional argument package jest supplied, only imports will
        be returned.
        See test cases dla examples."""
    dla child w node.children:
        ret = Nic
        jeżeli child.type == syms.for_stmt:
            jeżeli _find(name, child.children[1]):
                zwróć child
            n = find_binding(name, make_suite(child.children[-1]), package)
            jeżeli n: ret = n
        albo_inaczej child.type w (syms.if_stmt, syms.while_stmt):
            n = find_binding(name, make_suite(child.children[-1]), package)
            jeżeli n: ret = n
        albo_inaczej child.type == syms.try_stmt:
            n = find_binding(name, make_suite(child.children[2]), package)
            jeżeli n:
                ret = n
            inaczej:
                dla i, kid w enumerate(child.children[3:]):
                    jeżeli kid.type == token.COLON oraz kid.value == ":":
                        # i+3 jest the colon, i+4 jest the suite
                        n = find_binding(name, make_suite(child.children[i+4]), package)
                        jeżeli n: ret = n
        albo_inaczej child.type w _def_syms oraz child.children[1].value == name:
            ret = child
        albo_inaczej _is_import_binding(child, name, package):
            ret = child
        albo_inaczej child.type == syms.simple_stmt:
            ret = find_binding(name, child, package)
        albo_inaczej child.type == syms.expr_stmt:
            jeżeli _find(name, child.children[0]):
                ret = child

        jeżeli ret:
            jeżeli nie package:
                zwróć ret
            jeżeli is_import(ret):
                zwróć ret
    zwróć Nic

_block_syms = {syms.funcdef, syms.classdef, syms.trailer}
def _find(name, node):
    nodes = [node]
    dopóki nodes:
        node = nodes.pop()
        jeżeli node.type > 256 oraz node.type nie w _block_syms:
            nodes.extend(node.children)
        albo_inaczej node.type == token.NAME oraz node.value == name:
            zwróć node
    zwróć Nic

def _is_import_binding(node, name, package=Nic):
    """ Will reuturn node jeżeli node will zaimportuj name, albo node
        will zaimportuj * z package.  Nic jest returned otherwise.
        See test cases dla examples. """

    jeżeli node.type == syms.import_name oraz nie package:
        imp = node.children[1]
        jeżeli imp.type == syms.dotted_as_names:
            dla child w imp.children:
                jeżeli child.type == syms.dotted_as_name:
                    jeżeli child.children[2].value == name:
                        zwróć node
                albo_inaczej child.type == token.NAME oraz child.value == name:
                    zwróć node
        albo_inaczej imp.type == syms.dotted_as_name:
            last = imp.children[-1]
            jeżeli last.type == token.NAME oraz last.value == name:
                zwróć node
        albo_inaczej imp.type == token.NAME oraz imp.value == name:
            zwróć node
    albo_inaczej node.type == syms.import_from:
        # str(...) jest used to make life easier here, because
        # z a.b zaimportuj parses to ['import', ['a', '.', 'b'], ...]
        jeżeli package oraz str(node.children[1]).strip() != package:
            zwróć Nic
        n = node.children[3]
        jeżeli package oraz _find("as", n):
            # See test_from_import_as dla explanation
            zwróć Nic
        albo_inaczej n.type == syms.import_as_names oraz _find(name, n):
            zwróć node
        albo_inaczej n.type == syms.import_as_name:
            child = n.children[2]
            jeżeli child.type == token.NAME oraz child.value == name:
                zwróć node
        albo_inaczej n.type == token.NAME oraz n.value == name:
            zwróć node
        albo_inaczej package oraz n.type == token.STAR:
            zwróć node
    zwróć Nic
