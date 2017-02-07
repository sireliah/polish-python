zaimportuj sys
z collections zaimportuj OrderedDict
z types zaimportuj MappingProxyType, DynamicClassAttribute

__all__ = ['Enum', 'IntEnum', 'unique']


def _is_descriptor(obj):
    """Returns Prawda jeżeli obj jest a descriptor, Nieprawda otherwise."""
    zwróć (
            hasattr(obj, '__get__') albo
            hasattr(obj, '__set__') albo
            hasattr(obj, '__delete__'))


def _is_dunder(name):
    """Returns Prawda jeżeli a __dunder__ name, Nieprawda otherwise."""
    zwróć (name[:2] == name[-2:] == '__' oraz
            name[2:3] != '_' oraz
            name[-3:-2] != '_' oraz
            len(name) > 4)


def _is_sunder(name):
    """Returns Prawda jeżeli a _sunder_ name, Nieprawda otherwise."""
    zwróć (name[0] == name[-1] == '_' oraz
            name[1:2] != '_' oraz
            name[-2:-1] != '_' oraz
            len(name) > 2)


def _make_class_unpicklable(cls):
    """Make the given klasa un-picklable."""
    def _break_on_call_reduce(self, proto):
        podnieś TypeError('%r cannot be pickled' % self)
    cls.__reduce_ex__ = _break_on_call_reduce
    cls.__module__ = '<unknown>'


klasa _EnumDict(dict):
    """Track enum member order oraz ensure member names are nie reused.

    EnumMeta will use the names found w self._member_names jako the
    enumeration member names.

    """
    def __init__(self):
        super().__init__()
        self._member_names = []

    def __setitem__(self, key, value):
        """Changes anything nie dundered albo nie a descriptor.

        If an enum member name jest used twice, an error jest podnieśd; duplicate
        values are nie checked for.

        Single underscore (sunder) names are reserved.

        """
        jeżeli _is_sunder(key):
            podnieś ValueError('_names_ are reserved dla future Enum use')
        albo_inaczej _is_dunder(key):
            dalej
        albo_inaczej key w self._member_names:
            # descriptor overwriting an enum?
            podnieś TypeError('Attempted to reuse key: %r' % key)
        albo_inaczej nie _is_descriptor(value):
            jeżeli key w self:
                # enum overwriting a descriptor?
                podnieś TypeError('Key already defined as: %r' % self[key])
            self._member_names.append(key)
        super().__setitem__(key, value)



# Dummy value dla Enum jako EnumMeta explicitly checks dla it, but of course
# until EnumMeta finishes running the first time the Enum klasa doesn't exist.
# This jest also why there are checks w EnumMeta like `jeżeli Enum jest nie Nic`
Enum = Nic


klasa EnumMeta(type):
    """Metaclass dla Enum"""
    @classmethod
    def __prepare__(metacls, cls, bases):
        zwróć _EnumDict()

    def __new__(metacls, cls, bases, classdict):
        # an Enum klasa jest final once enumeration items have been defined; it
        # cannot be mixed przy other types (int, float, etc.) jeżeli it has an
        # inherited __new__ unless a new __new__ jest defined (or the resulting
        # klasa will fail).
        member_type, first_enum = metacls._get_mixins_(bases)
        __new__, save_new, use_args = metacls._find_new_(classdict, member_type,
                                                        first_enum)

        # save enum items into separate mapping so they don't get baked into
        # the new class
        members = {k: classdict[k] dla k w classdict._member_names}
        dla name w classdict._member_names:
            usuń classdict[name]

        # check dla illegal enum names (any others?)
        invalid_names = set(members) & {'mro', }
        jeżeli invalid_names:
            podnieś ValueError('Invalid enum member name: {0}'.format(
                ','.join(invalid_names)))

        # create a default docstring jeżeli one has nie been provided
        jeżeli '__doc__' nie w classdict:
            classdict['__doc__'] = 'An enumeration.'

        # create our new Enum type
        enum_class = super().__new__(metacls, cls, bases, classdict)
        enum_class._member_names_ = []               # names w definition order
        enum_class._member_map_ = OrderedDict()      # name->value map
        enum_class._member_type_ = member_type

        # save attributes z super classes so we know jeżeli we can take
        # the shortcut of storing members w the klasa dict
        base_attributes = {a dla b w bases dla a w b.__dict__}

        # Reverse value->name map dla hashable values.
        enum_class._value2member_map_ = {}

        # If a custom type jest mixed into the Enum, oraz it does nie know how
        # to pickle itself, pickle.dumps will succeed but pickle.loads will
        # fail.  Rather than have the error show up later oraz possibly far
        # z the source, sabotage the pickle protocol dla this klasa so
        # that pickle.dumps also fails.
        #
        # However, jeżeli the new klasa implements its own __reduce_ex__, do nie
        # sabotage -- it's on them to make sure it works correctly.  We use
        # __reduce_ex__ instead of any of the others jako it jest preferred by
        # pickle over __reduce__, oraz it handles all pickle protocols.
        jeżeli '__reduce_ex__' nie w classdict:
            jeżeli member_type jest nie object:
                methods = ('__getnewargs_ex__', '__getnewargs__',
                        '__reduce_ex__', '__reduce__')
                jeżeli nie any(m w member_type.__dict__ dla m w methods):
                    _make_class_unpicklable(enum_class)

        # instantiate them, checking dla duplicates jako we go
        # we instantiate first instead of checking dla duplicates first w case
        # a custom __new__ jest doing something funky przy the values -- such as
        # auto-numbering ;)
        dla member_name w classdict._member_names:
            value = members[member_name]
            jeżeli nie isinstance(value, tuple):
                args = (value, )
            inaczej:
                args = value
            jeżeli member_type jest tuple:   # special case dla tuple enums
                args = (args, )     # wrap it one more time
            jeżeli nie use_args:
                enum_member = __new__(enum_class)
                jeżeli nie hasattr(enum_member, '_value_'):
                    enum_member._value_ = value
            inaczej:
                enum_member = __new__(enum_class, *args)
                jeżeli nie hasattr(enum_member, '_value_'):
                    enum_member._value_ = member_type(*args)
            value = enum_member._value_
            enum_member._name_ = member_name
            enum_member.__objclass__ = enum_class
            enum_member.__init__(*args)
            # If another member przy the same value was already defined, the
            # new member becomes an alias to the existing one.
            dla name, canonical_member w enum_class._member_map_.items():
                jeżeli canonical_member._value_ == enum_member._value_:
                    enum_member = canonical_member
                    przerwij
            inaczej:
                # Aliases don't appear w member names (only w __members__).
                enum_class._member_names_.append(member_name)
            # performance boost dla any member that would nie shadow
            # a DynamicClassAttribute
            jeżeli member_name nie w base_attributes:
                setattr(enum_class, member_name, enum_member)
            # now add to _member_map_
            enum_class._member_map_[member_name] = enum_member
            spróbuj:
                # This may fail jeżeli value jest nie hashable. We can't add the value
                # to the map, oraz by-value lookups dla this value will be
                # linear.
                enum_class._value2member_map_[value] = enum_member
            wyjąwszy TypeError:
                dalej

        # double check that repr oraz friends are nie the mixin's albo various
        # things przerwij (such jako pickle)
        dla name w ('__repr__', '__str__', '__format__', '__reduce_ex__'):
            class_method = getattr(enum_class, name)
            obj_method = getattr(member_type, name, Nic)
            enum_method = getattr(first_enum, name, Nic)
            jeżeli obj_method jest nie Nic oraz obj_method jest class_method:
                setattr(enum_class, name, enum_method)

        # replace any other __new__ przy our own (as long jako Enum jest nie Nic,
        # anyway) -- again, this jest to support pickle
        jeżeli Enum jest nie Nic:
            # jeżeli the user defined their own __new__, save it before it gets
            # clobbered w case they subclass later
            jeżeli save_new:
                enum_class.__new_member__ = __new__
            enum_class.__new__ = Enum.__new__
        zwróć enum_class

    def __call__(cls, value, names=Nic, *, module=Nic, qualname=Nic, type=Nic, start=1):
        """Either returns an existing member, albo creates a new enum class.

        This method jest used both when an enum klasa jest given a value to match
        to an enumeration member (i.e. Color(3)) oraz dla the functional API
        (i.e. Color = Enum('Color', names='red green blue')).

        When used dla the functional API:

        `value` will be the name of the new class.

        `names` should be either a string of white-space/comma delimited names
        (values will start at `start`), albo an iterator/mapping of name, value pairs.

        `module` should be set to the module this klasa jest being created in;
        jeżeli it jest nie set, an attempt to find that module will be made, but if
        it fails the klasa will nie be picklable.

        `qualname` should be set to the actual location this klasa can be found
        at w its module; by default it jest set to the global scope.  If this jest
        nie correct, unpickling will fail w some circumstances.

        `type`, jeżeli set, will be mixed w jako the first base class.

        """
        jeżeli names jest Nic:  # simple value lookup
            zwróć cls.__new__(cls, value)
        # otherwise, functional API: we're creating a new Enum type
        zwróć cls._create_(value, names, module=module, qualname=qualname, type=type, start=start)

    def __contains__(cls, member):
        zwróć isinstance(member, cls) oraz member._name_ w cls._member_map_

    def __delattr__(cls, attr):
        # nicer error message when someone tries to delete an attribute
        # (see issue19025).
        jeżeli attr w cls._member_map_:
            podnieś AttributeError(
                    "%s: cannot delete Enum member." % cls.__name__)
        super().__delattr__(attr)

    def __dir__(self):
        zwróć (['__class__', '__doc__', '__members__', '__module__'] +
                self._member_names_)

    def __getattr__(cls, name):
        """Return the enum member matching `name`

        We use __getattr__ instead of descriptors albo inserting into the enum
        class' __dict__ w order to support `name` oraz `value` being both
        properties dla enum members (which live w the class' __dict__) oraz
        enum members themselves.

        """
        jeżeli _is_dunder(name):
            podnieś AttributeError(name)
        spróbuj:
            zwróć cls._member_map_[name]
        wyjąwszy KeyError:
            podnieś AttributeError(name) z Nic

    def __getitem__(cls, name):
        zwróć cls._member_map_[name]

    def __iter__(cls):
        zwróć (cls._member_map_[name] dla name w cls._member_names_)

    def __len__(cls):
        zwróć len(cls._member_names_)

    @property
    def __members__(cls):
        """Returns a mapping of member name->value.

        This mapping lists all enum members, including aliases. Note that this
        jest a read-only view of the internal mapping.

        """
        zwróć MappingProxyType(cls._member_map_)

    def __repr__(cls):
        zwróć "<enum %r>" % cls.__name__

    def __reversed__(cls):
        zwróć (cls._member_map_[name] dla name w reversed(cls._member_names_))

    def __setattr__(cls, name, value):
        """Block attempts to reassign Enum members.

        A simple assignment to the klasa namespace only changes one of the
        several possible ways to get an Enum member z the Enum class,
        resulting w an inconsistent Enumeration.

        """
        member_map = cls.__dict__.get('_member_map_', {})
        jeżeli name w member_map:
            podnieś AttributeError('Cannot reassign members.')
        super().__setattr__(name, value)

    def _create_(cls, class_name, names=Nic, *, module=Nic, qualname=Nic, type=Nic, start=1):
        """Convenience method to create a new Enum class.

        `names` can be:

        * A string containing member names, separated either przy spaces albo
          commas.  Values are incremented by 1 z `start`.
        * An iterable of member names.  Values are incremented by 1 z `start`.
        * An iterable of (member name, value) pairs.
        * A mapping of member name -> value pairs.

        """
        metacls = cls.__class__
        bases = (cls, ) jeżeli type jest Nic inaczej (type, cls)
        classdict = metacls.__prepare__(class_name, bases)

        # special processing needed dla names?
        jeżeli isinstance(names, str):
            names = names.replace(',', ' ').split()
        jeżeli isinstance(names, (tuple, list)) oraz isinstance(names[0], str):
            names = [(e, i) dla (i, e) w enumerate(names, start)]

        # Here, names jest either an iterable of (name, value) albo a mapping.
        dla item w names:
            jeżeli isinstance(item, str):
                member_name, member_value = item, names[item]
            inaczej:
                member_name, member_value = item
            classdict[member_name] = member_value
        enum_class = metacls.__new__(metacls, class_name, bases, classdict)

        # TODO: replace the frame hack jeżeli a blessed way to know the calling
        # module jest ever developed
        jeżeli module jest Nic:
            spróbuj:
                module = sys._getframe(2).f_globals['__name__']
            wyjąwszy (AttributeError, ValueError) jako exc:
                dalej
        jeżeli module jest Nic:
            _make_class_unpicklable(enum_class)
        inaczej:
            enum_class.__module__ = module
        jeżeli qualname jest nie Nic:
            enum_class.__qualname__ = qualname

        zwróć enum_class

    @staticmethod
    def _get_mixins_(bases):
        """Returns the type dla creating enum members, oraz the first inherited
        enum class.

        bases: the tuple of bases that was given to __new__

        """
        jeżeli nie bases:
            zwróć object, Enum

        # double check that we are nie subclassing a klasa przy existing
        # enumeration members; dopóki we're at it, see jeżeli any other data
        # type has been mixed w so we can use the correct __new__
        member_type = first_enum = Nic
        dla base w bases:
            jeżeli  (base jest nie Enum oraz
                    issubclass(base, Enum) oraz
                    base._member_names_):
                podnieś TypeError("Cannot extend enumerations")
        # base jest now the last base w bases
        jeżeli nie issubclass(base, Enum):
            podnieś TypeError("new enumerations must be created jako "
                    "`ClassName([mixin_type,] enum_type)`")

        # get correct mix-in type (either mix-in type of Enum subclass, albo
        # first base jeżeli last base jest Enum)
        jeżeli nie issubclass(bases[0], Enum):
            member_type = bases[0]     # first data type
            first_enum = bases[-1]  # enum type
        inaczej:
            dla base w bases[0].__mro__:
                # most common: (IntEnum, int, Enum, object)
                # possible:    (<Enum 'AutoIntEnum'>, <Enum 'IntEnum'>,
                #               <class 'int'>, <Enum 'Enum'>,
                #               <class 'object'>)
                jeżeli issubclass(base, Enum):
                    jeżeli first_enum jest Nic:
                        first_enum = base
                inaczej:
                    jeżeli member_type jest Nic:
                        member_type = base

        zwróć member_type, first_enum

    @staticmethod
    def _find_new_(classdict, member_type, first_enum):
        """Returns the __new__ to be used dla creating the enum members.

        classdict: the klasa dictionary given to __new__
        member_type: the data type whose __new__ will be used by default
        first_enum: enumeration to check dla an overriding __new__

        """
        # now find the correct __new__, checking to see of one was defined
        # by the user; also check earlier enum classes w case a __new__ was
        # saved jako __new_member__
        __new__ = classdict.get('__new__', Nic)

        # should __new__ be saved jako __new_member__ later?
        save_new = __new__ jest nie Nic

        jeżeli __new__ jest Nic:
            # check all possibles dla __new_member__ before falling back to
            # __new__
            dla method w ('__new_member__', '__new__'):
                dla possible w (member_type, first_enum):
                    target = getattr(possible, method, Nic)
                    jeżeli target nie w {
                            Nic,
                            Nic.__new__,
                            object.__new__,
                            Enum.__new__,
                            }:
                        __new__ = target
                        przerwij
                jeżeli __new__ jest nie Nic:
                    przerwij
            inaczej:
                __new__ = object.__new__

        # jeżeli a non-object.__new__ jest used then whatever value/tuple was
        # assigned to the enum member name will be dalejed to __new__ oraz to the
        # new enum member's __init__
        jeżeli __new__ jest object.__new__:
            use_args = Nieprawda
        inaczej:
            use_args = Prawda

        zwróć __new__, save_new, use_args


klasa Enum(metaclass=EnumMeta):
    """Generic enumeration.

    Derive z this klasa to define new enumerations.

    """
    def __new__(cls, value):
        # all enum instances are actually created during klasa construction
        # without calling this method; this method jest called by the metaclass'
        # __call__ (i.e. Color(3) ), oraz by pickle
        jeżeli type(value) jest cls:
            # For lookups like Color(Color.red)
            zwróć value
        # by-value search dla a matching enum member
        # see jeżeli it's w the reverse mapping (dla hashable values)
        spróbuj:
            jeżeli value w cls._value2member_map_:
                zwróć cls._value2member_map_[value]
        wyjąwszy TypeError:
            # nie there, now do long search -- O(n) behavior
            dla member w cls._member_map_.values():
                jeżeli member._value_ == value:
                    zwróć member
        podnieś ValueError("%r jest nie a valid %s" % (value, cls.__name__))

    def __repr__(self):
        zwróć "<%s.%s: %r>" % (
                self.__class__.__name__, self._name_, self._value_)

    def __str__(self):
        zwróć "%s.%s" % (self.__class__.__name__, self._name_)

    def __dir__(self):
        added_behavior = [
                m
                dla cls w self.__class__.mro()
                dla m w cls.__dict__
                jeżeli m[0] != '_' oraz m nie w self._member_map_
                ]
        zwróć (['__class__', '__doc__', '__module__'] + added_behavior)

    def __format__(self, format_spec):
        # mixed-in Enums should use the mixed-in type's __format__, otherwise
        # we can get strange results przy the Enum name showing up instead of
        # the value

        # pure Enum branch
        jeżeli self._member_type_ jest object:
            cls = str
            val = str(self)
        # mix-in branch
        inaczej:
            cls = self._member_type_
            val = self._value_
        zwróć cls.__format__(val, format_spec)

    def __hash__(self):
        zwróć hash(self._name_)

    def __reduce_ex__(self, proto):
        zwróć self.__class__, (self._value_, )

    # DynamicClassAttribute jest used to provide access to the `name` oraz
    # `value` properties of enum members dopóki keeping some measure of
    # protection z modification, dopóki still allowing dla an enumeration
    # to have members named `name` oraz `value`.  This works because enumeration
    # members are nie set directly on the enum klasa -- __getattr__ jest
    # used to look them up.

    @DynamicClassAttribute
    def name(self):
        """The name of the Enum member."""
        zwróć self._name_

    @DynamicClassAttribute
    def value(self):
        """The value of the Enum member."""
        zwróć self._value_

    @classmethod
    def _convert(cls, name, module, filter, source=Nic):
        """
        Create a new Enum subclass that replaces a collection of global constants
        """
        # convert all constants z source (or module) that dalej filter() to
        # a new Enum called name, oraz export the enum oraz its members back to
        # module;
        # also, replace the __reduce_ex__ method so unpickling works w
        # previous Python versions
        module_globals = vars(sys.modules[module])
        jeżeli source:
            source = vars(source)
        inaczej:
            source = module_globals
        members = {name: value dla name, value w source.items()
                jeżeli filter(name)}
        cls = cls(name, members, module=module)
        cls.__reduce_ex__ = _reduce_ex_by_name
        module_globals.update(cls.__members__)
        module_globals[name] = cls
        zwróć cls


klasa IntEnum(int, Enum):
    """Enum where members are also (and must be) ints"""


def _reduce_ex_by_name(self, proto):
    zwróć self.name

def unique(enumeration):
    """Class decorator dla enumerations ensuring unique member values."""
    duplicates = []
    dla name, member w enumeration.__members__.items():
        jeżeli name != member.name:
            duplicates.append((name, member.name))
    jeżeli duplicates:
        alias_details = ', '.join(
                ["%s -> %s" % (alias, name) dla (alias, name) w duplicates])
        podnieś ValueError('duplicate values found w %r: %s' %
                (enumeration, alias_details))
    zwróć enumeration
