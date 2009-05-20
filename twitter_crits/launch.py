#!/usr/bin/python

import crits.twitlib as twitlib
import crits.models as models
import crits.trackable_fetcher as trackable_fetcher
import itertools

import math

from multiprocessing import Pool

NUM_PROCESSES = 4

# fetch movies...
fetcher = trackable_fetcher.Fetcher(
    'http://www.metacritic.com/rss/movie/film.xml'
)
fetcher.import_feed()

# search twitter
trackables    = models.Trackable.objects.all()
print trackables
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
