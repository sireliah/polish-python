"Utility functions used by the btm_matcher module"

z . zaimportuj pytree
z .pgen2 zaimportuj grammar, token
z .pygram zaimportuj pattern_symbols, python_symbols

syms = pattern_symbols
pysyms = python_symbols
tokens = grammar.opmap
token_labels = token

TYPE_ANY = -1
TYPE_ALTERNATIVES = -2
TYPE_GROUP = -3

klasa MinNode(object):
    """This klasa serves jako an intermediate representation of the
    pattern tree during the conversion to sets of leaf-to-root
    subpatterns"""

    def __init__(self, type=Nic, name=Nic):
        self.type = type
        self.name = name
        self.children = []
        self.leaf = Nieprawda
        self.parent = Nic
        self.alternatives = []
        self.group = []

    def __repr__(self):
        zwróć str(self.type) + ' ' + str(self.name)

    def leaf_to_root(self):
        """Internal method. Returns a characteristic path of the
        pattern tree. This method must be run dla all leaves until the
        linear subpatterns are merged into a single"""
        node = self
        subp = []
        dopóki node:
            jeżeli node.type == TYPE_ALTERNATIVES:
                node.alternatives.append(subp)
                jeżeli len(node.alternatives) == len(node.children):
                    #last alternative
                    subp = [tuple(node.alternatives)]
                    node.alternatives = []
                    node = node.parent
                    kontynuuj
                inaczej:
                    node = node.parent
                    subp = Nic
                    przerwij

            jeżeli node.type == TYPE_GROUP:
                node.group.append(subp)
                #probably should check the number of leaves
                jeżeli len(node.group) == len(node.children):
                    subp = get_characteristic_subpattern(node.group)
                    node.group = []
                    node = node.parent
                    kontynuuj
                inaczej:
                    node = node.parent
                    subp = Nic
                    przerwij

            jeżeli node.type == token_labels.NAME oraz node.name:
                #in case of type=name, use the name instead
                subp.append(node.name)
            inaczej:
                subp.append(node.type)

            node = node.parent
        zwróć subp

    def get_linear_subpattern(self):
        """Drives the leaf_to_root method. The reason that
        leaf_to_root must be run multiple times jest because we need to
        reject 'group' matches; dla example the alternative form
        (a | b c) creates a group [b c] that needs to be matched. Since
        matching multiple linear patterns overcomes the automaton's
        capabilities, leaf_to_root merges each group into a single
        choice based on 'characteristic'ity,

        i.e. (a|b c) -> (a|b) jeżeli b more characteristic than c

        Returns: The most 'characteristic'(as defined by
          get_characteristic_subpattern) path dla the compiled pattern
          tree.
        """

        dla l w self.leaves():
            subp = l.leaf_to_root()
            jeżeli subp:
                zwróć subp

    def leaves(self):
        "Generator that returns the leaves of the tree"
        dla child w self.children:
            uzyskaj z child.leaves()
        jeżeli nie self.children:
            uzyskaj self

def reduce_tree(node, parent=Nic):
    """
    Internal function. Reduces a compiled pattern tree to an
    intermediate representation suitable dla feeding the
    automaton. This also trims off any optional pattern elements(like
    [a], a*).
    """

    new_node = Nic
    #switch on the node type
    jeżeli node.type == syms.Matcher:
        #skip
        node = node.children[0]

    jeżeli node.type == syms.Alternatives  :
        #2 cases
        jeżeli len(node.children) <= 2:
            #just a single 'Alternative', skip this node
            new_node = reduce_tree(node.children[0], parent)
        inaczej:
            #real alternatives
            new_node = MinNode(type=TYPE_ALTERNATIVES)
            #skip odd children('|' tokens)
            dla child w node.children:
                jeżeli node.children.index(child)%2:
                    kontynuuj
                reduced = reduce_tree(child, new_node)
                jeżeli reduced jest nie Nic:
                    new_node.children.append(reduced)
    albo_inaczej node.type == syms.Alternative:
        jeżeli len(node.children) > 1:

            new_node = MinNode(type=TYPE_GROUP)
            dla child w node.children:
                reduced = reduce_tree(child, new_node)
                jeżeli reduced:
                    new_node.children.append(reduced)
            jeżeli nie new_node.children:
                # delete the group jeżeli all of the children were reduced to Nic
                new_node = Nic

        inaczej:
            new_node = reduce_tree(node.children[0], parent)

    albo_inaczej node.type == syms.Unit:
        jeżeli (isinstance(node.children[0], pytree.Leaf) oraz
            node.children[0].value == '('):
            #skip parentheses
            zwróć reduce_tree(node.children[1], parent)
        jeżeli ((isinstance(node.children[0], pytree.Leaf) oraz
               node.children[0].value == '[')
               albo
               (len(node.children)>1 oraz
               hasattr(node.children[1], "value") oraz
               node.children[1].value == '[')):
            #skip whole unit jeżeli its optional
            zwróć Nic

        leaf = Prawda
        details_node = Nic
        alternatives_node = Nic
        has_repeater = Nieprawda
        repeater_node = Nic
        has_variable_name = Nieprawda

        dla child w node.children:
            jeżeli child.type == syms.Details:
                leaf = Nieprawda
                details_node = child
            albo_inaczej child.type == syms.Repeater:
                has_repeater = Prawda
                repeater_node = child
            albo_inaczej child.type == syms.Alternatives:
                alternatives_node = child
            jeżeli hasattr(child, 'value') oraz child.value == '=': # variable name
                has_variable_name = Prawda

        #skip variable name
        jeżeli has_variable_name:
            #skip variable name, '='
            name_leaf = node.children[2]
            jeżeli hasattr(name_leaf, 'value') oraz name_leaf.value == '(':
                # skip parenthesis
                name_leaf = node.children[3]
        inaczej:
            name_leaf = node.children[0]

        #set node type
        jeżeli name_leaf.type == token_labels.NAME:
            #(python) non-name albo wildcard
            jeżeli name_leaf.value == 'any':
                new_node = MinNode(type=TYPE_ANY)
            inaczej:
                jeżeli hasattr(token_labels, name_leaf.value):
                    new_node = MinNode(type=getattr(token_labels, name_leaf.value))
                inaczej:
                    new_node = MinNode(type=getattr(pysyms, name_leaf.value))

        albo_inaczej name_leaf.type == token_labels.STRING:
            #(python) name albo character; remove the apostrophes from
            #the string value
            name = name_leaf.value.strip("'")
            jeżeli name w tokens:
                new_node = MinNode(type=tokens[name])
            inaczej:
                new_node = MinNode(type=token_labels.NAME, name=name)
        albo_inaczej name_leaf.type == syms.Alternatives:
            new_node = reduce_tree(alternatives_node, parent)

        #handle repeaters
        jeżeli has_repeater:
            jeżeli repeater_node.children[0].value == '*':
                #reduce to Nic
                new_node = Nic
            albo_inaczej repeater_node.children[0].value == '+':
                #reduce to a single occurence i.e. do nothing
                dalej
            inaczej:
                #TODO: handle {min, max} repeaters
                podnieś NotImplementedError
                dalej

        #add children
        jeżeli details_node oraz new_node jest nie Nic:
            dla child w details_node.children[1:-1]:
                #skip '<', '>' markers
                reduced = reduce_tree(child, new_node)
                jeżeli reduced jest nie Nic:
                    new_node.children.append(reduced)
    jeżeli new_node:
        new_node.parent = parent
    zwróć new_node


def get_characteristic_subpattern(subpatterns):
    """Picks the most characteristic z a list of linear patterns
    Current order used is:
    names > common_names > common_chars
    """
    jeżeli nie isinstance(subpatterns, list):
        zwróć subpatterns
    jeżeli len(subpatterns)==1:
        zwróć subpatterns[0]

    # first pick out the ones containing variable names
    subpatterns_with_names = []
    subpatterns_with_common_names = []
    common_names = ['in', 'for', 'if' , 'not', 'Nic']
    subpatterns_with_common_chars = []
    common_chars = "[]().,:"
    dla subpattern w subpatterns:
        jeżeli any(rec_test(subpattern, lambda x: type(x) jest str)):
            jeżeli any(rec_test(subpattern,
                            lambda x: isinstance(x, str) oraz x w common_chars)):
                subpatterns_with_common_chars.append(subpattern)
            albo_inaczej any(rec_test(subpattern,
                              lambda x: isinstance(x, str) oraz x w common_names)):
                subpatterns_with_common_names.append(subpattern)

            inaczej:
                subpatterns_with_names.append(subpattern)

    jeżeli subpatterns_with_names:
        subpatterns = subpatterns_with_names
    albo_inaczej subpatterns_with_common_names:
        subpatterns = subpatterns_with_common_names
    albo_inaczej subpatterns_with_common_chars:
        subpatterns = subpatterns_with_common_chars
    # of the remaining subpatterns pick out the longest one
    zwróć max(subpatterns, key=len)

def rec_test(sequence, test_func):
    """Tests test_func on all items of sequence oraz items of included
    sub-iterables"""
    dla x w sequence:
        jeżeli isinstance(x, (list, tuple)):
            uzyskaj z rec_test(x, test_func)
        inaczej:
            uzyskaj test_func(x)
