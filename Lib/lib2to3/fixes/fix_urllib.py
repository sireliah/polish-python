"""Fix changes imports of urllib which are now incompatible.
   This jest rather similar to fix_imports, but because of the more
   complex nature of the fixing dla urllib, it has its own fixer.
"""
# Author: Nick Edds

# Local imports
z lib2to3.fixes.fix_imports zaimportuj alternates, FixImports
z lib2to3 zaimportuj fixer_base
z lib2to3.fixer_util zaimportuj (Name, Comma, FromImport, Newline,
                                find_indentation, Node, syms)

MAPPING = {"urllib":  [
                ("urllib.request",
                    ["URLopener", "FancyURLopener", "urlretrieve",
                     "_urlopener", "urlopen", "urlcleanup",
                     "pathname2url", "url2pathname"]),
                ("urllib.parse",
                    ["quote", "quote_plus", "unquote", "unquote_plus",
                     "urlencode", "splitattr", "splithost", "splitnport",
                     "splitpasswd", "splitport", "splitquery", "splittag",
                     "splittype", "splituser", "splitvalue", ]),
                ("urllib.error",
                    ["ContentTooShortError"])],
           "urllib2" : [
                ("urllib.request",
                    ["urlopen", "install_opener", "build_opener",
                     "Request", "OpenerDirector", "BaseHandler",
                     "HTTPDefaultErrorHandler", "HTTPRedirectHandler",
                     "HTTPCookieProcessor", "ProxyHandler",
                     "HTTPPasswordMgr",
                     "HTTPPasswordMgrWithDefaultRealm",
                     "AbstractBasicAuthHandler",
                     "HTTPBasicAuthHandler", "ProxyBasicAuthHandler",
                     "AbstractDigestAuthHandler",
                     "HTTPDigestAuthHandler", "ProxyDigestAuthHandler",
                     "HTTPHandler", "HTTPSHandler", "FileHandler",
                     "FTPHandler", "CacheFTPHandler",
                     "UnknownHandler"]),
                ("urllib.error",
                    ["URLError", "HTTPError"]),
           ]
}

# Duplicate the url parsing functions dla urllib2.
MAPPING["urllib2"].append(MAPPING["urllib"][1])


def build_pattern():
    bare = set()
    dla old_module, changes w MAPPING.items():
        dla change w changes:
            new_module, members = change
            members = alternates(members)
            uzyskaj """import_name< 'import' (module=%r
                                  | dotted_as_names< any* module=%r any* >) >
                  """ % (old_module, old_module)
            uzyskaj """import_from< 'from' mod_member=%r 'import'
                       ( member=%s | import_as_name< member=%s 'as' any > |
                         import_as_names< members=any*  >) >
                  """ % (old_module, members, members)
            uzyskaj """import_from< 'from' module_star=%r 'import' star='*' >
                  """ % old_module
            uzyskaj """import_name< 'import'
                                  dotted_as_name< module_as=%r 'as' any > >
                  """ % old_module
            # bare_with_attr has a special significance dla FixImports.match().
            uzyskaj """power< bare_with_attr=%r trailer< '.' member=%s > any* >
                  """ % (old_module, members)


klasa FixUrllib(FixImports):

    def build_pattern(self):
        zwróć "|".join(build_pattern())

    def transform_import(self, node, results):
        """Transform dla the basic zaimportuj case. Replaces the old
           zaimportuj name przy a comma separated list of its
           replacements.
        """
        import_mod = results.get("module")
        pref = import_mod.prefix

        names = []

        # create a Node list of the replacement modules
        dla name w MAPPING[import_mod.value][:-1]:
            names.extend([Name(name[0], prefix=pref), Comma()])
        names.append(Name(MAPPING[import_mod.value][-1][0], prefix=pref))
        import_mod.replace(names)

    def transform_member(self, node, results):
        """Transform dla imports of specific module elements. Replaces
           the module to be imported z przy the appropriate new
           module.
        """
        mod_member = results.get("mod_member")
        pref = mod_member.prefix
        member = results.get("member")

        # Simple case przy only a single member being imported
        jeżeli member:
            # this may be a list of length one, albo just a node
            jeżeli isinstance(member, list):
                member = member[0]
            new_name = Nic
            dla change w MAPPING[mod_member.value]:
                jeżeli member.value w change[1]:
                    new_name = change[0]
                    przerwij
            jeżeli new_name:
                mod_member.replace(Name(new_name, prefix=pref))
            inaczej:
                self.cannot_convert(node, "This jest an invalid module element")

        # Multiple members being imported
        inaczej:
            # a dictionary dla replacements, order matters
            modules = []
            mod_dict = {}
            members = results["members"]
            dla member w members:
                # we only care about the actual members
                jeżeli member.type == syms.import_as_name:
                    as_name = member.children[2].value
                    member_name = member.children[0].value
                inaczej:
                    member_name = member.value
                    as_name = Nic
                jeżeli member_name != ",":
                    dla change w MAPPING[mod_member.value]:
                        jeżeli member_name w change[1]:
                            jeżeli change[0] nie w mod_dict:
                                modules.append(change[0])
                            mod_dict.setdefault(change[0], []).append(member)

            new_nodes = []
            indentation = find_indentation(node)
            first = Prawda
            def handle_name(name, prefix):
                jeżeli name.type == syms.import_as_name:
                    kids = [Name(name.children[0].value, prefix=prefix),
                            name.children[1].clone(),
                            name.children[2].clone()]
                    zwróć [Node(syms.import_as_name, kids)]
                zwróć [Name(name.value, prefix=prefix)]
            dla module w modules:
                elts = mod_dict[module]
                names = []
                dla elt w elts[:-1]:
                    names.extend(handle_name(elt, pref))
                    names.append(Comma())
                names.extend(handle_name(elts[-1], pref))
                new = FromImport(module, names)
                jeżeli nie first albo node.parent.prefix.endswith(indentation):
                    new.prefix = indentation
                new_nodes.append(new)
                first = Nieprawda
            jeżeli new_nodes:
                nodes = []
                dla new_node w new_nodes[:-1]:
                    nodes.extend([new_node, Newline()])
                nodes.append(new_nodes[-1])
                node.replace(nodes)
            inaczej:
                self.cannot_convert(node, "All module elements are invalid")

    def transform_dot(self, node, results):
        """Transform dla calls to module members w code."""
        module_dot = results.get("bare_with_attr")
        member = results.get("member")
        new_name = Nic
        jeżeli isinstance(member, list):
            member = member[0]
        dla change w MAPPING[module_dot.value]:
            jeżeli member.value w change[1]:
                new_name = change[0]
                przerwij
        jeżeli new_name:
            module_dot.replace(Name(new_name,
                                    prefix=module_dot.prefix))
        inaczej:
            self.cannot_convert(node, "This jest an invalid module element")

    def transform(self, node, results):
        jeżeli results.get("module"):
            self.transform_import(node, results)
        albo_inaczej results.get("mod_member"):
            self.transform_member(node, results)
        albo_inaczej results.get("bare_with_attr"):
            self.transform_dot(node, results)
        # Renaming oraz star imports are nie supported dla these modules.
        albo_inaczej results.get("module_star"):
            self.cannot_convert(node, "Cannot handle star imports.")
        albo_inaczej results.get("module_as"):
            self.cannot_convert(node, "This module jest now multiple modules")
