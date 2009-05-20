import models
import urllib
import urllib2
import simplejson as json
import re

from datetime import datetime

PLUS_LIST = [ 'cool', 'awesome', 'like', 'good', 'great', 'enjoy', 'amazing' ]
MINUS_LIST = [ 'dislike', 'hate', 'sucks', 'don\'t like' ]

class TwitterFetcher(object):
    def __init__(self, query_string, since_id=1, fetch_lib=urllib2):
        self.query_string = query_string
        self.since_id = since_id
        self.fetch_lib = fetch_lib

    def fetch(self):
        str = urllib.urlencode({
            'q': self.query_string,
            'since_id': self.since_id
        })
        result = self.fetch_lib.urlopen( 
            'http://search.twitter.com/search.json?{query}'.format(query=str)
        ).read()
        return json.loads(result)

def find_or_create_user(name):
    return models.User.objects.get_or_create(
        name=name,
        network='twitter',
        url="http://twitter.com/{name}".format(name=name)
    )[0]

def get_score(msg):
    if any(map(lambda a: re.search(a, msg), MINUS_LIST)):
        return -1
    if any(map(lambda a: re.search(a, msg), PLUS_LIST)):
        return 1
    return 0

def create_review(user, trackable, msg):
    review = models.Review.objects.get_or_create(
        user=user,
        trackable=trackable
    )[0]
    score = get_score(msg)
    if score != 0: review.score = score 
    review.save()

def create_data(trackable, results):
    for result in results:
        user = find_or_create_user(result['from_user'])
        create_review(user, trackable, result['text'])

def fetch_data(fetch_class=TwitterFetcher):
    for t in models.Trackable.objects.all():
        f = fetch_class(t.name, since_id=t.last_id)
        result = f.fetch()
        create_data(t, result['results'])
