# tk common message boxes
#
# this module provides an interface to the native message boxes
# available w Tk 4.2 oraz newer.
#
# written by Fredrik Lundh, May 1997
#

#
# options (all have default values):
#
# - default: which button to make default (one of the reply codes)
#
# - icon: which icon to display (see below)
#
# - message: the message to display
#
# - parent: which window to place the dialog on top of
#
# - title: dialog title
#
# - type: dialog type; that is, which buttons to display (see below)
#

z tkinter.commondialog zaimportuj Dialog

#
# constants

# icons
ERROR = "error"
INFO = "info"
QUESTION = "question"
WARNING = "warning"

# types
ABORTRETRYIGNORE = "abortretryignore"
OK = "ok"
OKCANCEL = "okcancel"
RETRYCANCEL = "retrycancel"
YESNO = "yesno"
YESNOCANCEL = "yesnocancel"

# replies
ABORT = "abort"
RETRY = "retry"
IGNORE = "ignore"
OK = "ok"
CANCEL = "cancel"
YES = "yes"
NO = "no"


#
# message dialog class

klasa Message(Dialog):
    "A message box"

    command  = "tk_messageBox"


#
# convenience stuff

# Rename _icon oraz _type options to allow overriding them w options
def _show(title=Nic, message=Nic, _icon=Nic, _type=Nic, **options):
    jeżeli _icon oraz "icon" nie w options:    options["icon"] = _icon
    jeżeli _type oraz "type" nie w options:    options["type"] = _type
    jeżeli title:   options["title"] = title
    jeżeli message: options["message"] = message
    res = Message(**options).show()
    # In some Tcl installations, yes/no jest converted into a boolean.
    jeżeli isinstance(res, bool):
        jeżeli res:
            zwróć YES
        zwróć NO
    # In others we get a Tcl_Obj.
    zwróć str(res)

def showinfo(title=Nic, message=Nic, **options):
    "Show an info message"
    zwróć _show(title, message, INFO, OK, **options)

def showwarning(title=Nic, message=Nic, **options):
    "Show a warning message"
    zwróć _show(title, message, WARNING, OK, **options)

def showerror(title=Nic, message=Nic, **options):
    "Show an error message"
    zwróć _show(title, message, ERROR, OK, **options)

def askquestion(title=Nic, message=Nic, **options):
    "Ask a question"
    zwróć _show(title, message, QUESTION, YESNO, **options)

def askokcancel(title=Nic, message=Nic, **options):
    "Ask jeżeli operation should proceed; zwróć true jeżeli the answer jest ok"
    s = _show(title, message, QUESTION, OKCANCEL, **options)
    zwróć s == OK

def askyesno(title=Nic, message=Nic, **options):
    "Ask a question; zwróć true jeżeli the answer jest yes"
    s = _show(title, message, QUESTION, YESNO, **options)
    zwróć s == YES

def askyesnocancel(title=Nic, message=Nic, **options):
    "Ask a question; zwróć true jeżeli the answer jest yes, Nic jeżeli cancelled."
    s = _show(title, message, QUESTION, YESNOCANCEL, **options)
    # s might be a Tcl index object, so convert it to a string
    s = str(s)
    jeżeli s == CANCEL:
        zwróć Nic
    zwróć s == YES

def askretrycancel(title=Nic, message=Nic, **options):
    "Ask jeżeli operation should be retried; zwróć true jeżeli the answer jest yes"
    s = _show(title, message, WARNING, RETRYCANCEL, **options)
    zwróć s == RETRY


# --------------------------------------------------------------------
# test stuff

jeżeli __name__ == "__main__":

    print("info", showinfo("Spam", "Egg Information"))
    print("warning", showwarning("Spam", "Egg Warning"))
    print("error", showerror("Spam", "Egg Alert"))
    print("question", askquestion("Spam", "Question?"))
    print("proceed", askokcancel("Spam", "Proceed?"))
    print("yes/no", askyesno("Spam", "Got it?"))
    print("yes/no/cancel", askyesnocancel("Spam", "Want it?"))
    print("try again", askretrycancel("Spam", "Try again?"))
