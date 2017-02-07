'''Run human tests of Idle's window, dialog, oraz popup widgets.

run(*tests)
Create a master Tk window.  Within that, run each callable w tests
after finding the matching test spec w this file.  If tests jest empty,
run an htest dla each spec dict w this file after finding the matching
callable w the module named w the spec.  Close the window to skip albo
end the test.

In a tested module, let X be a global name bound to a callable (class
or function) whose .__name__ attrubute jest also X (the usual situation).
The first parameter of X must be 'parent'.  When called, the parent
argument will be the root window.  X must create a child Toplevel
window (or subclass thereof).  The Toplevel may be a test widget albo
dialog, w which case the callable jest the corresonding class.  Or the
Toplevel may contain the widget to be tested albo set up a context w
which a test widget jest invoked.  In this latter case, the callable jest a
wrapper function that sets up the Toplevel oraz other objects.  Wrapper
function names, such jako _editor_window', should start przy '_'.


End the module with

jeżeli __name__ == '__main__':
    <unittest, jeżeli there jest one>
    z idlelib.idle_test.htest zaimportuj run
    run(X)

To have wrapper functions oraz test invocation code ignored by coveragepy
reports, put '# htest #' on the def statement header line.

def _wrapper(parent):  # htest #

Also make sure that the 'jeżeli __name__' line matches the above.  Then have
make sure that .coveragerc includes the following.

[report]
exclude_lines =
    .*# htest #
    jeżeli __name__ == .__main__.:

(The "." instead of "'" jest intentional oraz necessary.)


To run any X, this file must contain a matching instance of the
following template, przy X.__name__ prepended to '_spec'.
When all tests are run, the prefix jest use to get X.

_spec = {
    'file': '',
    'kwds': {'title': ''},
    'msg': ""
    }

file (no .py): run() imports file.py.
kwds: augmented przy {'parent':root} oraz dalejed to X jako **kwds.
title: an example kwd; some widgets need this, delete jeżeli not.
msg: master window hints about testing the widget.


Modules oraz classes nie being tested at the moment:
PyShell.PyShellEditorWindow
Debugger.Debugger
AutoCompleteWindow.AutoCompleteWindow
OutputWindow.OutputWindow (indirectly being tested przy grep test)
'''

z importlib zaimportuj import_module
z idlelib.macosxSupport zaimportuj _initializeTkVariantTests
zaimportuj tkinter jako tk

AboutDialog_spec = {
    'file': 'aboutDialog',
    'kwds': {'title': 'aboutDialog test',
             '_htest': Prawda,
             },
    'msg': "Test every button. Ensure Python, TK oraz IDLE versions "
           "are correctly displayed.\n [Close] to exit.",
    }

_calltip_window_spec = {
    'file': 'CallTipWindow',
    'kwds': {},
    'msg': "Typing '(' should display a calltip.\n"
           "Typing ') should hide the calltip.\n"
    }

_class_browser_spec = {
    'file': 'ClassBrowser',
    'kwds': {},
    'msg': "Inspect names of module, class(przy superclass jeżeli "
           "applicable), methods oraz functions.\nToggle nested items.\n"
           "Double clicking on items prints a traceback dla an exception "
           "that jest ignored."
    }
ConfigExtensionsDialog_spec = {
    'file': 'configDialog',
    'kwds': {'title': 'Test Extension Configuration',
             '_htest': Prawda,},
    'msg': "IDLE extensions dialog.\n"
           "\n[Ok] to close the dialog.[Apply] to apply the settings oraz "
           "and [Cancel] to revert all changes.\nRe-run the test to ensure "
           "changes made have persisted."
    }

_color_delegator_spec = {
    'file': 'ColorDelegator',
    'kwds': {},
    'msg': "The text jest sample Python code.\n"
           "Ensure components like comments, keywords, builtins,\n"
           "string, definitions, oraz przerwij are correctly colored.\n"
           "The default color scheme jest w idlelib/config-highlight.def"
    }

ConfigDialog_spec = {
    'file': 'configDialog',
    'kwds': {'title': 'ConfigDialogTest',
             '_htest': Prawda,},
    'msg': "IDLE preferences dialog.\n"
           "In the 'Fonts/Tabs' tab, changing font face, should update the "
           "font face of the text w the area below it.\nIn the "
           "'Highlighting' tab, try different color schemes. Clicking "
           "items w the sample program should update the choices above it."
           "\nIn the 'Keys' oraz 'General' tab, test settings of interest."
           "\n[Ok] to close the dialog.[Apply] to apply the settings oraz "
           "and [Cancel] to revert all changes.\nRe-run the test to ensure "
           "changes made have persisted."
    }

# TODO Improve message
_dyn_option_menu_spec = {
    'file': 'dynOptionMenuWidget',
    'kwds': {},
    'msg': "Select one of the many options w the 'old option set'.\n"
           "Click the button to change the option set.\n"
           "Select one of the many options w the 'new option set'."
    }

# TODO edit wrapper
_editor_window_spec = {
   'file': 'EditorWindow',
    'kwds': {},
    'msg': "Test editor functions of interest.\n"
           "Best to close editor first."
    }

GetCfgSectionNameDialog_spec = {
    'file': 'configSectionNameDialog',
    'kwds': {'title':'Get Name',
             'message':'Enter something',
             'used_names': {'abc'},
             '_htest': Prawda},
    'msg': "After the text entered przy [Ok] jest stripped, <nothing>, "
           "'abc', albo more that 30 chars are errors.\n"
           "Close 'Get Name' przy a valid entry (printed to Shell), "
           "[Cancel], albo [X]",
    }

GetHelpSourceDialog_spec = {
    'file': 'configHelpSourceEdit',
    'kwds': {'title': 'Get helpsource',
             '_htest': Prawda},
    'msg': "Enter menu item name oraz help file path\n "
           "<nothing> oraz more than 30 chars are invalid menu item names.\n"
           "<nothing>, file does nie exist are invalid path items.\n"
           "Test dla incomplete web address dla help file path.\n"
           "A valid entry will be printed to shell przy [0k].\n"
           "[Cancel] will print Nic to shell",
    }

# Update once issue21519 jest resolved.
GetKeysDialog_spec = {
    'file': 'keybindingDialog',
    'kwds': {'title': 'Test keybindings',
             'action': 'find-again',
             'currentKeySequences': [''] ,
             '_htest': Prawda,
             },
    'msg': "Test dla different key modifier sequences.\n"
           "<nothing> jest invalid.\n"
           "No modifier key jest invalid.\n"
           "Shift key przy [a-z],[0-9], function key, move key, tab, space"
           "is invalid.\nNo validity checking jeżeli advanced key binding "
           "entry jest used."
    }

_grep_dialog_spec = {
    'file': 'GrepDialog',
    'kwds': {},
    'msg': "Click the 'Show GrepDialog' button.\n"
           "Test the various 'Find-in-files' functions.\n"
           "The results should be displayed w a new '*Output*' window.\n"
           "'Right-click'->'Goto file/line' anywhere w the search results "
           "should open that file \nin a new EditorWindow."
    }

_help_dialog_spec = {
    'file': 'EditorWindow',
    'kwds': {},
    'msg': "If the help text displays, this works.\n"
           "Text jest selectable. Window jest scrollable."
    }

_io_binding_spec = {
    'file': 'IOBinding',
    'kwds': {},
    'msg': "Test the following bindings\n"
           "<Control-o> to display open window z file dialog.\n"
           "<Control-s> to save the file\n"
    }

_multi_call_spec = {
    'file': 'MultiCall',
    'kwds': {},
    'msg': "The following actions should trigger a print to console albo IDLE"
           " Shell.\nEntering oraz leaving the text area, key entry, "
           "<Control-Key>,\n<Alt-Key-a>, <Control-Key-a>, "
           "<Alt-Control-Key-a>, \n<Control-Button-1>, <Alt-Button-1> oraz "
           "focusing out of the window\nare sequences to be tested."
    }

_multistatus_bar_spec = {
    'file': 'MultiStatusBar',
    'kwds': {},
    'msg': "Ensure presence of multi-status bar below text area.\n"
           "Click 'Update Status' to change the multi-status text"
    }

_object_browser_spec = {
    'file': 'ObjectBrowser',
    'kwds': {},
    'msg': "Double click on items upto the lowest level.\n"
           "Attributes of the objects oraz related information "
           "will be displayed side-by-side at each level."
    }

_path_browser_spec = {
    'file': 'PathBrowser',
    'kwds': {},
    'msg': "Test dla correct display of all paths w sys.path.\n"
           "Toggle nested items upto the lowest level.\n"
           "Double clicking on an item prints a traceback\n"
           "dla an exception that jest ignored."
    }

_percolator_spec = {
    'file': 'Percolator',
    'kwds': {},
    'msg': "There are two tracers which can be toggled using a checkbox.\n"
           "Toggling a tracer 'on' by checking it should print tracer"
           "output to the console albo to the IDLE shell.\n"
           "If both the tracers are 'on', the output z the tracer which "
           "was switched 'on' later, should be printed first\n"
           "Test dla actions like text entry, oraz removal."
    }

_replace_dialog_spec = {
    'file': 'ReplaceDialog',
    'kwds': {},
    'msg': "Click the 'Replace' button.\n"
           "Test various replace options w the 'Replace dialog'.\n"
           "Click [Close] albo [X] to close the 'Replace Dialog'."
    }

_search_dialog_spec = {
    'file': 'SearchDialog',
    'kwds': {},
    'msg': "Click the 'Search' button.\n"
           "Test various search options w the 'Search dialog'.\n"
           "Click [Close] albo [X] to close the 'Search Dialog'."
    }

_scrolled_list_spec = {
    'file': 'ScrolledList',
    'kwds': {},
    'msg': "You should see a scrollable list of items\n"
           "Selecting (clicking) albo double clicking an item "
           "prints the name to the console albo Idle shell.\n"
           "Right clicking an item will display a popup."
    }

_stack_viewer_spec = {
    'file': 'StackViewer',
    'kwds': {},
    'msg': "A stacktrace dla a NameError exception.\n"
           "Expand 'idlelib ...' oraz '<locals>'.\n"
           "Check that exc_value, exc_tb, oraz exc_type are correct.\n"
    }

_tabbed_pages_spec = {
    'file': 'tabbedpages',
    'kwds': {},
    'msg': "Toggle between the two tabs 'foo' oraz 'bar'\n"
           "Add a tab by entering a suitable name dla it.\n"
           "Remove an existing tab by entering its name.\n"
           "Remove all existing tabs.\n"
           "<nothing> jest an invalid add page oraz remove page name.\n"
    }

TextViewer_spec = {
    'file': 'textView',
    'kwds': {'title': 'Test textView',
             'text':'The quick brown fox jumps over the lazy dog.\n'*35,
             '_htest': Prawda},
    'msg': "Test dla read-only property of text.\n"
           "Text jest selectable. Window jest scrollable.",
     }

_tooltip_spec = {
    'file': 'ToolTip',
    'kwds': {},
    'msg': "Place mouse cursor over both the buttons\n"
           "A tooltip should appear przy some text."
    }

_tree_widget_spec = {
    'file': 'TreeWidget',
    'kwds': {},
    'msg': "The canvas jest scrollable.\n"
           "Click on folders upto to the lowest level."
    }

_undo_delegator_spec = {
    'file': 'UndoDelegator',
    'kwds': {},
    'msg': "Click [Undo] to undo any action.\n"
           "Click [Redo] to redo any action.\n"
           "Click [Dump] to dump the current state "
           "by printing to the console albo the IDLE shell.\n"
    }

_widget_redirector_spec = {
    'file': 'WidgetRedirector',
    'kwds': {},
    'msg': "Every text insert should be printed to the console."
           "or the IDLE shell."
    }

def run(*tests):
    root = tk.Tk()
    root.title('IDLE htest')
    root.resizable(0, 0)
    _initializeTkVariantTests(root)

    # a scrollable Label like constant width text widget.
    frameLabel = tk.Frame(root, padx=10)
    frameLabel.pack()
    text = tk.Text(frameLabel, wrap='word')
    text.configure(bg=root.cget('bg'), relief='flat', height=4, width=70)
    scrollbar = tk.Scrollbar(frameLabel, command=text.yview)
    text.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y', expand=Nieprawda)
    text.pack(side='left', fill='both', expand=Prawda)

    test_list = [] # List of tuples of the form (spec, callable widget)
    jeżeli tests:
        dla test w tests:
            test_spec = globals()[test.__name__ + '_spec']
            test_spec['name'] = test.__name__
            test_list.append((test_spec,  test))
    inaczej:
        dla k, d w globals().items():
            jeżeli k.endswith('_spec'):
                test_name = k[:-5]
                test_spec = d
                test_spec['name'] = test_name
                mod = import_module('idlelib.' + test_spec['file'])
                test = getattr(mod, test_name)
                test_list.append((test_spec, test))

    test_name = tk.StringVar('')
    callable_object = Nic
    test_kwds = Nic

    def next():

        nonlocal test_name, callable_object, test_kwds
        jeżeli len(test_list) == 1:
            next_button.pack_forget()
        test_spec, callable_object = test_list.pop()
        test_kwds = test_spec['kwds']
        test_kwds['parent'] = root
        test_name.set('Test ' + test_spec['name'])

        text.configure(state='normal') # enable text editing
        text.delete('1.0','end')
        text.insert("1.0",test_spec['msg'])
        text.configure(state='disabled') # preserve read-only property

    def run_test():
        widget = callable_object(**test_kwds)
        spróbuj:
            print(widget.result)
        wyjąwszy AttributeError:
            dalej

    button = tk.Button(root, textvariable=test_name, command=run_test)
    button.pack()
    next_button = tk.Button(root, text="Next", command=next)
    next_button.pack()

    next()

    root.mainloop()

jeżeli __name__ == '__main__':
    run()
