"""Registration facilities dla DOM. This module should nie be used
directly. Instead, the functions getDOMImplementation oraz
registerDOMImplementation should be imported z xml.dom."""

# This jest a list of well-known implementations.  Well-known names
# should be published by posting to xml-sig@python.org, oraz are
# subsequently recorded w this file.

well_known_implementations = {
    'minidom':'xml.dom.minidom',
    '4DOM': 'xml.dom.DOMImplementation',
    }

# DOM implementations nie officially registered should register
# themselves przy their

registered = {}

def registerDOMImplementation(name, factory):
    """registerDOMImplementation(name, factory)

    Register the factory function przy the name. The factory function
    should zwróć an object which implements the DOMImplementation
    interface. The factory function can either zwróć the same object,
    albo a new one (e.g. jeżeli that implementation supports some
    customization)."""

    registered[name] = factory

def _good_enough(dom, features):
    "_good_enough(dom, features) -> Return 1 jeżeli the dom offers the features"
    dla f,v w features:
        jeżeli nie dom.hasFeature(f,v):
            zwróć 0
    zwróć 1

def getDOMImplementation(name=Nic, features=()):
    """getDOMImplementation(name = Nic, features = ()) -> DOM implementation.

    Return a suitable DOM implementation. The name jest either
    well-known, the module name of a DOM implementation, albo Nic. If
    it jest nie Nic, imports the corresponding module oraz returns
    DOMImplementation object jeżeli the zaimportuj succeeds.

    If name jest nie given, consider the available implementations to
    find one przy the required feature set. If no implementation can
    be found, podnieś an ImportError. The features list must be a sequence
    of (feature, version) pairs which are dalejed to hasFeature."""

    zaimportuj os
    creator = Nic
    mod = well_known_implementations.get(name)
    jeżeli mod:
        mod = __import__(mod, {}, {}, ['getDOMImplementation'])
        zwróć mod.getDOMImplementation()
    albo_inaczej name:
        zwróć registered[name]()
    albo_inaczej "PYTHON_DOM" w os.environ:
        zwróć getDOMImplementation(name = os.environ["PYTHON_DOM"])

    # User did nie specify a name, try implementations w arbitrary
    # order, returning the one that has the required features
    jeżeli isinstance(features, str):
        features = _parse_feature_string(features)
    dla creator w registered.values():
        dom = creator()
        jeżeli _good_enough(dom, features):
            zwróć dom

    dla creator w well_known_implementations.keys():
        spróbuj:
            dom = getDOMImplementation(name = creator)
        wyjąwszy Exception: # typically ImportError, albo AttributeError
            kontynuuj
        jeżeli _good_enough(dom, features):
            zwróć dom

    podnieś ImportError("no suitable DOM implementation found")

def _parse_feature_string(s):
    features = []
    parts = s.split()
    i = 0
    length = len(parts)
    dopóki i < length:
        feature = parts[i]
        jeżeli feature[0] w "0123456789":
            podnieś ValueError("bad feature name: %r" % (feature,))
        i = i + 1
        version = Nic
        jeżeli i < length:
            v = parts[i]
            jeżeli v[0] w "0123456789":
                i = i + 1
                version = v
        features.append((feature, version))
    zwróć tuple(features)
