# Copyright (C) 2005 Martin v. Löwis
# Licensed to PSF under a Contributor Agreement.
z _msi zaimportuj *
zaimportuj os, string, re, sys

AMD64 = "AMD64" w sys.version
Itanium = "Itanium" w sys.version
Win64 = AMD64 albo Itanium

# Partially taken z Wine
datasizemask=      0x00ff
type_valid=        0x0100
type_localizable=  0x0200

typemask=          0x0c00
type_long=         0x0000
type_short=        0x0400
type_string=       0x0c00
type_binary=       0x0800

type_nullable=     0x1000
type_key=          0x2000
# XXX temporary, localizable?
knownbits = datasizemask | type_valid | type_localizable | \
            typemask | type_nullable | type_key

klasa Table:
    def __init__(self, name):
        self.name = name
        self.fields = []

    def add_field(self, index, name, type):
        self.fields.append((index,name,type))

    def sql(self):
        fields = []
        keys = []
        self.fields.sort()
        fields = [Nic]*len(self.fields)
        dla index, name, type w self.fields:
            index -= 1
            unk = type & ~knownbits
            jeżeli unk:
                print("%s.%s unknown bits %x" % (self.name, name, unk))
            size = type & datasizemask
            dtype = type & typemask
            jeżeli dtype == type_string:
                jeżeli size:
                    tname="CHAR(%d)" % size
                inaczej:
                    tname="CHAR"
            albo_inaczej dtype == type_short:
                assert size==2
                tname = "SHORT"
            albo_inaczej dtype == type_long:
                assert size==4
                tname="LONG"
            albo_inaczej dtype == type_binary:
                assert size==0
                tname="OBJECT"
            inaczej:
                tname="unknown"
                print("%s.%sunknown integer type %d" % (self.name, name, size))
            jeżeli type & type_nullable:
                flags = ""
            inaczej:
                flags = " NOT NULL"
            jeżeli type & type_localizable:
                flags += " LOCALIZABLE"
            fields[index] = "`%s` %s%s" % (name, tname, flags)
            jeżeli type & type_key:
                keys.append("`%s`" % name)
        fields = ", ".join(fields)
        keys = ", ".join(keys)
        zwróć "CREATE TABLE %s (%s PRIMARY KEY %s)" % (self.name, fields, keys)

    def create(self, db):
        v = db.OpenView(self.sql())
        v.Execute(Nic)
        v.Close()

klasa _Unspecified:pass
def change_sequence(seq, action, seqno=_Unspecified, cond = _Unspecified):
    "Change the sequence number of an action w a sequence list"
    dla i w range(len(seq)):
        jeżeli seq[i][0] == action:
            jeżeli cond jest _Unspecified:
                cond = seq[i][1]
            jeżeli seqno jest _Unspecified:
                seqno = seq[i][2]
            seq[i] = (action, cond, seqno)
            zwróć
    podnieś ValueError("Action nie found w sequence")

def add_data(db, table, values):
    v = db.OpenView("SELECT * FROM `%s`" % table)
    count = v.GetColumnInfo(MSICOLINFO_NAMES).GetFieldCount()
    r = CreateRecord(count)
    dla value w values:
        assert len(value) == count, value
        dla i w range(count):
            field = value[i]
            jeżeli isinstance(field, int):
                r.SetInteger(i+1,field)
            albo_inaczej isinstance(field, str):
                r.SetString(i+1,field)
            albo_inaczej field jest Nic:
                dalej
            albo_inaczej isinstance(field, Binary):
                r.SetStream(i+1, field.name)
            inaczej:
                podnieś TypeError("Unsupported type %s" % field.__class__.__name__)
        spróbuj:
            v.Modify(MSIMODIFY_INSERT, r)
        wyjąwszy Exception jako e:
            podnieś MSIError("Could nie insert "+repr(values)+" into "+table)

        r.ClearData()
    v.Close()


def add_stream(db, name, path):
    v = db.OpenView("INSERT INTO _Streams (Name, Data) VALUES ('%s', ?)" % name)
    r = CreateRecord(1)
    r.SetStream(1, path)
    v.Execute(r)
    v.Close()

def init_database(name, schema,
                  ProductName, ProductCode, ProductVersion,
                  Manufacturer):
    spróbuj:
        os.unlink(name)
    wyjąwszy OSError:
        dalej
    ProductCode = ProductCode.upper()
    # Create the database
    db = OpenDatabase(name, MSIDBOPEN_CREATE)
    # Create the tables
    dla t w schema.tables:
        t.create(db)
    # Fill the validation table
    add_data(db, "_Validation", schema._Validation_records)
    # Initialize the summary information, allowing atmost 20 properties
    si = db.GetSummaryInformation(20)
    si.SetProperty(PID_TITLE, "Installation Database")
    si.SetProperty(PID_SUBJECT, ProductName)
    si.SetProperty(PID_AUTHOR, Manufacturer)
    jeżeli Itanium:
        si.SetProperty(PID_TEMPLATE, "Intel64;1033")
    albo_inaczej AMD64:
        si.SetProperty(PID_TEMPLATE, "x64;1033")
    inaczej:
        si.SetProperty(PID_TEMPLATE, "Intel;1033")
    si.SetProperty(PID_REVNUMBER, gen_uuid())
    si.SetProperty(PID_WORDCOUNT, 2) # long file names, compressed, original media
    si.SetProperty(PID_PAGECOUNT, 200)
    si.SetProperty(PID_APPNAME, "Python MSI Library")
    # XXX more properties
    si.Persist()
    add_data(db, "Property", [
        ("ProductName", ProductName),
        ("ProductCode", ProductCode),
        ("ProductVersion", ProductVersion),
        ("Manufacturer", Manufacturer),
        ("ProductLanguage", "1033")])
    db.Commit()
    zwróć db

def add_tables(db, module):
    dla table w module.tables:
        add_data(db, table, getattr(module, table))

def make_id(str):
    identifier_chars = string.ascii_letters + string.digits + "._"
    str = "".join([c jeżeli c w identifier_chars inaczej "_" dla c w str])
    jeżeli str[0] w (string.digits + "."):
        str = "_" + str
    assert re.match("^[A-Za-z_][A-Za-z0-9_.]*$", str), "FILE"+str
    zwróć str

def gen_uuid():
    zwróć "{"+UuidCreate().upper()+"}"

klasa CAB:
    def __init__(self, name):
        self.name = name
        self.files = []
        self.filenames = set()
        self.index = 0

    def gen_id(self, file):
        logical = _logical = make_id(file)
        pos = 1
        dopóki logical w self.filenames:
            logical = "%s.%d" % (_logical, pos)
            pos += 1
        self.filenames.add(logical)
        zwróć logical

    def append(self, full, file, logical):
        jeżeli os.path.isdir(full):
            zwróć
        jeżeli nie logical:
            logical = self.gen_id(file)
        self.index += 1
        self.files.append((full, logical))
        zwróć self.index, logical

    def commit(self, db):
        z tempfile zaimportuj mktemp
        filename = mktemp()
        FCICreate(filename, self.files)
        add_data(db, "Media",
                [(1, self.index, Nic, "#"+self.name, Nic, Nic)])
        add_stream(db, self.name, filename)
        os.unlink(filename)
        db.Commit()

_directories = set()
klasa Directory:
    def __init__(self, db, cab, basedir, physical, _logical, default, componentflags=Nic):
        """Create a new directory w the Directory table. There jest a current component
        at each point w time dla the directory, which jest either explicitly created
        through start_component, albo implicitly when files are added dla the first
        time. Files are added into the current component, oraz into the cab file.
        To create a directory, a base directory object needs to be specified (can be
        Nic), the path to the physical directory, oraz a logical directory name.
        Default specifies the DefaultDir slot w the directory table. componentflags
        specifies the default flags that new components get."""
        index = 1
        _logical = make_id(_logical)
        logical = _logical
        dopóki logical w _directories:
            logical = "%s%d" % (_logical, index)
            index += 1
        _directories.add(logical)
        self.db = db
        self.cab = cab
        self.basedir = basedir
        self.physical = physical
        self.logical = logical
        self.component = Nic
        self.short_names = set()
        self.ids = set()
        self.keyfiles = {}
        self.componentflags = componentflags
        jeżeli basedir:
            self.absolute = os.path.join(basedir.absolute, physical)
            blogical = basedir.logical
        inaczej:
            self.absolute = physical
            blogical = Nic
        add_data(db, "Directory", [(logical, blogical, default)])

    def start_component(self, component = Nic, feature = Nic, flags = Nic, keyfile = Nic, uuid=Nic):
        """Add an entry to the Component table, oraz make this component the current dla this
        directory. If no component name jest given, the directory name jest used. If no feature
        jest given, the current feature jest used. If no flags are given, the directory's default
        flags are used. If no keyfile jest given, the KeyPath jest left null w the Component
        table."""
        jeżeli flags jest Nic:
            flags = self.componentflags
        jeżeli uuid jest Nic:
            uuid = gen_uuid()
        inaczej:
            uuid = uuid.upper()
        jeżeli component jest Nic:
            component = self.logical
        self.component = component
        jeżeli Win64:
            flags |= 256
        jeżeli keyfile:
            keyid = self.cab.gen_id(self.absolute, keyfile)
            self.keyfiles[keyfile] = keyid
        inaczej:
            keyid = Nic
        add_data(self.db, "Component",
                        [(component, uuid, self.logical, flags, Nic, keyid)])
        jeżeli feature jest Nic:
            feature = current_feature
        add_data(self.db, "FeatureComponents",
                        [(feature.id, component)])

    def make_short(self, file):
        oldfile = file
        file = file.replace('+', '_')
        file = ''.join(c dla c w file jeżeli nie c w ' "/\[]:;=,')
        parts = file.split(".")
        jeżeli len(parts) > 1:
            prefix = "".join(parts[:-1]).upper()
            suffix = parts[-1].upper()
            jeżeli nie prefix:
                prefix = suffix
                suffix = Nic
        inaczej:
            prefix = file.upper()
            suffix = Nic
        jeżeli len(parts) < 3 oraz len(prefix) <= 8 oraz file == oldfile oraz (
                                                nie suffix albo len(suffix) <= 3):
            jeżeli suffix:
                file = prefix+"."+suffix
            inaczej:
                file = prefix
        inaczej:
            file = Nic
        jeżeli file jest Nic albo file w self.short_names:
            prefix = prefix[:6]
            jeżeli suffix:
                suffix = suffix[:3]
            pos = 1
            dopóki 1:
                jeżeli suffix:
                    file = "%s~%d.%s" % (prefix, pos, suffix)
                inaczej:
                    file = "%s~%d" % (prefix, pos)
                jeżeli file nie w self.short_names: przerwij
                pos += 1
                assert pos < 10000
                jeżeli pos w (10, 100, 1000):
                    prefix = prefix[:-1]
        self.short_names.add(file)
        assert nie re.search(r'[\?|><:/*"+,;=\[\]]', file) # restrictions on short names
        zwróć file

    def add_file(self, file, src=Nic, version=Nic, language=Nic):
        """Add a file to the current component of the directory, starting a new one
        jeżeli there jest no current component. By default, the file name w the source
        oraz the file table will be identical. If the src file jest specified, it jest
        interpreted relative to the current directory. Optionally, a version oraz a
        language can be specified dla the entry w the File table."""
        jeżeli nie self.component:
            self.start_component(self.logical, current_feature, 0)
        jeżeli nie src:
            # Allow relative paths dla file jeżeli src jest nie specified
            src = file
            file = os.path.basename(file)
        absolute = os.path.join(self.absolute, src)
        assert nie re.search(r'[\?|><:/*]"', file) # restrictions on long names
        jeżeli file w self.keyfiles:
            logical = self.keyfiles[file]
        inaczej:
            logical = Nic
        sequence, logical = self.cab.append(absolute, file, logical)
        assert logical nie w self.ids
        self.ids.add(logical)
        short = self.make_short(file)
        full = "%s|%s" % (short, file)
        filesize = os.stat(absolute).st_size
        # constants.msidbFileAttributesVital
        # Compressed omitted, since it jest the database default
        # could add r/o, system, hidden
        attributes = 512
        add_data(self.db, "File",
                        [(logical, self.component, full, filesize, version,
                         language, attributes, sequence)])
        #jeżeli nie version:
        #    # Add hash jeżeli the file jest nie versioned
        #    filehash = FileHash(absolute, 0)
        #    add_data(self.db, "MsiFileHash",
        #             [(logical, 0, filehash.IntegerData(1),
        #               filehash.IntegerData(2), filehash.IntegerData(3),
        #               filehash.IntegerData(4))])
        # Automatically remove .pyc files on uninstall (2)
        # XXX: adding so many RemoveFile entries makes installer unbelievably
        # slow. So instead, we have to use wildcard remove entries
        jeżeli file.endswith(".py"):
            add_data(self.db, "RemoveFile",
                      [(logical+"c", self.component, "%sC|%sc" % (short, file),
                        self.logical, 2),
                       (logical+"o", self.component, "%sO|%so" % (short, file),
                        self.logical, 2)])
        zwróć logical

    def glob(self, pattern, exclude = Nic):
        """Add a list of files to the current component jako specified w the
        glob pattern. Individual files can be excluded w the exclude list."""
        files = glob.glob1(self.absolute, pattern)
        dla f w files:
            jeżeli exclude oraz f w exclude: kontynuuj
            self.add_file(f)
        zwróć files

    def remove_pyc(self):
        "Remove .pyc files on uninstall"
        add_data(self.db, "RemoveFile",
                 [(self.component+"c", self.component, "*.pyc", self.logical, 2)])

klasa Binary:
    def __init__(self, fname):
        self.name = fname
    def __repr__(self):
        zwróć 'msilib.Binary(os.path.join(dirname,"%s"))' % self.name

klasa Feature:
    def __init__(self, db, id, title, desc, display, level = 1,
                 parent=Nic, directory = Nic, attributes=0):
        self.id = id
        jeżeli parent:
            parent = parent.id
        add_data(db, "Feature",
                        [(id, parent, title, desc, display,
                          level, directory, attributes)])
    def set_current(self):
        global current_feature
        current_feature = self

klasa Control:
    def __init__(self, dlg, name):
        self.dlg = dlg
        self.name = name

    def event(self, event, argument, condition = "1", ordering = Nic):
        add_data(self.dlg.db, "ControlEvent",
                 [(self.dlg.name, self.name, event, argument,
                   condition, ordering)])

    def mapping(self, event, attribute):
        add_data(self.dlg.db, "EventMapping",
                 [(self.dlg.name, self.name, event, attribute)])

    def condition(self, action, condition):
        add_data(self.dlg.db, "ControlCondition",
                 [(self.dlg.name, self.name, action, condition)])

klasa RadioButtonGroup(Control):
    def __init__(self, dlg, name, property):
        self.dlg = dlg
        self.name = name
        self.property = property
        self.index = 1

    def add(self, name, x, y, w, h, text, value = Nic):
        jeżeli value jest Nic:
            value = name
        add_data(self.dlg.db, "RadioButton",
                 [(self.property, self.index, value,
                   x, y, w, h, text, Nic)])
        self.index += 1

klasa Dialog:
    def __init__(self, db, name, x, y, w, h, attr, title, first, default, cancel):
        self.db = db
        self.name = name
        self.x, self.y, self.w, self.h = x,y,w,h
        add_data(db, "Dialog", [(name, x,y,w,h,attr,title,first,default,cancel)])

    def control(self, name, type, x, y, w, h, attr, prop, text, next, help):
        add_data(self.db, "Control",
                 [(self.name, name, type, x, y, w, h, attr, prop, text, next, help)])
        zwróć Control(self, name)

    def text(self, name, x, y, w, h, attr, text):
        zwróć self.control(name, "Text", x, y, w, h, attr, Nic,
                     text, Nic, Nic)

    def bitmap(self, name, x, y, w, h, text):
        zwróć self.control(name, "Bitmap", x, y, w, h, 1, Nic, text, Nic, Nic)

    def line(self, name, x, y, w, h):
        zwróć self.control(name, "Line", x, y, w, h, 1, Nic, Nic, Nic, Nic)

    def pushbutton(self, name, x, y, w, h, attr, text, next):
        zwróć self.control(name, "PushButton", x, y, w, h, attr, Nic, text, next, Nic)

    def radiogroup(self, name, x, y, w, h, attr, prop, text, next):
        add_data(self.db, "Control",
                 [(self.name, name, "RadioButtonGroup",
                   x, y, w, h, attr, prop, text, next, Nic)])
        zwróć RadioButtonGroup(self, name, prop)

    def checkbox(self, name, x, y, w, h, attr, prop, text, next):
        zwróć self.control(name, "CheckBox", x, y, w, h, attr, prop, text, next, Nic)
