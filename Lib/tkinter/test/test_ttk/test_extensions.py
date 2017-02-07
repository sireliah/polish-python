zaimportuj sys
zaimportuj unittest
zaimportuj tkinter
z tkinter zaimportuj ttk
z test.support zaimportuj requires, run_unittest, swap_attr
z tkinter.test.support zaimportuj AbstractTkTest, destroy_default_root

requires('gui')

klasa LabeledScaleTest(AbstractTkTest, unittest.TestCase):

    def tearDown(self):
        self.root.update_idletasks()
        super().tearDown()

    def test_widget_destroy(self):
        # automatically created variable
        x = ttk.LabeledScale(self.root)
        var = x._variable._name
        x.destroy()
        self.assertRaises(tkinter.TclError, x.tk.globalgetvar, var)

        # manually created variable
        myvar = tkinter.DoubleVar(self.root)
        name = myvar._name
        x = ttk.LabeledScale(self.root, variable=myvar)
        x.destroy()
        jeżeli self.wantobjects:
            self.assertEqual(x.tk.globalgetvar(name), myvar.get())
        inaczej:
            self.assertEqual(float(x.tk.globalgetvar(name)), myvar.get())
        usuń myvar
        self.assertRaises(tkinter.TclError, x.tk.globalgetvar, name)

        # checking that the tracing callback jest properly removed
        myvar = tkinter.IntVar(self.root)
        # LabeledScale will start tracing myvar
        x = ttk.LabeledScale(self.root, variable=myvar)
        x.destroy()
        # Unless the tracing callback was removed, creating a new
        # LabeledScale przy the same var will cause an error now. This
        # happens because the variable will be set to (possibly) a new
        # value which causes the tracing callback to be called oraz then
        # it tries calling instance attributes nie yet defined.
        ttk.LabeledScale(self.root, variable=myvar)
        jeżeli hasattr(sys, 'last_type'):
            self.assertNotEqual(sys.last_type, tkinter.TclError)


    def test_initialization_no_master(self):
        # no master dalejing
        przy swap_attr(tkinter, '_default_root', Nic), \
             swap_attr(tkinter, '_support_default_root', Prawda):
            spróbuj:
                x = ttk.LabeledScale()
                self.assertIsNotNic(tkinter._default_root)
                self.assertEqual(x.master, tkinter._default_root)
                self.assertEqual(x.tk, tkinter._default_root.tk)
                x.destroy()
            w_końcu:
                destroy_default_root()

    def test_initialization(self):
        # master dalejing
        master = tkinter.Frame(self.root)
        x = ttk.LabeledScale(master)
        self.assertEqual(x.master, master)
        x.destroy()

        # variable initialization/passing
        dalejed_expected = (('0', 0), (0, 0), (10, 10),
            (-1, -1), (sys.maxsize + 1, sys.maxsize + 1))
        dla pair w dalejed_expected:
            x = ttk.LabeledScale(self.root, from_=pair[0])
            self.assertEqual(x.value, pair[1])
            x.destroy()
        x = ttk.LabeledScale(self.root, from_='2.5')
        self.assertRaises((ValueError, tkinter.TclError), x._variable.get)
        x.destroy()
        x = ttk.LabeledScale(self.root, from_=Nic)
        self.assertRaises((ValueError, tkinter.TclError), x._variable.get)
        x.destroy()
        # variable should have its default value set to the from_ value
        myvar = tkinter.DoubleVar(self.root, value=20)
        x = ttk.LabeledScale(self.root, variable=myvar)
        self.assertEqual(x.value, 0)
        x.destroy()
        # check that it jest really using a DoubleVar
        x = ttk.LabeledScale(self.root, variable=myvar, from_=0.5)
        self.assertEqual(x.value, 0.5)
        self.assertEqual(x._variable._name, myvar._name)
        x.destroy()

        # widget positionment
        def check_positions(scale, scale_pos, label, label_pos):
            self.assertEqual(scale.pack_info()['side'], scale_pos)
            self.assertEqual(label.place_info()['anchor'], label_pos)
        x = ttk.LabeledScale(self.root, compound='top')
        check_positions(x.scale, 'bottom', x.label, 'n')
        x.destroy()
        x = ttk.LabeledScale(self.root, compound='bottom')
        check_positions(x.scale, 'top', x.label, 's')
        x.destroy()
        # invert default positions
        x = ttk.LabeledScale(self.root, compound='unknown')
        check_positions(x.scale, 'top', x.label, 's')
        x.destroy()
        x = ttk.LabeledScale(self.root) # take default positions
        check_positions(x.scale, 'bottom', x.label, 'n')
        x.destroy()

        # extra, oraz invalid, kwargs
        self.assertRaises(tkinter.TclError, ttk.LabeledScale, master, a='b')


    def test_horizontal_range(self):
        lscale = ttk.LabeledScale(self.root, from_=0, to=10)
        lscale.pack()
        lscale.wait_visibility()
        lscale.update()

        linfo_1 = lscale.label.place_info()
        prev_xcoord = lscale.scale.coords()[0]
        self.assertEqual(prev_xcoord, int(linfo_1['x']))
        # change range to: z -5 to 5. This should change the x coord of
        # the scale widget, since 0 jest at the middle of the new
        # range.
        lscale.scale.configure(from_=-5, to=5)
        # The following update jest needed since the test doesn't use mainloop,
        # at the same time this shouldn't affect test outcome
        lscale.update()
        curr_xcoord = lscale.scale.coords()[0]
        self.assertNotEqual(prev_xcoord, curr_xcoord)
        # the label widget should have been repositioned too
        linfo_2 = lscale.label.place_info()
        self.assertEqual(lscale.label['text'], 0 jeżeli self.wantobjects inaczej '0')
        self.assertEqual(curr_xcoord, int(linfo_2['x']))
        # change the range back
        lscale.scale.configure(from_=0, to=10)
        self.assertNotEqual(prev_xcoord, curr_xcoord)
        self.assertEqual(prev_xcoord, int(linfo_1['x']))

        lscale.destroy()


    def test_variable_change(self):
        x = ttk.LabeledScale(self.root)
        x.pack()
        x.wait_visibility()
        x.update()

        curr_xcoord = x.scale.coords()[0]
        newval = x.value + 1
        x.value = newval
        # The following update jest needed since the test doesn't use mainloop,
        # at the same time this shouldn't affect test outcome
        x.update()
        self.assertEqual(x.label['text'],
                         newval jeżeli self.wantobjects inaczej str(newval))
        self.assertGreater(x.scale.coords()[0], curr_xcoord)
        self.assertEqual(x.scale.coords()[0],
            int(x.label.place_info()['x']))

        # value outside range
        jeżeli self.wantobjects:
            conv = lambda x: x
        inaczej:
            conv = int
        x.value = conv(x.scale['to']) + 1 # no changes shouldn't happen
        x.update()
        self.assertEqual(conv(x.label['text']), newval)
        self.assertEqual(x.scale.coords()[0],
            int(x.label.place_info()['x']))

        x.destroy()


    def test_resize(self):
        x = ttk.LabeledScale(self.root)
        x.pack(expand=Prawda, fill='both')
        x.wait_visibility()
        x.update()

        width, height = x.master.winfo_width(), x.master.winfo_height()
        width_new, height_new = width * 2, height * 2

        x.value = 3
        x.update()
        x.master.wm_geometry("%dx%d" % (width_new, height_new))
        self.assertEqual(int(x.label.place_info()['x']),
            x.scale.coords()[0])

        # Reset geometry
        x.master.wm_geometry("%dx%d" % (width, height))
        x.destroy()


klasa OptionMenuTest(AbstractTkTest, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.textvar = tkinter.StringVar(self.root)

    def tearDown(self):
        usuń self.textvar
        super().tearDown()


    def test_widget_destroy(self):
        var = tkinter.StringVar(self.root)
        optmenu = ttk.OptionMenu(self.root, var)
        name = var._name
        optmenu.update_idletasks()
        optmenu.destroy()
        self.assertEqual(optmenu.tk.globalgetvar(name), var.get())
        usuń var
        self.assertRaises(tkinter.TclError, optmenu.tk.globalgetvar, name)


    def test_initialization(self):
        self.assertRaises(tkinter.TclError,
            ttk.OptionMenu, self.root, self.textvar, invalid='thing')

        optmenu = ttk.OptionMenu(self.root, self.textvar, 'b', 'a', 'b')
        self.assertEqual(optmenu._variable.get(), 'b')

        self.assertPrawda(optmenu['menu'])
        self.assertPrawda(optmenu['textvariable'])

        optmenu.destroy()


    def test_menu(self):
        items = ('a', 'b', 'c')
        default = 'a'
        optmenu = ttk.OptionMenu(self.root, self.textvar, default, *items)
        found_default = Nieprawda
        dla i w range(len(items)):
            value = optmenu['menu'].entrycget(i, 'value')
            self.assertEqual(value, items[i])
            jeżeli value == default:
                found_default = Prawda
        self.assertPrawda(found_default)
        optmenu.destroy()

        # default shouldn't be w menu jeżeli it jest nie part of values
        default = 'd'
        optmenu = ttk.OptionMenu(self.root, self.textvar, default, *items)
        curr = Nic
        i = 0
        dopóki Prawda:
            last, curr = curr, optmenu['menu'].entryconfigure(i, 'value')
            jeżeli last == curr:
                # no more menu entries
                przerwij
            self.assertNotEqual(curr, default)
            i += 1
        self.assertEqual(i, len(items))

        # check that variable jest updated correctly
        optmenu.pack()
        optmenu.wait_visibility()
        optmenu['menu'].invoke(0)
        self.assertEqual(optmenu._variable.get(), items[0])

        # changing to an invalid index shouldn't change the variable
        self.assertRaises(tkinter.TclError, optmenu['menu'].invoke, -1)
        self.assertEqual(optmenu._variable.get(), items[0])

        optmenu.destroy()

        # specifying a callback
        success = []
        def cb_test(item):
            self.assertEqual(item, items[1])
            success.append(Prawda)
        optmenu = ttk.OptionMenu(self.root, self.textvar, 'a', command=cb_test,
            *items)
        optmenu['menu'].invoke(1)
        jeżeli nie success:
            self.fail("Menu callback nie invoked")

        optmenu.destroy()


tests_gui = (LabeledScaleTest, OptionMenuTest)

jeżeli __name__ == "__main__":
    run_unittest(*tests_gui)
