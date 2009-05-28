import test
import crits.twitlib as twitlib
import re
import crits.models as models

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

TWITTER_USER_TEST_DATA = '''
[{"created_at":"Fri May 22 10:45:21 +0000 2009","in_reply_to_status_id":null,"user":{"created_at":"Mon May 11 11:41:01 +0000 2009","profile_text_color":"333333","description":"LegendaryBadass is the chosen one","profile_background_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_background_images\/12393820\/Resident-Evil-5-Sucks-Final.jpg","utc_offset":-21600,"profile_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_images\/206741620\/n1538191362_30086999_3561275_normal.jpg","time_zone":"Central Time (US & Canada)","profile_link_color":"0084B4","profile_background_tile":true,"screen_name":"jgibbies2","profile_background_color":"9AE4E8","url":"http:\/\/www.youtube.com\/user\/LegendaryBadass","name":"Joanna","favourites_count":0,"protected":false,"notifications":null,"statuses_count":1965,"profile_sidebar_fill_color":"DDFFCC","following":null,"profile_sidebar_border_color":"BDDCAD","followers_count":162,"location":"","id":39235043,"friends_count":66},"truncated":false,"in_reply_to_user_id":null,"text":"Sweet video review for Terminator Salvation: http:\/\/bit.ly\/2Ma41R","favorited":false,"id":1881146749,"in_reply_to_screen_name":null,"source":"web"},
{"favorited":false,"user":{"profile_sidebar_border_color":"BDDCAD","followers_count":162,"description":"LegendaryBadass is the chosen one","utc_offset":-21600,"friends_count":66,"created_at":"Mon May 11 11:41:01 +0000 2009","profile_text_color":"333333","profile_background_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_background_images\/12393820\/Resident-Evil-5-Sucks-Final.jpg","url":"http:\/\/www.youtube.com\/user\/LegendaryBadass","profile_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_images\/206741620\/n1538191362_30086999_3561275_normal.jpg","name":"Joanna","time_zone":"Central Time (US & Canada)","profile_link_color":"0084B4","protected":false,"profile_background_tile":true,"screen_name":"jgibbies2","following":null,"profile_background_color":"9AE4E8","favourites_count":0,"notifications":null,"statuses_count":1964,"profile_sidebar_fill_color":"DDFFCC","location":"","id":39235043},"in_reply_to_screen_name":null,"created_at":"Fri May 22 10:44:54 +0000 2009","in_reply_to_status_id":null,"text":"Great video review for Star Trek right here: http:\/\/bit.ly\/VENqf","truncated":false,"in_reply_to_user_id":null,"id":1881144259,"source":"web"},
{"created_at":"Fri May 22 10:43:57 +0000 2009","in_reply_to_status_id":null,"user":{"created_at":"Mon May 11 11:41:01 +0000 2009","profile_text_color":"333333","description":"LegendaryBadass is the chosen one","profile_background_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_background_images\/12393820\/Resident-Evil-5-Sucks-Final.jpg","utc_offset":-21600,"profile_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_images\/206741620\/n1538191362_30086999_3561275_normal.jpg","time_zone":"Central Time (US & Canada)","profile_link_color":"0084B4","profile_background_tile":true,"screen_name":"jgibbies2","profile_background_color":"9AE4E8","url":"http:\/\/www.youtube.com\/user\/LegendaryBadass","name":"Joanna","favourites_count":0,"protected":false,"notifications":false,"statuses_count":1963,"profile_sidebar_fill_color":"DDFFCC","following":false,"profile_sidebar_border_color":"BDDCAD","followers_count":162,"location":"","id":39235043,"friends_count":66},"truncated":false,"in_reply_to_user_id":null,"text":"Sweet video review for Terminator Salvation: http:\/\/bit.ly\/2Ma41R","favorited":false,"id":1881139425,"in_reply_to_screen_name":null,"source":"web"},
{"created_at":"Fri May 22 10:43:27 +0000 2009","in_reply_to_status_id":null,"user":{"created_at":"Mon May 11 11:41:01 +0000 2009","profile_text_color":"333333","description":"LegendaryBadass is the chosen one","profile_background_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_background_images\/12393820\/Resident-Evil-5-Sucks-Final.jpg","utc_offset":-21600,"profile_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_images\/206741620\/n1538191362_30086999_3561275_normal.jpg","time_zone":"Central Time (US & Canada)","profile_link_color":"0084B4","profile_background_tile":true,"screen_name":"jgibbies2","profile_background_color":"9AE4E8","url":"http:\/\/www.youtube.com\/user\/LegendaryBadass","name":"Joanna","favourites_count":0,"protected":false,"notifications":null,"statuses_count":1962,"profile_sidebar_fill_color":"DDFFCC","following":null,"profile_sidebar_border_color":"BDDCAD","followers_count":162,"location":"","id":39235043,"friends_count":66},"truncated":false,"in_reply_to_user_id":null,"text":"Great video review for Star Trek right here: http:\/\/bit.ly\/VENqf","favorited":false,"id":1881136907,"in_reply_to_screen_name":null,"source":"web"}]
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
            { 'text': u'like Movie1', 'from_user': 'testuser1', 'id': 2 },
            { 'text': u'hate Movie1', 'from_user': 'testuser2', 'id': 2 },
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

    def test_should_create_two_reviews(self):
        self.assertEqual(len(models.Review.objects.all()), 2)

class TwitterSpawnerMultipleTrackablesTest(TestCase):
    def setUp(self):
        pyfactory.Factory.create('trackable', name='Movie1')
        self.mock_class = Mock()
        self.mock_object = self.mock_class.return_value
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': u'like Movie1', 'from_user': 'testuser1', 'id': 2 },
            { 'text': u'hate Movie1', 'from_user': 'testuser2', 'id': 2 },
        ] }

        twitlib.fetch_data(fetch_class=self.mock_class)
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': u'hate Movie1', 'from_user': 'testuser1', 'id': 2 },
            { 'text': u'like Movie1', 'from_user': 'testuser2', 'id': 2 },
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

class TwitterSpawnerLastIDTest(TestCase):
    def setUp(self):
        pyfactory.Factory.create('trackable', name='Movie1', score=0)
        self.mock_class = Mock()
        self.mock_object = self.mock_class.return_value
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': u'like Movie1', 'from_user': 'testuser1', 'id': 2 },
            { 'text': u'like Movie1', 'from_user': 'testuser2', 'id': 5 },
        ] }

        twitlib.fetch_data(fetch_class=self.mock_class)
        self.trackable = models.Trackable.objects.get(name='Movie1')

    def test_should_update_last_id(self):
        self.assertEqual(self.trackable.last_id, 5)

    def test_should_recompute_score(self):
        self.assertEqual(self.trackable.score, 2)

class TwitterSpawnerNeutralScoresTest(TestCase):
    def setUp(self):
        pyfactory.Factory.create('trackable', name='Movie1')
        self.mock_class = Mock()
        self.mock_object = self.mock_class.return_value
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': 'like Movie1', 'from_user': 'testuser1', 'id': 2 },
            { 'text': 'hate Movie1', 'from_user': 'testuser2', 'id': 2 },
        ] }

        twitlib.fetch_data(fetch_class=self.mock_class)
        self.mock_object.fetch.return_value = { 'results': [
            { 'text': u'neutral Movie1', 'from_user': 'testuser1', 'id': 2 },
            { 'text': u'neutral Movie1', 'from_user': 'testuser2', 'id': 2 },
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

class TwitterFetchUserTest(TestCase):
    def setUp(self):
        pyfactory.Factory.create('trackable', name='Movie1')
        self.user = pyfactory.Factory.create('user')

        self.mock_class = Mock()
        self.mock_object = self.mock_class.return_value
        self.mock_object.fetch.return_value = [
            { 'text': 'like Movie1', 'id': 2 },
            { 'text': 'hate Movie1', 'id': 2 },
        ]

        self.result = twitlib.fetch_user(
            self.user,
            fetch_class=self.mock_class
        )

    def test_should_pass_user_name(self):
        args, opts = self.mock_class.call_args
        self.assertEqual(args[0], self.user.name)
   
    def test_should_pass_since_id(self):
        args, opts = self.mock_class.call_args
        self.assertEqual(opts['since_id'], self.user.last_id)

    def test_should_call_fetch(self):
        self.assertTrue(self.mock_object.fetch)

    def test_should_return_the_correct_results(self):
        self.assertEqual(len(self.result), 2)
        self.assertEqual(self.result[0]['text'], 'like Movie1')
        self.assertEqual(self.result[1]['text'], 'hate Movie1')

class TwitterUserFetcherTest(TestCase):
    def setUp(self):
        self.user = pyfactory.Factory.create('user')
        self.mock = urllib_mock(
            'http://twitter.com/statuses/user_timeline.json?screen_name=' +\
            self.user.name + '&since_id=1&count=1000',
            TWITTER_USER_TEST_DATA
        )
        self.fetcher = twitlib.TwitterUserFetcher(
            self.user.name,
            since_id=1,
            fetch_lib=self.mock)
        self.result = self.fetcher.fetch()

    def test_should_call_urlopen_with_correct_url(self):
        url = 'http://twitter.com/statuses/user_timeline.json?' +\
            'count=1000&screen_name=' + self.user.name + '&since_id=1'
        self.assertTrue(any(map(lambda b: b[1][0] == url,
            filter(lambda a: a[0] == 'urlopen', self.mock.method_calls)
        )))

    def test_should_return_the_correct_result(self):
        self.assertEqual(len(self.result), 4)

class TwitterFetchUserUpdaterTest(TestCase):
    def setUp(self):
        self.user       = pyfactory.Factory.create('user')
        self.trackable1 = pyfactory.Factory.create(
            'trackable', name='Movie1', score=0
        )
        self.trackable2 = pyfactory.Factory.create(
            'trackable', name='Movie2', score=0
        )
        self.trackable3 = pyfactory.Factory.create(
            'trackable', name='Movie3', score=0
        )

        self.mock_class = Mock()
        self.mock_object = self.mock_class.return_value
        self.mock_object.fetch.return_value = [
            { 'text': u'like Movie1', 'id': 2 },
            { 'text': u'like Movie2', 'id': 8 },
            { 'text': u'hate Movie3', 'id': 5 },
        ]

        twitlib.fetch_user_data(fetch_class=self.mock_class)

    def test_should_create_review_for_movies(self):
        self.assertEqual(len(self.user.review_set.all()), 3)

    def test_should_create_update_last_id_on_user(self):
        self.assertEqual(models.User.objects.get(id=self.user.id).last_id, 8)

    def test_should_create_review_for_movie1(self):
        review = self.user.review_set.get(trackable=self.trackable1)
        self.assertEqual(review.score, 1)

    def test_should_create_review_for_movie2(self):
        review = self.user.review_set.get(trackable=self.trackable2)
        self.assertEqual(review.score, 1)

    def test_should_create_review_for_movie3(self):
        review = self.user.review_set.get(trackable=self.trackable3)
        self.assertEqual(review.score, -1)

class MovieStringTester(TestCase):
    def setUp(self):
        pass

    def test_should_detect_valid_mentions(self):
        self.assertTrue(
            twitlib.contains_movie('hello some rocks', 'some')
        )

    def test_should_ignore_postfix_words(self):
        self.assertFalse(
            twitlib.contains_movie('hello something rocks', 'some')
        )

    def test_should_ignore_prefix_words(self):
        self.assertFalse(
            twitlib.contains_movie('hello something rocks', 'thing')
        )

    def test_should_have_no_problems_with_tweet_endings(self):
        self.assertTrue(
            twitlib.contains_movie('hello thing', 'thing')
        )
    
    def test_should_have_no_problems_with_tweet_beginnings(self):
        self.assertTrue(
            twitlib.contains_movie('thing', 'thing')
        )

    def test_should_work_with_concatenated_movie_titles(self):
        self.assertTrue(
            twitlib.contains_movie('foo is bar great', 'foo bar')
        )

    def test_should_work_with_concatenated_movie_titles_and_signs(self):
        self.assertTrue(
            twitlib.contains_movie('foo is bar great.', 'foo bar')
        )

    def test_should_fail_with_concatenated_infix_words(self):
        self.assertFalse(
            twitlib.contains_movie('foois bar great.', 'foo bar')
        )
        self.assertFalse(
            twitlib.contains_movie('foobar great.', 'foo bar')
        )
    
    def test_should_have_no_problems_with_digits(self):
        self.assertTrue(
            twitlib.contains_movie('like movie1', 'movie1')
        )
