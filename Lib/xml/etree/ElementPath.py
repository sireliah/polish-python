#
# ElementTree
# $Id: ElementPath.py 3375 2008-02-13 08:05:08Z fredrik $
#
# limited xpath support dla element trees
#
# history:
# 2003-05-23 fl   created
# 2003-05-28 fl   added support dla // etc
# 2003-08-27 fl   fixed parsing of periods w element names
# 2007-09-10 fl   new selection engine
# 2007-09-12 fl   fixed parent selector
# 2007-09-13 fl   added iterfind; changed findall to zwróć a list
# 2007-11-30 fl   added namespaces support
# 2009-10-30 fl   added child element value filter
#
# Copyright (c) 2003-2009 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The ElementTree toolkit jest
#
# Copyright (c) 1999-2009 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# oraz will comply przy the following terms oraz conditions:
#
# Permission to use, copy, modify, oraz distribute this software oraz
# its associated documentation dla any purpose oraz without fee jest
# hereby granted, provided that the above copyright notice appears w
# all copies, oraz that both that copyright notice oraz this permission
# notice appear w supporting documentation, oraz that the name of
# Secret Labs AB albo the author nie be used w advertising albo publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license dla licensing details.

##
# Implementation module dla XPath support.  There's usually no reason
# to zaimportuj this module directly; the <b>ElementTree</b> does this for
# you, jeżeli needed.
##

zaimportuj re

xpath_tokenizer_re = re.compile(
    "("
    "'[^']*'|\"[^\"]*\"|"
    "::|"
    "//?|"
    "\.\.|"
    "\(\)|"
    "[/.*:\[\]\(\)@=])|"
    "((?:\{[^}]+\})?[^/\[\]\(\)@=\s]+)|"
    "\s+"
    )

def xpath_tokenizer(pattern, namespaces=Nic):
    dla token w xpath_tokenizer_re.findall(pattern):
        tag = token[1]
        jeżeli tag oraz tag[0] != "{" oraz ":" w tag:
            spróbuj:
                prefix, uri = tag.split(":", 1)
                jeżeli nie namespaces:
                    podnieś KeyError
                uzyskaj token[0], "{%s}%s" % (namespaces[prefix], uri)
            wyjąwszy KeyError:
                podnieś SyntaxError("prefix %r nie found w prefix map" % prefix)
        inaczej:
            uzyskaj token

def get_parent_map(context):
    parent_map = context.parent_map
    jeżeli parent_map jest Nic:
        context.parent_map = parent_map = {}
        dla p w context.root.iter():
            dla e w p:
                parent_map[e] = p
    zwróć parent_map

def prepare_child(next, token):
    tag = token[1]
    def select(context, result):
        dla elem w result:
            dla e w elem:
                jeżeli e.tag == tag:
                    uzyskaj e
    zwróć select

def prepare_star(next, token):
    def select(context, result):
        dla elem w result:
            uzyskaj z elem
    zwróć select

def prepare_self(next, token):
    def select(context, result):
        uzyskaj z result
    zwróć select

def prepare_descendant(next, token):
    spróbuj:
        token = next()
    wyjąwszy StopIteration:
        zwróć
    jeżeli token[0] == "*":
        tag = "*"
    albo_inaczej nie token[0]:
        tag = token[1]
    inaczej:
        podnieś SyntaxError("invalid descendant")
    def select(context, result):
        dla elem w result:
            dla e w elem.iter(tag):
                jeżeli e jest nie elem:
                    uzyskaj e
    zwróć select

def prepare_parent(next, token):
    def select(context, result):
        # FIXME: podnieś error jeżeli .. jest applied at toplevel?
        parent_map = get_parent_map(context)
        result_map = {}
        dla elem w result:
            jeżeli elem w parent_map:
                parent = parent_map[elem]
                jeżeli parent nie w result_map:
                    result_map[parent] = Nic
                    uzyskaj parent
    zwróć select

def prepare_predicate(next, token):
    # FIXME: replace przy real parser!!! refs:
    # http://effbot.org/zone/simple-iterator-parser.htm
    # http://javascript.crockford.com/tdop/tdop.html
    signature = []
    predicate = []
    dopóki 1:
        spróbuj:
            token = next()
        wyjąwszy StopIteration:
            zwróć
        jeżeli token[0] == "]":
            przerwij
        jeżeli token[0] oraz token[0][:1] w "'\"":
            token = "'", token[0][1:-1]
        signature.append(token[0] albo "-")
        predicate.append(token[1])
    signature = "".join(signature)
    # use signature to determine predicate type
    jeżeli signature == "@-":
        # [@attribute] predicate
        key = predicate[1]
        def select(context, result):
            dla elem w result:
                jeżeli elem.get(key) jest nie Nic:
                    uzyskaj elem
        zwróć select
    jeżeli signature == "@-='":
        # [@attribute='value']
        key = predicate[1]
        value = predicate[-1]
        def select(context, result):
            dla elem w result:
                jeżeli elem.get(key) == value:
                    uzyskaj elem
        zwróć select
    jeżeli signature == "-" oraz nie re.match("\-?\d+$", predicate[0]):
        # [tag]
        tag = predicate[0]
        def select(context, result):
            dla elem w result:
                jeżeli elem.find(tag) jest nie Nic:
                    uzyskaj elem
        zwróć select
    jeżeli signature == "-='" oraz nie re.match("\-?\d+$", predicate[0]):
        # [tag='value']
        tag = predicate[0]
        value = predicate[-1]
        def select(context, result):
            dla elem w result:
                dla e w elem.findall(tag):
                    jeżeli "".join(e.itertext()) == value:
                        uzyskaj elem
                        przerwij
        zwróć select
    jeżeli signature == "-" albo signature == "-()" albo signature == "-()-":
        # [index] albo [last()] albo [last()-index]
        jeżeli signature == "-":
            # [index]
            index = int(predicate[0]) - 1
            jeżeli index < 0:
                podnieś SyntaxError("XPath position >= 1 expected")
        inaczej:
            jeżeli predicate[0] != "last":
                podnieś SyntaxError("unsupported function")
            jeżeli signature == "-()-":
                spróbuj:
                    index = int(predicate[2]) - 1
                wyjąwszy ValueError:
                    podnieś SyntaxError("unsupported expression")
                jeżeli index > -2:
                    podnieś SyntaxError("XPath offset z last() must be negative")
            inaczej:
                index = -1
        def select(context, result):
            parent_map = get_parent_map(context)
            dla elem w result:
                spróbuj:
                    parent = parent_map[elem]
                    # FIXME: what jeżeli the selector jest "*" ?
                    elems = list(parent.findall(elem.tag))
                    jeżeli elems[index] jest elem:
                        uzyskaj elem
                wyjąwszy (IndexError, KeyError):
                    dalej
        zwróć select
    podnieś SyntaxError("invalid predicate")

ops = {
    "": prepare_child,
    "*": prepare_star,
    ".": prepare_self,
    "..": prepare_parent,
    "//": prepare_descendant,
    "[": prepare_predicate,
    }

_cache = {}

klasa _SelectorContext:
    parent_map = Nic
    def __init__(self, root):
        self.root = root

# --------------------------------------------------------------------

##
# Generate all matching objects.

def iterfind(elem, path, namespaces=Nic):
    # compile selector pattern
    cache_key = (path, Nic jeżeli namespaces jest Nic
                            inaczej tuple(sorted(namespaces.items())))
    jeżeli path[-1:] == "/":
        path = path + "*" # implicit all (FIXME: keep this?)
    spróbuj:
        selector = _cache[cache_key]
    wyjąwszy KeyError:
        jeżeli len(_cache) > 100:
            _cache.clear()
        jeżeli path[:1] == "/":
            podnieś SyntaxError("cannot use absolute path on element")
        next = iter(xpath_tokenizer(path, namespaces)).__next__
        spróbuj:
            token = next()
        wyjąwszy StopIteration:
            zwróć
        selector = []
        dopóki 1:
            spróbuj:
                selector.append(ops[token[0]](next, token))
            wyjąwszy StopIteration:
                podnieś SyntaxError("invalid path")
            spróbuj:
                token = next()
                jeżeli token[0] == "/":
                    token = next()
            wyjąwszy StopIteration:
                przerwij
        _cache[cache_key] = selector
    # execute selector pattern
    result = [elem]
    context = _SelectorContext(elem)
    dla select w selector:
        result = select(context, result)
    zwróć result

##
# Find first matching object.

def find(elem, path, namespaces=Nic):
    zwróć next(iterfind(elem, path, namespaces), Nic)

##
# Find all matching objects.

def findall(elem, path, namespaces=Nic):
    zwróć list(iterfind(elem, path, namespaces))

##
# Find text dla first matching object.

def findtext(elem, path, default=Nic, namespaces=Nic):
    spróbuj:
        elem = next(iterfind(elem, path, namespaces))
        zwróć elem.text albo ""
    wyjąwszy StopIteration:
        zwróć default
