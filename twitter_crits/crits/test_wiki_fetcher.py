from __future__ import with_statement

import os
import wiki_fetcher
import urllib

from django.test import TestCase
from mock import Mock
from BeautifulSoup import BeautifulSoup

class TestWikiFetcher(TestCase):
    def _read_test_page(self):
        file = os.path.join(os.path.dirname(__file__), 'wiki_site')
        with open(file, 'r') as fp:
            return fp.read()

    def setUp(self):
        self.title = 'Angels & Demons (film)'

        self.mock = Mock()
        self.request = self.mock.Request.return_value
        self.request.add_header.return_value = ''

        self.result_mock = Mock()
        self.result_mock.read.return_value = self._read_test_page()
        self.mock.urlopen.return_value = self.result_mock

        self.result = wiki_fetcher.fetch(self.title, fetch_lib=self.mock)
        

    def test_should_escape_url_correctly(self):
        args, dict = self.mock.Request.call_args
        url = 'http://en.wikipedia.org/wiki/%s' % (urllib.quote(self.title))
        self.assertEqual(url, args[0])

    def test_should_add_an_user_agent(self):
        args, dict = self.request.add_header.call_args
        self.assertEqual('User-agent', args[0])
        self.assertEqual('Mozilla/5.0', args[1])

    def test_should_call_urlopen_with_request(self):
        args, dict = self.mock.urlopen.call_args
        self.assertEqual(args[0], self.request)

    def test_should_read_response(self):
        self.assertTrue(self.result_mock.read.called)

    def test_should_return_first_paragraph(self):
        soup = BeautifulSoup(self._read_test_page())
        self.assertEqual(self.result, unicode(soup.first('p')))
