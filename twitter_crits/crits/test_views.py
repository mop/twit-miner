import models
import test_factories
import pyfactory

from django.test import Client
from django.test import TestCase
from django.test.utils import setup_test_environment, teardown_test_environment

from mock import Mock

class MovieIndexListTest(TestCase):
    def setUp(self):
        setup_test_environment()
        for i in xrange(40):
            pyfactory.Factory.create(
                'trackable',
                score=i,
                name='Movie{i}'.format(i=i)
            )

        self.response = self.client.get('/movies/')

    def tearDown(self):
        teardown_test_environment()

    def test_should_be_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_should_render_movies_index_template(self):
        self.assertTemplateUsed(self.response, 'movies/index.html')

    def test_should_contain_top_20_movies(self):
        for i in xrange(20, 40):
            self.assertContains(self.response, 'Movie{i}'.format(i=i))

class SingleMovieRecommendTest(TestCase):
    def setUp(self):
        setup_test_environment()

        self.movie = pyfactory.Factory.create('trackable')

        self.mock = Mock()
        self.old_recommend = models.Trackable.recommend
        models.Trackable.recommend = self.mock
        self.mock.return_value = [self.movie]

        self.response = self.client.get('/movies/recommend', { 
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

        self.movie = pyfactory.Factory.create('trackable')

        self.mock = Mock()
        self.old_recommend = models.Trackable.recommend
        models.Trackable.recommend = self.mock
        self.mock.return_value = [self.movie]

        self.response = self.client.get('/movies/recommend', { 
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

