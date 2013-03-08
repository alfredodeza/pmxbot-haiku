from pmxbot.core import command
from pmxbot_haiku.models import HaikusFives, HaikusSevens


_help = """
Get your Haiku fix from stored phrases. With no arguments
it will get you a haiku, other commands available are:
'add-fives', 'add-use-fives', 'add-sevens', 'add-use-sevens'
and 'delete'.
"""

valid_args = ['delete', 'add-fives',
              'add-use-fives', 'add-sevens',
              'add-use-sevens']


@command("haiku", doc=_help)
def haiku(client, event, channel, nick, rest):
    rest = rest.strip()
    return main(rest)


#
# Command Functions
#

def add_fives(phrase):
    HaikusFives.store.add(phrase)
    return 'Added!'


def add_use_fives(phrase):
    add_fives(phrase)
    return make_haiku(first=phrase)


def add_sevens(phrase):
    HaikusSevens.store.add(phrase)
    return 'Added!'


def add_use_sevens(phrase):
    add_sevens(phrase)
    return make_haiku(second=phrase)


def delete(phrase):
    pass


def main(args):
    arg = get_argument(args)
    command = get_cmd_function(arg)
    if not command:
        return  make_haiku()
    phrase = args.split(arg)[1].strip()
    return command(phrase)

#
# Helpers
#


def make_haiku(first=None, second=None, third=None):
    first = first or HaikusFives.store.get_one()
    second = second or HaikusSevens.store.get_one()
    third = third or HaikusFives.store.get_one()
    yield first
    yield second
    yield third


def get_argument(args):
    for arg in valid_args:
        if args.startswith(arg):
            return arg


def get_cmd_function(cmd):
    func_map = {'delete': delete, 'add-fives': add_fives,
                'add-use-fives': add_use_fives,
                'add-sevens': add_sevens,
                'add-use-sevens': add_use_sevens}
    return func_map.get(cmd)


