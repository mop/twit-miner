from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^movies/?$', 'crits.views.movies_index', {}, 'movies')
)
