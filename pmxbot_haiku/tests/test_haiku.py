from mock import Mock, patch
from pmxbot_haiku import haiku


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


