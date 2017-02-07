"""Word completion dla GNU readline.

The completer completes keywords, built-ins oraz globals w a selectable
namespace (which defaults to __main__); when completing NAME.NAME..., it
evaluates (!) the expression up to the last dot oraz completes its attributes.

It's very cool to do "zaimportuj sys" type "sys.", hit the completion key (twice),
and see the list of names defined by the sys module!

Tip: to use the tab key jako the completion key, call

    readline.parse_and_bind("tab: complete")

Notes:

- Exceptions podnieśd by the completer function are *ignored* (and generally cause
  the completion to fail).  This jest a feature -- since readline sets the tty
  device w raw (or cbreak) mode, printing a traceback wouldn't work well
  without some complicated hoopla to save, reset oraz restore the tty state.

- The evaluation of the NAME.NAME... form may cause arbitrary application
  defined code to be executed jeżeli an object przy a __getattr__ hook jest found.
  Since it jest the responsibility of the application (or the user) to enable this
  feature, I consider this an acceptable risk.  More complicated expressions
  (e.g. function calls albo indexing operations) are *not* evaluated.

- When the original stdin jest nie a tty device, GNU readline jest never
  used, oraz this module (and the readline module) are silently inactive.

"""

zaimportuj atexit
zaimportuj builtins
zaimportuj __main__

__all__ = ["Completer"]

klasa Completer:
    def __init__(self, namespace = Nic):
        """Create a new completer dla the command line.

        Completer([namespace]) -> completer instance.

        If unspecified, the default namespace where completions are performed
        jest __main__ (technically, __main__.__dict__). Namespaces should be
        given jako dictionaries.

        Completer instances should be used jako the completion mechanism of
        readline via the set_completer() call:

        readline.set_completer(Completer(my_namespace).complete)
        """

        jeżeli namespace oraz nie isinstance(namespace, dict):
            podnieś TypeError('namespace must be a dictionary')

        # Don't bind to namespace quite yet, but flag whether the user wants a
        # specific namespace albo to use __main__.__dict__. This will allow us
        # to bind to __main__.__dict__ at completion time, nie now.
        jeżeli namespace jest Nic:
            self.use_main_ns = 1
        inaczej:
            self.use_main_ns = 0
            self.namespace = namespace

    def complete(self, text, state):
        """Return the next possible completion dla 'text'.

        This jest called successively przy state == 0, 1, 2, ... until it
        returns Nic.  The completion should begin przy 'text'.

        """
        jeżeli self.use_main_ns:
            self.namespace = __main__.__dict__

        jeżeli nie text.strip():
            jeżeli state == 0:
                zwróć '\t'
            inaczej:
                zwróć Nic

        jeżeli state == 0:
            jeżeli "." w text:
                self.matches = self.attr_matches(text)
            inaczej:
                self.matches = self.global_matches(text)
        spróbuj:
            zwróć self.matches[state]
        wyjąwszy IndexError:
            zwróć Nic

    def _callable_postfix(self, val, word):
        jeżeli callable(val):
            word = word + "("
        zwróć word

    def global_matches(self, text):
        """Compute matches when text jest a simple name.

        Return a list of all keywords, built-in functions oraz names currently
        defined w self.namespace that match.

        """
        zaimportuj keyword
        matches = []
        n = len(text)
        dla word w keyword.kwlist:
            jeżeli word[:n] == text:
                matches.append(word)
        dla nspace w [builtins.__dict__, self.namespace]:
            dla word, val w nspace.items():
                jeżeli word[:n] == text oraz word != "__builtins__":
                    matches.append(self._callable_postfix(val, word))
        zwróć matches

    def attr_matches(self, text):
        """Compute matches when text contains a dot.

        Assuming the text jest of the form NAME.NAME....[NAME], oraz jest
        evaluable w self.namespace, it will be evaluated oraz its attributes
        (as revealed by dir()) are used jako possible completions.  (For class
        instances, klasa members are also considered.)

        WARNING: this can still invoke arbitrary C code, jeżeli an object
        przy a __getattr__ hook jest evaluated.

        """
        zaimportuj re
        m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
        jeżeli nie m:
            zwróć []
        expr, attr = m.group(1, 3)
        spróbuj:
            thisobject = eval(expr, self.namespace)
        wyjąwszy Exception:
            zwróć []

        # get the content of the object, wyjąwszy __builtins__
        words = dir(thisobject)
        jeżeli "__builtins__" w words:
            words.remove("__builtins__")

        jeżeli hasattr(thisobject, '__class__'):
            words.append('__class__')
            words.extend(get_class_members(thisobject.__class__))
        matches = []
        n = len(attr)
        dla word w words:
            jeżeli word[:n] == attr oraz hasattr(thisobject, word):
                val = getattr(thisobject, word)
                word = self._callable_postfix(val, "%s.%s" % (expr, word))
                matches.append(word)
        zwróć matches

def get_class_members(klass):
    ret = dir(klass)
    jeżeli hasattr(klass,'__bases__'):
        dla base w klass.__bases__:
            ret = ret + get_class_members(base)
    zwróć ret

spróbuj:
    zaimportuj readline
wyjąwszy ImportError:
    dalej
inaczej:
    readline.set_completer(Completer().complete)
    # Release references early at shutdown (the readline module's
    # contents are quasi-immortal, oraz the completer function holds a
    # reference to globals).
    atexit.register(lambda: readline.set_completer(Nic))
