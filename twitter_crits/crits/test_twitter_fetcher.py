import test
import twitlib
import re
import models

import pyfactory
import test_factories
from mock import Mock
from django.test import TestCase

# Some random twitter test data
TWITTER_TEST_DATA = '''
{ "results":[
{"text":"Test post","to_user_id":null,"from_user":"cohenbarnes","id":1850887152,"from_user_id":17863064,"source":"&lt;a href=&quot;http:\/\/twitter.com\/&quot;&gt;web&lt;\/a&gt;","profile_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_images\/219385391\/Untitled_normal.jpg","created_at":"Tue, 19 May 2009 19:55:31 +0000"},
{"text":"time for the big test, deep breath.","to_user_id":null,"from_user":"xcupcakekidx","id":1850887359,"from_user_id":1085728,"iso_language_code":"en","source":"&lt;a href=&quot;http:\/\/twitterhelp.blogspot.com\/2008\/05\/twitter-via-mobile-web-mtwittercom.html&quot;&gt;mobile web&lt;\/a&gt;","profile_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_images\/77199928\/tumblr_normal.JPG","created_at":"Tue, 19 May 2009 19:55:32 +0000"},
{"text":"Oil change 4 her car then 2 hospital 4 yet another test.","to_user_id":null,"from_user":"wenelda","id":1850887355,"from_user_id":4067722,"iso_language_code":"en","source":"&lt;a href=&quot;http:\/\/help.twitter.com\/index.php?pg=kb.page&amp;id=75&quot;&gt;txt&lt;\/a&gt;","profile_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_images\/84812985\/feb09_03_normal.jpg","created_at":"Tue, 19 May 2009 19:55:32 +0000"}
] }
'''

def urllib_mock(url, result):
    lib = Mock()
    response = lib.urlopen.return_value
    response.read.return_value = result
    
    return lib

class TwitterFetcherTest(TestCase):
    def setUp(self):
        self.mock = urllib_mock(
            'http://search.twitter.com/search.json?q=test&since_id=1',
            TWITTER_TEST_DATA
        )
        self.fetcher = twitlib.TwitterFetcher(
            'test',
            since_id=1,
            fetch_lib=self.mock)
        self.result = self.fetcher.fetch()

    def test_should_fetch_all_results_with_the_given_query_string(self):
        self.assertEqual(len(self.result['results']), 3)
    
    def test_should_find_text(self):
        text = map(lambda a: a['text'], self.result['results'])
        self.assertTrue(
            all(map(lambda a: re.search(r'test', a, re.I), text))
        )

    def test_should_call_urlopen_with_correct_url(self):
        url = 'http://search.twitter.com/search.json?q=test&since_id=1'
        self.assertTrue(any(map(lambda b: b[1][0] == url,
            filter(lambda a: a[0] == 'urlopen', self.mock.method_calls)
        )))

class TwitterSpawnerTest(TestCase):
    def setUp(self):
        pyfactory.Factory.create('trackable', name='Movie1')
        pyfactory.Factory.create('trackable', name='Movie2')
        self.mock_class = Mock()
        self.mock_object = self.mock_class.return_value
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': 'like Movie1', 'from_user': 'testuser1' },
            { 'text': 'hate Movie1', 'from_user': 'testuser2' },
        ] }

        twitlib.fetch_data(fetch_class=self.mock_class)
    
    def test_should_create_two_objects(self):
        self.assertEqual(len(self.mock_class.call_args_list), 2)
        first_arg  = self.mock_class.call_args_list[0]
        second_arg = self.mock_class.call_args_list[1]

        self.assertEqual(first_arg[0][0], u'Movie1')
        self.assertEqual(first_arg[1]['since_id'], 1)
        self.assertEqual(second_arg[0][0], u'Movie2')
        self.assertEqual(second_arg[1]['since_id'], 1)

    def test_should_call_fetch_twice(self):
        self.assertEqual(len(self.mock_object.method_calls), 2)

    def test_should_create_two_users(self):
        user1 = models.User.objects.get(name='testuser1')
        user2 = models.User.objects.get(name='testuser2')

        self.assertEqual(user1.network, 'twitter')
        self.assertEqual(user2.network, 'twitter')
        self.assertEqual(user1.url, 'http://twitter.com/testuser1')
        self.assertEqual(user2.url, 'http://twitter.com/testuser2')

    def test_should_create_two_users(self):
        self.assertEqual(len(models.User.objects.all()), 2)

    def test_should_create_four_reviews(self):
        self.assertEqual(len(models.Review.objects.all()), 4)

class TwitterSpawnerMultipleTrackablesTest(TestCase):
    def setUp(self):
        pyfactory.Factory.create('trackable', name='Movie1')
        self.mock_class = Mock()
        self.mock_object = self.mock_class.return_value
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': 'like Movie1', 'from_user': 'testuser1' },
            { 'text': 'hate Movie1', 'from_user': 'testuser2' },
        ] }

        twitlib.fetch_data(fetch_class=self.mock_class)
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': 'hate Movie1', 'from_user': 'testuser1' },
            { 'text': 'like Movie1', 'from_user': 'testuser2' },
        ] }
        twitlib.fetch_data(fetch_class=self.mock_class)

    def test_should_create_two_reviews(self):
        self.assertEqual(len(models.Review.objects.all()), 2)

    def test_should_update_the_review_of_testuser1_to_hate(self):
        user1 = models.User.objects.get(name='testuser1')
        review = user1.review_set.all()[0]
        self.assertEqual(review.score, -1)

    def test_should_update_the_review_of_testuser2_to_like(self):
        user2 = models.User.objects.get(name='testuser2')
        review = user2.review_set.all()[0]
        self.assertEqual(review.score, 1)

class TwitterSpawnerNeutralScoresTest(TestCase):
    def setUp(self):
        pyfactory.Factory.create('trackable', name='Movie1')
        self.mock_class = Mock()
        self.mock_object = self.mock_class.return_value
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': 'like Movie1', 'from_user': 'testuser1' },
            { 'text': 'hate Movie1', 'from_user': 'testuser2' },
        ] }

        twitlib.fetch_data(fetch_class=self.mock_class)
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': 'neutral Movie1', 'from_user': 'testuser1' },
            { 'text': 'neutral Movie1', 'from_user': 'testuser2' },
        ] }
        twitlib.fetch_data(fetch_class=self.mock_class)

    def test_should_have_a_positive_score_for_testuser1_review(self):
        user1 = models.User.objects.get(name='testuser1')
        review = user1.review_set.all()[0]
        self.assertEqual(review.score, 1)

    def test_should_have_a_negative_score_for_testuser2_review(self):
        user2 = models.User.objects.get(name='testuser2')
        review = user2.review_set.all()[0]
        self.assertEqual(review.score, -1)
