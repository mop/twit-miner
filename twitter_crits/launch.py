#!/usr/bin/python

import crits.twitlib as twitlib
import crits.models as models
import crits.trackable_fetcher as trackable_fetcher

from django.core.cache import cache

from multiprocessing import Pool

FEED_LISTS = [
    'http://www.imsdb.com/feeds/newreleases.php',
    'http://www.metacritic.com/rss/movie/film.xml'
]
NUM_PROCESSES = 4

# fetch movies...
for feed in FEED_LISTS:
    fetcher = trackable_fetcher.Fetcher(feed)
    fetcher.import_feed()

# search twitter
trackables    = models.Trackable.objects.all()

p = Pool(NUM_PROCESSES)
results = p.map(twitlib.fetch_trackable, trackables)
results = zip(results, trackables)
for result, trackable in results:
    twitlib.create_data(trackable, result['results'])

users   = models.User.objects.order_by('last_id')[0:50]
results = p.map(twitlib.fetch_user, users)
for result, user in zip(results, users):
    twitlib.create_user_data(user, trackables, result)
    
# prune users
for user in models.User.objects.all():
    if user.review_set.count() <= 1:
        user.delete()

cache.set('movie_svd', None)
models.Trackable.recommend('movie', []) # refill cache
