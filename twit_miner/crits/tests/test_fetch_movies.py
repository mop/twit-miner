import crits.models as models
import crits.trackable_fetcher as trackable_fetcher

from django.test import TestCase
from mock import Mock

class FeedItem(object):
    def __init__(self, title):
        self.title = title

class FeedStub(object):
    def __init__(self):
        self.entries = [
            FeedItem('test1'),
            FeedItem('test2'),
            FeedItem('test3')
        ]

class FetcherTest(TestCase):
    def setUp(self):
        parser = Mock()
        parser.parse = Mock()
        parser.parse.return_value = FeedStub()
        self.fetcher = trackable_fetcher.Fetcher(
            'feedurl', 
            parser=parser,
            type='movie'
        )
        self.fetcher.import_feed()

    def test_should_store_the_feed_titles_in_the_database(self):
        self.assertEqual(len(models.Trackable.objects.filter(type='movie')), 3)
        
    def test_should_ignore_duplicated_titles(self):
        self.fetcher.import_feed()
        self.assertEqual(len(models.Trackable.objects.filter(type='movie')), 3)

    def test_should_store_the_correct_type(self):
        self.assertEqual(models.Trackable.objects.get(id=1).type, 'movie')
