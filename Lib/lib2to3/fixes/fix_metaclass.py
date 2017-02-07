"""Fixer dla __metaclass__ = X -> (metaclass=X) methods.

   The various forms of classef (inherits nothing, inherits once, inherints
   many) don't parse the same w the CST so we look at ALL classes for
   a __metaclass__ oraz jeżeli we find one normalize the inherits to all be
   an arglist.

   For one-liner classes ('class X: dalej') there jest no indent/dedent so
   we normalize those into having a suite.

   Moving the __metaclass__ into the classdef can also cause the class
   body to be empty so there jest some special casing dla that jako well.

   This fixer also tries very hard to keep original indenting oraz spacing
   w all those corner cases.

"""
# Author: Jack Diederich

# Local imports
z .. zaimportuj fixer_base
z ..pygram zaimportuj token
z ..fixer_util zaimportuj Name, syms, Node, Leaf


def has_metaclass(parent):
    """ we have to check the cls_node without changing it.
        There are two possiblities:
          1)  clsdef => suite => simple_stmt => expr_stmt => Leaf('__meta')
          2)  clsdef => simple_stmt => expr_stmt => Leaf('__meta')
    """
    dla node w parent.children:
        jeżeli node.type == syms.suite:
            zwróć has_metaclass(node)
        albo_inaczej node.type == syms.simple_stmt oraz node.children:
            expr_node = node.children[0]
            jeżeli expr_node.type == syms.expr_stmt oraz expr_node.children:
                left_side = expr_node.children[0]
                jeżeli isinstance(left_side, Leaf) oraz \
                        left_side.value == '__metaclass__':
                    zwróć Prawda
    zwróć Nieprawda


def fixup_parse_tree(cls_node):
    """ one-line classes don't get a suite w the parse tree so we add
        one to normalize the tree
    """
    dla node w cls_node.children:
        jeżeli node.type == syms.suite:
            # already w the preferred format, do nothing
            zwróć

    # !%@#! oneliners have no suite node, we have to fake one up
    dla i, node w enumerate(cls_node.children):
        jeżeli node.type == token.COLON:
            przerwij
    inaczej:
        podnieś ValueError("No klasa suite oraz no ':'!")

    # move everything into a suite node
    suite = Node(syms.suite, [])
    dopóki cls_node.children[i+1:]:
        move_node = cls_node.children[i+1]
        suite.append_child(move_node.clone())
        move_node.remove()
    cls_node.append_child(suite)
    node = suite


def fixup_simple_stmt(parent, i, stmt_node):
    """ jeżeli there jest a semi-colon all the parts count jako part of the same
        simple_stmt.  We just want the __metaclass__ part so we move
        everything after the semi-colon into its own simple_stmt node
    """
    dla semi_ind, node w enumerate(stmt_node.children):
        jeżeli node.type == token.SEMI: # *sigh*
            przerwij
    inaczej:
        zwróć

    node.remove() # kill the semicolon
    new_expr = Node(syms.expr_stmt, [])
    new_stmt = Node(syms.simple_stmt, [new_expr])
    dopóki stmt_node.children[semi_ind:]:
        move_node = stmt_node.children[semi_ind]
        new_expr.append_child(move_node.clone())
        move_node.remove()
    parent.insert_child(i, new_stmt)
    new_leaf1 = new_stmt.children[0].children[0]
    old_leaf1 = stmt_node.children[0].children[0]
    new_leaf1.prefix = old_leaf1.prefix


def remove_trailing_newline(node):
    jeżeli node.children oraz node.children[-1].type == token.NEWLINE:
        node.children[-1].remove()


def find_metas(cls_node):
    # find the suite node (Mmm, sweet nodes)
    dla node w cls_node.children:
        jeżeli node.type == syms.suite:
            przerwij
    inaczej:
        podnieś ValueError("No klasa suite!")

    # look dla simple_stmt[ expr_stmt[ Leaf('__metaclass__') ] ]
    dla i, simple_node w list(enumerate(node.children)):
        jeżeli simple_node.type == syms.simple_stmt oraz simple_node.children:
            expr_node = simple_node.children[0]
            jeżeli expr_node.type == syms.expr_stmt oraz expr_node.children:
                # Check jeżeli the expr_node jest a simple assignment.
                left_node = expr_node.children[0]
                jeżeli isinstance(left_node, Leaf) oraz \
                        left_node.value == '__metaclass__':
                    # We found a assignment to __metaclass__.
                    fixup_simple_stmt(node, i, simple_node)
                    remove_trailing_newline(simple_node)
                    uzyskaj (node, i, simple_node)


def fixup_indent(suite):
    """ If an INDENT jest followed by a thing przy a prefix then nuke the prefix
        Otherwise we get w trouble when removing __metaclass__ at suite start
    """
    kids = suite.children[::-1]
    # find the first indent
    dopóki kids:
        node = kids.pop()
        jeżeli node.type == token.INDENT:
            przerwij

    # find the first Leaf
    dopóki kids:
        node = kids.pop()
        jeżeli isinstance(node, Leaf) oraz node.type != token.DEDENT:
            jeżeli node.prefix:
                node.prefix = ''
            zwróć
        inaczej:
            kids.extend(node.children[::-1])


klasa FixMetaclass(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """
    classdef<any*>
    """

    def transform(self, node, results):
        jeżeli nie has_metaclass(node):
            zwróć

        fixup_parse_tree(node)

        # find metaclasses, keep the last one
        last_metaclass = Nic
        dla suite, i, stmt w find_metas(node):
            last_metaclass = stmt
            stmt.remove()

        text_type = node.children[0].type # always Leaf(nnn, 'class')

        # figure out what kind of classdef we have
        jeżeli len(node.children) == 7:
            # Node(classdef, ['class', 'name', '(', arglist, ')', ':', suite])
            #                 0        1       2    3        4    5    6
            jeżeli node.children[3].type == syms.arglist:
                arglist = node.children[3]
            # Node(classdef, ['class', 'name', '(', 'Parent', ')', ':', suite])
            inaczej:
                parent = node.children[3].clone()
                arglist = Node(syms.arglist, [parent])
                node.set_child(3, arglist)
        albo_inaczej len(node.children) == 6:
            # Node(classdef, ['class', 'name', '(',  ')', ':', suite])
            #                 0        1       2     3    4    5
            arglist = Node(syms.arglist, [])
            node.insert_child(3, arglist)
        albo_inaczej len(node.children) == 4:
            # Node(classdef, ['class', 'name', ':', suite])
            #                 0        1       2    3
            arglist = Node(syms.arglist, [])
            node.insert_child(2, Leaf(token.RPAR, ')'))
            node.insert_child(2, arglist)
            node.insert_child(2, Leaf(token.LPAR, '('))
        inaczej:
            podnieś ValueError("Unexpected klasa definition")

        # now stick the metaclass w the arglist
        meta_txt = last_metaclass.children[0].children[0]
        meta_txt.value = 'metaclass'
        orig_meta_prefix = meta_txt.prefix

        jeżeli arglist.children:
            arglist.append_child(Leaf(token.COMMA, ','))
            meta_txt.prefix = ' '
        inaczej:
            meta_txt.prefix = ''

        # compact the expression "metaclass = Meta" -> "metaclass=Meta"
        expr_stmt = last_metaclass.children[0]
        assert expr_stmt.type == syms.expr_stmt
        expr_stmt.children[1].prefix = ''
        expr_stmt.children[2].prefix = ''

        arglist.append_child(last_metaclass)

        fixup_indent(suite)

        # check dla empty suite
        jeżeli nie suite.children:
            # one-liner that was just __metaclass_
            suite.remove()
            dalej_leaf = Leaf(text_type, 'pass')
            dalej_leaf.prefix = orig_meta_prefix
            node.append_child(pass_leaf)
            node.append_child(Leaf(token.NEWLINE, '\n'))

        albo_inaczej len(suite.children) > 1 oraz \
                 (suite.children[-2].type == token.INDENT oraz
                  suite.children[-1].type == token.DEDENT):
            # there was only one line w the klasa body oraz it was __metaclass__
            dalej_leaf = Leaf(text_type, 'pass')
            suite.insert_child(-1, dalej_leaf)
            suite.insert_child(-1, Leaf(token.NEWLINE, '\n'))
