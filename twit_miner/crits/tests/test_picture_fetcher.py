from __future__ import with_statement

import crits.picture_fetcher as picture_fetcher
import os
import urllib
import StringIO
import Image

from django.test import TestCase
from django.core.urlresolvers import reverse
from mock import Mock

class TestPictureFetcher(TestCase):
    def _read_test_page(self):
        file = os.path.join(os.path.dirname(__file__), 'picture_query_result')
        with open(file, 'r') as fp:
            return fp.read()

    def setUp(self):
        self.mock = Mock()
        self.request = self.mock.urlopen.return_value
        self.request.read.return_value = self._read_test_page()
        self.image_class = Mock()
        self.image_object = self.image_class.open.return_value

        self.old_square = picture_fetcher.square_image
        m = Mock()
        m.return_value = self.image_object
        picture_fetcher.square_image = m
        
        self.result = picture_fetcher.fetch_thumbnail(
            'test query', urllib=self.mock, image_class=self.image_class
        )

    def tearDown(self):
        picture_fetcher.square_image = self.old_square
        
    def test_should_return_thumbnail(self):
        self.assertEqual(self.image_object, self.result)

    def test_should_call_mock_with_correct_url(self):
        arg_list = self.mock.urlopen.call_args_list
        url = \
            'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s' % (
            urllib.quote('test query')
        )
        self.assertTrue(len(filter(lambda a: a[0][0] == url, arg_list)) > 0)

    def test_should_call_read(self):
        self.assertTrue(self.request.read.called)

    def test_should_call_urlopen_with_image_url(self):
        arg_list = self.mock.urlopen.call_args_list
        url = \
    'http://www.sswug.org/docimages/303570/MySQL%20SQLDataSource/test%20query.jpg'
        self.assertTrue(len(filter(lambda a: a[0][0] == url, arg_list)) > 0)

    def test_should_call_open_on_image_with_string_io(self):
        args, kwds = self.image_class.open.call_args
        self.assertTrue(isinstance(args[0], StringIO.StringIO))

    def test_should_call_thumbnail(self):
        self.assertTrue(self.image_object.thumbnail.called)

class TestPictureStorer(TestCase):
    def setUp(self):
        self.old_fetcher = picture_fetcher.fetch_thumbnail
        self.fetch_mock = Mock()
        self.fetch_mock.return_value = Image.new('RGB', (10, 10))
        picture_fetcher.fetch_thumbnail = self.fetch_mock

        self.path = os.path.dirname(__file__) + \
            '/../../public/downloads/the_thumbnail.png'

        self.result = picture_fetcher.download_thumbnail(
            'the thumbnail'
        )

    def tearDown(self):
        picture_fetcher.fetch_thumbnail = self.old_fetcher

    def test_should_save_the_image(self):
        self.assertTrue(os.path.exists(self.path))

    def test_should_return_the_url_to_the_image(self):
        self.assertEqual(
            reverse('public', args=('downloads/the_thumbnail.png',)),
            self.result
        )
