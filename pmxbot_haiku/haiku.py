import random

import pmxbot
from pmxbot.core import command
from pmxbot import storage


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
    phrase = args.split(arg)[1]
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


#
# Storage
#

class Haikus(storage.SelectableStorage):
    lib = 'pmx'

    @classmethod
    def initialize(cls):
        cls.store = cls.from_URI(pmxbot.config.database)
        cls._finalizers.append(cls.finalize)

    @classmethod
    def finalize(cls):
        del cls.store


class MongoDBHaikus(Haikus, storage.MongoDBStorage):

    def lookup_num(self, rest=''):
        rest = rest.strip()
        if rest:
            if rest.split()[-1].isdigit():
                num = rest.split()[-1]
                query = ' '.join(rest.split()[:-1])
                qt, i, n = self.quoteLookup(query, num)
            else:
                qt, i, n = self.quoteLookup(rest)
        else:
            qt, i, n = self.quoteLookup()
        return qt, i, n

    def get_one(self):
        results = [
            row['text'] for row in
            self.db.find(dict(library=self.lib)).sort('_id')
        ]
        total = len(results)
        if not total:
            return ''
        random_index = random.randrange(total)
        return results[random_index]

    def lookup(self, thing='', num=0):
        thing = thing.strip().lower()
        num = int(num)
        words = thing.split()

        def matches(quote):
            quote = quote.lower()
            return all(word in quote for word in words)
        results = [
            row['text'] for row in
            self.db.find(dict(library=self.lib)).sort('_id')
            if matches(row['text'])
        ]
        n = len(results)
        if n > 0:
            if num:
                i = num - 1
            else:
                i = random.randrange(n)
            quote = results[i]
        else:
            i = 0
            quote = ''
        return (quote, i + 1, n)

    def add(self, quote):
        quote = quote.strip()
        quote_id = self.db.insert(dict(library=self.lib, text=quote))
        # see if the quote added is in the last IRC message logged
        newest_first = [('_id', storage.pymongo.DESCENDING)]
        last_message = self.db.database.logs.find_one(sort=newest_first)
        if last_message and quote in last_message['message']:
            self.db.update({'_id': quote_id},
                           {'$set': dict(log_id=last_message['_id'])})

    def __iter__(self):
        return self.db.find(library=self.lib)

    def _build_log_id_map(self):
        from . import logging
        if not hasattr(logging.Logger, 'log_id_map'):
            log_db = self.db.database.logs
            logging.Logger.log_id_map = dict(
                (logging.MongoDBLogger.extract_legacy_id(rec['_id']), rec['_id'])
                for rec in log_db.find(fields=[])
            )
        return logging.Logger.log_id_map

    def import_(self, quote):
        log_id_map = self._build_log_id_map()
        log_id = quote.pop('log_id', None)
        log_id = log_id_map.get(log_id, log_id)
        if log_id is not None:
            quote['log_id'] = log_id
        self.db.insert(quote)


class HaikusSevens(MongoDBHaikus):

    collection_name = 'haikus_sevens'


class HaikusFives(MongoDBHaikus):

    collection_name = 'haikus_fives'


