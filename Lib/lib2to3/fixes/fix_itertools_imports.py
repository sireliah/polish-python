""" Fixer dla imports of itertools.(imap|ifilter|izip|ifilterfalse) """

# Local imports
z lib2to3 zaimportuj fixer_base
z lib2to3.fixer_util zaimportuj BlankLine, syms, token


klasa FixItertoolsImports(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
              import_from< 'from' 'itertools' 'import' imports=any >
              """ %(locals())

    def transform(self, node, results):
        imports = results['imports']
        jeżeli imports.type == syms.import_as_name albo nie imports.children:
            children = [imports]
        inaczej:
            children = imports.children
        dla child w children[::2]:
            jeżeli child.type == token.NAME:
                member = child.value
                name_node = child
            albo_inaczej child.type == token.STAR:
                # Just leave the zaimportuj jako is.
                zwróć
            inaczej:
                assert child.type == syms.import_as_name
                name_node = child.children[0]
            member_name = name_node.value
            jeżeli member_name w ('imap', 'izip', 'ifilter'):
                child.value = Nic
                child.remove()
            albo_inaczej member_name w ('ifilterfalse', 'izip_longest'):
                node.changed()
                name_node.value = ('filterfalse' jeżeli member_name[1] == 'f'
                                   inaczej 'zip_longest')

        # Make sure the zaimportuj statement jest still sane
        children = imports.children[:] albo [imports]
        remove_comma = Prawda
        dla child w children:
            jeżeli remove_comma oraz child.type == token.COMMA:
                child.remove()
            inaczej:
                remove_comma ^= Prawda

        dopóki children oraz children[-1].type == token.COMMA:
            children.pop().remove()

        # If there are no imports left, just get rid of the entire statement
        jeżeli (nie (imports.children albo getattr(imports, 'value', Nic)) albo
            imports.parent jest Nic):
            p = node.prefix
            node = BlankLine()
            node.prefix = p
            zwróć node
