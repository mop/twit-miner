from django.conf.urls.defaults import *

import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
MEDIA_DIR   = CURRENT_DIR + '/public/'

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

ver = '%d.%d' % (sys.version_info[0], sys.version_info[1])

ADMIN_MEDIA_DIR = \
    '/usr/lib/python%s/site-packages/django/contrib/admin/media/' % ver

urlpatterns = patterns('',
    # Example:
    (r'^twit-miner/public/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': MEDIA_DIR, 'show_indexes': True }, 'public'),
    (r'^twit-miner/media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': ADMIN_MEDIA_DIR, 'show_indexes': True }, 
        'admin_static'),
    (r'^twit-miner/admin/(.*)', admin.site.root),
    url(r'^twit-miner/', include('twit_miner.crits.urls')),
    # (r'^twit_miner/', include('twit_miner.crits.urls')),
    # (r'^twit_miner/', include('twit_miner.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
)
