import crits.models as models
import test_factories
import pyfactory
import crits.wiki_fetcher as wiki_fetcher
import urllib
import simplejson
import operator
import crits.picture_fetcher as picture_fetcher

from django.test import Client
from django.test import TestCase
from django.test.utils import setup_test_environment, teardown_test_environment
from django.core.urlresolvers import reverse

from crits.utils import clear_cache

from mock import Mock

class MovieIndexListTest(TestCase):
    def setUp(self):
        setup_test_environment()
        for i in xrange(40):
            pyfactory.Factory.create(
                'trackable',
                score=i,
                name='Movie%d' % i
            )

        self.response = self.client.get(
            reverse('types', args=['movies'])
        )

    def tearDown(self):
        teardown_test_environment()

    def test_should_be_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_should_render_movies_index_template(self):
        self.assertTemplateUsed(self.response, 'movies/index.html')

    def test_should_contain_top_20_movies(self):
        for i in xrange(20, 40):
            self.assertContains(self.response, 'Movie%d' % i)

class SingleMovieRecommendTest(TestCase):
    def setUp(self):
        setup_test_environment()

        self.movie = pyfactory.Factory.create('trackable', score=0)

        self.mock = Mock()
        self.old_recommend = models.Trackable.recommend
        models.Trackable.recommend = self.mock
        self.mock.return_value = [self.movie]

        self.response = self.client.get(
            reverse('types_recommend', args=['movies']), { 
            'movies': 'Testmovie'
        })
    
    def tearDown(self):
        teardown_test_environment()
        models.Trackable.recommend = self.old_recommend

    def test_should_be_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_should_call_recommend_with_one_movie(self):
        self.assertTrue(self.mock.called)

    def test_should_render_the_recommend_template(self):
        self.assertTemplateUsed(self.response, 'movies/recommend.html')
    
    def test_should_call_recommend_with_correct_args(self):
        args = self.mock.call_args[0]
        self.assertEqual(args[0], 'movie')
        self.assertEqual(args[1], ['Testmovie'])

class MultipleMovieListTest(TestCase):
    def setUp(self):
        setup_test_environment()

        self.movie = pyfactory.Factory.create('trackable', score=0)

        self.mock = Mock()
        self.old_recommend = models.Trackable.recommend
        models.Trackable.recommend = self.mock
        self.mock.return_value = [self.movie]

        self.response = self.client.get(
            reverse('types_recommend', args=['movies']), { 
            'movies': 'Testmovie, Testmovie2,Testmovie3    , Testmovie4'
        })
    
    def tearDown(self):
        teardown_test_environment()
        models.Trackable.recommend = self.old_recommend

    def test_should_call_recommend_with_correct_args(self):
        type, movies = self.mock.call_args[0]
        self.assertEqual(
            movies, 
            ['Testmovie', 'Testmovie2', 'Testmovie3', 'Testmovie4']
        )

TEST_TYPES = [
    ('movies', 'movie'), 
    ('animes', 'anime'),
    ('music', 'music'),
    ('dvds', 'dvd')
]
class ViewRankingGenericTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.mock = Mock()
        self.mock.return_value = []
        self.old_ranking = models.Trackable.ranking_by_type
        models.Trackable.ranking_by_type = self.mock

        self.responses = map(
            lambda a: self.client.get(
                reverse('types', args=[a[0]])
            ),
            TEST_TYPES
        )
        
    def tearDown(self):
        models.Trackable.ranking_by_type = self.old_ranking
        teardown_test_environment()

    def test_should_be_successful(self):
        self.assertTrue(all(map(
            lambda a: a.status_code == 200,
            self.responses
        )))

    def test_should_call_ranking_by_type_with_correct_args(self):
        call_args = map(lambda a: a[0][0], self.mock.call_args_list)
        self.assertEqual(call_args, map(operator.itemgetter(1), TEST_TYPES))

    def test_should_render_correct_templates(self):
        for response, type in zip(self.responses, TEST_TYPES):
            self.assertTemplateUsed(response, '%s/index.html' % type[0])

class ViewRecommendGenericTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.obj = pyfactory.Factory.create('trackable', score=0)

        self.mock = Mock()
        self.old_recommend = models.Trackable.recommend
        models.Trackable.recommend = self.mock
        self.mock.return_value = [self.obj]

        self.responses = map(
            lambda t: self.client.get('/%s/recommend' % t[0], {
                t[0]: 'Testmovie, Testmovie2,Testmovie3    , Testmovie4'
            }), TEST_TYPES
        )

    def tearDown(self):
        teardown_test_environment()

    def test_should_call_recommend_with_correct_args(self):
        for args, type in zip(self.mock.call_args_list, TEST_TYPES):
            called_type, objects = args[0]
            self.assertEqual(
                objects, 
                ['Testmovie', 'Testmovie2', 'Testmovie3', 'Testmovie4']
            )
            self.assertEqual(called_type, type[1])

class WikiFetcherTest(TestCase):
    def setUp(self):
        clear_cache()
        setup_test_environment()

        self.mock = Mock()

        self.old_fetcher = wiki_fetcher.fetch
        wiki_fetcher.fetch = self.mock

        self.mock.return_value = \
            '<p>A paragraph which should be {}"escaped\'</p>'

        self.title  = urllib.quote('Angels & Demons')
        self.response = self.client.get(
            reverse('wiki', args=[self.title])
        )

    def tearDown(self):
        wiki_fetcher.fetch = self.old_fetcher
        teardown_test_environment()
    
    def test_should_be_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_should_call_wiki_fetcher_with_correct_args(self):
        args, dict = self.mock.call_args
        self.assertEqual(args[0], 'Angels & Demons')

    def test_should_escape_response(self):
        self.assertContains(self.response, "\\\"")
        
    def test_should_return_json_response(self):
        json = simplejson.loads(unicode(self.response.content))
        self.assertTrue('result' in json)
        self.assertEqual(json['result'], {'Angels & Demons': self.mock()})

class MultiWikiFetcher(TestCase):
    def setUp(self):
        clear_cache()
        setup_test_environment()

        self.mock = Mock()

        self.old_fetcher = wiki_fetcher.fetch
        wiki_fetcher.fetch = self.mock

        self.mock.return_value = \
            '<p>A paragraph which should be {}"escaped\'</p>'

        self.response = self.client.get(reverse('wiki', args=["/"]), {
            'titles': ['Angels & Demons', 'Another']
        })

    def assertCalledWith(self, mock, called, times=1):
        call_args = mock.call_args_list
        args = map(lambda a: a[0][0], call_args)
        angels_count = filter(lambda a: a == called, args)
        self.assertEqual(len(angels_count), times)

    def tearDown(self):
        wiki_fetcher.fetch = self.old_fetcher
        teardown_test_environment()

    def test_should_be_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_should_call_wiki_fetcher_twice(self):
        call_args = self.mock.call_args_list
        self.assertEqual(len(call_args), 2)

    def test_should_call_wiki_fetcher_with_angels(self):
        self.assertCalledWith(self.mock, u'Angels & Demons')

    def test_should_call_wiki_fetcher_with_another(self):
        self.assertCalledWith(self.mock, u'Another')

class AbstractPictureFetcher(TestCase):
    def setUp(self):
        setup_test_environment()
        
        clear_cache()

        self.download_mock = Mock()
        self.download_mock.return_value = 'the url'
        self.old_downloader = picture_fetcher.download_thumbnail
        picture_fetcher.download_thumbnail = self.download_mock

    def tearDown(self):
        picture_fetcher.download_thumbnail = self.old_downloader
        teardown_test_environment()

    def assertCalledWith(self, mock, param, num=1):
        call_list = mock.call_args_list
        self.assertEqual(
            len(filter(lambda a: a[0][0] == param, call_list)), num
        )

class MultiPictureFetcher(AbstractPictureFetcher):
    def setUp(self):
        super(MultiPictureFetcher, self).setUp()

        self.response = self.client.get(
            reverse('pictures', args=('/',)), {
                'queries': [ 'Image 1', 'Image 2' ]
        })

    def tearDown(self):
        super(MultiPictureFetcher, self).tearDown()
        
    def test_should_be_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_should_call_download_thumbnail_for_image_1(self):
        self.assertCalledWith(self.download_mock, u'Image 1')
    
    def test_should_call_download_thumbnail_for_image_2(self):
        self.assertCalledWith(self.download_mock, u'Image 2')

    def test_should_return_json_response(self):
        json = simplejson.loads(unicode(self.response.content))
        self.assertTrue('result' in json)
        self.assertEqual(json['result'], {
            'Image 1': 'the url',
            'Image 2': 'the url'
        })

        
class SinglePictureFetcher(AbstractPictureFetcher):
    def setUp(self):
        super(SinglePictureFetcher, self).setUp()
        self.response = self.client.get(
            reverse('pictures', args=('Image 1',))
        )

    def tearDown(self):
        super(SinglePictureFetcher, self).tearDown()

    def test_should_be_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_should_return_json_response(self):
        json = simplejson.loads(unicode(self.response.content))
        self.assertTrue('result' in json)
        self.assertEqual(json['result'], {
            'Image 1': 'the url'
        })

    def test_should_call_download_thumbnail_for_image1(self):
        self.assertCalledWith(self.download_mock, u'Image 1')
