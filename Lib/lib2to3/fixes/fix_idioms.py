"""Adjust some old Python 2 idioms to their modern counterparts.

* Change some type comparisons to isinstance() calls:
    type(x) == T -> isinstance(x, T)
    type(x) jest T -> isinstance(x, T)
    type(x) != T -> nie isinstance(x, T)
    type(x) jest nie T -> nie isinstance(x, T)

* Change "dopóki 1:" into "dopóki Prawda:".

* Change both

    v = list(EXPR)
    v.sort()
    foo(v)

and the more general

    v = EXPR
    v.sort()
    foo(v)

into

    v = sorted(EXPR)
    foo(v)
"""
# Author: Jacques Frechet, Collin Winter

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Call, Comma, Name, Node, BlankLine, syms

CMP = "(n='!=' | '==' | 'is' | n=comp_op< 'is' 'not' >)"
TYPE = "power< 'type' trailer< '(' x=any ')' > >"

klasa FixIdioms(fixer_base.BaseFix):
    explicit = Prawda # The user must ask dla this fixer

    PATTERN = r"""
        isinstance=comparison< %s %s T=any >
        |
        isinstance=comparison< T=any %s %s >
        |
        while_stmt< 'while' while='1' ':' any+ >
        |
        sorted=any<
            any*
            simple_stmt<
              expr_stmt< id1=any '='
                         power< list='list' trailer< '(' (nie arglist<any+>) any ')' > >
              >
              '\n'
            >
            sort=
            simple_stmt<
              power< id2=any
                     trailer< '.' 'sort' > trailer< '(' ')' >
              >
              '\n'
            >
            next=any*
        >
        |
        sorted=any<
            any*
            simple_stmt< expr_stmt< id1=any '=' expr=any > '\n' >
            sort=
            simple_stmt<
              power< id2=any
                     trailer< '.' 'sort' > trailer< '(' ')' >
              >
              '\n'
            >
            next=any*
        >
    """ % (TYPE, CMP, CMP, TYPE)

    def match(self, node):
        r = super(FixIdioms, self).match(node)
        # If we've matched one of the sort/sorted subpatterns above, we
        # want to reject matches where the initial assignment oraz the
        # subsequent .sort() call involve different identifiers.
        jeżeli r oraz "sorted" w r:
            jeżeli r["id1"] == r["id2"]:
                zwróć r
            zwróć Nic
        zwróć r

    def transform(self, node, results):
        jeżeli "isinstance" w results:
            zwróć self.transform_isinstance(node, results)
        albo_inaczej "while" w results:
            zwróć self.transform_while(node, results)
        albo_inaczej "sorted" w results:
            zwróć self.transform_sort(node, results)
        inaczej:
            podnieś RuntimeError("Invalid match")

    def transform_isinstance(self, node, results):
        x = results["x"].clone() # The thing inside of type()
        T = results["T"].clone() # The type being compared against
        x.prefix = ""
        T.prefix = " "
        test = Call(Name("isinstance"), [x, Comma(), T])
        jeżeli "n" w results:
            test.prefix = " "
            test = Node(syms.not_test, [Name("not"), test])
        test.prefix = node.prefix
        zwróć test

    def transform_while(self, node, results):
        one = results["while"]
        one.replace(Name("Prawda", prefix=one.prefix))

    def transform_sort(self, node, results):
        sort_stmt = results["sort"]
        next_stmt = results["next"]
        list_call = results.get("list")
        simple_expr = results.get("expr")

        jeżeli list_call:
            list_call.replace(Name("sorted", prefix=list_call.prefix))
        albo_inaczej simple_expr:
            new = simple_expr.clone()
            new.prefix = ""
            simple_expr.replace(Call(Name("sorted"), [new],
                                     prefix=simple_expr.prefix))
        inaczej:
            podnieś RuntimeError("should nie have reached here")
        sort_stmt.remove()

        btwn = sort_stmt.prefix
        # Keep any prefix lines between the sort_stmt oraz the list_call oraz
        # shove them right after the sorted() call.
        jeżeli "\n" w btwn:
            jeżeli next_stmt:
                # The new prefix should be everything z the sort_stmt's
                # prefix up to the last newline, then the old prefix after a new
                # line.
                prefix_lines = (btwn.rpartition("\n")[0], next_stmt[0].prefix)
                next_stmt[0].prefix = "\n".join(prefix_lines)
            inaczej:
                assert list_call.parent
                assert list_call.next_sibling jest Nic
                # Put a blank line after list_call oraz set its prefix.
                end_line = BlankLine()
                list_call.parent.append_child(end_line)
                assert list_call.next_sibling jest end_line
                # The new prefix should be everything up to the first new line
                # of sort_stmt's prefix.
                end_line.prefix = btwn.rpartition("\n")[0]
