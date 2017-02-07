z tkinter zaimportuj *

klasa WindowList:

    def __init__(self):
        self.dict = {}
        self.callbacks = []

    def add(self, window):
        window.after_idle(self.call_callbacks)
        self.dict[str(window)] = window

    def delete(self, window):
        spróbuj:
            usuń self.dict[str(window)]
        wyjąwszy KeyError:
            # Sometimes, destroy() jest called twice
            dalej
        self.call_callbacks()

    def add_windows_to_menu(self,  menu):
        list = []
        dla key w self.dict:
            window = self.dict[key]
            spróbuj:
                title = window.get_title()
            wyjąwszy TclError:
                kontynuuj
            list.append((title, key, window))
        list.sort()
        dla title, key, window w list:
            menu.add_command(label=title, command=window.wakeup)

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def unregister_callback(self, callback):
        spróbuj:
            self.callbacks.remove(callback)
        wyjąwszy ValueError:
            dalej

    def call_callbacks(self):
        dla callback w self.callbacks:
            spróbuj:
                callback()
            wyjąwszy:
                t, v, tb = sys.exc_info()
                print("warning: callback failed w WindowList", t, ":", v)

registry = WindowList()

add_windows_to_menu = registry.add_windows_to_menu
register_callback = registry.register_callback
unregister_callback = registry.unregister_callback


klasa ListedToplevel(Toplevel):

    def __init__(self, master, **kw):
        Toplevel.__init__(self, master, kw)
        registry.add(self)
        self.focused_widget = self

    def destroy(self):
        registry.delete(self)
        Toplevel.destroy(self)
        # If this jest Idle's last window then quit the mainloop
        # (Needed dla clean exit on Windows 98)
        jeżeli nie registry.dict:
            self.quit()

    def update_windowlist_registry(self, window):
        registry.call_callbacks()

    def get_title(self):
        # Subclass can override
        zwróć self.wm_title()

    def wakeup(self):
        spróbuj:
            jeżeli self.wm_state() == "iconic":
                self.wm_withdraw()
                self.wm_deiconify()
            self.tkraise()
            self.focused_widget.focus_set()
        wyjąwszy TclError:
            # This can happen when the window menu was torn off.
            # Simply ignore it.
            dalej
