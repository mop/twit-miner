import models
import wiki_fetcher
import picture_fetcher
import simplejson
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.cache import cache

SINGULAR_DICT = {
    'movies': 'movie',
    'animes': 'anime',
    'dvds':   'dvd',
    'music':  'music'
}

def type_index(request, type):
    objects = models.Trackable.ranking_by_type(SINGULAR_DICT[type])
    return render_to_response('%s/index.html' % type, {
        type: objects,
        'type': type 
    })

def type_recommend(request, type):
    obj_list = map(unicode.strip, request.GET[type].split(','))
    results = models.Trackable.recommend(SINGULAR_DICT[type], obj_list)
    return render_to_response('%s/recommend.html' % type, { 
        'objects': results,
        'type': type 
    })

def pics(request, query):
    query_list = []
    if 'queries' in request.GET:
        query_list = request.GET.getlist('queries')
    else:
        query_list = [query]
    result_dict = dict(map(_cached_thumbnail_fetch, query_list))
    json = simplejson.dumps({'result': result_dict})
    return HttpResponse(json, mimetype='application/json')

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

def _cached_thumbnail_fetch(title):
    result = cache.get('_pics_%s' % title)
    if not result:
        result = picture_fetcher.download_thumbnail(title)
        cache.set('_pics_%s' % title, result, 3600 * 5)
    return (title, result)
