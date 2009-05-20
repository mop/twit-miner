import models
import test_factories
import pyfactory

from django.test import Client
from django.test import TestCase

class MovieIndexListTest(TestCase):
    def setUp(self):
        for i in xrange(40):
            pyfactory.Factory.create(
                'trackable',
                score=i,
                name='Movie{i}'.format(i=i)
            )
        self.response = self.client.get('/movies')

    def test_should_be_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_should_render_movies_index_template(self):
        self.assertTemplateUsed(self.response, 'movies/index.html')

    def test_should_contain_top_20_movies(self):
        for i in xrange(20, 40):
            self.assertContains(self.response, 'Movie{i}'.format(i=i))
