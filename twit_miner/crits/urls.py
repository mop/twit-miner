from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^movies/?$', 'crits.views.movies_index', {}, 'movies'),
	(r'^wiki/?(?P<page>.+)/?$', 'crits.views.wiki', {}, 'wiki'),
	(r'^movies/recommend/?$', 'crits.views.movies_recommend', {}, 
        'movie_recommend')
)
