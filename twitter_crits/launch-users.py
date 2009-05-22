#!/usr/bin/python


import crits.twitlib as twitlib
import crits.models as models
from django.core.cache import cache

from multiprocessing import Pool

NUM_PROCESSES = 4

users      = models.User.objects.order_by('-last_id')[0:80]
trackables = models.Trackable.objects.all()

p = Pool(NUM_PROCESSES)

results = p.map(twitlib.fetch_user, users)
results = zip(results, users)
for result, user in results:
    twitlib.create_user_data(user, trackables, result)

cache.set('movie_svd', None)
models.Trackable.recommend('movie', []) # refill cache
