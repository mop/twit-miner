import feedparser
import models
from django.db import IntegrityError

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
