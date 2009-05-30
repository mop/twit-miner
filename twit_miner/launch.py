#!/usr/bin/python

import crits.twitlib as twitlib
import crits.models as models
import crits.trackable_fetcher as trackable_fetcher
import feedparser
from crits.trackable_fetcher import MyAnimeListParser

from django.core.cache import cache
from django.db import connection

from multiprocessing import Pool
from operator import itemgetter

FEED_LISTS = {
    'movie': [
        ('http://www.imsdb.com/feeds/newreleases.php', feedparser),
        ('http://www.metacritic.com/rss/movie/film.xml', feedparser)
    ],
    'anime': [
        ('http://myanimelist.net/anime.php?popular', MyAnimeListParser()),
    ]
}
NUM_PROCESSES = 4

# fetch movies...
for type in FEED_LISTS:
    for feed, parser in FEED_LISTS[type]:
        fetcher = trackable_fetcher.Fetcher(feed, parser=parser, type=type)
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
cur = connection.cursor()
ids = cur.execute('''
    select u.id
    from crits_user u
    left outer join crits_review r on (r.user_id = u.id)
    group by u.id
    having count(r.trackable_id) <= 1
''').fetchall()
ids = map(itemgetter(0), ids)
print ids
models.User.objects.filter(id__in=ids).delete()
#for user in models.User.objects.all():
#    if user.review_set.count() <= 1:
#        user.delete()

for type in FEED_LISTS:
    cache.set('%s_svd' % type, None)
    cache.set('%s_maps' % type, None)
    models.Trackable.recommend(type, []) # refill cache
