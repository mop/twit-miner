from django.db import models
import numpy as np
import numpy.linalg as linalg
import itertools
from operator import itemgetter
from django.core.cache import cache

# Create your models here.

class RankingManager(models.Manager):
    def get_query_set(self):
        return super(RankingManager, self).get_query_set().order_by('-score')

class Trackable(models.Model):
    type       = models.CharField(max_length=20)
    name       = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now=True)
    score      = models.IntegerField()
    last_id    = models.IntegerField()

    objects    = models.Manager()
    ranking    = RankingManager()

    def __unicode__(self):
        return self.name

    def recompute_score(self):
        self.score = sum(map(lambda a: a.score, self.review_set.all()))

    @classmethod
    def ranking_by_type(self, type):
        return self.ranking.filter(type=type)[0:20]

    @classmethod
    def tuples_to_vector(cls, tuples):
        num_trackables = Trackable.objects.order_by('-id')[0].id

        result = [0] * num_trackables
        for id, score in tuples:
            result[id - 1] = score
        return result

    @classmethod
    def vector_for_query(cls, type, objects):
        trackables = map(
            lambda a: Trackable.objects.filter(type=type, name__icontains=a),
            objects
        )
        result = []
        for trackable_list in trackables:
            for trackable in trackable_list:
                result.append((trackable.id, 1))
        return result

    @classmethod
    def lsi(cls, u, s, v, query_vector):
        u2  =  u[:, 0:2]
        v2  =  v[0:2, :].transpose()
        s2  =  np.matrix([[s[0], 0], [0, s[1]]])

        query_matrix = np.matrix(query_vector)
        query = query_matrix * u2 * linalg.inv(s2)

        user_sim = zip(cls.compute_distances(query, v2), itertools.count(0))
        user_sim.sort(key=lambda a: a[0])
        return user_sim

    @classmethod
    def compute_distances(cls, vec, matrix):
        return map(
            lambda i: cls.cdist(vec, matrix[i,:].transpose()),
            xrange(matrix.shape[0])
        )

    @classmethod
    def cdist(cls, u, v):
        return np.dot(u, v)[0,0] / (linalg.norm(u) * linalg.norm(v))

    @classmethod
    def reviews_for_users(cls, type):
        num_trackables = Trackable.objects.order_by('-id')[0].id
        num_users      = User.objects.order_by('-id')[0].id
        matrix         = map(lambda a: [0] * num_trackables, xrange(num_users))
        
        from django.db import connection
        cur = connection.cursor()
        result = cur.execute('''
            select u.id, t.id, r.score
            from crits_user u
            inner join crits_review r on (u.id = r.user_id)
            inner join crits_trackable t on (t.id = r.trackable_id)
            where t.type = %s
        ''', [type]).fetchall()
        for (uid, tid, score) in result:
            matrix[uid - 1][tid - 1] = score
        return matrix

    @classmethod
    def recommend(cls, type, objects):
        query_vector = cls.tuples_to_vector(
            cls.vector_for_query(type, objects)
        )
        usv_matrix = cache.get('%s_svd' % type)
        if usv_matrix is None:
            review_vectors = cls.reviews_for_users(type)
            #       movie1 movie2 ...
            # user1      0      1
            # user2      1      0
            matrix = np.matrix(review_vectors).transpose()
            #        user1  user2 ...
            # movie1     0      1
            # movie2     1      0
        
            u, s, v = linalg.svd(matrix)
            usv_matrix = (u, s, v, matrix)
            cache.set('%s_svd' % type, usv_matrix, 3600*10)
        u, s, v, matrix = usv_matrix
        user_sim = cls.lsi(u, s, v, query_vector)
        return cls.fetch_trackables(matrix, user_sim, query_vector)

    @classmethod
    def fetch_trackables(cls, matrix, user_sim, query_vector):
        result = []
        user_sim = filter(lambda a: a[0] > 0.90, user_sim)
        for cos, id in user_sim:
            items = [ i[0] for i in matrix[:,id].tolist() ]
            for id, i in zip(itertools.count(0), items):
                if i > 0 and query_vector[id] == 0: result.append(id)
        results = zip(itertools.count(0), result)
        results.sort(key=itemgetter(1))
        results = map(
            lambda a: list(a[1])[0], 
            itertools.groupby(results, key=itemgetter(1))
        )
        results.sort(key=itemgetter(0)) # restore order
        results = map(itemgetter(1), results)
        id_list = map(lambda a: a + 1, result)
        return Trackable.objects.filter(id__in=id_list)


class User(models.Model):
    name    = models.CharField(max_length = 50)
    url     = models.URLField()
    network = models.CharField(max_length = 50)
    reviews = models.ManyToManyField(Trackable, through='Review')
    last_id = models.IntegerField(default=1)

    def review(self, trackable, score):
        (review, created) = Review.objects.get_or_create(
            user=self, 
            trackable=trackable
        )
        if created and score == 0:
            review.delete()
            return
        if score != 0: review.score = score
        review.save()
        return review
    
class Review(models.Model):
    score      = models.IntegerField(default=0)
    user       = models.ForeignKey(User)
    trackable  = models.ForeignKey(Trackable)
    created_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.user_id, self.trackable_id, self.score)

    class Meta:
        unique_together = ('user', 'trackable',)
