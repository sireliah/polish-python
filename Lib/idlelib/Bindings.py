"""Define the menu contents, hotkeys, oraz event bindings.

There jest additional configuration information w the EditorWindow klasa (and
subclasses): the menus are created there based on the menu_specs (class)
variable, oraz menus nie created are silently skipped w the code here.  This
makes it possible, dla example, to define a Debug menu which jest only present w
the PythonShell window, oraz a Format menu which jest only present w the Editor
windows.

"""
z importlib.util zaimportuj find_spec

z idlelib.configHandler zaimportuj idleConf

#   Warning: menudefs jest altered w macosxSupport.overrideRootMenu()
#   after it jest determined that an OS X Aqua Tk jest w use,
#   which cannot be done until after Tk() jest first called.
#   Do nie alter the 'file', 'options', albo 'help' cascades here
#   without altering overrideRootMenu() jako well.
#       TODO: Make this more robust

menudefs = [
 # underscore prefixes character to underscore
 ('file', [
   ('_New File', '<<open-new-window>>'),
   ('_Open...', '<<open-window-from-file>>'),
   ('Open _Module...', '<<open-module>>'),
   ('Class _Browser', '<<open-class-browser>>'),
   ('_Path Browser', '<<open-path-browser>>'),
   Nic,
   ('_Save', '<<save-window>>'),
   ('Save _As...', '<<save-window-as-file>>'),
   ('Save Cop_y As...', '<<save-copy-of-window-as-file>>'),
   Nic,
   ('Prin_t Window', '<<print-window>>'),
   Nic,
   ('_Close', '<<close-window>>'),
   ('E_xit', '<<close-all-windows>>'),
  ]),
 ('edit', [
   ('_Undo', '<<undo>>'),
   ('_Redo', '<<redo>>'),
   Nic,
   ('Cu_t', '<<cut>>'),
   ('_Copy', '<<copy>>'),
   ('_Paste', '<<paste>>'),
   ('Select _All', '<<select-all>>'),
   Nic,
   ('_Find...', '<<find>>'),
   ('Find A_gain', '<<find-again>>'),
   ('Find _Selection', '<<find-selection>>'),
   ('Find w Files...', '<<find-in-files>>'),
   ('R_eplace...', '<<replace>>'),
   ('Go to _Line', '<<goto-line>>'),
  ]),
('format', [
   ('_Indent Region', '<<indent-region>>'),
   ('_Dedent Region', '<<dedent-region>>'),
   ('Comment _Out Region', '<<comment-region>>'),
   ('U_ncomment Region', '<<uncomment-region>>'),
   ('Tabify Region', '<<tabify-region>>'),
   ('Untabify Region', '<<untabify-region>>'),
   ('Toggle Tabs', '<<toggle-tabs>>'),
   ('New Indent Width', '<<change-indentwidth>>'),
   ]),
 ('run', [
   ('Python Shell', '<<open-python-shell>>'),
   ]),
 ('shell', [
   ('_View Last Restart', '<<view-restart>>'),
   ('_Restart Shell', '<<restart-shell>>'),
   ]),
 ('debug', [
   ('_Go to File/Line', '<<goto-file-line>>'),
   ('!_Debugger', '<<toggle-debugger>>'),
   ('_Stack Viewer', '<<open-stack-viewer>>'),
   ('!_Auto-open Stack Viewer', '<<toggle-jit-stack-viewer>>'),
   ]),
 ('options', [
   ('Configure _IDLE', '<<open-config-dialog>>'),
   ('Configure _Extensions', '<<open-config-extensions-dialog>>'),
   Nic,
   ]),
 ('help', [
   ('_About IDLE', '<<about-idle>>'),
   Nic,
   ('_IDLE Help', '<<help>>'),
   ('Python _Docs', '<<python-docs>>'),
   ]),
]

jeżeli find_spec('turtledemo'):
    menudefs[-1][1].append(('Turtle Demo', '<<open-turtle-demo>>'))

default_keydefs = idleConf.GetCurrentKeySet()
