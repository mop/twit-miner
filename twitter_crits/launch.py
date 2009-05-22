#!/usr/bin/python

import crits.twitlib as twitlib
import crits.models as models
import crits.trackable_fetcher as trackable_fetcher
import itertools

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
#per_thread    = math.ceil(len(trackables) / float(NUM_PROCESSES))
#zipped_items  = zip(trackables, itertools.count(0))
#zipped_items.sort(key=lambda a: a[1] % NUM_PROCESSES)
#grouped_items = itertools.groupby(zipped_items, lambda a: a[1] % NUM_PROCESSES)
#item_groups   = map(lambda a: list(a[1]), grouped_items)
## => [[(trackable, 0), (trackable, 1)], [(...), (...)]]
#item_groups   = map(lambda l: map(lambda a: a[0], l), item_groups)

p = Pool(NUM_PROCESSES)
results = p.map(twitlib.fetch_trackable, trackables)
results = zip(results, trackables)
for result, trackable in results:
    twitlib.create_data(trackable, result['results'])

cache.set('movie_svd', None)
models.Trackable.recommend('movie', []) # refill cache
