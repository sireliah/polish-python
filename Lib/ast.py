"""
    ast
    ~~~

    The `ast` module helps Python applications to process trees of the Python
    abstract syntax grammar.  The abstract syntax itself might change with
    each Python release; this module helps to find out programmatically what
    the current grammar looks like oraz allows modifications of it.

    An abstract syntax tree can be generated by dalejing `ast.PyCF_ONLY_AST` as
    a flag to the `compile()` builtin function albo by using the `parse()`
    function z this module.  The result will be a tree of objects whose
    classes all inherit z `ast.AST`.

    A modified abstract syntax tree can be compiled into a Python code object
    using the built-in `compile()` function.

    Additionally various helper functions are provided that make working with
    the trees simpler.  The main intention of the helper functions oraz this
    module w general jest to provide an easy to use interface dla libraries
    that work tightly przy the python syntax (template engines dla example).


    :copyright: Copyright 2008 by Armin Ronacher.
    :license: Python License.
"""
z _ast zaimportuj *


def parse(source, filename='<unknown>', mode='exec'):
    """
    Parse the source into an AST node.
    Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
    """
    zwróć compile(source, filename, mode, PyCF_ONLY_AST)


def literal_eval(node_or_string):
    """
    Safely evaluate an expression node albo a string containing a Python
    expression.  The string albo node provided may only consist of the following
    Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
    sets, booleans, oraz Nic.
    """
    jeżeli isinstance(node_or_string, str):
        node_or_string = parse(node_or_string, mode='eval')
    jeżeli isinstance(node_or_string, Expression):
        node_or_string = node_or_string.body
    def _convert(node):
        jeżeli isinstance(node, (Str, Bytes)):
            zwróć node.s
        albo_inaczej isinstance(node, Num):
            zwróć node.n
        albo_inaczej isinstance(node, Tuple):
            zwróć tuple(map(_convert, node.elts))
        albo_inaczej isinstance(node, List):
            zwróć list(map(_convert, node.elts))
        albo_inaczej isinstance(node, Set):
            zwróć set(map(_convert, node.elts))
        albo_inaczej isinstance(node, Dict):
            zwróć dict((_convert(k), _convert(v)) dla k, v
                        w zip(node.keys, node.values))
        albo_inaczej isinstance(node, NameConstant):
            zwróć node.value
        albo_inaczej isinstance(node, UnaryOp) oraz \
             isinstance(node.op, (UAdd, USub)) oraz \
             isinstance(node.operand, (Num, UnaryOp, BinOp)):
            operand = _convert(node.operand)
            jeżeli isinstance(node.op, UAdd):
                zwróć + operand
            inaczej:
                zwróć - operand
        albo_inaczej isinstance(node, BinOp) oraz \
             isinstance(node.op, (Add, Sub)) oraz \
             isinstance(node.right, (Num, UnaryOp, BinOp)) oraz \
             isinstance(node.left, (Num, UnaryOp, BinOp)):
            left = _convert(node.left)
            right = _convert(node.right)
            jeżeli isinstance(node.op, Add):
                zwróć left + right
            inaczej:
                zwróć left - right
        podnieś ValueError('malformed node albo string: ' + repr(node))
    zwróć _convert(node_or_string)


def dump(node, annotate_fields=Prawda, include_attributes=Nieprawda):
    """
    Return a formatted dump of the tree w *node*.  This jest mainly useful for
    debugging purposes.  The returned string will show the names oraz the values
    dla fields.  This makes the code impossible to evaluate, so jeżeli evaluation jest
    wanted *annotate_fields* must be set to Nieprawda.  Attributes such jako line
    numbers oraz column offsets are nie dumped by default.  If this jest wanted,
    *include_attributes* can be set to Prawda.
    """
    def _format(node):
        jeżeli isinstance(node, AST):
            fields = [(a, _format(b)) dla a, b w iter_fields(node)]
            rv = '%s(%s' % (node.__class__.__name__, ', '.join(
                ('%s=%s' % field dla field w fields)
                jeżeli annotate_fields inaczej
                (b dla a, b w fields)
            ))
            jeżeli include_attributes oraz node._attributes:
                rv += fields oraz ', ' albo ' '
                rv += ', '.join('%s=%s' % (a, _format(getattr(node, a)))
                                dla a w node._attributes)
            zwróć rv + ')'
        albo_inaczej isinstance(node, list):
            zwróć '[%s]' % ', '.join(_format(x) dla x w node)
        zwróć repr(node)
    jeżeli nie isinstance(node, AST):
        podnieś TypeError('expected AST, got %r' % node.__class__.__name__)
    zwróć _format(node)


def copy_location(new_node, old_node):
    """
    Copy source location (`lineno` oraz `col_offset` attributes) from
    *old_node* to *new_node* jeżeli possible, oraz zwróć *new_node*.
    """
    dla attr w 'lineno', 'col_offset':
        jeżeli attr w old_node._attributes oraz attr w new_node._attributes \
           oraz hasattr(old_node, attr):
            setattr(new_node, attr, getattr(old_node, attr))
    zwróć new_node


def fix_missing_locations(node):
    """
    When you compile a node tree przy compile(), the compiler expects lineno oraz
    col_offset attributes dla every node that supports them.  This jest rather
    tedious to fill w dla generated nodes, so this helper adds these attributes
    recursively where nie already set, by setting them to the values of the
    parent node.  It works recursively starting at *node*.
    """
    def _fix(node, lineno, col_offset):
        jeżeli 'lineno' w node._attributes:
            jeżeli nie hasattr(node, 'lineno'):
                node.lineno = lineno
            inaczej:
                lineno = node.lineno
        jeżeli 'col_offset' w node._attributes:
            jeżeli nie hasattr(node, 'col_offset'):
                node.col_offset = col_offset
            inaczej:
                col_offset = node.col_offset
        dla child w iter_child_nodes(node):
            _fix(child, lineno, col_offset)
    _fix(node, 1, 0)
    zwróć node


def increment_lineno(node, n=1):
    """
    Increment the line number of each node w the tree starting at *node* by *n*.
    This jest useful to "move code" to a different location w a file.
    """
    dla child w walk(node):
        jeżeli 'lineno' w child._attributes:
            child.lineno = getattr(child, 'lineno', 0) + n
    zwróć node


def iter_fields(node):
    """
    Yield a tuple of ``(fieldname, value)`` dla each field w ``node._fields``
    that jest present on *node*.
    """
    dla field w node._fields:
        spróbuj:
            uzyskaj field, getattr(node, field)
        wyjąwszy AttributeError:
            dalej


def iter_child_nodes(node):
    """
    Yield all direct child nodes of *node*, that is, all fields that are nodes
    oraz all items of fields that are lists of nodes.
    """
    dla name, field w iter_fields(node):
        jeżeli isinstance(field, AST):
            uzyskaj field
        albo_inaczej isinstance(field, list):
            dla item w field:
                jeżeli isinstance(item, AST):
                    uzyskaj item


def get_docstring(node, clean=Prawda):
    """
    Return the docstring dla the given node albo Nic jeżeli no docstring can
    be found.  If the node provided does nie have docstrings a TypeError
    will be podnieśd.
    """
    jeżeli nie isinstance(node, (AsyncFunctionDef, FunctionDef, ClassDef, Module)):
        podnieś TypeError("%r can't have docstrings" % node.__class__.__name__)
    jeżeli node.body oraz isinstance(node.body[0], Expr) oraz \
       isinstance(node.body[0].value, Str):
        jeżeli clean:
            zaimportuj inspect
            zwróć inspect.cleandoc(node.body[0].value.s)
        zwróć node.body[0].value.s


def walk(node):
    """
    Recursively uzyskaj all descendant nodes w the tree starting at *node*
    (including *node* itself), w no specified order.  This jest useful jeżeli you
    only want to modify nodes w place oraz don't care about the context.
    """
    z collections zaimportuj deque
    todo = deque([node])
    dopóki todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        uzyskaj node


klasa NodeVisitor(object):
    """
    A node visitor base klasa that walks the abstract syntax tree oraz calls a
    visitor function dla every node found.  This function may zwróć a value
    which jest forwarded by the `visit` method.

    This klasa jest meant to be subclassed, przy the subclass adding visitor
    methods.

    Per default the visitor functions dla the nodes are ``'visit_'`` +
    klasa name of the node.  So a `TryFinally` node visit function would
    be `visit_TryFinally`.  This behavior can be changed by overriding
    the `visit` method.  If no visitor function exists dla a node
    (return value `Nic`) the `generic_visit` visitor jest used instead.

    Don't use the `NodeVisitor` jeżeli you want to apply changes to nodes during
    traversing.  For this a special visitor exists (`NodeTransformer`) that
    allows modifications.
    """

    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        zwróć visitor(node)

    def generic_visit(self, node):
        """Called jeżeli no explicit visitor function exists dla a node."""
        dla field, value w iter_fields(node):
            jeżeli isinstance(value, list):
                dla item w value:
                    jeżeli isinstance(item, AST):
                        self.visit(item)
            albo_inaczej isinstance(value, AST):
                self.visit(value)


klasa NodeTransformer(NodeVisitor):
    """
    A :class:`NodeVisitor` subclass that walks the abstract syntax tree oraz
    allows modification of nodes.

    The `NodeTransformer` will walk the AST oraz use the zwróć value of the
    visitor methods to replace albo remove the old node.  If the zwróć value of
    the visitor method jest ``Nic``, the node will be removed z its location,
    otherwise it jest replaced przy the zwróć value.  The zwróć value may be the
    original node w which case no replacement takes place.

    Here jest an example transformer that rewrites all occurrences of name lookups
    (``foo``) to ``data['foo']``::

       klasa RewriteName(NodeTransformer):

           def visit_Name(self, node):
               zwróć copy_location(Subscript(
                   value=Name(id='data', ctx=Load()),
                   slice=Index(value=Str(s=node.id)),
                   ctx=node.ctx
               ), node)

    Keep w mind that jeżeli the node you're operating on has child nodes you must
    either transform the child nodes yourself albo call the :meth:`generic_visit`
    method dla the node first.

    For nodes that were part of a collection of statements (that applies to all
    statement nodes), the visitor may also zwróć a list of nodes rather than
    just a single node.

    Usually you use the transformer like this::

       node = YourTransformer().visit(node)
    """

    def generic_visit(self, node):
        dla field, old_value w iter_fields(node):
            old_value = getattr(node, field, Nic)
            jeżeli isinstance(old_value, list):
                new_values = []
                dla value w old_value:
                    jeżeli isinstance(value, AST):
                        value = self.visit(value)
                        jeżeli value jest Nic:
                            kontynuuj
                        albo_inaczej nie isinstance(value, AST):
                            new_values.extend(value)
                            kontynuuj
                    new_values.append(value)
                old_value[:] = new_values
            albo_inaczej isinstance(old_value, AST):
                new_node = self.visit(old_value)
                jeżeli new_node jest Nic:
                    delattr(node, field)
                inaczej:
                    setattr(node, field, new_node)
        zwróć node
