from __future__ import with_statement

import Image
import urllib2
import simplejson
import urllib as u
import StringIO
import os
import re
import math

from django.core.urlresolvers import reverse

thumbnail_size = (75, 75)

def fetch_query(query, urllib=urllib2):
    url = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s' % (
        u.quote(query)
    )
    result = urllib.urlopen(url)
    return simplejson.loads(result.read())

def fetch_image(url, urllib=urllib2, image_class=Image):
    try:
        result = urllib.urlopen(url)
        str = StringIO.StringIO(result.read())
        return image_class.open(str)
    except Exception, e:
        print e
        return None

def image_entropy(img):
    """calculate the entropy of an image"""
    hist = img.histogram()
    hist_size = sum(hist)
    hist = [float(h) / hist_size for h in hist]

    return -sum([p * math.log(p, 2) for p in hist if p != 0])

def square_y(img):
    """if the image is taller than it is wide, square it off. determine
    which pieces to cut off based on the entropy pieces."""
    x,y = img.size
    while y > x:
        #slice 10px at a time until square
        slice_height = min(y - x, 10)

        bottom = img.crop((0, y - slice_height, x, y))
        top = img.crop((0, 0, x, slice_height))

        #remove the slice with the least entropy
        if image_entropy(bottom) < image_entropy(top):
            img = img.crop((0, 0, x, y - slice_height))
        else:
            img = img.crop((0, slice_height, x, y))

        x,y = img.size
    return img

def square_x(img):
    x,y = img.size
    while x > y:
        #slice 10px at a time until square
        slice_width = min(x - y, 10)

        right = img.crop((x - slice_width, 0, x, y))
        left = img.crop((0, 0, slice_width, y))

        #remove the slice with the least entropy
        if image_entropy(right) < image_entropy(left):
            img = img.crop((0, 0, x - slice_width, y))
        else:
            img = img.crop((slice_width, 0, x, y))

        x,y = img.size
    return img

def square_image(img):
    """if the image is taller than it is wide, square it off. determine
    which pieces to cut off based on the entropy pieces."""
    x,y = img.size
    if y > x:
        return square_y(img)
    elif x > y:
        return square_x(img)
    return img

    
def resize_image(image, image_class=Image):
    image = square_image(image)
    image.thumbnail(thumbnail_size, image_class.ANTIALIAS)
    return image

def fetch_thumbnail(query, urllib=urllib2, image_class=Image):
    json_result = fetch_query(query, urllib=urllib)
    for result in json_result['responseData']['results']:
        url = result['unescapedUrl']
        image = fetch_image(url, urllib=urllib, image_class=image_class)
        if image: return resize_image(image)
    return None

def download_thumbnail(query, urllib=urllib2, image_class=Image):
    img = fetch_thumbnail(query, urllib=urllib, image_class=image_class)
    file_name = re.sub(' ', '_', query) + '.png'
    path = os.path.join(
        os.path.dirname(__file__), '..', 'public', 'downloads', file_name
    )

    with open(path, 'w') as fp:
        img.save(fp, format='png')
        return reverse('public', args=('downloads/%s' % file_name, ))
