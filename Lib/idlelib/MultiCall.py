"""
MultiCall - a klasa which inherits its methods z a Tkinter widget (Text, for
example), but enables multiple calls of functions per virtual event - all
matching events will be called, nie only the most specific one. This jest done
by wrapping the event functions - event_add, event_delete oraz event_info.
MultiCall recognizes only a subset of legal event sequences. Sequences which
are nie recognized are treated by the original Tk handling mechanism. A
more-specific event will be called before a less-specific event.

The recognized sequences are complete one-event sequences (no emacs-style
Ctrl-X Ctrl-C, no shortcuts like <3>), dla all types of events.
Key/Button Press/Release events can have modifiers.
The recognized modifiers are Shift, Control, Option oraz Command dla Mac, oraz
Control, Alt, Shift, Meta/M dla other platforms.

For all events which were handled by MultiCall, a new member jest added to the
event instance dalejed to the binded functions - mc_type. This jest one of the
event type constants defined w this module (such jako MC_KEYPRESS).
For Key/Button events (which are handled by MultiCall oraz may receive
modifiers), another member jest added - mc_state. This member gives the state
of the recognized modifiers, jako a combination of the modifier constants
also defined w this module (dla example, MC_SHIFT).
Using these members jest absolutely portable.

The order by which events are called jest defined by these rules:
1. A more-specific event will be called before a less-specific event.
2. A recently-binded event will be called before a previously-binded event,
   unless this conflicts przy the first rule.
Each function will be called at most once dla each event.
"""

zaimportuj sys
zaimportuj re
zaimportuj tkinter

# the event type constants, which define the meaning of mc_type
MC_KEYPRESS=0; MC_KEYRELEASE=1; MC_BUTTONPRESS=2; MC_BUTTONRELEASE=3;
MC_ACTIVATE=4; MC_CIRCULATE=5; MC_COLORMAP=6; MC_CONFIGURE=7;
MC_DEACTIVATE=8; MC_DESTROY=9; MC_ENTER=10; MC_EXPOSE=11; MC_FOCUSIN=12;
MC_FOCUSOUT=13; MC_GRAVITY=14; MC_LEAVE=15; MC_MAP=16; MC_MOTION=17;
MC_MOUSEWHEEL=18; MC_PROPERTY=19; MC_REPARENT=20; MC_UNMAP=21; MC_VISIBILITY=22;
# the modifier state constants, which define the meaning of mc_state
MC_SHIFT = 1<<0; MC_CONTROL = 1<<2; MC_ALT = 1<<3; MC_META = 1<<5
MC_OPTION = 1<<6; MC_COMMAND = 1<<7

# define the list of modifiers, to be used w complex event types.
jeżeli sys.platform == "darwin":
    _modifiers = (("Shift",), ("Control",), ("Option",), ("Command",))
    _modifier_masks = (MC_SHIFT, MC_CONTROL, MC_OPTION, MC_COMMAND)
inaczej:
    _modifiers = (("Control",), ("Alt",), ("Shift",), ("Meta", "M"))
    _modifier_masks = (MC_CONTROL, MC_ALT, MC_SHIFT, MC_META)

# a dictionary to map a modifier name into its number
_modifier_names = dict([(name, number)
                         dla number w range(len(_modifiers))
                         dla name w _modifiers[number]])

# In 3.4, jeżeli no shell window jest ever open, the underlying Tk widget jest
# destroyed before .__del__ methods here are called.  The following
# jest used to selectively ignore shutdown exceptions to avoid
# 'Exception ignored' messages.  See http://bugs.python.org/issue20167
APPLICATION_GONE = "application has been destroyed"

# A binder jest a klasa which binds functions to one type of event. It has two
# methods: bind oraz unbind, which get a function oraz a parsed sequence, as
# returned by _parse_sequence(). There are two types of binders:
# _SimpleBinder handles event types przy no modifiers oraz no detail.
# No Python functions are called when no events are binded.
# _ComplexBinder handles event types przy modifiers oraz a detail.
# A Python function jest called each time an event jest generated.

klasa _SimpleBinder:
    def __init__(self, type, widget, widgetinst):
        self.type = type
        self.sequence = '<'+_types[type][0]+'>'
        self.widget = widget
        self.widgetinst = widgetinst
        self.bindedfuncs = []
        self.handlerid = Nic

    def bind(self, triplet, func):
        jeżeli nie self.handlerid:
            def handler(event, l = self.bindedfuncs, mc_type = self.type):
                event.mc_type = mc_type
                wascalled = {}
                dla i w range(len(l)-1, -1, -1):
                    func = l[i]
                    jeżeli func nie w wascalled:
                        wascalled[func] = Prawda
                        r = func(event)
                        jeżeli r:
                            zwróć r
            self.handlerid = self.widget.bind(self.widgetinst,
                                              self.sequence, handler)
        self.bindedfuncs.append(func)

    def unbind(self, triplet, func):
        self.bindedfuncs.remove(func)
        jeżeli nie self.bindedfuncs:
            self.widget.unbind(self.widgetinst, self.sequence, self.handlerid)
            self.handlerid = Nic

    def __del__(self):
        jeżeli self.handlerid:
            spróbuj:
                self.widget.unbind(self.widgetinst, self.sequence,
                        self.handlerid)
            wyjąwszy tkinter.TclError jako e:
                jeżeli nie APPLICATION_GONE w e.args[0]:
                    podnieś

# An int w range(1 << len(_modifiers)) represents a combination of modifiers
# (jeżeli the least significent bit jest on, _modifiers[0] jest on, oraz so on).
# _state_subsets gives dla each combination of modifiers, albo *state*,
# a list of the states which are a subset of it. This list jest ordered by the
# number of modifiers jest the state - the most specific state comes first.
_states = range(1 << len(_modifiers))
_state_names = [''.join(m[0]+'-'
                        dla i, m w enumerate(_modifiers)
                        jeżeli (1 << i) & s)
                dla s w _states]

def expand_substates(states):
    '''For each item of states zwróć a list containing all combinations of
    that item przy individual bits reset, sorted by the number of set bits.
    '''
    def nbits(n):
        "number of bits set w n base 2"
        nb = 0
        dopóki n:
            n, rem = divmod(n, 2)
            nb += rem
        zwróć nb
    statelist = []
    dla state w states:
        substates = list(set(state & x dla x w states))
        substates.sort(key=nbits, reverse=Prawda)
        statelist.append(substates)
    zwróć statelist

_state_subsets = expand_substates(_states)

# _state_codes gives dla each state, the portable code to be dalejed jako mc_state
_state_codes = []
dla s w _states:
    r = 0
    dla i w range(len(_modifiers)):
        jeżeli (1 << i) & s:
            r |= _modifier_masks[i]
    _state_codes.append(r)

klasa _ComplexBinder:
    # This klasa binds many functions, oraz only unbinds them when it jest deleted.
    # self.handlerids jest the list of seqs oraz ids of binded handler functions.
    # The binded functions sit w a dictionary of lists of lists, which maps
    # a detail (or Nic) oraz a state into a list of functions.
    # When a new detail jest discovered, handlers dla all the possible states
    # are binded.

    def __create_handler(self, lists, mc_type, mc_state):
        def handler(event, lists = lists,
                    mc_type = mc_type, mc_state = mc_state,
                    ishandlerrunning = self.ishandlerrunning,
                    doafterhandler = self.doafterhandler):
            ishandlerrunning[:] = [Prawda]
            event.mc_type = mc_type
            event.mc_state = mc_state
            wascalled = {}
            r = Nic
            dla l w lists:
                dla i w range(len(l)-1, -1, -1):
                    func = l[i]
                    jeżeli func nie w wascalled:
                        wascalled[func] = Prawda
                        r = l[i](event)
                        jeżeli r:
                            przerwij
                jeżeli r:
                    przerwij
            ishandlerrunning[:] = []
            # Call all functions w doafterhandler oraz remove them z list
            dla f w doafterhandler:
                f()
            doafterhandler[:] = []
            jeżeli r:
                zwróć r
        zwróć handler

    def __init__(self, type, widget, widgetinst):
        self.type = type
        self.typename = _types[type][0]
        self.widget = widget
        self.widgetinst = widgetinst
        self.bindedfuncs = {Nic: [[] dla s w _states]}
        self.handlerids = []
        # we don't want to change the lists of functions dopóki a handler jest
        # running - it will mess up the loop oraz anyway, we usually want the
        # change to happen z the next event. So we have a list of functions
        # dla the handler to run after it finishes calling the binded functions.
        # It calls them only once.
        # ishandlerrunning jest a list. An empty one means no, otherwise - yes.
        # this jest done so that it would be mutable.
        self.ishandlerrunning = []
        self.doafterhandler = []
        dla s w _states:
            lists = [self.bindedfuncs[Nic][i] dla i w _state_subsets[s]]
            handler = self.__create_handler(lists, type, _state_codes[s])
            seq = '<'+_state_names[s]+self.typename+'>'
            self.handlerids.append((seq, self.widget.bind(self.widgetinst,
                                                          seq, handler)))

    def bind(self, triplet, func):
        jeżeli triplet[2] nie w self.bindedfuncs:
            self.bindedfuncs[triplet[2]] = [[] dla s w _states]
            dla s w _states:
                lists = [ self.bindedfuncs[detail][i]
                          dla detail w (triplet[2], Nic)
                          dla i w _state_subsets[s]       ]
                handler = self.__create_handler(lists, self.type,
                                                _state_codes[s])
                seq = "<%s%s-%s>"% (_state_names[s], self.typename, triplet[2])
                self.handlerids.append((seq, self.widget.bind(self.widgetinst,
                                                              seq, handler)))
        doit = lambda: self.bindedfuncs[triplet[2]][triplet[0]].append(func)
        jeżeli nie self.ishandlerrunning:
            doit()
        inaczej:
            self.doafterhandler.append(doit)

    def unbind(self, triplet, func):
        doit = lambda: self.bindedfuncs[triplet[2]][triplet[0]].remove(func)
        jeżeli nie self.ishandlerrunning:
            doit()
        inaczej:
            self.doafterhandler.append(doit)

    def __del__(self):
        dla seq, id w self.handlerids:
            spróbuj:
                self.widget.unbind(self.widgetinst, seq, id)
            wyjąwszy tkinter.TclError jako e:
                jeżeli nie APPLICATION_GONE w e.args[0]:
                    podnieś

# define the list of event types to be handled by MultiEvent. the order jest
# compatible przy the definition of event type constants.
_types = (
    ("KeyPress", "Key"), ("KeyRelease",), ("ButtonPress", "Button"),
    ("ButtonRelease",), ("Activate",), ("Circulate",), ("Colormap",),
    ("Configure",), ("Deactivate",), ("Destroy",), ("Enter",), ("Expose",),
    ("FocusIn",), ("FocusOut",), ("Gravity",), ("Leave",), ("Map",),
    ("Motion",), ("MouseWheel",), ("Property",), ("Reparent",), ("Unmap",),
    ("Visibility",),
)

# which binder should be used dla every event type?
_binder_classes = (_ComplexBinder,) * 4 + (_SimpleBinder,) * (len(_types)-4)

# A dictionary to map a type name into its number
_type_names = dict([(name, number)
                     dla number w range(len(_types))
                     dla name w _types[number]])

_keysym_re = re.compile(r"^\w+$")
_button_re = re.compile(r"^[1-5]$")
def _parse_sequence(sequence):
    """Get a string which should describe an event sequence. If it jest
    successfully parsed jako one, zwróć a tuple containing the state (as an int),
    the event type (as an index of _types), oraz the detail - Nic jeżeli none, albo a
    string jeżeli there jest one. If the parsing jest unsuccessful, zwróć Nic.
    """
    jeżeli nie sequence albo sequence[0] != '<' albo sequence[-1] != '>':
        zwróć Nic
    words = sequence[1:-1].split('-')
    modifiers = 0
    dopóki words oraz words[0] w _modifier_names:
        modifiers |= 1 << _modifier_names[words[0]]
        usuń words[0]
    jeżeli words oraz words[0] w _type_names:
        type = _type_names[words[0]]
        usuń words[0]
    inaczej:
        zwróć Nic
    jeżeli _binder_classes[type] jest _SimpleBinder:
        jeżeli modifiers albo words:
            zwróć Nic
        inaczej:
            detail = Nic
    inaczej:
        # _ComplexBinder
        jeżeli type w [_type_names[s] dla s w ("KeyPress", "KeyRelease")]:
            type_re = _keysym_re
        inaczej:
            type_re = _button_re

        jeżeli nie words:
            detail = Nic
        albo_inaczej len(words) == 1 oraz type_re.match(words[0]):
            detail = words[0]
        inaczej:
            zwróć Nic

    zwróć modifiers, type, detail

def _triplet_to_sequence(triplet):
    jeżeli triplet[2]:
        zwróć '<'+_state_names[triplet[0]]+_types[triplet[1]][0]+'-'+ \
               triplet[2]+'>'
    inaczej:
        zwróć '<'+_state_names[triplet[0]]+_types[triplet[1]][0]+'>'

_multicall_dict = {}
def MultiCallCreator(widget):
    """Return a MultiCall klasa which inherits its methods z the
    given widget klasa (dla example, Tkinter.Text). This jest used
    instead of a templating mechanism.
    """
    jeżeli widget w _multicall_dict:
        zwróć _multicall_dict[widget]

    klasa MultiCall (widget):
        assert issubclass(widget, tkinter.Misc)

        def __init__(self, *args, **kwargs):
            widget.__init__(self, *args, **kwargs)
            # a dictionary which maps a virtual event to a tuple with:
            #  0. the function binded
            #  1. a list of triplets - the sequences it jest binded to
            self.__eventinfo = {}
            self.__binders = [_binder_classes[i](i, widget, self)
                              dla i w range(len(_types))]

        def bind(self, sequence=Nic, func=Nic, add=Nic):
            #print("bind(%s, %s, %s)" % (sequence, func, add),
            #      file=sys.__stderr__)
            jeżeli type(sequence) jest str oraz len(sequence) > 2 oraz \
               sequence[:2] == "<<" oraz sequence[-2:] == ">>":
                jeżeli sequence w self.__eventinfo:
                    ei = self.__eventinfo[sequence]
                    jeżeli ei[0] jest nie Nic:
                        dla triplet w ei[1]:
                            self.__binders[triplet[1]].unbind(triplet, ei[0])
                    ei[0] = func
                    jeżeli ei[0] jest nie Nic:
                        dla triplet w ei[1]:
                            self.__binders[triplet[1]].bind(triplet, func)
                inaczej:
                    self.__eventinfo[sequence] = [func, []]
            zwróć widget.bind(self, sequence, func, add)

        def unbind(self, sequence, funcid=Nic):
            jeżeli type(sequence) jest str oraz len(sequence) > 2 oraz \
               sequence[:2] == "<<" oraz sequence[-2:] == ">>" oraz \
               sequence w self.__eventinfo:
                func, triplets = self.__eventinfo[sequence]
                jeżeli func jest nie Nic:
                    dla triplet w triplets:
                        self.__binders[triplet[1]].unbind(triplet, func)
                    self.__eventinfo[sequence][0] = Nic
            zwróć widget.unbind(self, sequence, funcid)

        def event_add(self, virtual, *sequences):
            #print("event_add(%s, %s)" % (repr(virtual), repr(sequences)),
            #      file=sys.__stderr__)
            jeżeli virtual nie w self.__eventinfo:
                self.__eventinfo[virtual] = [Nic, []]

            func, triplets = self.__eventinfo[virtual]
            dla seq w sequences:
                triplet = _parse_sequence(seq)
                jeżeli triplet jest Nic:
                    #print("Tkinter event_add(%s)" % seq, file=sys.__stderr__)
                    widget.event_add(self, virtual, seq)
                inaczej:
                    jeżeli func jest nie Nic:
                        self.__binders[triplet[1]].bind(triplet, func)
                    triplets.append(triplet)

        def event_delete(self, virtual, *sequences):
            jeżeli virtual nie w self.__eventinfo:
                zwróć
            func, triplets = self.__eventinfo[virtual]
            dla seq w sequences:
                triplet = _parse_sequence(seq)
                jeżeli triplet jest Nic:
                    #print("Tkinter event_delete: %s" % seq, file=sys.__stderr__)
                    widget.event_delete(self, virtual, seq)
                inaczej:
                    jeżeli func jest nie Nic:
                        self.__binders[triplet[1]].unbind(triplet, func)
                    triplets.remove(triplet)

        def event_info(self, virtual=Nic):
            jeżeli virtual jest Nic albo virtual nie w self.__eventinfo:
                zwróć widget.event_info(self, virtual)
            inaczej:
                zwróć tuple(map(_triplet_to_sequence,
                                 self.__eventinfo[virtual][1])) + \
                       widget.event_info(self, virtual)

        def __del__(self):
            dla virtual w self.__eventinfo:
                func, triplets = self.__eventinfo[virtual]
                jeżeli func:
                    dla triplet w triplets:
                        spróbuj:
                            self.__binders[triplet[1]].unbind(triplet, func)
                        wyjąwszy tkinter.TclError jako e:
                            jeżeli nie APPLICATION_GONE w e.args[0]:
                                podnieś

    _multicall_dict[widget] = MultiCall
    zwróć MultiCall


def _multi_call(parent):
    root = tkinter.Tk()
    root.title("Test MultiCall")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    text = MultiCallCreator(tkinter.Text)(root)
    text.pack()
    def bindseq(seq, n=[0]):
        def handler(event):
            print(seq)
        text.bind("<<handler%d>>"%n[0], handler)
        text.event_add("<<handler%d>>"%n[0], seq)
        n[0] += 1
    bindseq("<Key>")
    bindseq("<Control-Key>")
    bindseq("<Alt-Key-a>")
    bindseq("<Control-Key-a>")
    bindseq("<Alt-Control-Key-a>")
    bindseq("<Key-b>")
    bindseq("<Control-Button-1>")
    bindseq("<Button-2>")
    bindseq("<Alt-Button-1>")
    bindseq("<FocusOut>")
    bindseq("<Enter>")
    bindseq("<Leave>")
    root.mainloop()

jeżeli __name__ == "__main__":
    z idlelib.idle_test.htest zaimportuj run
    run(_multi_call)
