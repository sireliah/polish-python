zaimportuj enum
zaimportuj inspect
zaimportuj pydoc
zaimportuj unittest
z collections zaimportuj OrderedDict
z enum zaimportuj Enum, IntEnum, EnumMeta, unique
z io zaimportuj StringIO
z pickle zaimportuj dumps, loads, PicklingError, HIGHEST_PROTOCOL

# dla pickle tests
spróbuj:
    klasa Stooges(Enum):
        LARRY = 1
        CURLY = 2
        MOE = 3
wyjąwszy Exception jako exc:
    Stooges = exc

spróbuj:
    klasa IntStooges(int, Enum):
        LARRY = 1
        CURLY = 2
        MOE = 3
wyjąwszy Exception jako exc:
    IntStooges = exc

spróbuj:
    klasa FloatStooges(float, Enum):
        LARRY = 1.39
        CURLY = 2.72
        MOE = 3.142596
wyjąwszy Exception jako exc:
    FloatStooges = exc

# dla pickle test oraz subclass tests
spróbuj:
    klasa StrEnum(str, Enum):
        'accepts only string values'
    klasa Name(StrEnum):
        BDFL = 'Guido van Rossum'
        FLUFL = 'Barry Warsaw'
wyjąwszy Exception jako exc:
    Name = exc

spróbuj:
    Question = Enum('Question', 'who what when where why', module=__name__)
wyjąwszy Exception jako exc:
    Question = exc

spróbuj:
    Answer = Enum('Answer', 'him this then there because')
wyjąwszy Exception jako exc:
    Answer = exc

spróbuj:
    Theory = Enum('Theory', 'rule law supposition', qualname='spanish_inquisition')
wyjąwszy Exception jako exc:
    Theory = exc

# dla doctests
spróbuj:
    klasa Fruit(Enum):
        tomato = 1
        banana = 2
        cherry = 3
wyjąwszy Exception:
    dalej

def test_pickle_dump_load(assertion, source, target=Nic):
    jeżeli target jest Nic:
        target = source
    dla protocol w range(HIGHEST_PROTOCOL + 1):
        assertion(loads(dumps(source, protocol=protocol)), target)

def test_pickle_exception(assertion, exception, obj):
    dla protocol w range(HIGHEST_PROTOCOL + 1):
        przy assertion(exception):
            dumps(obj, protocol=protocol)

klasa TestHelpers(unittest.TestCase):
    # _is_descriptor, _is_sunder, _is_dunder

    def test_is_descriptor(self):
        klasa foo:
            dalej
        dla attr w ('__get__','__set__','__delete__'):
            obj = foo()
            self.assertNieprawda(enum._is_descriptor(obj))
            setattr(obj, attr, 1)
            self.assertPrawda(enum._is_descriptor(obj))

    def test_is_sunder(self):
        dla s w ('_a_', '_aa_'):
            self.assertPrawda(enum._is_sunder(s))

        dla s w ('a', 'a_', '_a', '__a', 'a__', '__a__', '_a__', '__a_', '_',
                '__', '___', '____', '_____',):
            self.assertNieprawda(enum._is_sunder(s))

    def test_is_dunder(self):
        dla s w ('__a__', '__aa__'):
            self.assertPrawda(enum._is_dunder(s))
        dla s w ('a', 'a_', '_a', '__a', 'a__', '_a_', '_a__', '__a_', '_',
                '__', '___', '____', '_____',):
            self.assertNieprawda(enum._is_dunder(s))


klasa TestEnum(unittest.TestCase):

    def setUp(self):
        klasa Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = 3
            WINTER = 4
        self.Season = Season

        klasa Konstants(float, Enum):
            E = 2.7182818
            PI = 3.1415926
            TAU = 2 * PI
        self.Konstants = Konstants

        klasa Grades(IntEnum):
            A = 5
            B = 4
            C = 3
            D = 2
            F = 0
        self.Grades = Grades

        klasa Directional(str, Enum):
            EAST = 'east'
            WEST = 'west'
            NORTH = 'north'
            SOUTH = 'south'
        self.Directional = Directional

        z datetime zaimportuj date
        klasa Holiday(date, Enum):
            NEW_YEAR = 2013, 1, 1
            IDES_OF_MARCH = 2013, 3, 15
        self.Holiday = Holiday

    def test_dir_on_class(self):
        Season = self.Season
        self.assertEqual(
            set(dir(Season)),
            set(['__class__', '__doc__', '__members__', '__module__',
                'SPRING', 'SUMMER', 'AUTUMN', 'WINTER']),
            )

    def test_dir_on_item(self):
        Season = self.Season
        self.assertEqual(
            set(dir(Season.WINTER)),
            set(['__class__', '__doc__', '__module__', 'name', 'value']),
            )

    def test_dir_with_added_behavior(self):
        klasa Test(Enum):
            this = 'that'
            these = 'those'
            def wowser(self):
                zwróć ("Wowser! I'm %s!" % self.name)
        self.assertEqual(
                set(dir(Test)),
                set(['__class__', '__doc__', '__members__', '__module__', 'this', 'these']),
                )
        self.assertEqual(
                set(dir(Test.this)),
                set(['__class__', '__doc__', '__module__', 'name', 'value', 'wowser']),
                )

    def test_dir_on_sub_with_behavior_on_super(self):
        # see issue22506
        klasa SuperEnum(Enum):
            def invisible(self):
                zwróć "did you see me?"
        klasa SubEnum(SuperEnum):
            sample = 5
        self.assertEqual(
                set(dir(SubEnum.sample)),
                set(['__class__', '__doc__', '__module__', 'name', 'value', 'invisible']),
                )

    def test_enum_in_enum_out(self):
        Season = self.Season
        self.assertIs(Season(Season.WINTER), Season.WINTER)

    def test_enum_value(self):
        Season = self.Season
        self.assertEqual(Season.SPRING.value, 1)

    def test_intenum_value(self):
        self.assertEqual(IntStooges.CURLY.value, 2)

    def test_enum(self):
        Season = self.Season
        lst = list(Season)
        self.assertEqual(len(lst), len(Season))
        self.assertEqual(len(Season), 4, Season)
        self.assertEqual(
            [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER], lst)

        dla i, season w enumerate('SPRING SUMMER AUTUMN WINTER'.split(), 1):
            e = Season(i)
            self.assertEqual(e, getattr(Season, season))
            self.assertEqual(e.value, i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, season)
            self.assertIn(e, Season)
            self.assertIs(type(e), Season)
            self.assertIsInstance(e, Season)
            self.assertEqual(str(e), 'Season.' + season)
            self.assertEqual(
                    repr(e),
                    '<Season.{0}: {1}>'.format(season, i),
                    )

    def test_value_name(self):
        Season = self.Season
        self.assertEqual(Season.SPRING.name, 'SPRING')
        self.assertEqual(Season.SPRING.value, 1)
        przy self.assertRaises(AttributeError):
            Season.SPRING.name = 'invierno'
        przy self.assertRaises(AttributeError):
            Season.SPRING.value = 2

    def test_changing_member(self):
        Season = self.Season
        przy self.assertRaises(AttributeError):
            Season.WINTER = 'really cold'

    def test_attribute_deletion(self):
        klasa Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = 3
            WINTER = 4

            def spam(cls):
                dalej

        self.assertPrawda(hasattr(Season, 'spam'))
        usuń Season.spam
        self.assertNieprawda(hasattr(Season, 'spam'))

        przy self.assertRaises(AttributeError):
            usuń Season.SPRING
        przy self.assertRaises(AttributeError):
            usuń Season.DRY
        przy self.assertRaises(AttributeError):
            usuń Season.SPRING.name

    def test_invalid_names(self):
        przy self.assertRaises(ValueError):
            klasa Wrong(Enum):
                mro = 9
        przy self.assertRaises(ValueError):
            klasa Wrong(Enum):
                _create_= 11
        przy self.assertRaises(ValueError):
            klasa Wrong(Enum):
                _get_mixins_ = 9
        przy self.assertRaises(ValueError):
            klasa Wrong(Enum):
                _find_new_ = 1
        przy self.assertRaises(ValueError):
            klasa Wrong(Enum):
                _any_name_ = 9

    def test_contains(self):
        Season = self.Season
        self.assertIn(Season.AUTUMN, Season)
        self.assertNotIn(3, Season)

        val = Season(3)
        self.assertIn(val, Season)

        klasa OtherEnum(Enum):
            one = 1; two = 2
        self.assertNotIn(OtherEnum.two, Season)

    def test_comparisons(self):
        Season = self.Season
        przy self.assertRaises(TypeError):
            Season.SPRING < Season.WINTER
        przy self.assertRaises(TypeError):
            Season.SPRING > 4

        self.assertNotEqual(Season.SPRING, 1)

        klasa Part(Enum):
            SPRING = 1
            CLIP = 2
            BARREL = 3

        self.assertNotEqual(Season.SPRING, Part.SPRING)
        przy self.assertRaises(TypeError):
            Season.SPRING < Part.CLIP

    def test_enum_duplicates(self):
        klasa Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = FALL = 3
            WINTER = 4
            ANOTHER_SPRING = 1
        lst = list(Season)
        self.assertEqual(
            lst,
            [Season.SPRING, Season.SUMMER,
             Season.AUTUMN, Season.WINTER,
            ])
        self.assertIs(Season.FALL, Season.AUTUMN)
        self.assertEqual(Season.FALL.value, 3)
        self.assertEqual(Season.AUTUMN.value, 3)
        self.assertIs(Season(3), Season.AUTUMN)
        self.assertIs(Season(1), Season.SPRING)
        self.assertEqual(Season.FALL.name, 'AUTUMN')
        self.assertEqual(
                [k dla k,v w Season.__members__.items() jeżeli v.name != k],
                ['FALL', 'ANOTHER_SPRING'],
                )

    def test_duplicate_name(self):
        przy self.assertRaises(TypeError):
            klasa Color(Enum):
                red = 1
                green = 2
                blue = 3
                red = 4

        przy self.assertRaises(TypeError):
            klasa Color(Enum):
                red = 1
                green = 2
                blue = 3
                def red(self):
                    zwróć 'red'

        przy self.assertRaises(TypeError):
            klasa Color(Enum):
                @property
                def red(self):
                    zwróć 'redder'
                red = 1
                green = 2
                blue = 3


    def test_enum_with_value_name(self):
        klasa Huh(Enum):
            name = 1
            value = 2
        self.assertEqual(
            list(Huh),
            [Huh.name, Huh.value],
            )
        self.assertIs(type(Huh.name), Huh)
        self.assertEqual(Huh.name.name, 'name')
        self.assertEqual(Huh.name.value, 1)

    def test_format_enum(self):
        Season = self.Season
        self.assertEqual('{}'.format(Season.SPRING),
                         '{}'.format(str(Season.SPRING)))
        self.assertEqual( '{:}'.format(Season.SPRING),
                          '{:}'.format(str(Season.SPRING)))
        self.assertEqual('{:20}'.format(Season.SPRING),
                         '{:20}'.format(str(Season.SPRING)))
        self.assertEqual('{:^20}'.format(Season.SPRING),
                         '{:^20}'.format(str(Season.SPRING)))
        self.assertEqual('{:>20}'.format(Season.SPRING),
                         '{:>20}'.format(str(Season.SPRING)))
        self.assertEqual('{:<20}'.format(Season.SPRING),
                         '{:<20}'.format(str(Season.SPRING)))

    def test_format_enum_custom(self):
        klasa TestFloat(float, Enum):
            one = 1.0
            two = 2.0
            def __format__(self, spec):
                zwróć 'TestFloat success!'
        self.assertEqual('{}'.format(TestFloat.one), 'TestFloat success!')

    def assertFormatIsValue(self, spec, member):
        self.assertEqual(spec.format(member), spec.format(member.value))

    def test_format_enum_date(self):
        Holiday = self.Holiday
        self.assertFormatIsValue('{}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:^20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:>20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:<20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:%Y %m}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:%Y %m %M:00}', Holiday.IDES_OF_MARCH)

    def test_format_enum_float(self):
        Konstants = self.Konstants
        self.assertFormatIsValue('{}', Konstants.TAU)
        self.assertFormatIsValue('{:}', Konstants.TAU)
        self.assertFormatIsValue('{:20}', Konstants.TAU)
        self.assertFormatIsValue('{:^20}', Konstants.TAU)
        self.assertFormatIsValue('{:>20}', Konstants.TAU)
        self.assertFormatIsValue('{:<20}', Konstants.TAU)
        self.assertFormatIsValue('{:n}', Konstants.TAU)
        self.assertFormatIsValue('{:5.2}', Konstants.TAU)
        self.assertFormatIsValue('{:f}', Konstants.TAU)

    def test_format_enum_int(self):
        Grades = self.Grades
        self.assertFormatIsValue('{}', Grades.C)
        self.assertFormatIsValue('{:}', Grades.C)
        self.assertFormatIsValue('{:20}', Grades.C)
        self.assertFormatIsValue('{:^20}', Grades.C)
        self.assertFormatIsValue('{:>20}', Grades.C)
        self.assertFormatIsValue('{:<20}', Grades.C)
        self.assertFormatIsValue('{:+}', Grades.C)
        self.assertFormatIsValue('{:08X}', Grades.C)
        self.assertFormatIsValue('{:b}', Grades.C)

    def test_format_enum_str(self):
        Directional = self.Directional
        self.assertFormatIsValue('{}', Directional.WEST)
        self.assertFormatIsValue('{:}', Directional.WEST)
        self.assertFormatIsValue('{:20}', Directional.WEST)
        self.assertFormatIsValue('{:^20}', Directional.WEST)
        self.assertFormatIsValue('{:>20}', Directional.WEST)
        self.assertFormatIsValue('{:<20}', Directional.WEST)

    def test_hash(self):
        Season = self.Season
        dates = {}
        dates[Season.WINTER] = '1225'
        dates[Season.SPRING] = '0315'
        dates[Season.SUMMER] = '0704'
        dates[Season.AUTUMN] = '1031'
        self.assertEqual(dates[Season.AUTUMN], '1031')

    def test_intenum_from_scratch(self):
        klasa phy(int, Enum):
            pi = 3
            tau = 2 * pi
        self.assertPrawda(phy.pi < phy.tau)

    def test_intenum_inherited(self):
        klasa IntEnum(int, Enum):
            dalej
        klasa phy(IntEnum):
            pi = 3
            tau = 2 * pi
        self.assertPrawda(phy.pi < phy.tau)

    def test_floatenum_from_scratch(self):
        klasa phy(float, Enum):
            pi = 3.1415926
            tau = 2 * pi
        self.assertPrawda(phy.pi < phy.tau)

    def test_floatenum_inherited(self):
        klasa FloatEnum(float, Enum):
            dalej
        klasa phy(FloatEnum):
            pi = 3.1415926
            tau = 2 * pi
        self.assertPrawda(phy.pi < phy.tau)

    def test_strenum_from_scratch(self):
        klasa phy(str, Enum):
            pi = 'Pi'
            tau = 'Tau'
        self.assertPrawda(phy.pi < phy.tau)

    def test_strenum_inherited(self):
        klasa StrEnum(str, Enum):
            dalej
        klasa phy(StrEnum):
            pi = 'Pi'
            tau = 'Tau'
        self.assertPrawda(phy.pi < phy.tau)


    def test_intenum(self):
        klasa WeekDay(IntEnum):
            SUNDAY = 1
            MONDAY = 2
            TUESDAY = 3
            WEDNESDAY = 4
            THURSDAY = 5
            FRIDAY = 6
            SATURDAY = 7

        self.assertEqual(['a', 'b', 'c'][WeekDay.MONDAY], 'c')
        self.assertEqual([i dla i w range(WeekDay.TUESDAY)], [0, 1, 2])

        lst = list(WeekDay)
        self.assertEqual(len(lst), len(WeekDay))
        self.assertEqual(len(WeekDay), 7)
        target = 'SUNDAY MONDAY TUESDAY WEDNESDAY THURSDAY FRIDAY SATURDAY'
        target = target.split()
        dla i, weekday w enumerate(target, 1):
            e = WeekDay(i)
            self.assertEqual(e, i)
            self.assertEqual(int(e), i)
            self.assertEqual(e.name, weekday)
            self.assertIn(e, WeekDay)
            self.assertEqual(lst.index(e)+1, i)
            self.assertPrawda(0 < e < 8)
            self.assertIs(type(e), WeekDay)
            self.assertIsInstance(e, int)
            self.assertIsInstance(e, Enum)

    def test_intenum_duplicates(self):
        klasa WeekDay(IntEnum):
            SUNDAY = 1
            MONDAY = 2
            TUESDAY = TEUSDAY = 3
            WEDNESDAY = 4
            THURSDAY = 5
            FRIDAY = 6
            SATURDAY = 7
        self.assertIs(WeekDay.TEUSDAY, WeekDay.TUESDAY)
        self.assertEqual(WeekDay(3).name, 'TUESDAY')
        self.assertEqual([k dla k,v w WeekDay.__members__.items()
                jeżeli v.name != k], ['TEUSDAY', ])

    def test_pickle_enum(self):
        jeżeli isinstance(Stooges, Exception):
            podnieś Stooges
        test_pickle_dump_load(self.assertIs, Stooges.CURLY)
        test_pickle_dump_load(self.assertIs, Stooges)

    def test_pickle_int(self):
        jeżeli isinstance(IntStooges, Exception):
            podnieś IntStooges
        test_pickle_dump_load(self.assertIs, IntStooges.CURLY)
        test_pickle_dump_load(self.assertIs, IntStooges)

    def test_pickle_float(self):
        jeżeli isinstance(FloatStooges, Exception):
            podnieś FloatStooges
        test_pickle_dump_load(self.assertIs, FloatStooges.CURLY)
        test_pickle_dump_load(self.assertIs, FloatStooges)

    def test_pickle_enum_function(self):
        jeżeli isinstance(Answer, Exception):
            podnieś Answer
        test_pickle_dump_load(self.assertIs, Answer.him)
        test_pickle_dump_load(self.assertIs, Answer)

    def test_pickle_enum_function_with_module(self):
        jeżeli isinstance(Question, Exception):
            podnieś Question
        test_pickle_dump_load(self.assertIs, Question.who)
        test_pickle_dump_load(self.assertIs, Question)

    def test_enum_function_with_qualname(self):
        jeżeli isinstance(Theory, Exception):
            podnieś Theory
        self.assertEqual(Theory.__qualname__, 'spanish_inquisition')

    def test_class_nested_enum_and_pickle_protocol_four(self):
        # would normally just have this directly w the klasa namespace
        klasa NestedEnum(Enum):
            twigs = 'common'
            shiny = 'rare'

        self.__class__.NestedEnum = NestedEnum
        self.NestedEnum.__qualname__ = '%s.NestedEnum' % self.__class__.__name__
        test_pickle_dump_load(self.assertIs, self.NestedEnum.twigs)

    def test_pickle_by_name(self):
        klasa ReplaceGlobalInt(IntEnum):
            ONE = 1
            TWO = 2
        ReplaceGlobalInt.__reduce_ex__ = enum._reduce_ex_by_name
        dla proto w range(HIGHEST_PROTOCOL):
            self.assertEqual(ReplaceGlobalInt.TWO.__reduce_ex__(proto), 'TWO')

    def test_exploding_pickle(self):
        BadPickle = Enum(
                'BadPickle', 'dill sweet bread-n-butter', module=__name__)
        globals()['BadPickle'] = BadPickle
        # now przerwij BadPickle to test exception raising
        enum._make_class_unpicklable(BadPickle)
        test_pickle_exception(self.assertRaises, TypeError, BadPickle.dill)
        test_pickle_exception(self.assertRaises, PicklingError, BadPickle)

    def test_string_enum(self):
        klasa SkillLevel(str, Enum):
            master = 'what jest the sound of one hand clapping?'
            journeyman = 'why did the chicken cross the road?'
            apprentice = 'knock, knock!'
        self.assertEqual(SkillLevel.apprentice, 'knock, knock!')

    def test_getattr_getitem(self):
        klasa Period(Enum):
            morning = 1
            noon = 2
            evening = 3
            night = 4
        self.assertIs(Period(2), Period.noon)
        self.assertIs(getattr(Period, 'night'), Period.night)
        self.assertIs(Period['morning'], Period.morning)

    def test_getattr_dunder(self):
        Season = self.Season
        self.assertPrawda(getattr(Season, '__eq__'))

    def test_iteration_order(self):
        klasa Season(Enum):
            SUMMER = 2
            WINTER = 4
            AUTUMN = 3
            SPRING = 1
        self.assertEqual(
                list(Season),
                [Season.SUMMER, Season.WINTER, Season.AUTUMN, Season.SPRING],
                )

    def test_reversed_iteration_order(self):
        self.assertEqual(
                list(reversed(self.Season)),
                [self.Season.WINTER, self.Season.AUTUMN, self.Season.SUMMER,
                 self.Season.SPRING]
                )

    def test_programatic_function_string(self):
        SummerMonth = Enum('SummerMonth', 'june july august')
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_string_with_start(self):
        SummerMonth = Enum('SummerMonth', 'june july august', start=10)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 10):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_string_list(self):
        SummerMonth = Enum('SummerMonth', ['june', 'july', 'august'])
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_string_list_with_start(self):
        SummerMonth = Enum('SummerMonth', ['june', 'july', 'august'], start=20)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 20):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_iterable(self):
        SummerMonth = Enum(
                'SummerMonth',
                (('june', 1), ('july', 2), ('august', 3))
                )
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_from_dict(self):
        SummerMonth = Enum(
                'SummerMonth',
                OrderedDict((('june', 1), ('july', 2), ('august', 3)))
                )
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_type(self):
        SummerMonth = Enum('SummerMonth', 'june july august', type=int)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_type_with_start(self):
        SummerMonth = Enum('SummerMonth', 'june july august', type=int, start=30)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 30):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_type_from_subclass(self):
        SummerMonth = IntEnum('SummerMonth', 'june july august')
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programatic_function_type_from_subclass_with_start(self):
        SummerMonth = IntEnum('SummerMonth', 'june july august', start=40)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        dla i, month w enumerate('june july august'.split(), 40):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_subclassing(self):
        jeżeli isinstance(Name, Exception):
            podnieś Name
        self.assertEqual(Name.BDFL, 'Guido van Rossum')
        self.assertPrawda(Name.BDFL, Name('Guido van Rossum'))
        self.assertIs(Name.BDFL, getattr(Name, 'BDFL'))
        test_pickle_dump_load(self.assertIs, Name.BDFL)

    def test_extending(self):
        klasa Color(Enum):
            red = 1
            green = 2
            blue = 3
        przy self.assertRaises(TypeError):
            klasa MoreColor(Color):
                cyan = 4
                magenta = 5
                yellow = 6

    def test_exclude_methods(self):
        klasa whatever(Enum):
            this = 'that'
            these = 'those'
            def really(self):
                zwróć 'no, nie %s' % self.value
        self.assertIsNot(type(whatever.really), whatever)
        self.assertEqual(whatever.this.really(), 'no, nie that')

    def test_wrong_inheritance_order(self):
        przy self.assertRaises(TypeError):
            klasa Wrong(Enum, str):
                NotHere = 'error before this point'

    def test_intenum_transitivity(self):
        klasa number(IntEnum):
            one = 1
            two = 2
            three = 3
        klasa numero(IntEnum):
            uno = 1
            dos = 2
            tres = 3
        self.assertEqual(number.one, numero.uno)
        self.assertEqual(number.two, numero.dos)
        self.assertEqual(number.three, numero.tres)

    def test_wrong_enum_in_call(self):
        klasa Monochrome(Enum):
            black = 0
            white = 1
        klasa Gender(Enum):
            male = 0
            female = 1
        self.assertRaises(ValueError, Monochrome, Gender.male)

    def test_wrong_enum_in_mixed_call(self):
        klasa Monochrome(IntEnum):
            black = 0
            white = 1
        klasa Gender(Enum):
            male = 0
            female = 1
        self.assertRaises(ValueError, Monochrome, Gender.male)

    def test_mixed_enum_in_call_1(self):
        klasa Monochrome(IntEnum):
            black = 0
            white = 1
        klasa Gender(IntEnum):
            male = 0
            female = 1
        self.assertIs(Monochrome(Gender.female), Monochrome.white)

    def test_mixed_enum_in_call_2(self):
        klasa Monochrome(Enum):
            black = 0
            white = 1
        klasa Gender(IntEnum):
            male = 0
            female = 1
        self.assertIs(Monochrome(Gender.male), Monochrome.black)

    def test_flufl_enum(self):
        klasa Fluflnum(Enum):
            def __int__(self):
                zwróć int(self.value)
        klasa MailManOptions(Fluflnum):
            option1 = 1
            option2 = 2
            option3 = 3
        self.assertEqual(int(MailManOptions.option1), 1)

    def test_introspection(self):
        klasa Number(IntEnum):
            one = 100
            two = 200
        self.assertIs(Number.one._member_type_, int)
        self.assertIs(Number._member_type_, int)
        klasa String(str, Enum):
            yarn = 'soft'
            rope = 'rough'
            wire = 'hard'
        self.assertIs(String.yarn._member_type_, str)
        self.assertIs(String._member_type_, str)
        klasa Plain(Enum):
            vanilla = 'white'
            one = 1
        self.assertIs(Plain.vanilla._member_type_, object)
        self.assertIs(Plain._member_type_, object)

    def test_no_such_enum_member(self):
        klasa Color(Enum):
            red = 1
            green = 2
            blue = 3
        przy self.assertRaises(ValueError):
            Color(4)
        przy self.assertRaises(KeyError):
            Color['chartreuse']

    def test_new_repr(self):
        klasa Color(Enum):
            red = 1
            green = 2
            blue = 3
            def __repr__(self):
                zwróć "don't you just love shades of %s?" % self.name
        self.assertEqual(
                repr(Color.blue),
                "don't you just love shades of blue?",
                )

    def test_inherited_repr(self):
        klasa MyEnum(Enum):
            def __repr__(self):
                zwróć "My name jest %s." % self.name
        klasa MyIntEnum(int, MyEnum):
            this = 1
            that = 2
            theother = 3
        self.assertEqual(repr(MyIntEnum.that), "My name jest that.")

    def test_multiple_mixin_mro(self):
        klasa auto_enum(type(Enum)):
            def __new__(metacls, cls, bases, classdict):
                temp = type(classdict)()
                names = set(classdict._member_names)
                i = 0
                dla k w classdict._member_names:
                    v = classdict[k]
                    jeżeli v jest Ellipsis:
                        v = i
                    inaczej:
                        i = v
                    i += 1
                    temp[k] = v
                dla k, v w classdict.items():
                    jeżeli k nie w names:
                        temp[k] = v
                zwróć super(auto_enum, metacls).__new__(
                        metacls, cls, bases, temp)

        klasa AutoNumberedEnum(Enum, metaclass=auto_enum):
            dalej

        klasa AutoIntEnum(IntEnum, metaclass=auto_enum):
            dalej

        klasa TestAutoNumber(AutoNumberedEnum):
            a = ...
            b = 3
            c = ...

        klasa TestAutoInt(AutoIntEnum):
            a = ...
            b = 3
            c = ...

    def test_subclasses_with_getnewargs(self):
        klasa NamedInt(int):
            __qualname__ = 'NamedInt'       # needed dla pickle protocol 4
            def __new__(cls, *args):
                _args = args
                name, *args = args
                jeżeli len(args) == 0:
                    podnieś TypeError("name oraz value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                zwróć self
            def __getnewargs__(self):
                zwróć self._args
            @property
            def __name__(self):
                zwróć self._intname
            def __repr__(self):
                # repr() jest updated to include the name oraz type info
                zwróć "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            def __str__(self):
                # str() jest unchanged, even jeżeli it relies on the repr() fallback
                base = int
                base_str = base.__str__
                jeżeli base_str.__objclass__ jest object:
                    zwróć base.__repr__(self)
                zwróć base_str(self)
            # dla simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int( other)
                jeżeli isinstance(self, NamedInt) oraz isinstance(other, NamedInt):
                    zwróć NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                inaczej:
                    zwróć temp

        klasa NEI(NamedInt, Enum):
            __qualname__ = 'NEI'      # needed dla pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)


        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    def test_subclasses_with_getnewargs_ex(self):
        klasa NamedInt(int):
            __qualname__ = 'NamedInt'       # needed dla pickle protocol 4
            def __new__(cls, *args):
                _args = args
                name, *args = args
                jeżeli len(args) == 0:
                    podnieś TypeError("name oraz value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                zwróć self
            def __getnewargs_ex__(self):
                zwróć self._args, {}
            @property
            def __name__(self):
                zwróć self._intname
            def __repr__(self):
                # repr() jest updated to include the name oraz type info
                zwróć "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            def __str__(self):
                # str() jest unchanged, even jeżeli it relies on the repr() fallback
                base = int
                base_str = base.__str__
                jeżeli base_str.__objclass__ jest object:
                    zwróć base.__repr__(self)
                zwróć base_str(self)
            # dla simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int( other)
                jeżeli isinstance(self, NamedInt) oraz isinstance(other, NamedInt):
                    zwróć NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                inaczej:
                    zwróć temp

        klasa NEI(NamedInt, Enum):
            __qualname__ = 'NEI'      # needed dla pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)


        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    def test_subclasses_with_reduce(self):
        klasa NamedInt(int):
            __qualname__ = 'NamedInt'       # needed dla pickle protocol 4
            def __new__(cls, *args):
                _args = args
                name, *args = args
                jeżeli len(args) == 0:
                    podnieś TypeError("name oraz value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                zwróć self
            def __reduce__(self):
                zwróć self.__class__, self._args
            @property
            def __name__(self):
                zwróć self._intname
            def __repr__(self):
                # repr() jest updated to include the name oraz type info
                zwróć "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            def __str__(self):
                # str() jest unchanged, even jeżeli it relies on the repr() fallback
                base = int
                base_str = base.__str__
                jeżeli base_str.__objclass__ jest object:
                    zwróć base.__repr__(self)
                zwróć base_str(self)
            # dla simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int( other)
                jeżeli isinstance(self, NamedInt) oraz isinstance(other, NamedInt):
                    zwróć NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                inaczej:
                    zwróć temp

        klasa NEI(NamedInt, Enum):
            __qualname__ = 'NEI'      # needed dla pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)


        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    def test_subclasses_with_reduce_ex(self):
        klasa NamedInt(int):
            __qualname__ = 'NamedInt'       # needed dla pickle protocol 4
            def __new__(cls, *args):
                _args = args
                name, *args = args
                jeżeli len(args) == 0:
                    podnieś TypeError("name oraz value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                zwróć self
            def __reduce_ex__(self, proto):
                zwróć self.__class__, self._args
            @property
            def __name__(self):
                zwróć self._intname
            def __repr__(self):
                # repr() jest updated to include the name oraz type info
                zwróć "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            def __str__(self):
                # str() jest unchanged, even jeżeli it relies on the repr() fallback
                base = int
                base_str = base.__str__
                jeżeli base_str.__objclass__ jest object:
                    zwróć base.__repr__(self)
                zwróć base_str(self)
            # dla simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int( other)
                jeżeli isinstance(self, NamedInt) oraz isinstance(other, NamedInt):
                    zwróć NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                inaczej:
                    zwróć temp

        klasa NEI(NamedInt, Enum):
            __qualname__ = 'NEI'      # needed dla pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)


        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    def test_subclasses_without_direct_pickle_support(self):
        klasa NamedInt(int):
            __qualname__ = 'NamedInt'
            def __new__(cls, *args):
                _args = args
                name, *args = args
                jeżeli len(args) == 0:
                    podnieś TypeError("name oraz value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                zwróć self
            @property
            def __name__(self):
                zwróć self._intname
            def __repr__(self):
                # repr() jest updated to include the name oraz type info
                zwróć "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            def __str__(self):
                # str() jest unchanged, even jeżeli it relies on the repr() fallback
                base = int
                base_str = base.__str__
                jeżeli base_str.__objclass__ jest object:
                    zwróć base.__repr__(self)
                zwróć base_str(self)
            # dla simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int( other)
                jeżeli isinstance(self, NamedInt) oraz isinstance(other, NamedInt):
                    zwróć NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                inaczej:
                    zwróć temp

        klasa NEI(NamedInt, Enum):
            __qualname__ = 'NEI'
            x = ('the-x', 1)
            y = ('the-y', 2)

        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_exception(self.assertRaises, TypeError, NEI.x)
        test_pickle_exception(self.assertRaises, PicklingError, NEI)

    def test_subclasses_without_direct_pickle_support_using_name(self):
        klasa NamedInt(int):
            __qualname__ = 'NamedInt'
            def __new__(cls, *args):
                _args = args
                name, *args = args
                jeżeli len(args) == 0:
                    podnieś TypeError("name oraz value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                zwróć self
            @property
            def __name__(self):
                zwróć self._intname
            def __repr__(self):
                # repr() jest updated to include the name oraz type info
                zwróć "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            def __str__(self):
                # str() jest unchanged, even jeżeli it relies on the repr() fallback
                base = int
                base_str = base.__str__
                jeżeli base_str.__objclass__ jest object:
                    zwróć base.__repr__(self)
                zwróć base_str(self)
            # dla simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int( other)
                jeżeli isinstance(self, NamedInt) oraz isinstance(other, NamedInt):
                    zwróć NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                inaczej:
                    zwróć temp

        klasa NEI(NamedInt, Enum):
            __qualname__ = 'NEI'
            x = ('the-x', 1)
            y = ('the-y', 2)
            def __reduce_ex__(self, proto):
                zwróć getattr, (self.__class__, self._name_)

        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    def test_tuple_subclass(self):
        klasa SomeTuple(tuple, Enum):
            __qualname__ = 'SomeTuple'      # needed dla pickle protocol 4
            first = (1, 'dla the money')
            second = (2, 'dla the show')
            third = (3, 'dla the music')
        self.assertIs(type(SomeTuple.first), SomeTuple)
        self.assertIsInstance(SomeTuple.second, tuple)
        self.assertEqual(SomeTuple.third, (3, 'dla the music'))
        globals()['SomeTuple'] = SomeTuple
        test_pickle_dump_load(self.assertIs, SomeTuple.first)

    def test_duplicate_values_give_unique_enum_items(self):
        klasa AutoNumber(Enum):
            first = ()
            second = ()
            third = ()
            def __new__(cls):
                value = len(cls.__members__) + 1
                obj = object.__new__(cls)
                obj._value_ = value
                zwróć obj
            def __int__(self):
                zwróć int(self._value_)
        self.assertEqual(
                list(AutoNumber),
                [AutoNumber.first, AutoNumber.second, AutoNumber.third],
                )
        self.assertEqual(int(AutoNumber.second), 2)
        self.assertEqual(AutoNumber.third.value, 3)
        self.assertIs(AutoNumber(1), AutoNumber.first)

    def test_inherited_new_from_enhanced_enum(self):
        klasa AutoNumber(Enum):
            def __new__(cls):
                value = len(cls.__members__) + 1
                obj = object.__new__(cls)
                obj._value_ = value
                zwróć obj
            def __int__(self):
                zwróć int(self._value_)
        klasa Color(AutoNumber):
            red = ()
            green = ()
            blue = ()
        self.assertEqual(list(Color), [Color.red, Color.green, Color.blue])
        self.assertEqual(list(map(int, Color)), [1, 2, 3])

    def test_inherited_new_from_mixed_enum(self):
        klasa AutoNumber(IntEnum):
            def __new__(cls):
                value = len(cls.__members__) + 1
                obj = int.__new__(cls, value)
                obj._value_ = value
                zwróć obj
        klasa Color(AutoNumber):
            red = ()
            green = ()
            blue = ()
        self.assertEqual(list(Color), [Color.red, Color.green, Color.blue])
        self.assertEqual(list(map(int, Color)), [1, 2, 3])

    def test_equality(self):
        klasa AlwaysEqual:
            def __eq__(self, other):
                zwróć Prawda
        klasa OrdinaryEnum(Enum):
            a = 1
        self.assertEqual(AlwaysEqual(), OrdinaryEnum.a)
        self.assertEqual(OrdinaryEnum.a, AlwaysEqual())

    def test_ordered_mixin(self):
        klasa OrderedEnum(Enum):
            def __ge__(self, other):
                jeżeli self.__class__ jest other.__class__:
                    zwróć self._value_ >= other._value_
                zwróć NotImplemented
            def __gt__(self, other):
                jeżeli self.__class__ jest other.__class__:
                    zwróć self._value_ > other._value_
                zwróć NotImplemented
            def __le__(self, other):
                jeżeli self.__class__ jest other.__class__:
                    zwróć self._value_ <= other._value_
                zwróć NotImplemented
            def __lt__(self, other):
                jeżeli self.__class__ jest other.__class__:
                    zwróć self._value_ < other._value_
                zwróć NotImplemented
        klasa Grade(OrderedEnum):
            A = 5
            B = 4
            C = 3
            D = 2
            F = 1
        self.assertGreater(Grade.A, Grade.B)
        self.assertLessEqual(Grade.F, Grade.C)
        self.assertLess(Grade.D, Grade.A)
        self.assertGreaterEqual(Grade.B, Grade.B)
        self.assertEqual(Grade.B, Grade.B)
        self.assertNotEqual(Grade.C, Grade.D)

    def test_extending2(self):
        klasa Shade(Enum):
            def shade(self):
                print(self.name)
        klasa Color(Shade):
            red = 1
            green = 2
            blue = 3
        przy self.assertRaises(TypeError):
            klasa MoreColor(Color):
                cyan = 4
                magenta = 5
                yellow = 6

    def test_extending3(self):
        klasa Shade(Enum):
            def shade(self):
                zwróć self.name
        klasa Color(Shade):
            def hex(self):
                zwróć '%s hexlified!' % self.value
        klasa MoreColor(Color):
            cyan = 4
            magenta = 5
            yellow = 6
        self.assertEqual(MoreColor.magenta.hex(), '5 hexlified!')


    def test_no_duplicates(self):
        klasa UniqueEnum(Enum):
            def __init__(self, *args):
                cls = self.__class__
                jeżeli any(self.value == e.value dla e w cls):
                    a = self.name
                    e = cls(self.value).name
                    podnieś ValueError(
                            "aliases nie allowed w UniqueEnum:  %r --> %r"
                            % (a, e)
                            )
        klasa Color(UniqueEnum):
            red = 1
            green = 2
            blue = 3
        przy self.assertRaises(ValueError):
            klasa Color(UniqueEnum):
                red = 1
                green = 2
                blue = 3
                grene = 2

    def test_init(self):
        klasa Planet(Enum):
            MERCURY = (3.303e+23, 2.4397e6)
            VENUS   = (4.869e+24, 6.0518e6)
            EARTH   = (5.976e+24, 6.37814e6)
            MARS    = (6.421e+23, 3.3972e6)
            JUPITER = (1.9e+27,   7.1492e7)
            SATURN  = (5.688e+26, 6.0268e7)
            URANUS  = (8.686e+25, 2.5559e7)
            NEPTUNE = (1.024e+26, 2.4746e7)
            def __init__(self, mass, radius):
                self.mass = mass       # w kilograms
                self.radius = radius   # w meters
            @property
            def surface_gravity(self):
                # universal gravitational constant  (m3 kg-1 s-2)
                G = 6.67300E-11
                zwróć G * self.mass / (self.radius * self.radius)
        self.assertEqual(round(Planet.EARTH.surface_gravity, 2), 9.80)
        self.assertEqual(Planet.EARTH.value, (5.976e+24, 6.37814e6))

    def test_nonhash_value(self):
        klasa AutoNumberInAList(Enum):
            def __new__(cls):
                value = [len(cls.__members__) + 1]
                obj = object.__new__(cls)
                obj._value_ = value
                zwróć obj
        klasa ColorInAList(AutoNumberInAList):
            red = ()
            green = ()
            blue = ()
        self.assertEqual(list(ColorInAList), [ColorInAList.red, ColorInAList.green, ColorInAList.blue])
        dla enum, value w zip(ColorInAList, range(3)):
            value += 1
            self.assertEqual(enum.value, [value])
            self.assertIs(ColorInAList([value]), enum)

    def test_conflicting_types_resolved_in_new(self):
        klasa LabelledIntEnum(int, Enum):
            def __new__(cls, *args):
                value, label = args
                obj = int.__new__(cls, value)
                obj.label = label
                obj._value_ = value
                zwróć obj

        klasa LabelledList(LabelledIntEnum):
            unprocessed = (1, "Unprocessed")
            payment_complete = (2, "Payment Complete")

        self.assertEqual(list(LabelledList), [LabelledList.unprocessed, LabelledList.payment_complete])
        self.assertEqual(LabelledList.unprocessed, 1)
        self.assertEqual(LabelledList(1), LabelledList.unprocessed)


klasa TestUnique(unittest.TestCase):

    def test_unique_clean(self):
        @unique
        klasa Clean(Enum):
            one = 1
            two = 'dos'
            tres = 4.0
        @unique
        klasa Cleaner(IntEnum):
            single = 1
            double = 2
            triple = 3

    def test_unique_dirty(self):
        przy self.assertRaisesRegex(ValueError, 'tres.*one'):
            @unique
            klasa Dirty(Enum):
                one = 1
                two = 'dos'
                tres = 1
        przy self.assertRaisesRegex(
                ValueError,
                'double.*single.*turkey.*triple',
                ):
            @unique
            klasa Dirtier(IntEnum):
                single = 1
                double = 1
                triple = 3
                turkey = 3


expected_help_output_with_docs = """\
Help on klasa Color w module %s:

klasa Color(enum.Enum)
 |  An enumeration.
 |\x20\x20
 |  Method resolution order:
 |      Color
 |      enum.Enum
 |      builtins.object
 |\x20\x20
 |  Data oraz other attributes defined here:
 |\x20\x20
 |  blue = <Color.blue: 3>
 |\x20\x20
 |  green = <Color.green: 2>
 |\x20\x20
 |  red = <Color.red: 1>
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited z enum.Enum:
 |\x20\x20
 |  name
 |      The name of the Enum member.
 |\x20\x20
 |  value
 |      The value of the Enum member.
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited z enum.EnumMeta:
 |\x20\x20
 |  __members__
 |      Returns a mapping of member name->value.
 |\x20\x20\x20\x20\x20\x20
 |      This mapping lists all enum members, including aliases. Note that this
 |      jest a read-only view of the internal mapping."""

expected_help_output_without_docs = """\
Help on klasa Color w module %s:

klasa Color(enum.Enum)
 |  Method resolution order:
 |      Color
 |      enum.Enum
 |      builtins.object
 |\x20\x20
 |  Data oraz other attributes defined here:
 |\x20\x20
 |  blue = <Color.blue: 3>
 |\x20\x20
 |  green = <Color.green: 2>
 |\x20\x20
 |  red = <Color.red: 1>
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited z enum.Enum:
 |\x20\x20
 |  name
 |\x20\x20
 |  value
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited z enum.EnumMeta:
 |\x20\x20
 |  __members__"""

klasa TestStdLib(unittest.TestCase):

    maxDiff = Nic

    klasa Color(Enum):
        red = 1
        green = 2
        blue = 3

    def test_pydoc(self):
        # indirectly test __objclass__
        jeżeli StrEnum.__doc__ jest Nic:
            expected_text = expected_help_output_without_docs % __name__
        inaczej:
            expected_text = expected_help_output_with_docs % __name__
        output = StringIO()
        helper = pydoc.Helper(output=output)
        helper(self.Color)
        result = output.getvalue().strip()
        self.assertEqual(result, expected_text)

    def test_inspect_getmembers(self):
        values = dict((
                ('__class__', EnumMeta),
                ('__doc__', 'An enumeration.'),
                ('__members__', self.Color.__members__),
                ('__module__', __name__),
                ('blue', self.Color.blue),
                ('green', self.Color.green),
                ('name', Enum.__dict__['name']),
                ('red', self.Color.red),
                ('value', Enum.__dict__['value']),
                ))
        result = dict(inspect.getmembers(self.Color))
        self.assertEqual(values.keys(), result.keys())
        failed = Nieprawda
        dla k w values.keys():
            jeżeli result[k] != values[k]:
                print()
                print('\n%s\n     key: %s\n  result: %s\nexpected: %s\n%s\n' %
                        ('=' * 75, k, result[k], values[k], '=' * 75), sep='')
                failed = Prawda
        jeżeli failed:
            self.fail("result does nie equal expected, see print above")

    def test_inspect_classify_class_attrs(self):
        # indirectly test __objclass__
        z inspect zaimportuj Attribute
        values = [
                Attribute(name='__class__', kind='data',
                    defining_class=object, object=EnumMeta),
                Attribute(name='__doc__', kind='data',
                    defining_class=self.Color, object='An enumeration.'),
                Attribute(name='__members__', kind='property',
                    defining_class=EnumMeta, object=EnumMeta.__members__),
                Attribute(name='__module__', kind='data',
                    defining_class=self.Color, object=__name__),
                Attribute(name='blue', kind='data',
                    defining_class=self.Color, object=self.Color.blue),
                Attribute(name='green', kind='data',
                    defining_class=self.Color, object=self.Color.green),
                Attribute(name='red', kind='data',
                    defining_class=self.Color, object=self.Color.red),
                Attribute(name='name', kind='data',
                    defining_class=Enum, object=Enum.__dict__['name']),
                Attribute(name='value', kind='data',
                    defining_class=Enum, object=Enum.__dict__['value']),
                ]
        values.sort(key=lambda item: item.name)
        result = list(inspect.classify_class_attrs(self.Color))
        result.sort(key=lambda item: item.name)
        failed = Nieprawda
        dla v, r w zip(values, result):
            jeżeli r != v:
                print('\n%s\n%s\n%s\n%s\n' % ('=' * 75, r, v, '=' * 75), sep='')
                failed = Prawda
        jeżeli failed:
            self.fail("result does nie equal expected, see print above")

jeżeli __name__ == '__main__':
    unittest.main()
