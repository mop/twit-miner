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

CHECK_WORD = re.compile(r'^([\w\d\-_]+?)[\.\?\!,\-]?( |$)')

PLUS_LIST = map(stemmer, PLUS_LIST)
MINUS_LIST = map(stemmer, MINUS_LIST)

plus_expr = '(%s)' % '|'.join(PLUS_LIST)
minus_expr = '(%s)' % '|'.join(MINUS_LIST)
PLUS_EXPR = re.compile(plus_expr)
MINUS_EXPR = re.compile(minus_expr)

class TwitterFetcher(object):
    def __init__(self, query_string, since_id=1, fetch_lib=urllib2):
        self.query_string = query_string
        self.since_id = since_id
        self.fetch_lib = fetch_lib

    def fetch(self):
        str = urllib.urlencode({
            u'q': self.query_string.encode('utf-8'),
            u'since_id': self.since_id
        })
        result = self.fetch_lib.urlopen( 
            u'http://search.twitter.com/search.json?%s' % str
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
        url = 'http://twitter.com/statuses/user_timeline.json?%s' % str
        result = self.fetch_lib.urlopen(url).read()
        return json.loads(result)

def find_or_create_user(name):
    return models.User.objects.get_or_create(
        name=name,
        network='twitter',
        url="http://twitter.com/%s" % name
    )[0]

def get_score(msg):
    if MINUS_EXPR.search(msg):
        return -1
    if PLUS_EXPR.search(msg):
        return 1
    #if any(map(lambda a: a in msg, MINUS_LIST)):
    #    return -1
    #if any(map(lambda a: a in msg, PLUS_LIST)):
    #    return 1
    #for minus in MINUS_LIST:
    #    if minus in msg:
    #        return -1
    #for plus in PLUS_LIST:
    #    if plus in msg:
    #        return 1
    return 0

def update_trackable(trackable, id, score):
    trackable.last_id = id if id > trackable.last_id else trackable.last_id
    trackable.score += score
    trackable.save()

def create_data(trackable, results):
    stemmer = Stemmer()
    name = stemmer(trackable.name)

    for result in results:
        txt = stemmer(result['text'])
        if not contains_movie(txt, name):
            continue
        user = find_or_create_user(result['from_user'])
        score = get_score(stemmer(result['text'].lower()))
        user.review(trackable, score)
        update_trackable(trackable, result['id'], score)

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

def contains_movie(text, movie_name):
    names_list = movie_name.split(' ')
    for name in names_list:
        if name not in text: return False
    positions = map(text.find, names_list)
    sub_strings = map(lambda i: text[i:], positions)

    if any(map(
        lambda i: i != 0 and 
                  re.match(r'[\w]', text[i - 1]) is not None, positions
        )): return False

    # more sophisticated tests
    contains_full_words = map(lambda a: CHECK_WORD.match(a), sub_strings)
    if any(map(lambda i: i is None, contains_full_words)): return False

    sub_matches = map(lambda a: a.groups()[0], contains_full_words)
    if any(map(lambda a: a not in names_list, sub_matches)): return False
    return True

def find_trackable(trackables, text):
    stemmer = Stemmer()
    for trackable in trackables:
        if contains_movie(text, stemmer(trackable.name)):
            return trackable
    return None

def create_user_data(user, trackables, results):
    stemmer = Stemmer()
    for result in results:
        msg = stemmer(result['text'])
        trackable = find_trackable(trackables, msg)
        score = get_score(msg)
        if result['id'] > user.last_id: user.last_id = result['id']
        if not trackable: continue
        update_trackable(trackable, 0, score)
        user.review(trackable, score)
    user.save()

def fetch_user_data(fetch_class=TwitterFetcher):
    trackables = models.Trackable.objects.all()
    for user in models.User.objects.all():
        results = fetch_user(user, fetch_class=fetch_class)
        create_user_data(user, trackables, results)
