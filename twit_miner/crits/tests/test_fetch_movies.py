# vim: set fileencoding=utf8 :
import crits.models as models
import crits.trackable_fetcher as trackable_fetcher
import os

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

class MyAnimeListParserTest(TestCase):
    def setUp(self):
        self.mock = Mock()
        tmp = self.mock.urlopen.return_value
        tmp.read.return_value = self._file_contents()

        self.parser = trackable_fetcher.MyAnimeListParser(
            urllib=self.mock
        )
        self.fetcher = trackable_fetcher.Fetcher(
            'http://myanimelist.net/anime.php?popular',
            type='anime',
            parser=self.parser
        )
        self.fetcher.import_feed()

    def _file_contents(self):
        path = os.path.join(os.path.dirname(__file__), 'test_myanilist')
        with open(path, 'r') as f:
            return f.read()
    
    def test_should_call_urllib_correctly(self):
        args, kwds = self.mock.urlopen.call_args
        self.assertEqual(
            args[0],
            'http://myanimelist.net/anime.php?popular'
        )

    def test_should_create_the_trackables(self):
        ani_list =  [
            u"Bleach", u"Naruto: Shippuuden", u"One Piece",
            u"Fullmetal Alchemist: Brotherhood", u"Valkyria Chronicles",
            u"Soul Eater", u"K-ON!", u"07-Ghost", u"Katekyo Hitman Reborn!",
            u"Higashi no Eden", u"Gintama",
            u"The Melancholy of Haruhi-chan Suzumiya",
            u"Hatsukoi Limited", u"Code Geass - Hangyaku no Lelouch R2",
            u"Hetalia Axis Powers", u"Toradora!", u"Pandora Hearts",
            u"Code Geass - Hangyaku no Lelouch", u"Clannad ~After Story~",
            u"Kuroshitsuji", u"Naruto", u"Death Note",
            u"Phantom ~Requiem for the Phantom~", u"Shangri-La",
            u"Fullmetal Alchemist", u"The Melancholy of Haruhi Suzumiya 2",
            u"Hajime no Ippo: New Challenger", u"Darker than BLACK",
            u"Lucky ☆ Star", u"Tengen Toppa Gurren Lagann",
            u"Ouran High School Host Club",
            u"The Melancholy of Haruhi Suzumiya", u"Chrome Shelled Regios",
            u"D.Gray-man", u"Clannad", "Higurashi no Naku Koro ni",
            u"Eureka Seven", u"Hajime no Ippo", u"Dragon Ball Kai",
            u"Kurokami", u"Hayate the Combat Butler!", u"NANA", u"Basquash!",
            u"Guin Saga", u"Asura Cryin'", u"Fate/stay night",
            u"Neon Genesis Evangelion", u"Great Teacher Onizuka",
            u"Skip Beat!", u"Sora wo Kakeru Shoujo"
        ]
        self.assertTrue(all(map(
            lambda a: models.Trackable.objects.get(
                type='anime', name=a) != None, 
            ani_list
        )))
