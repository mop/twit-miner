import models
import wiki_fetcher
import simplejson
from django.shortcuts import render_to_response
from django.http import HttpResponse

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
    result = wiki_fetcher.fetch(page)
    json = simplejson.dumps({'result': result})
    return HttpResponse(json, mimetype='application/json')
