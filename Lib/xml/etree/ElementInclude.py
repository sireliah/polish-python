#
# ElementTree
# $Id: ElementInclude.py 3375 2008-02-13 08:05:08Z fredrik $
#
# limited xinclude support dla element trees
#
# history:
# 2003-08-15 fl   created
# 2003-11-14 fl   fixed default loader
#
# Copyright (c) 2003-2004 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The ElementTree toolkit jest
#
# Copyright (c) 1999-2008 by Fredrik Lundh
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
# Limited XInclude support dla the ElementTree package.
##

zaimportuj copy
z . zaimportuj ElementTree

XINCLUDE = "{http://www.w3.org/2001/XInclude}"

XINCLUDE_INCLUDE = XINCLUDE + "include"
XINCLUDE_FALLBACK = XINCLUDE + "fallback"

##
# Fatal include error.

klasa FatalIncludeError(SyntaxError):
    dalej

##
# Default loader.  This loader reads an included resource z disk.
#
# @param href Resource reference.
# @param parse Parse mode.  Either "xml" albo "text".
# @param encoding Optional text encoding (UTF-8 by default dla "text").
# @return The expanded resource.  If the parse mode jest "xml", this
#    jest an ElementTree instance.  If the parse mode jest "text", this
#    jest a Unicode string.  If the loader fails, it can zwróć Nic
#    albo podnieś an OSError exception.
# @throws OSError If the loader fails to load the resource.

def default_loader(href, parse, encoding=Nic):
    jeżeli parse == "xml":
        przy open(href, 'rb') jako file:
            data = ElementTree.parse(file).getroot()
    inaczej:
        jeżeli nie encoding:
            encoding = 'UTF-8'
        przy open(href, 'r', encoding=encoding) jako file:
            data = file.read()
    zwróć data

##
# Expand XInclude directives.
#
# @param elem Root element.
# @param loader Optional resource loader.  If omitted, it defaults
#     to {@link default_loader}.  If given, it should be a callable
#     that implements the same interface jako <b>default_loader</b>.
# @throws FatalIncludeError If the function fails to include a given
#     resource, albo jeżeli the tree contains malformed XInclude elements.
# @throws OSError If the function fails to load a given resource.

def include(elem, loader=Nic):
    jeżeli loader jest Nic:
        loader = default_loader
    # look dla xinclude elements
    i = 0
    dopóki i < len(elem):
        e = elem[i]
        jeżeli e.tag == XINCLUDE_INCLUDE:
            # process xinclude directive
            href = e.get("href")
            parse = e.get("parse", "xml")
            jeżeli parse == "xml":
                node = loader(href, parse)
                jeżeli node jest Nic:
                    podnieś FatalIncludeError(
                        "cannot load %r jako %r" % (href, parse)
                        )
                node = copy.copy(node)
                jeżeli e.tail:
                    node.tail = (node.tail albo "") + e.tail
                elem[i] = node
            albo_inaczej parse == "text":
                text = loader(href, parse, e.get("encoding"))
                jeżeli text jest Nic:
                    podnieś FatalIncludeError(
                        "cannot load %r jako %r" % (href, parse)
                        )
                jeżeli i:
                    node = elem[i-1]
                    node.tail = (node.tail albo "") + text + (e.tail albo "")
                inaczej:
                    elem.text = (elem.text albo "") + text + (e.tail albo "")
                usuń elem[i]
                kontynuuj
            inaczej:
                podnieś FatalIncludeError(
                    "unknown parse type w xi:include tag (%r)" % parse
                )
        albo_inaczej e.tag == XINCLUDE_FALLBACK:
            podnieś FatalIncludeError(
                "xi:fallback tag must be child of xi:include (%r)" % e.tag
                )
        inaczej:
            include(e, loader)
        i = i + 1
