from mock import Mock, patch
from pmxbot_haiku import haiku



class SomeFives:
    """Used in tests for non-repeating fives.
    """

    def __init__(self, foo_until=0):
        self.i = 0
        self.foo_until = foo_until

    def __call__(self, about=None):
        self.i += 1
        if self.i > self.foo_until:
            return "wheee!!!"
        return "foo"


class TestMakeHaiku(object):

    def setup(self):
        pass

    @patch('pmxbot_haiku.haiku.HaikusFives')
    @patch('pmxbot_haiku.haiku.HaikusSevens')
    def test_make_haiku_use_first(self, fake_fives, fake_sevens):
        fake_fives.store.get_one = Mock(return_value=None)
        fake_sevens.store.get_one = Mock(return_value=None)
        result = [i for i in haiku.make_haiku(first='foo')]
        assert result == ['foo', None, None]

    @patch('pmxbot_haiku.haiku.HaikusFives')
    @patch('pmxbot_haiku.haiku.HaikusSevens')
    def test_make_haiku_use_second(self, fake_fives, fake_sevens):
        fake_fives.store.get_one = Mock(return_value=None)
        fake_sevens.store.get_one = Mock(return_value=None)
        result = [i for i in haiku.make_haiku(second='foo')]
        assert result == [None, 'foo', None]

    @patch('pmxbot_haiku.haiku.HaikusFives')
    @patch('pmxbot_haiku.haiku.HaikusSevens')
    def test_make_haiku_use_third(self, fake_fives, fake_sevens):
        fake_fives.store.get_one = Mock(return_value=None)
        fake_sevens.store.get_one = Mock(return_value=None)
        result = [i for i in haiku.make_haiku(third='foo')]
        assert result == [None, None, 'foo']

    @patch('pmxbot_haiku.haiku.HaikusFives')
    @patch('pmxbot_haiku.haiku.HaikusSevens')
    def test_make_haiku_doesnt_reuse_fives(self, fake_sevens, fake_fives):
        fake_fives.store.get_one = SomeFives(3)
        fake_sevens.store.get_one = Mock(return_value='bar')
        result = [i for i in haiku.make_haiku()]
        assert result == ['foo', 'bar', 'wheee!!!']

    @patch('pmxbot_haiku.haiku.HaikusFives')
    @patch('pmxbot_haiku.haiku.HaikusSevens')
    def test_make_haiku_tries_hard_not_to_resuse_fives(self, fake_sevens, \
                                                                   fake_fives):
        fake_fives.store.get_one = SomeFives(10)
        fake_sevens.store.get_one = Mock(return_value='bar')
        result = [i for i in haiku.make_haiku()]
        assert result == ['foo', 'bar', 'wheee!!!']


class TestGetArgument(object):

    def test_no_args_is_none(self):
        result = haiku.get_argument('')
        assert result is None

    def test_some_non_matching_arg_is_none(self):
        assert haiku.get_argument('some foo') is None

    def test_delete_matches_as_arg(self):
        assert haiku.get_argument('delete some foo') == 'delete'

    def test_add_fives_matches_as_arg(self):
        assert haiku.get_argument('add-fives some foo') == 'add-fives'

    def test_add_use_fives_matches_as_arg(self):
        assert haiku.get_argument('add-use-fives some foo') == 'add-use-fives'

    def test_add_sevens_matches_as_arg(self):
        assert haiku.get_argument('add-sevens some foo') == 'add-sevens'

    def test_add_use_sevens_matches_as_arg(self):
        result = haiku.get_argument('add-use-sevens some foo')
        assert result == 'add-use-sevens'


class TestGetCmdFunction(object):

    def test_no_match_returns_none(self):
        result = haiku.get_cmd_function('foo')
        assert result is None

    def test_delete_matches(self):
        result = haiku.get_cmd_function('delete')
        assert result == haiku.delete

    def test_add_fives_matches(self):
        result = haiku.get_cmd_function('add-fives')
        assert result == haiku.add_fives

    def test_add_use_fives_matches(self):
        result = haiku.get_cmd_function('add-use-fives')
        assert result == haiku.add_use_fives

    def test_add_sevens_matches(self):
        result = haiku.get_cmd_function('add-sevens')
        assert result == haiku.add_sevens

    def test_add_use_sevens_matches(self):
        result = haiku.get_cmd_function('add-use-sevens')
        assert result == haiku.add_use_sevens


fake_model = Mock()
fake_model.store.get_one = Mock(return_value='some phrase')


class TestMain(object):

    def setup(self):
        self.store = Mock()
        self.store.get_one = Mock(return_value='some phrase')

    @patch('pmxbot_haiku.haiku.HaikusFives', fake_model)
    @patch('pmxbot_haiku.haiku.HaikusSevens', fake_model)
    def test_main_simple_fallback(self):
        result = [i for i in haiku.main('add phrase')]
        assert len(result) == 3
        assert result == ['some phrase', 'some phrase', 'some phrase']

    @patch('pmxbot_haiku.haiku.HaikusFives', fake_model)
    @patch('pmxbot_haiku.haiku.HaikusSevens', fake_model)
    def test_main_add_fives(self):
        result = haiku.main('add-fives phrase')
        assert result == 'Added!'

    @patch('pmxbot_haiku.haiku.HaikusFives', fake_model)
    @patch('pmxbot_haiku.haiku.HaikusSevens', fake_model)
    def test_add_use_fives(self):
        result = [i for i in haiku.main('add-use-fives phrase')]
        assert len(result) == 3
        assert result == ['phrase', 'some phrase', 'some phrase']

    @patch('pmxbot_haiku.haiku.HaikusFives', fake_model)
    @patch('pmxbot_haiku.haiku.HaikusSevens', fake_model)
    def test_add_sevens(self):
        result = haiku.main('add-sevens phrase')
        assert result == 'Added!'

    @patch('pmxbot_haiku.haiku.HaikusFives', fake_model)
    @patch('pmxbot_haiku.haiku.HaikusSevens', fake_model)
    def test_add_use_sevens(self):
        result = [i for i in haiku.main('add-use-sevens this is a seven')]
        assert len(result) == 3
        assert result == ['some phrase', 'this is a seven', 'some phrase']

