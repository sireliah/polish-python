# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""
Python parse tree definitions.

This jest a very concrete parse tree; we need to keep every token oraz
even the comments oraz whitespace between tokens.

There's also a pattern matching implementation here.
"""

__author__ = "Guido van Rossum <guido@python.org>"

zaimportuj sys
zaimportuj warnings
z io zaimportuj StringIO

HUGE = 0x7FFFFFFF  # maximum repeat count, default max

_type_reprs = {}
def type_repr(type_num):
    global _type_reprs
    jeżeli nie _type_reprs:
        z .pygram zaimportuj python_symbols
        # printing tokens jest possible but nie jako useful
        # z .pgen2 zaimportuj token // token.__dict__.items():
        dla name, val w python_symbols.__dict__.items():
            jeżeli type(val) == int: _type_reprs[val] = name
    zwróć _type_reprs.setdefault(type_num, type_num)

klasa Base(object):

    """
    Abstract base klasa dla Node oraz Leaf.

    This provides some default functionality oraz boilerplate using the
    template pattern.

    A node may be a subnode of at most one parent.
    """

    # Default values dla instance variables
    type = Nic    # int: token number (< 256) albo symbol number (>= 256)
    parent = Nic  # Parent node pointer, albo Nic
    children = ()  # Tuple of subnodes
    was_changed = Nieprawda
    was_checked = Nieprawda

    def __new__(cls, *args, **kwds):
        """Constructor that prevents Base z being instantiated."""
        assert cls jest nie Base, "Cannot instantiate Base"
        zwróć object.__new__(cls)

    def __eq__(self, other):
        """
        Compare two nodes dla equality.

        This calls the method _eq().
        """
        jeżeli self.__class__ jest nie other.__class__:
            zwróć NotImplemented
        zwróć self._eq(other)

    __hash__ = Nic # For Py3 compatibility.

    def _eq(self, other):
        """
        Compare two nodes dla equality.

        This jest called by __eq__ oraz __ne__.  It jest only called jeżeli the two nodes
        have the same type.  This must be implemented by the concrete subclass.
        Nodes should be considered equal jeżeli they have the same structure,
        ignoring the prefix string oraz other context information.
        """
        podnieś NotImplementedError

    def clone(self):
        """
        Return a cloned (deep) copy of self.

        This must be implemented by the concrete subclass.
        """
        podnieś NotImplementedError

    def post_order(self):
        """
        Return a post-order iterator dla the tree.

        This must be implemented by the concrete subclass.
        """
        podnieś NotImplementedError

    def pre_order(self):
        """
        Return a pre-order iterator dla the tree.

        This must be implemented by the concrete subclass.
        """
        podnieś NotImplementedError

    def replace(self, new):
        """Replace this node przy a new one w the parent."""
        assert self.parent jest nie Nic, str(self)
        assert new jest nie Nic
        jeżeli nie isinstance(new, list):
            new = [new]
        l_children = []
        found = Nieprawda
        dla ch w self.parent.children:
            jeżeli ch jest self:
                assert nie found, (self.parent.children, self, new)
                jeżeli new jest nie Nic:
                    l_children.extend(new)
                found = Prawda
            inaczej:
                l_children.append(ch)
        assert found, (self.children, self, new)
        self.parent.changed()
        self.parent.children = l_children
        dla x w new:
            x.parent = self.parent
        self.parent = Nic

    def get_lineno(self):
        """Return the line number which generated the invocant node."""
        node = self
        dopóki nie isinstance(node, Leaf):
            jeżeli nie node.children:
                zwróć
            node = node.children[0]
        zwróć node.lineno

    def changed(self):
        jeżeli self.parent:
            self.parent.changed()
        self.was_changed = Prawda

    def remove(self):
        """
        Remove the node z the tree. Returns the position of the node w its
        parent's children before it was removed.
        """
        jeżeli self.parent:
            dla i, node w enumerate(self.parent.children):
                jeżeli node jest self:
                    self.parent.changed()
                    usuń self.parent.children[i]
                    self.parent = Nic
                    zwróć i

    @property
    def next_sibling(self):
        """
        The node immediately following the invocant w their parent's children
        list. If the invocant does nie have a next sibling, it jest Nic
        """
        jeżeli self.parent jest Nic:
            zwróć Nic

        # Can't use index(); we need to test by identity
        dla i, child w enumerate(self.parent.children):
            jeżeli child jest self:
                spróbuj:
                    zwróć self.parent.children[i+1]
                wyjąwszy IndexError:
                    zwróć Nic

    @property
    def prev_sibling(self):
        """
        The node immediately preceding the invocant w their parent's children
        list. If the invocant does nie have a previous sibling, it jest Nic.
        """
        jeżeli self.parent jest Nic:
            zwróć Nic

        # Can't use index(); we need to test by identity
        dla i, child w enumerate(self.parent.children):
            jeżeli child jest self:
                jeżeli i == 0:
                    zwróć Nic
                zwróć self.parent.children[i-1]

    def leaves(self):
        dla child w self.children:
            uzyskaj z child.leaves()

    def depth(self):
        jeżeli self.parent jest Nic:
            zwróć 0
        zwróć 1 + self.parent.depth()

    def get_suffix(self):
        """
        Return the string immediately following the invocant node. This jest
        effectively equivalent to node.next_sibling.prefix
        """
        next_sib = self.next_sibling
        jeżeli next_sib jest Nic:
            zwróć ""
        zwróć next_sib.prefix

    jeżeli sys.version_info < (3, 0):
        def __str__(self):
            zwróć str(self).encode("ascii")

klasa Node(Base):

    """Concrete implementation dla interior nodes."""

    def __init__(self,type, children,
                 context=Nic,
                 prefix=Nic,
                 fixers_applied=Nic):
        """
        Initializer.

        Takes a type constant (a symbol number >= 256), a sequence of
        child nodes, oraz an optional context keyword argument.

        As a side effect, the parent pointers of the children are updated.
        """
        assert type >= 256, type
        self.type = type
        self.children = list(children)
        dla ch w self.children:
            assert ch.parent jest Nic, repr(ch)
            ch.parent = self
        jeżeli prefix jest nie Nic:
            self.prefix = prefix
        jeżeli fixers_applied:
            self.fixers_applied = fixers_applied[:]
        inaczej:
            self.fixers_applied = Nic

    def __repr__(self):
        """Return a canonical string representation."""
        zwróć "%s(%s, %r)" % (self.__class__.__name__,
                               type_repr(self.type),
                               self.children)

    def __unicode__(self):
        """
        Return a pretty string representation.

        This reproduces the input source exactly.
        """
        zwróć "".join(map(str, self.children))

    jeżeli sys.version_info > (3, 0):
        __str__ = __unicode__

    def _eq(self, other):
        """Compare two nodes dla equality."""
        zwróć (self.type, self.children) == (other.type, other.children)

    def clone(self):
        """Return a cloned (deep) copy of self."""
        zwróć Node(self.type, [ch.clone() dla ch w self.children],
                    fixers_applied=self.fixers_applied)

    def post_order(self):
        """Return a post-order iterator dla the tree."""
        dla child w self.children:
            uzyskaj z child.post_order()
        uzyskaj self

    def pre_order(self):
        """Return a pre-order iterator dla the tree."""
        uzyskaj self
        dla child w self.children:
            uzyskaj z child.pre_order()

    def _prefix_getter(self):
        """
        The whitespace oraz comments preceding this node w the input.
        """
        jeżeli nie self.children:
            zwróć ""
        zwróć self.children[0].prefix

    def _prefix_setter(self, prefix):
        jeżeli self.children:
            self.children[0].prefix = prefix

    prefix = property(_prefix_getter, _prefix_setter)

    def set_child(self, i, child):
        """
        Equivalent to 'node.children[i] = child'. This method also sets the
        child's parent attribute appropriately.
        """
        child.parent = self
        self.children[i].parent = Nic
        self.children[i] = child
        self.changed()

    def insert_child(self, i, child):
        """
        Equivalent to 'node.children.insert(i, child)'. This method also sets
        the child's parent attribute appropriately.
        """
        child.parent = self
        self.children.insert(i, child)
        self.changed()

    def append_child(self, child):
        """
        Equivalent to 'node.children.append(child)'. This method also sets the
        child's parent attribute appropriately.
        """
        child.parent = self
        self.children.append(child)
        self.changed()


klasa Leaf(Base):

    """Concrete implementation dla leaf nodes."""

    # Default values dla instance variables
    _prefix = ""  # Whitespace oraz comments preceding this token w the input
    lineno = 0    # Line where this token starts w the input
    column = 0    # Column where this token tarts w the input

    def __init__(self, type, value,
                 context=Nic,
                 prefix=Nic,
                 fixers_applied=[]):
        """
        Initializer.

        Takes a type constant (a token number < 256), a string value, oraz an
        optional context keyword argument.
        """
        assert 0 <= type < 256, type
        jeżeli context jest nie Nic:
            self._prefix, (self.lineno, self.column) = context
        self.type = type
        self.value = value
        jeżeli prefix jest nie Nic:
            self._prefix = prefix
        self.fixers_applied = fixers_applied[:]

    def __repr__(self):
        """Return a canonical string representation."""
        zwróć "%s(%r, %r)" % (self.__class__.__name__,
                               self.type,
                               self.value)

    def __unicode__(self):
        """
        Return a pretty string representation.

        This reproduces the input source exactly.
        """
        zwróć self.prefix + str(self.value)

    jeżeli sys.version_info > (3, 0):
        __str__ = __unicode__

    def _eq(self, other):
        """Compare two nodes dla equality."""
        zwróć (self.type, self.value) == (other.type, other.value)

    def clone(self):
        """Return a cloned (deep) copy of self."""
        zwróć Leaf(self.type, self.value,
                    (self.prefix, (self.lineno, self.column)),
                    fixers_applied=self.fixers_applied)

    def leaves(self):
        uzyskaj self

    def post_order(self):
        """Return a post-order iterator dla the tree."""
        uzyskaj self

    def pre_order(self):
        """Return a pre-order iterator dla the tree."""
        uzyskaj self

    def _prefix_getter(self):
        """
        The whitespace oraz comments preceding this token w the input.
        """
        zwróć self._prefix

    def _prefix_setter(self, prefix):
        self.changed()
        self._prefix = prefix

    prefix = property(_prefix_getter, _prefix_setter)

def convert(gr, raw_node):
    """
    Convert raw node information to a Node albo Leaf instance.

    This jest dalejed to the parser driver which calls it whenever a reduction of a
    grammar rule produces a new complete node, so that the tree jest build
    strictly bottom-up.
    """
    type, value, context, children = raw_node
    jeżeli children albo type w gr.number2symbol:
        # If there's exactly one child, zwróć that child instead of
        # creating a new node.
        jeżeli len(children) == 1:
            zwróć children[0]
        zwróć Node(type, children, context=context)
    inaczej:
        zwróć Leaf(type, value, context=context)


klasa BasePattern(object):

    """
    A pattern jest a tree matching pattern.

    It looks dla a specific node type (token albo symbol), oraz
    optionally dla a specific content.

    This jest an abstract base class.  There are three concrete
    subclasses:

    - LeafPattern matches a single leaf node;
    - NodePattern matches a single node (usually non-leaf);
    - WildcardPattern matches a sequence of nodes of variable length.
    """

    # Defaults dla instance variables
    type = Nic     # Node type (token jeżeli < 256, symbol jeżeli >= 256)
    content = Nic  # Optional content matching pattern
    name = Nic     # Optional name used to store match w results dict

    def __new__(cls, *args, **kwds):
        """Constructor that prevents BasePattern z being instantiated."""
        assert cls jest nie BasePattern, "Cannot instantiate BasePattern"
        zwróć object.__new__(cls)

    def __repr__(self):
        args = [type_repr(self.type), self.content, self.name]
        dopóki args oraz args[-1] jest Nic:
            usuń args[-1]
        zwróć "%s(%s)" % (self.__class__.__name__, ", ".join(map(repr, args)))

    def optimize(self):
        """
        A subclass can define this jako a hook dla optimizations.

        Returns either self albo another node przy the same effect.
        """
        zwróć self

    def match(self, node, results=Nic):
        """
        Does this pattern exactly match a node?

        Returns Prawda jeżeli it matches, Nieprawda jeżeli not.

        If results jest nie Nic, it must be a dict which will be
        updated przy the nodes matching named subpatterns.

        Default implementation dla non-wildcard patterns.
        """
        jeżeli self.type jest nie Nic oraz node.type != self.type:
            zwróć Nieprawda
        jeżeli self.content jest nie Nic:
            r = Nic
            jeżeli results jest nie Nic:
                r = {}
            jeżeli nie self._submatch(node, r):
                zwróć Nieprawda
            jeżeli r:
                results.update(r)
        jeżeli results jest nie Nic oraz self.name:
            results[self.name] = node
        zwróć Prawda

    def match_seq(self, nodes, results=Nic):
        """
        Does this pattern exactly match a sequence of nodes?

        Default implementation dla non-wildcard patterns.
        """
        jeżeli len(nodes) != 1:
            zwróć Nieprawda
        zwróć self.match(nodes[0], results)

    def generate_matches(self, nodes):
        """
        Generator uzyskajing all matches dla this pattern.

        Default implementation dla non-wildcard patterns.
        """
        r = {}
        jeżeli nodes oraz self.match(nodes[0], r):
            uzyskaj 1, r


klasa LeafPattern(BasePattern):

    def __init__(self, type=Nic, content=Nic, name=Nic):
        """
        Initializer.  Takes optional type, content, oraz name.

        The type, jeżeli given must be a token type (< 256).  If nie given,
        this matches any *leaf* node; the content may still be required.

        The content, jeżeli given, must be a string.

        If a name jest given, the matching node jest stored w the results
        dict under that key.
        """
        jeżeli type jest nie Nic:
            assert 0 <= type < 256, type
        jeżeli content jest nie Nic:
            assert isinstance(content, str), repr(content)
        self.type = type
        self.content = content
        self.name = name

    def match(self, node, results=Nic):
        """Override match() to insist on a leaf node."""
        jeżeli nie isinstance(node, Leaf):
            zwróć Nieprawda
        zwróć BasePattern.match(self, node, results)

    def _submatch(self, node, results=Nic):
        """
        Match the pattern's content to the node's children.

        This assumes the node type matches oraz self.content jest nie Nic.

        Returns Prawda jeżeli it matches, Nieprawda jeżeli not.

        If results jest nie Nic, it must be a dict which will be
        updated przy the nodes matching named subpatterns.

        When returning Nieprawda, the results dict may still be updated.
        """
        zwróć self.content == node.value


klasa NodePattern(BasePattern):

    wildcards = Nieprawda

    def __init__(self, type=Nic, content=Nic, name=Nic):
        """
        Initializer.  Takes optional type, content, oraz name.

        The type, jeżeli given, must be a symbol type (>= 256).  If the
        type jest Nic this matches *any* single node (leaf albo not),
        wyjąwszy jeżeli content jest nie Nic, w which it only matches
        non-leaf nodes that also match the content pattern.

        The content, jeżeli nie Nic, must be a sequence of Patterns that
        must match the node's children exactly.  If the content jest
        given, the type must nie be Nic.

        If a name jest given, the matching node jest stored w the results
        dict under that key.
        """
        jeżeli type jest nie Nic:
            assert type >= 256, type
        jeżeli content jest nie Nic:
            assert nie isinstance(content, str), repr(content)
            content = list(content)
            dla i, item w enumerate(content):
                assert isinstance(item, BasePattern), (i, item)
                jeżeli isinstance(item, WildcardPattern):
                    self.wildcards = Prawda
        self.type = type
        self.content = content
        self.name = name

    def _submatch(self, node, results=Nic):
        """
        Match the pattern's content to the node's children.

        This assumes the node type matches oraz self.content jest nie Nic.

        Returns Prawda jeżeli it matches, Nieprawda jeżeli not.

        If results jest nie Nic, it must be a dict which will be
        updated przy the nodes matching named subpatterns.

        When returning Nieprawda, the results dict may still be updated.
        """
        jeżeli self.wildcards:
            dla c, r w generate_matches(self.content, node.children):
                jeżeli c == len(node.children):
                    jeżeli results jest nie Nic:
                        results.update(r)
                    zwróć Prawda
            zwróć Nieprawda
        jeżeli len(self.content) != len(node.children):
            zwróć Nieprawda
        dla subpattern, child w zip(self.content, node.children):
            jeżeli nie subpattern.match(child, results):
                zwróć Nieprawda
        zwróć Prawda


klasa WildcardPattern(BasePattern):

    """
    A wildcard pattern can match zero albo more nodes.

    This has all the flexibility needed to implement patterns like:

    .*      .+      .?      .{m,n}
    (a b c | d e | f)
    (...)*  (...)+  (...)?  (...){m,n}

    wyjąwszy it always uses non-greedy matching.
    """

    def __init__(self, content=Nic, min=0, max=HUGE, name=Nic):
        """
        Initializer.

        Args:
            content: optional sequence of subsequences of patterns;
                     jeżeli absent, matches one node;
                     jeżeli present, each subsequence jest an alternative [*]
            min: optional minimum number of times to match, default 0
            max: optional maximum number of times to match, default HUGE
            name: optional name assigned to this match

        [*] Thus, jeżeli content jest [[a, b, c], [d, e], [f, g, h]] this jest
            equivalent to (a b c | d e | f g h); jeżeli content jest Nic,
            this jest equivalent to '.' w regular expression terms.
            The min oraz max parameters work jako follows:
                min=0, max=maxint: .*
                min=1, max=maxint: .+
                min=0, max=1: .?
                min=1, max=1: .
            If content jest nie Nic, replace the dot przy the parenthesized
            list of alternatives, e.g. (a b c | d e | f g h)*
        """
        assert 0 <= min <= max <= HUGE, (min, max)
        jeżeli content jest nie Nic:
            content = tuple(map(tuple, content))  # Protect against alterations
            # Check sanity of alternatives
            assert len(content), repr(content)  # Can't have zero alternatives
            dla alt w content:
                assert len(alt), repr(alt) # Can have empty alternatives
        self.content = content
        self.min = min
        self.max = max
        self.name = name

    def optimize(self):
        """Optimize certain stacked wildcard patterns."""
        subpattern = Nic
        jeżeli (self.content jest nie Nic oraz
            len(self.content) == 1 oraz len(self.content[0]) == 1):
            subpattern = self.content[0][0]
        jeżeli self.min == 1 oraz self.max == 1:
            jeżeli self.content jest Nic:
                zwróć NodePattern(name=self.name)
            jeżeli subpattern jest nie Nic oraz  self.name == subpattern.name:
                zwróć subpattern.optimize()
        jeżeli (self.min <= 1 oraz isinstance(subpattern, WildcardPattern) oraz
            subpattern.min <= 1 oraz self.name == subpattern.name):
            zwróć WildcardPattern(subpattern.content,
                                   self.min*subpattern.min,
                                   self.max*subpattern.max,
                                   subpattern.name)
        zwróć self

    def match(self, node, results=Nic):
        """Does this pattern exactly match a node?"""
        zwróć self.match_seq([node], results)

    def match_seq(self, nodes, results=Nic):
        """Does this pattern exactly match a sequence of nodes?"""
        dla c, r w self.generate_matches(nodes):
            jeżeli c == len(nodes):
                jeżeli results jest nie Nic:
                    results.update(r)
                    jeżeli self.name:
                        results[self.name] = list(nodes)
                zwróć Prawda
        zwróć Nieprawda

    def generate_matches(self, nodes):
        """
        Generator uzyskajing matches dla a sequence of nodes.

        Args:
            nodes: sequence of nodes

        Yields:
            (count, results) tuples where:
            count: the match comprises nodes[:count];
            results: dict containing named submatches.
        """
        jeżeli self.content jest Nic:
            # Shortcut dla special case (see __init__.__doc__)
            dla count w range(self.min, 1 + min(len(nodes), self.max)):
                r = {}
                jeżeli self.name:
                    r[self.name] = nodes[:count]
                uzyskaj count, r
        albo_inaczej self.name == "bare_name":
            uzyskaj self._bare_name_matches(nodes)
        inaczej:
            # The reason dla this jest that hitting the recursion limit usually
            # results w some ugly messages about how RuntimeErrors are being
            # ignored. We only have to do this on CPython, though, because other
            # implementations don't have this nasty bug w the first place.
            jeżeli hasattr(sys, "getrefcount"):
                save_stderr = sys.stderr
                sys.stderr = StringIO()
            spróbuj:
                dla count, r w self._recursive_matches(nodes, 0):
                    jeżeli self.name:
                        r[self.name] = nodes[:count]
                    uzyskaj count, r
            wyjąwszy RuntimeError:
                # We fall back to the iterative pattern matching scheme jeżeli the recursive
                # scheme hits the recursion limit.
                dla count, r w self._iterative_matches(nodes):
                    jeżeli self.name:
                        r[self.name] = nodes[:count]
                    uzyskaj count, r
            w_końcu:
                jeżeli hasattr(sys, "getrefcount"):
                    sys.stderr = save_stderr

    def _iterative_matches(self, nodes):
        """Helper to iteratively uzyskaj the matches."""
        nodelen = len(nodes)
        jeżeli 0 >= self.min:
            uzyskaj 0, {}

        results = []
        # generate matches that use just one alt z self.content
        dla alt w self.content:
            dla c, r w generate_matches(alt, nodes):
                uzyskaj c, r
                results.append((c, r))

        # dla each match, iterate down the nodes
        dopóki results:
            new_results = []
            dla c0, r0 w results:
                # stop jeżeli the entire set of nodes has been matched
                jeżeli c0 < nodelen oraz c0 <= self.max:
                    dla alt w self.content:
                        dla c1, r1 w generate_matches(alt, nodes[c0:]):
                            jeżeli c1 > 0:
                                r = {}
                                r.update(r0)
                                r.update(r1)
                                uzyskaj c0 + c1, r
                                new_results.append((c0 + c1, r))
            results = new_results

    def _bare_name_matches(self, nodes):
        """Special optimized matcher dla bare_name."""
        count = 0
        r = {}
        done = Nieprawda
        max = len(nodes)
        dopóki nie done oraz count < max:
            done = Prawda
            dla leaf w self.content:
                jeżeli leaf[0].match(nodes[count], r):
                    count += 1
                    done = Nieprawda
                    przerwij
        r[self.name] = nodes[:count]
        zwróć count, r

    def _recursive_matches(self, nodes, count):
        """Helper to recursively uzyskaj the matches."""
        assert self.content jest nie Nic
        jeżeli count >= self.min:
            uzyskaj 0, {}
        jeżeli count < self.max:
            dla alt w self.content:
                dla c0, r0 w generate_matches(alt, nodes):
                    dla c1, r1 w self._recursive_matches(nodes[c0:], count+1):
                        r = {}
                        r.update(r0)
                        r.update(r1)
                        uzyskaj c0 + c1, r


klasa NegatedPattern(BasePattern):

    def __init__(self, content=Nic):
        """
        Initializer.

        The argument jest either a pattern albo Nic.  If it jest Nic, this
        only matches an empty sequence (effectively '$' w regex
        lingo).  If it jest nie Nic, this matches whenever the argument
        pattern doesn't have any matches.
        """
        jeżeli content jest nie Nic:
            assert isinstance(content, BasePattern), repr(content)
        self.content = content

    def match(self, node):
        # We never match a node w its entirety
        zwróć Nieprawda

    def match_seq(self, nodes):
        # We only match an empty sequence of nodes w its entirety
        zwróć len(nodes) == 0

    def generate_matches(self, nodes):
        jeżeli self.content jest Nic:
            # Return a match jeżeli there jest an empty sequence
            jeżeli len(nodes) == 0:
                uzyskaj 0, {}
        inaczej:
            # Return a match jeżeli the argument pattern has no matches
            dla c, r w self.content.generate_matches(nodes):
                zwróć
            uzyskaj 0, {}


def generate_matches(patterns, nodes):
    """
    Generator uzyskajing matches dla a sequence of patterns oraz nodes.

    Args:
        patterns: a sequence of patterns
        nodes: a sequence of nodes

    Yields:
        (count, results) tuples where:
        count: the entire sequence of patterns matches nodes[:count];
        results: dict containing named submatches.
        """
    jeżeli nie patterns:
        uzyskaj 0, {}
    inaczej:
        p, rest = patterns[0], patterns[1:]
        dla c0, r0 w p.generate_matches(nodes):
            jeżeli nie rest:
                uzyskaj c0, r0
            inaczej:
                dla c1, r1 w generate_matches(rest, nodes[c0:]):
                    r = {}
                    r.update(r0)
                    r.update(r1)
                    uzyskaj c0 + c1, r
