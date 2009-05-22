import models
import urllib
import urllib2
import simplejson as json
import re

from porterstemmer import Stemmer
from datetime import datetime
from itertools import count

stemmer = Stemmer()

PLUS_LIST = [ 
    'cool',
    'awesome',
    'like',
    'good',
    'love',
    'great',
    'enjoy',
    'amazing',
    'good' 
]

MINUS_LIST = [ 
    'dislike',
    'hate',
    'sucks',
    'not like',
    'don\'t like',
    'bad' 
]

PLUS_LIST = map(stemmer, PLUS_LIST)
MINUS_LIST = map(stemmer, MINUS_LIST)

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

class TwitterUserFetcher(object):
    def __init__(self, user, since_id=1, fetch_lib=urllib2):
        self.user = user
        self.since_id = since_id
        self.fetch_lib = fetch_lib

    def fetch(self):
        str = urllib.urlencode({
            'screen_name': self.user,
            'since_id': self.since_id,
            'count': 1000
        })
        url = 'http://twitter.com/statuses/user_timeline.json?{query}'.format(
            query=str
        )
        result = self.fetch_lib.urlopen(url).read()
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

def update_trackable(trackable, id):
    trackable.last_id = id if id > trackable.last_id else trackable.last_id
    trackable.recompute_score()
    trackable.save()

def create_data(trackable, results):
    stemmer = Stemmer()
    for result in results:
        user = find_or_create_user(result['from_user'])
        create_review(user, trackable, stemmer(result['text'].lower()))
        update_trackable(trackable, result['id'])

def fetch_trackable(trackable, fetch_class=TwitterFetcher):
    f = fetch_class(trackable.name, since_id=trackable.last_id)
    return f.fetch()
    
def fetch_data(fetch_class=TwitterFetcher):
    for t in models.Trackable.objects.all():
        result = fetch_trackable(t, fetch_class=fetch_class)
        create_data(t, result['results'])
        
def fetch_user(user, fetch_class=TwitterUserFetcher):
    f = fetch_class(user.name, since_id=user.last_id)
    try:
        return f.fetch()
    except Exception, e:
        print e
        return []

def find_trackable(trackables, text):
    stemmer = Stemmer()
    names = map(lambda a: a.name, trackables)
    names = map(stemmer, names)
    names_lists = map(lambda n: n.split(' '), names)
    results = filter(
        lambda l: all(map(lambda i: text.find(i) != -1, l[1])), 
        zip(count(0), names_lists)
    )
    if not results: return None
    return trackables[results[0][0]]

def create_user_data(user, trackables, results):
    stemmer = Stemmer()
    for result in results:
        msg = stemmer(result['text'])
        trackable = find_trackable(trackables, msg)
        score = get_score(msg)
        if not trackable: continue
        if result['id'] > user.last_id: user.last_id = result['id']
        user.review(trackable, score)
    user.save()

def fetch_user_data(fetch_class=TwitterFetcher):
    trackables = models.Trackable.objects.all()
    for user in models.User.objects.all():
        results = fetch_user(user, fetch_class=fetch_class)
        create_user_data(user, trackables, results)
