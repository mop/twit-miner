import models
import wiki_fetcher
import simplejson
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.cache import cache

# Create your views here.
def movies_index(request):
    objects = models.Trackable.ranking_by_type('movie')
    return render_to_response('movies/index.html', {
        'movies': objects,
    })

def movies_recommend(request):
    movie_list = map(unicode.strip, request.GET['movies'].split(','))
    results = models.Trackable.recommend('movie', movie_list)
    return render_to_response('movies/recommend.html', { 'objects': results })

def wiki(request, page):
    query_list = []
    if 'titles' in request.GET:
        query_list = request.GET.getlist('titles')
    else:
        query_list = [page]
    result_dict = dict(map(_cached_wiki_fetch, query_list))
    json = simplejson.dumps({'result': result_dict})
    return HttpResponse(json, mimetype='application/json')

def _cached_wiki_fetch(title):
    result = cache.get('_wiki_%s' % title)
    if not result:
        result = wiki_fetcher.fetch(title)
        cache.set('_wiki_%s' % title, result, 3600 * 5)
    return (title, result)
