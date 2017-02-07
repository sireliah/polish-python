"""A bottom-up tree matching algorithm implementation meant to speed
up 2to3's matching process. After the tree patterns are reduced to
their rarest linear path, a linear Aho-Corasick automaton jest
created. The linear automaton traverses the linear paths z the
leaves to the root of the AST oraz returns a set of nodes dla further
matching. This reduces significantly the number of candidate nodes."""

__author__ = "George Boutsioukis <gboutsioukis@gmail.com>"

zaimportuj logging
zaimportuj itertools
z collections zaimportuj defaultdict

z . zaimportuj pytree
z .btm_utils zaimportuj reduce_tree

klasa BMNode(object):
    """Class dla a node of the Aho-Corasick automaton used w matching"""
    count = itertools.count()
    def __init__(self):
        self.transition_table = {}
        self.fixers = []
        self.id = next(BMNode.count)
        self.content = ''

klasa BottomMatcher(object):
    """The main matcher class. After instantiating the patterns should
    be added using the add_fixer method"""

    def __init__(self):
        self.match = set()
        self.root = BMNode()
        self.nodes = [self.root]
        self.fixers = []
        self.logger = logging.getLogger("RefactoringTool")

    def add_fixer(self, fixer):
        """Reduces a fixer's pattern tree to a linear path oraz adds it
        to the matcher(a common Aho-Corasick automaton). The fixer jest
        appended on the matching states oraz called when they are
        reached"""
        self.fixers.append(fixer)
        tree = reduce_tree(fixer.pattern_tree)
        linear = tree.get_linear_subpattern()
        match_nodes = self.add(linear, start=self.root)
        dla match_node w match_nodes:
            match_node.fixers.append(fixer)

    def add(self, pattern, start):
        "Recursively adds a linear pattern to the AC automaton"
        #print("adding pattern", pattern, "to", start)
        jeżeli nie pattern:
            #print("empty pattern")
            zwróć [start]
        jeżeli isinstance(pattern[0], tuple):
            #alternatives
            #print("alternatives")
            match_nodes = []
            dla alternative w pattern[0]:
                #add all alternatives, oraz add the rest of the pattern
                #to each end node
                end_nodes = self.add(alternative, start=start)
                dla end w end_nodes:
                    match_nodes.extend(self.add(pattern[1:], end))
            zwróć match_nodes
        inaczej:
            #single token
            #not last
            jeżeli pattern[0] nie w start.transition_table:
                #transition did nie exist, create new
                next_node = BMNode()
                start.transition_table[pattern[0]] = next_node
            inaczej:
                #transition exists already, follow
                next_node = start.transition_table[pattern[0]]

            jeżeli pattern[1:]:
                end_nodes = self.add(pattern[1:], start=next_node)
            inaczej:
                end_nodes = [next_node]
            zwróć end_nodes

    def run(self, leaves):
        """The main interface przy the bottom matcher. The tree jest
        traversed z the bottom using the constructed
        automaton. Nodes are only checked once jako the tree jest
        retraversed. When the automaton fails, we give it one more
        shot(in case the above tree matches jako a whole przy the
        rejected leaf), then we przerwij dla the next leaf. There jest the
        special case of multiple arguments(see code comments) where we
        recheck the nodes

        Args:
           The leaves of the AST tree to be matched

        Returns:
           A dictionary of node matches przy fixers jako the keys
        """
        current_ac_node = self.root
        results = defaultdict(list)
        dla leaf w leaves:
            current_ast_node = leaf
            dopóki current_ast_node:
                current_ast_node.was_checked = Prawda
                dla child w current_ast_node.children:
                    # multiple statements, recheck
                    jeżeli isinstance(child, pytree.Leaf) oraz child.value == ";":
                        current_ast_node.was_checked = Nieprawda
                        przerwij
                jeżeli current_ast_node.type == 1:
                    #name
                    node_token = current_ast_node.value
                inaczej:
                    node_token = current_ast_node.type

                jeżeli node_token w current_ac_node.transition_table:
                    #token matches
                    current_ac_node = current_ac_node.transition_table[node_token]
                    dla fixer w current_ac_node.fixers:
                        jeżeli nie fixer w results:
                            results[fixer] = []
                        results[fixer].append(current_ast_node)

                inaczej:
                    #matching failed, reset automaton
                    current_ac_node = self.root
                    jeżeli (current_ast_node.parent jest nie Nic
                        oraz current_ast_node.parent.was_checked):
                        #the rest of the tree upwards has been checked, next leaf
                        przerwij

                    #recheck the rejected node once z the root
                    jeżeli node_token w current_ac_node.transition_table:
                        #token matches
                        current_ac_node = current_ac_node.transition_table[node_token]
                        dla fixer w current_ac_node.fixers:
                            jeżeli nie fixer w results.keys():
                                results[fixer] = []
                            results[fixer].append(current_ast_node)

                current_ast_node = current_ast_node.parent
        zwróć results

    def print_ac(self):
        "Prints a graphviz diagram of the BM automaton(dla debugging)"
        print("digraph g{")
        def print_node(node):
            dla subnode_key w node.transition_table.keys():
                subnode = node.transition_table[subnode_key]
                print("%d -> %d [label=%s] //%s" %
                      (node.id, subnode.id, type_repr(subnode_key), str(subnode.fixers)))
                jeżeli subnode_key == 1:
                    print(subnode.content)
                print_node(subnode)
        print_node(self.root)
        print("}")

# taken z pytree.py dla debugging; only used by print_ac
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
