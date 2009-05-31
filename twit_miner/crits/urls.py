from django.conf.urls.defaults import *

urlpatterns = patterns('',
	#(r'^movies/?$', 'crits.views.movies_index', {}, 'movies'),
	url(r'^wiki/?(?P<page>.+)/?$', 'crits.views.wiki', name='wiki'),
	url(r'^pics/?(?P<query>.+)/?$', 'crits.views.pics', name='pictures'),
	url(r'^(?P<type>[^/]+)/?$', 'crits.views.type_index', name='types'),
	url(r'^(?P<type>[^/]+)/recommend/?$', 'crits.views.type_recommend', 
        name='types_recommend'),
)
