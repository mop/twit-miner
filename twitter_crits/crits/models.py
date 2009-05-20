from django.db import models

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


class User(models.Model):
    name    = models.CharField(max_length = 50)
    url     = models.URLField()
    network = models.CharField(max_length = 50)
    reviews = models.ManyToManyField(Trackable, through='Review')
    
class Review(models.Model):
    score      = models.IntegerField(default=0)
    user       = models.ForeignKey(User)
    trackable  = models.ForeignKey(Trackable)
    created_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{user_id} - {trackable_id} - {score}".format(
            user_id=self.user_id,
            trackable_id=self.trackable_id,
            score=self.score
        )

    class Meta:
        unique_together = ('user', 'trackable',)
