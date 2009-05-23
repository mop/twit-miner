from django.conf.urls.defaults import *

import os

CURRENT_DIR = os.path.dirname(__file__)
MEDIA_DIR   = CURRENT_DIR + '/public/'

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^public/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': MEDIA_DIR, 'show_indexes': True }),
    (r'^', include('twit_miner.crits.urls')),
    # (r'^twit_miner/', include('twit_miner.crits.urls')),
    # (r'^twit_miner/', include('twit_miner.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
