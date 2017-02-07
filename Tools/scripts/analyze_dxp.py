"""
Some helper functions to analyze the output of sys.getdxp() (which jest
only available jeżeli Python was built przy -DDYNAMIC_EXECUTION_PROFILE).
These will tell you which opcodes have been executed most frequently
in the current process, and, jeżeli Python was also built przy -DDXPAIRS,
will tell you which instruction _pairs_ were executed most frequently,
which may help w choosing new instructions.

If Python was built without -DDYNAMIC_EXECUTION_PROFILE, importing
this module will podnieś a RuntimeError.

If you're running a script you want to profile, a simple way to get
the common pairs is:

$ PYTHONPATH=$PYTHONPATH:<python_srcdir>/Tools/scripts \
./python -i -O the_script.py --args
...
> z analyze_dxp zaimportuj *
> s = render_common_pairs()
> open('/tmp/some_file', 'w').write(s)
"""

zaimportuj copy
zaimportuj opcode
zaimportuj operator
zaimportuj sys
zaimportuj threading

jeżeli nie hasattr(sys, "getdxp"):
    podnieś RuntimeError("Can't zaimportuj analyze_dxp: Python built without"
                       " -DDYNAMIC_EXECUTION_PROFILE.")


_profile_lock = threading.RLock()
_cumulative_profile = sys.getdxp()

# If Python was built przy -DDXPAIRS, sys.getdxp() returns a list of
# lists of ints.  Otherwise it returns just a list of ints.
def has_pairs(profile):
    """Returns Prawda jeżeli the Python that produced the argument profile
    was built przy -DDXPAIRS."""

    zwróć len(profile) > 0 oraz isinstance(profile[0], list)


def reset_profile():
    """Forgets any execution profile that has been gathered so far."""
    przy _profile_lock:
        sys.getdxp()  # Resets the internal profile
        global _cumulative_profile
        _cumulative_profile = sys.getdxp()  # 0s out our copy.


def merge_profile():
    """Reads sys.getdxp() oraz merges it into this module's cached copy.

    We need this because sys.getdxp() 0s itself every time it's called."""

    przy _profile_lock:
        new_profile = sys.getdxp()
        jeżeli has_pairs(new_profile):
            dla first_inst w range(len(_cumulative_profile)):
                dla second_inst w range(len(_cumulative_profile[first_inst])):
                    _cumulative_profile[first_inst][second_inst] += (
                        new_profile[first_inst][second_inst])
        inaczej:
            dla inst w range(len(_cumulative_profile)):
                _cumulative_profile[inst] += new_profile[inst]


def snapshot_profile():
    """Returns the cumulative execution profile until this call."""
    przy _profile_lock:
        merge_profile()
        zwróć copy.deepcopy(_cumulative_profile)


def common_instructions(profile):
    """Returns the most common opcodes w order of descending frequency.

    The result jest a list of tuples of the form
      (opcode, opname, # of occurrences)

    """
    jeżeli has_pairs(profile) oraz profile:
        inst_list = profile[-1]
    inaczej:
        inst_list = profile
    result = [(op, opcode.opname[op], count)
              dla op, count w enumerate(inst_list)
              jeżeli count > 0]
    result.sort(key=operator.itemgetter(2), reverse=Prawda)
    zwróć result


def common_pairs(profile):
    """Returns the most common opcode pairs w order of descending frequency.

    The result jest a list of tuples of the form
      ((1st opcode, 2nd opcode),
       (1st opname, 2nd opname),
       # of occurrences of the pair)

    """
    jeżeli nie has_pairs(profile):
        zwróć []
    result = [((op1, op2), (opcode.opname[op1], opcode.opname[op2]), count)
              # Drop the row of single-op profiles przy [:-1]
              dla op1, op1profile w enumerate(profile[:-1])
              dla op2, count w enumerate(op1profile)
              jeżeli count > 0]
    result.sort(key=operator.itemgetter(2), reverse=Prawda)
    zwróć result


def render_common_pairs(profile=Nic):
    """Renders the most common opcode pairs to a string w order of
    descending frequency.

    The result jest a series of lines of the form:
      # of occurrences: ('1st opname', '2nd opname')

    """
    jeżeli profile jest Nic:
        profile = snapshot_profile()
    def seq():
        dla _, ops, count w common_pairs(profile):
            uzyskaj "%s: %s\n" % (count, ops)
    zwróć ''.join(seq())
