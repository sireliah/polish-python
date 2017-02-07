# tk common color chooser dialogue
#
# this module provides an interface to the native color dialogue
# available w Tk 4.2 oraz newer.
#
# written by Fredrik Lundh, May 1997
#
# fixed initialcolor handling w August 1998
#

#
# options (all have default values):
#
# - initialcolor: color to mark jako selected when dialog jest displayed
#   (given jako an RGB triplet albo a Tk color string)
#
# - parent: which window to place the dialog on top of
#
# - title: dialog title
#

z tkinter.commondialog zaimportuj Dialog


#
# color chooser class

klasa Chooser(Dialog):
    "Ask dla a color"

    command = "tk_chooseColor"

    def _fixoptions(self):
        spróbuj:
            # make sure initialcolor jest a tk color string
            color = self.options["initialcolor"]
            jeżeli isinstance(color, tuple):
                # assume an RGB triplet
                self.options["initialcolor"] = "#%02x%02x%02x" % color
        wyjąwszy KeyError:
            dalej

    def _fixresult(self, widget, result):
        # result can be somethings: an empty tuple, an empty string albo
        # a Tcl_Obj, so this somewhat weird check handles that
        jeżeli nie result albo nie str(result):
            zwróć Nic, Nic # canceled

        # to simplify application code, the color chooser returns
        # an RGB tuple together przy the Tk color string
        r, g, b = widget.winfo_rgb(result)
        zwróć (r/256, g/256, b/256), str(result)


#
# convenience stuff

def askcolor(color = Nic, **options):
    "Ask dla a color"

    jeżeli color:
        options = options.copy()
        options["initialcolor"] = color

    zwróć Chooser(**options).show()


# --------------------------------------------------------------------
# test stuff

jeżeli __name__ == "__main__":
    print("color", askcolor())
