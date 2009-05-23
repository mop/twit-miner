import test
import models
import pyfactory
import crits.test_factories
import django.db
from datetime import datetime
from django.test import TestCase

class TrackableTest(TestCase):
    def setUp(self):
        self.trackable = pyfactory.Factory.build('trackable')
        
    def test_should_have_a_type(self):
        self.assert_(self.trackable.type != None)
        self.assert_(isinstance(self.trackable.type, str))

    def test_should_have_a_name(self):
        self.assert_(self.trackable.name != None)
        self.assert_(isinstance(self.trackable.name, str))

    def test_should_have_a_score(self):
        self.assert_(self.trackable.score != None)

    def test_should_have_a_creation_date(self):
        self.assert_(self.trackable.created_at != None)
        self.assert_(isinstance(self.trackable.created_at, datetime))

    def test_should_have_an_last_id(self):
        self.assert_(self.trackable.last_id != None)

    def test_should_save(self):
        self.trackable.save()
        self.assert_(self.trackable.id != None)
    
    def test_should_not_allow_duplicates(self):
        tmp = pyfactory.Factory.create('trackable')
        try:
            tmp2 = pyfactory.Factory.create('trackable', name=tmp.name)
            self.fail("This should have been thrown an error")
        except django.db.IntegrityError:
            pass

class TrackableRankingFetchTest(TestCase):
    def setUp(self):
        for i in xrange(20):
            pyfactory.Factory.create(
                'trackable',
                score=i,
                name="Movie%d" % i
            )
        for i in xrange(20):
            pyfactory.Factory.create(
                'trackable',
                type='book',
                score=i,
                name="Book%d" % i
            )

    def test_should_fetch_the_best_20_items_for_given_type(self):
        self.assertEqual(len(models.Trackable.ranking_by_type('movie')), 20)

    def test_should_fetch_movie_20(self):
        rankings = models.Trackable.ranking_by_type('movie')
        self.assertEqual(rankings[0].score, 19)
        self.assertEqual(rankings[0].name, 'Movie19')
        

class UserTests(TestCase):
    def setUp(self):
        self.user = pyfactory.Factory.build('user')

    def test_should_have_a_name(self):
        self.assert_(self.user.name != None)
        self.assert_(isinstance(self.user.name, str))

    def test_should_have_a_url(self):
        self.assert_(self.user.url != None)
        self.assert_(isinstance(self.user.url, str))

    def test_should_have_a_network(self):
        self.assert_(self.user.network != None)
        self.assert_(isinstance(self.user.network, str))

    def test_should_have_a_last_id(self):
        self.assert_(self.user.last_id != None)
        self.assert_(self.user.last_id == 1)

    def test_should_save(self):
        self.user.save()
        self.assert_(self.user.id != None)

class UserReviewTests(TestCase):
    def setUp(self):
        self.user = pyfactory.Factory.create('user')
        self.trackable = pyfactory.Factory.create('trackable')

    def test_should_create_a_review_with_score_1(self):
        self.user.review(self.trackable, 1)

        self.assertEqual(len(models.Review.objects.all()), 1)
        self.assertEqual(models.Review.objects.all()[0].score, 1)

    def test_shouldnt_create_a_review(self):
        self.user.review(self.trackable, 0)

        self.assertEqual(len(models.Review.objects.all()), 0)
        
class ReviewTests(TestCase):
    def setUp(self):
        self.review = pyfactory.Factory.create('review')

    def test_should_have_a_score(self):
        self.assert_(self.review.score != None)

    def test_should_belong_to_a_user(self):
        self.assert_(self.review.id != None)
        self.assert_(self.review.user.id != None)

    def test_should_belong_to_a_trackable(self):
        self.assert_(self.review.id != None)
        self.assert_(self.review.trackable.id != None)

class ReviewWithoutSomeValuesTest(TestCase):
    def setUp(self):
        user        = pyfactory.Factory.create('user')
        trackable   = pyfactory.Factory.create('trackable')
        self.review = models.Review(user=user, trackable=trackable)
        self.review.save()
    
    def test_should_have_a_datetime(self):
        self.assert_(self.review.created_at != None)

    def test_should_have_0_scores(self):
        self.assertEqual(self.review.score, 0)
        
class UserWithReviewsTest(TestCase):
    def setUp(self):
        review = pyfactory.Factory.create('review')
        self.user = review.user
        self.trackable = review.trackable

        pyfactory.Factory.create(
            'review', user=self.user, score=3
        )
        pyfactory.Factory.create(
            'review', user=self.user, score=8
        )

    def test_should_have_many_reviews(self):
        self.assertEqual(len(self.user.reviews.all()), 3)
    
    def test_should_recompute_the_score_for_trackable(self):
        self.trackable.recompute_score()
        self.assertEqual(self.trackable.score, 10)

        self.trackable = models.Trackable.objects.all()[2]
        self.trackable.recompute_score()
        self.assertEqual(self.trackable.score, 8)

class UserWithDuplicatedReviewsTest(TestCase):
    def setUp(self):
        review = pyfactory.Factory.create('review')
        self.user = review.user
        self.trackable = review.trackable

    def test_should_not_allow_to_create_a_second_review_for_same_movie(self):
        try:
            pyfactory.Factory.create(
                'review', user=self.user, trackable=self.trackable
            )
            self.fail("this should throw an error")
        except django.db.IntegrityError:
            pass
