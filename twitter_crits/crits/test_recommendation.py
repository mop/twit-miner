import test_factories
import pyfactory
import models

from django.test import TestCase

class RecommendationTest(TestCase):
    def setUp(self):
        self.users = map(
            lambda a: pyfactory.Factory.create('user'),
            xrange(6)
        )
        
        self.trackable1 = pyfactory.Factory.create('trackable')
        self.trackable2 = pyfactory.Factory.create('trackable')
        self.trackable3 = pyfactory.Factory.create('trackable')
        self.trackable4 = pyfactory.Factory.create('trackable')

        for user in self.users:
            user.review(self.trackable1, 1)
            user.review(self.trackable2, 1)
            user.review(self.trackable3, -1)
            user.review(self.trackable4, 1)

    def test_should_return_the_correct_recommendation_for_trackable1(self):
        results = models.Trackable.recommend('movie', [self.trackable1.name,
            self.trackable2.name])
        self.assertEqual(
            len(filter(lambda a: a.name == self.trackable4.name, results)), 1
        )
    
    def test_should_not_return_unpopular_movies(self):
        results = models.Trackable.recommend('movie', [self.trackable1.name])
        self.assertEqual(
            len(filter(lambda a: a.name == self.trackable3.name, results)), 0
        )

