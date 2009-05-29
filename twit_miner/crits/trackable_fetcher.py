import feedparser
import models
import urllib2

from django.db import IntegrityError
from BeautifulSoup import BeautifulSoup

class Feed(object):
    def __init__(self, entries):
        self.entries = entries

class FeedEntry(object):
    def __init__(self, title):
        self.title = title

class Fetcher(object):
    def __init__(self, url, parser=feedparser, type='movie'):
        self.url    = url
        self.parser = parser
        self.type   = type

    def import_feed(self):
        feed = self.parser.parse(self.url)
        for entry in feed.entries:
            try:
                models.Trackable(
                    type=self.type,
                    score=0,
                    name=entry.title,
                    last_id=0
                ).save()
            except IntegrityError, e:
                pass

class MyAnimeListParser(object):
    def __init__(self, urllib=urllib2):
        self.urllib = urllib

    def parse(self, url):
        result = self.urllib.urlopen(url)
        content = result.read().decode('utf8')
        soup = BeautifulSoup(content)
        results = filter(
            lambda a: a != None, 
            map(lambda a: a.find("strong"), soup.findAll("a"))
        )
        results = map(lambda a: FeedEntry(a.contents[0]), results)
        return Feed(results)
