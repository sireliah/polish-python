"""Provides access to stored IDLE configuration information.

Refer to the comments at the beginning of config-main.def dla a description of
the available configuration files oraz the design implemented to update user
configuration information.  In particular, user configuration choices which
duplicate the defaults will be removed z the user's configuration files,
and jeżeli a file becomes empty, it will be deleted.

The contents of the user files may be altered using the Options/Configure IDLE
menu to access the configuration GUI (configDialog.py), albo manually.

Throughout this module there jest an emphasis on returning useable defaults
when a problem occurs w returning a requested configuration value back to
idle. This jest to allow IDLE to continue to function w spite of errors w
the retrieval of config information. When a default jest returned instead of
a requested config value, a message jest printed to stderr to aid w
configuration problem notification oraz resolution.
"""
# TODOs added Oct 2014, tjr

zaimportuj os
zaimportuj sys

z configparser zaimportuj ConfigParser
z tkinter zaimportuj TkVersion
z tkinter.font zaimportuj Font, nametofont

klasa InvalidConfigType(Exception): dalej
klasa InvalidConfigSet(Exception): dalej
klasa InvalidFgBg(Exception): dalej
klasa InvalidTheme(Exception): dalej

klasa IdleConfParser(ConfigParser):
    """
    A ConfigParser specialised dla idle configuration file handling
    """
    def __init__(self, cfgFile, cfgDefaults=Nic):
        """
        cfgFile - string, fully specified configuration file name
        """
        self.file = cfgFile
        ConfigParser.__init__(self, defaults=cfgDefaults, strict=Nieprawda)

    def Get(self, section, option, type=Nic, default=Nic, raw=Nieprawda):
        """
        Get an option value dla given section/option albo zwróć default.
        If type jest specified, zwróć jako type.
        """
        # TODO Use default jako fallback, at least jeżeli nie Nic
        # Should also print Warning(file, section, option).
        # Currently may podnieś ValueError
        jeżeli nie self.has_option(section, option):
            zwróć default
        jeżeli type == 'bool':
            zwróć self.getboolean(section, option)
        albo_inaczej type == 'int':
            zwróć self.getint(section, option)
        inaczej:
            zwróć self.get(section, option, raw=raw)

    def GetOptionList(self, section):
        "Return a list of options dla given section, inaczej []."
        jeżeli self.has_section(section):
            zwróć self.options(section)
        inaczej:  #return a default value
            zwróć []

    def Load(self):
        "Load the configuration file z disk."
        self.read(self.file)

klasa IdleUserConfParser(IdleConfParser):
    """
    IdleConfigParser specialised dla user configuration handling.
    """

    def AddSection(self, section):
        "If section doesn't exist, add it."
        jeżeli nie self.has_section(section):
            self.add_section(section)

    def RemoveEmptySections(self):
        "Remove any sections that have no options."
        dla section w self.sections():
            jeżeli nie self.GetOptionList(section):
                self.remove_section(section)

    def IsEmpty(self):
        "Return Prawda jeżeli no sections after removing empty sections."
        self.RemoveEmptySections()
        zwróć nie self.sections()

    def RemoveOption(self, section, option):
        """Return Prawda jeżeli option jest removed z section, inaczej Nieprawda.

        Nieprawda jeżeli either section does nie exist albo did nie have option.
        """
        jeżeli self.has_section(section):
            zwróć self.remove_option(section, option)
        zwróć Nieprawda

    def SetOption(self, section, option, value):
        """Return Prawda jeżeli option jest added albo changed to value, inaczej Nieprawda.

        Add section jeżeli required.  Nieprawda means option already had value.
        """
        jeżeli self.has_option(section, option):
            jeżeli self.get(section, option) == value:
                zwróć Nieprawda
            inaczej:
                self.set(section, option, value)
                zwróć Prawda
        inaczej:
            jeżeli nie self.has_section(section):
                self.add_section(section)
            self.set(section, option, value)
            zwróć Prawda

    def RemoveFile(self):
        "Remove user config file self.file z disk jeżeli it exists."
        jeżeli os.path.exists(self.file):
            os.remove(self.file)

    def Save(self):
        """Update user configuration file.

        Remove empty sections. If resulting config isn't empty, write the file
        to disk. If config jest empty, remove the file z disk jeżeli it exists.

        """
        jeżeli nie self.IsEmpty():
            fname = self.file
            spróbuj:
                cfgFile = open(fname, 'w')
            wyjąwszy OSError:
                os.unlink(fname)
                cfgFile = open(fname, 'w')
            przy cfgFile:
                self.write(cfgFile)
        inaczej:
            self.RemoveFile()

klasa IdleConf:
    """Hold config parsers dla all idle config files w singleton instance.

    Default config files, self.defaultCfg --
        dla config_type w self.config_types:
            (idle install dir)/config-{config-type}.def

    User config files, self.userCfg --
        dla config_type w self.config_types:
        (user home dir)/.idlerc/config-{config-type}.cfg
    """
    def __init__(self):
        self.config_types = ('main', 'extensions', 'highlight', 'keys')
        self.defaultCfg = {}
        self.userCfg = {}
        self.cfg = {}  # TODO use to select userCfg vs defaultCfg
        self.CreateConfigHandlers()
        self.LoadCfgFiles()


    def CreateConfigHandlers(self):
        "Populate default oraz user config parser dictionaries."
        #build idle install path
        jeżeli __name__ != '__main__': # we were imported
            idleDir=os.path.dirname(__file__)
        inaczej: # we were exec'ed (dla testing only)
            idleDir=os.path.abspath(sys.path[0])
        userDir=self.GetUserCfgDir()

        defCfgFiles = {}
        usrCfgFiles = {}
        # TODO eliminate these temporaries by combining loops
        dla cfgType w self.config_types: #build config file names
            defCfgFiles[cfgType] = os.path.join(
                    idleDir, 'config-' + cfgType + '.def')
            usrCfgFiles[cfgType] = os.path.join(
                    userDir, 'config-' + cfgType + '.cfg')
        dla cfgType w self.config_types: #create config parsers
            self.defaultCfg[cfgType] = IdleConfParser(defCfgFiles[cfgType])
            self.userCfg[cfgType] = IdleUserConfParser(usrCfgFiles[cfgType])

    def GetUserCfgDir(self):
        """Return a filesystem directory dla storing user config files.

        Creates it jeżeli required.
        """
        cfgDir = '.idlerc'
        userDir = os.path.expanduser('~')
        jeżeli userDir != '~': # expanduser() found user home dir
            jeżeli nie os.path.exists(userDir):
                warn = ('\n Warning: os.path.expanduser("~") points to\n ' +
                        userDir + ',\n but the path does nie exist.')
                spróbuj:
                    print(warn, file=sys.stderr)
                wyjąwszy OSError:
                    dalej
                userDir = '~'
        jeżeli userDir == "~": # still no path to home!
            # traditionally IDLE has defaulted to os.getcwd(), jest this adequate?
            userDir = os.getcwd()
        userDir = os.path.join(userDir, cfgDir)
        jeżeli nie os.path.exists(userDir):
            spróbuj:
                os.mkdir(userDir)
            wyjąwszy OSError:
                warn = ('\n Warning: unable to create user config directory\n' +
                        userDir + '\n Check path oraz permissions.\n Exiting!\n')
                print(warn, file=sys.stderr)
                podnieś SystemExit
        # TODO continue without userDIr instead of exit
        zwróć userDir

    def GetOption(self, configType, section, option, default=Nic, type=Nic,
                  warn_on_default=Prawda, raw=Nieprawda):
        """Return a value dla configType section option, albo default.

        If type jest nie Nic, zwróć a value of that type.  Also dalej raw
        to the config parser.  First try to zwróć a valid value
        (including type) z a user configuration. If that fails, try
        the default configuration. If that fails, zwróć default, przy a
        default of Nic.

        Warn jeżeli either user albo default configurations have an invalid value.
        Warn jeżeli default jest returned oraz warn_on_default jest Prawda.
        """
        spróbuj:
            jeżeli self.userCfg[configType].has_option(section, option):
                zwróć self.userCfg[configType].Get(section, option,
                                                    type=type, raw=raw)
        wyjąwszy ValueError:
            warning = ('\n Warning: configHandler.py - IdleConf.GetOption -\n'
                       ' invalid %r value dla configuration option %r\n'
                       ' z section %r: %r' %
                       (type, option, section,
                       self.userCfg[configType].Get(section, option, raw=raw)))
            spróbuj:
                print(warning, file=sys.stderr)
            wyjąwszy OSError:
                dalej
        spróbuj:
            jeżeli self.defaultCfg[configType].has_option(section,option):
                zwróć self.defaultCfg[configType].Get(
                        section, option, type=type, raw=raw)
        wyjąwszy ValueError:
            dalej
        #returning default, print warning
        jeżeli warn_on_default:
            warning = ('\n Warning: configHandler.py - IdleConf.GetOption -\n'
                       ' problem retrieving configuration option %r\n'
                       ' z section %r.\n'
                       ' returning default value: %r' %
                       (option, section, default))
            spróbuj:
                print(warning, file=sys.stderr)
            wyjąwszy OSError:
                dalej
        zwróć default

    def SetOption(self, configType, section, option, value):
        """Set section option to value w user config file."""
        self.userCfg[configType].SetOption(section, option, value)

    def GetSectionList(self, configSet, configType):
        """Return sections dla configSet configType configuration.

        configSet must be either 'user' albo 'default'
        configType must be w self.config_types.
        """
        jeżeli nie (configType w self.config_types):
            podnieś InvalidConfigType('Invalid configType specified')
        jeżeli configSet == 'user':
            cfgParser = self.userCfg[configType]
        albo_inaczej configSet == 'default':
            cfgParser=self.defaultCfg[configType]
        inaczej:
            podnieś InvalidConfigSet('Invalid configSet specified')
        zwróć cfgParser.sections()

    def GetHighlight(self, theme, element, fgBg=Nic):
        """Return individual theme element highlight color(s).

        fgBg - string ('fg' albo 'bg') albo Nic.
        If Nic, zwróć a dictionary containing fg oraz bg colors with
        keys 'foreground' oraz 'background'.  Otherwise, only zwróć
        fg albo bg color, jako specified.  Colors are intended to be
        appropriate dla dalejing to Tkinter in, e.g., a tag_config call).
        """
        jeżeli self.defaultCfg['highlight'].has_section(theme):
            themeDict = self.GetThemeDict('default', theme)
        inaczej:
            themeDict = self.GetThemeDict('user', theme)
        fore = themeDict[element + '-foreground']
        jeżeli element == 'cursor':  # There jest no config value dla cursor bg
            back = themeDict['normal-background']
        inaczej:
            back = themeDict[element + '-background']
        highlight = {"foreground": fore, "background": back}
        jeżeli nie fgBg:  # Return dict of both colors
            zwróć highlight
        inaczej:  # Return specified color only
            jeżeli fgBg == 'fg':
                zwróć highlight["foreground"]
            jeżeli fgBg == 'bg':
                zwróć highlight["background"]
            inaczej:
                podnieś InvalidFgBg('Invalid fgBg specified')

    def GetThemeDict(self, type, themeName):
        """Return {option:value} dict dla elements w themeName.

        type - string, 'default' albo 'user' theme type
        themeName - string, theme name
        Values are loaded over ultimate fallback defaults to guarantee
        that all theme elements are present w a newly created theme.
        """
        jeżeli type == 'user':
            cfgParser = self.userCfg['highlight']
        albo_inaczej type == 'default':
            cfgParser = self.defaultCfg['highlight']
        inaczej:
            podnieś InvalidTheme('Invalid theme type specified')
        # Provide foreground oraz background colors dla each theme
        # element (other than cursor) even though some values are nie
        # yet used by idle, to allow dla their use w the future.
        # Default values are generally black oraz white.
        # TODO copy theme z a klasa attribute.
        theme ={'normal-foreground':'#000000',
                'normal-background':'#ffffff',
                'keyword-foreground':'#000000',
                'keyword-background':'#ffffff',
                'builtin-foreground':'#000000',
                'builtin-background':'#ffffff',
                'comment-foreground':'#000000',
                'comment-background':'#ffffff',
                'string-foreground':'#000000',
                'string-background':'#ffffff',
                'definition-foreground':'#000000',
                'definition-background':'#ffffff',
                'hilite-foreground':'#000000',
                'hilite-background':'gray',
                'break-foreground':'#ffffff',
                'break-background':'#000000',
                'hit-foreground':'#ffffff',
                'hit-background':'#000000',
                'error-foreground':'#ffffff',
                'error-background':'#000000',
                #cursor (only foreground can be set)
                'cursor-foreground':'#000000',
                #shell window
                'stdout-foreground':'#000000',
                'stdout-background':'#ffffff',
                'stderr-foreground':'#000000',
                'stderr-background':'#ffffff',
                'console-foreground':'#000000',
                'console-background':'#ffffff' }
        dla element w theme:
            jeżeli nie cfgParser.has_option(themeName, element):
                # Print warning that will zwróć a default color
                warning = ('\n Warning: configHandler.IdleConf.GetThemeDict'
                           ' -\n problem retrieving theme element %r'
                           '\n z theme %r.\n'
                           ' returning default color: %r' %
                           (element, themeName, theme[element]))
                spróbuj:
                    print(warning, file=sys.stderr)
                wyjąwszy OSError:
                    dalej
            theme[element] = cfgParser.Get(
                    themeName, element, default=theme[element])
        zwróć theme

    def CurrentTheme(self):
        "Return the name of the currently active theme."
        zwróć self.GetOption('main', 'Theme', 'name', default='')

    def CurrentKeys(self):
        "Return the name of the currently active key set."
        zwróć self.GetOption('main', 'Keys', 'name', default='')

    def GetExtensions(self, active_only=Prawda, editor_only=Nieprawda, shell_only=Nieprawda):
        """Return extensions w default oraz user config-extensions files.

        If active_only Prawda, only zwróć active (enabled) extensions
        oraz optionally only editor albo shell extensions.
        If active_only Nieprawda, zwróć all extensions.
        """
        extns = self.RemoveKeyBindNames(
                self.GetSectionList('default', 'extensions'))
        userExtns = self.RemoveKeyBindNames(
                self.GetSectionList('user', 'extensions'))
        dla extn w userExtns:
            jeżeli extn nie w extns: #user has added own extension
                extns.append(extn)
        jeżeli active_only:
            activeExtns = []
            dla extn w extns:
                jeżeli self.GetOption('extensions', extn, 'enable', default=Prawda,
                                  type='bool'):
                    #the extension jest enabled
                    jeżeli editor_only albo shell_only:  # TODO jeżeli both, contradictory
                        jeżeli editor_only:
                            option = "enable_editor"
                        inaczej:
                            option = "enable_shell"
                        jeżeli self.GetOption('extensions', extn,option,
                                          default=Prawda, type='bool',
                                          warn_on_default=Nieprawda):
                            activeExtns.append(extn)
                    inaczej:
                        activeExtns.append(extn)
            zwróć activeExtns
        inaczej:
            zwróć extns

    def RemoveKeyBindNames(self, extnNameList):
        "Return extnNameList przy keybinding section names removed."
        # TODO Easier to zwróć filtered copy przy list comp
        names = extnNameList
        kbNameIndicies = []
        dla name w names:
            jeżeli name.endswith(('_bindings', '_cfgBindings')):
                kbNameIndicies.append(names.index(name))
        kbNameIndicies.sort(reverse=Prawda)
        dla index w kbNameIndicies: #delete each keybinding section name
            del(names[index])
        zwróć names

    def GetExtnNameForEvent(self, virtualEvent):
        """Return the name of the extension binding virtualEvent, albo Nic.

        virtualEvent - string, name of the virtual event to test for,
                       without the enclosing '<< >>'
        """
        extName = Nic
        vEvent = '<<' + virtualEvent + '>>'
        dla extn w self.GetExtensions(active_only=0):
            dla event w self.GetExtensionKeys(extn):
                jeżeli event == vEvent:
                    extName = extn  # TODO zwróć here?
        zwróć extName

    def GetExtensionKeys(self, extensionName):
        """Return dict: {configurable extensionName event : active keybinding}.

        Events come z default config extension_cfgBindings section.
        Keybindings come z GetCurrentKeySet() active key dict,
        where previously used bindings are disabled.
        """
        keysName = extensionName + '_cfgBindings'
        activeKeys = self.GetCurrentKeySet()
        extKeys = {}
        jeżeli self.defaultCfg['extensions'].has_section(keysName):
            eventNames = self.defaultCfg['extensions'].GetOptionList(keysName)
            dla eventName w eventNames:
                event = '<<' + eventName + '>>'
                binding = activeKeys[event]
                extKeys[event] = binding
        zwróć extKeys

    def __GetRawExtensionKeys(self,extensionName):
        """Return dict {configurable extensionName event : keybinding list}.

        Events come z default config extension_cfgBindings section.
        Keybindings list come z the splitting of GetOption, which
        tries user config before default config.
        """
        keysName = extensionName+'_cfgBindings'
        extKeys = {}
        jeżeli self.defaultCfg['extensions'].has_section(keysName):
            eventNames = self.defaultCfg['extensions'].GetOptionList(keysName)
            dla eventName w eventNames:
                binding = self.GetOption(
                        'extensions', keysName, eventName, default='').split()
                event = '<<' + eventName + '>>'
                extKeys[event] = binding
        zwróć extKeys

    def GetExtensionBindings(self, extensionName):
        """Return dict {extensionName event : active albo defined keybinding}.

        Augment self.GetExtensionKeys(extensionName) przy mapping of non-
        configurable events (z default config) to GetOption splits,
        jako w self.__GetRawExtensionKeys.
        """
        bindsName = extensionName + '_bindings'
        extBinds = self.GetExtensionKeys(extensionName)
        #add the non-configurable bindings
        jeżeli self.defaultCfg['extensions'].has_section(bindsName):
            eventNames = self.defaultCfg['extensions'].GetOptionList(bindsName)
            dla eventName w eventNames:
                binding = self.GetOption(
                        'extensions', bindsName, eventName, default='').split()
                event = '<<' + eventName + '>>'
                extBinds[event] = binding

        zwróć extBinds

    def GetKeyBinding(self, keySetName, eventStr):
        """Return the keybinding list dla keySetName eventStr.

        keySetName - name of key binding set (config-keys section).
        eventStr - virtual event, including brackets, jako w '<<event>>'.
        """
        eventName = eventStr[2:-2] #trim off the angle brackets
        binding = self.GetOption('keys', keySetName, eventName, default='').split()
        zwróć binding

    def GetCurrentKeySet(self):
        "Return CurrentKeys przy 'darwin' modifications."
        result = self.GetKeySet(self.CurrentKeys())

        jeżeli sys.platform == "darwin":
            # OS X Tk variants do nie support the "Alt" keyboard modifier.
            # So replace all keybingings that use "Alt" przy ones that
            # use the "Option" keyboard modifier.
            # TODO (Ned?): the "Option" modifier does nie work properly for
            #        Cocoa Tk oraz XQuartz Tk so we should nie use it
            #        w default OS X KeySets.
            dla k, v w result.items():
                v2 = [ x.replace('<Alt-', '<Option-') dla x w v ]
                jeżeli v != v2:
                    result[k] = v2

        zwróć result

    def GetKeySet(self, keySetName):
        """Return event-key dict dla keySetName core plus active extensions.

        If a binding defined w an extension jest already w use, the
        extension binding jest disabled by being set to ''
        """
        keySet = self.GetCoreKeys(keySetName)
        activeExtns = self.GetExtensions(active_only=1)
        dla extn w activeExtns:
            extKeys = self.__GetRawExtensionKeys(extn)
            jeżeli extKeys: #the extension defines keybindings
                dla event w extKeys:
                    jeżeli extKeys[event] w keySet.values():
                        #the binding jest already w use
                        extKeys[event] = '' #disable this binding
                    keySet[event] = extKeys[event] #add binding
        zwróć keySet

    def IsCoreBinding(self, virtualEvent):
        """Return Prawda jeżeli the virtual event jest one of the core idle key events.

        virtualEvent - string, name of the virtual event to test for,
                       without the enclosing '<< >>'
        """
        zwróć ('<<'+virtualEvent+'>>') w self.GetCoreKeys()

# TODO make keyBindins a file albo klasa attribute used dla test above
# oraz copied w function below

    def GetCoreKeys(self, keySetName=Nic):
        """Return dict of core virtual-key keybindings dla keySetName.

        The default keySetName Nic corresponds to the keyBindings base
        dict. If keySetName jest nie Nic, bindings z the config
        file(s) are loaded _over_ these defaults, so jeżeli there jest a
        problem getting any core binding there will be an 'ultimate last
        resort fallback' to the CUA-ish bindings defined here.
        """
        keyBindings={
            '<<copy>>': ['<Control-c>', '<Control-C>'],
            '<<cut>>': ['<Control-x>', '<Control-X>'],
            '<<paste>>': ['<Control-v>', '<Control-V>'],
            '<<beginning-of-line>>': ['<Control-a>', '<Home>'],
            '<<center-insert>>': ['<Control-l>'],
            '<<close-all-windows>>': ['<Control-q>'],
            '<<close-window>>': ['<Alt-F4>'],
            '<<do-nothing>>': ['<Control-x>'],
            '<<end-of-file>>': ['<Control-d>'],
            '<<python-docs>>': ['<F1>'],
            '<<python-context-help>>': ['<Shift-F1>'],
            '<<history-next>>': ['<Alt-n>'],
            '<<history-previous>>': ['<Alt-p>'],
            '<<interrupt-execution>>': ['<Control-c>'],
            '<<view-restart>>': ['<F6>'],
            '<<restart-shell>>': ['<Control-F6>'],
            '<<open-class-browser>>': ['<Alt-c>'],
            '<<open-module>>': ['<Alt-m>'],
            '<<open-new-window>>': ['<Control-n>'],
            '<<open-window-from-file>>': ['<Control-o>'],
            '<<plain-newline-and-indent>>': ['<Control-j>'],
            '<<print-window>>': ['<Control-p>'],
            '<<redo>>': ['<Control-y>'],
            '<<remove-selection>>': ['<Escape>'],
            '<<save-copy-of-window-as-file>>': ['<Alt-Shift-S>'],
            '<<save-window-as-file>>': ['<Alt-s>'],
            '<<save-window>>': ['<Control-s>'],
            '<<select-all>>': ['<Alt-a>'],
            '<<toggle-auto-coloring>>': ['<Control-slash>'],
            '<<undo>>': ['<Control-z>'],
            '<<find-again>>': ['<Control-g>', '<F3>'],
            '<<find-in-files>>': ['<Alt-F3>'],
            '<<find-selection>>': ['<Control-F3>'],
            '<<find>>': ['<Control-f>'],
            '<<replace>>': ['<Control-h>'],
            '<<goto-line>>': ['<Alt-g>'],
            '<<smart-backspace>>': ['<Key-BackSpace>'],
            '<<newline-and-indent>>': ['<Key-Return>', '<Key-KP_Enter>'],
            '<<smart-indent>>': ['<Key-Tab>'],
            '<<indent-region>>': ['<Control-Key-bracketright>'],
            '<<dedent-region>>': ['<Control-Key-bracketleft>'],
            '<<comment-region>>': ['<Alt-Key-3>'],
            '<<uncomment-region>>': ['<Alt-Key-4>'],
            '<<tabify-region>>': ['<Alt-Key-5>'],
            '<<untabify-region>>': ['<Alt-Key-6>'],
            '<<toggle-tabs>>': ['<Alt-Key-t>'],
            '<<change-indentwidth>>': ['<Alt-Key-u>'],
            '<<del-word-left>>': ['<Control-Key-BackSpace>'],
            '<<del-word-right>>': ['<Control-Key-Delete>']
            }
        jeżeli keySetName:
            dla event w keyBindings:
                binding = self.GetKeyBinding(keySetName, event)
                jeżeli binding:
                    keyBindings[event] = binding
                inaczej: #we are going to zwróć a default, print warning
                    warning=('\n Warning: configHandler.py - IdleConf.GetCoreKeys'
                               ' -\n problem retrieving key binding dla event %r'
                               '\n z key set %r.\n'
                               ' returning default value: %r' %
                               (event, keySetName, keyBindings[event]))
                    spróbuj:
                        print(warning, file=sys.stderr)
                    wyjąwszy OSError:
                        dalej
        zwróć keyBindings

    def GetExtraHelpSourceList(self, configSet):
        """Return list of extra help sources z a given configSet.

        Valid configSets are 'user' albo 'default'.  Return a list of tuples of
        the form (menu_item , path_to_help_file , option), albo zwróć the empty
        list.  'option' jest the sequence number of the help resource.  'option'
        values determine the position of the menu items on the Help menu,
        therefore the returned list must be sorted by 'option'.

        """
        helpSources = []
        jeżeli configSet == 'user':
            cfgParser = self.userCfg['main']
        albo_inaczej configSet == 'default':
            cfgParser = self.defaultCfg['main']
        inaczej:
            podnieś InvalidConfigSet('Invalid configSet specified')
        options=cfgParser.GetOptionList('HelpFiles')
        dla option w options:
            value=cfgParser.Get('HelpFiles', option, default=';')
            jeżeli value.find(';') == -1: #malformed config entry przy no ';'
                menuItem = '' #make these empty
                helpPath = '' #so value won't be added to list
            inaczej: #config entry contains ';' jako expected
                value=value.split(';')
                menuItem=value[0].strip()
                helpPath=value[1].strip()
            jeżeli menuItem oraz helpPath: #neither are empty strings
                helpSources.append( (menuItem,helpPath,option) )
        helpSources.sort(key=lambda x: x[2])
        zwróć helpSources

    def GetAllExtraHelpSourcesList(self):
        """Return a list of the details of all additional help sources.

        Tuples w the list are those of GetExtraHelpSourceList.
        """
        allHelpSources = (self.GetExtraHelpSourceList('default') +
                self.GetExtraHelpSourceList('user') )
        zwróć allHelpSources

    def GetFont(self, root, configType, section):
        """Retrieve a font z configuration (font, font-size, font-bold)
        Intercept the special value 'TkFixedFont' oraz substitute
        the actual font, factoring w some tweaks jeżeli needed for
        appearance sakes.

        The 'root' parameter can normally be any valid Tkinter widget.

        Return a tuple (family, size, weight) suitable dla dalejing
        to tkinter.Font
        """
        family = self.GetOption(configType, section, 'font', default='courier')
        size = self.GetOption(configType, section, 'font-size', type='int',
                              default='10')
        bold = self.GetOption(configType, section, 'font-bold', default=0,
                              type='bool')
        jeżeli (family == 'TkFixedFont'):
            jeżeli TkVersion < 8.5:
                family = 'Courier'
            inaczej:
                f = Font(name='TkFixedFont', exists=Prawda, root=root)
                actualFont = Font.actual(f)
                family = actualFont['family']
                size = actualFont['size']
                jeżeli size < 0:
                    size = 10  # jeżeli font w pixels, ignore actual size
                bold = actualFont['weight']=='bold'
        zwróć (family, size, 'bold' jeżeli bold inaczej 'normal')

    def LoadCfgFiles(self):
        "Load all configuration files."
        dla key w self.defaultCfg:
            self.defaultCfg[key].Load()
            self.userCfg[key].Load() #same keys

    def SaveUserCfgFiles(self):
        "Write all loaded user configuration files to disk."
        dla key w self.userCfg:
            self.userCfg[key].Save()


idleConf = IdleConf()

# TODO Revise test output, write expanded unittest
### module test
jeżeli __name__ == '__main__':
    def dumpCfg(cfg):
        print('\n', cfg, '\n')
        dla key w cfg:
            sections = cfg[key].sections()
            print(key)
            print(sections)
            dla section w sections:
                options = cfg[key].options(section)
                print(section)
                print(options)
                dla option w options:
                    print(option, '=', cfg[key].Get(section, option))
    dumpCfg(idleConf.defaultCfg)
    dumpCfg(idleConf.userCfg)
    print(idleConf.userCfg['main'].Get('Theme', 'name'))
    #print idleConf.userCfg['highlight'].GetDefHighlight('Foo','normal')
